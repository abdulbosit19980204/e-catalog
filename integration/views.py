from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import threading
from zeep import Client as ZeepClient, Settings
from zeep.cache import SqliteCache
from zeep.transports import Transport

from nomenklatura.models import Nomenklatura
from client.models import Client
from .models import Integration, IntegrationLog
from .serializers import (
    IntegrationSerializer,
    IntegrationSyncResponseSerializer,
    IntegrationSyncStatusSerializer,
)
import logging
import uuid
import time as time_module
from datetime import datetime
from decimal import Decimal, InvalidOperation
import json

logger = logging.getLogger(__name__)


def clean_value(value):
    """Ma'lumotlarni tozalash"""
    if not value or value in ["NULL", "None", "null", ""]:
        return None
    return str(value).strip()


def clean_boolean(value):
    """Boolean qiymatlarni tozalash va parse qilish"""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.strip().lower()
        if value in ["true", "1", "yes", "t"]:
            return True
        elif value in ["false", "0", "no", "f", "null", "none", ""]:
            return False
    # Integer uchun
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def clean_integer(value):
    """Integer qiymatlarni tozalash va parse qilish"""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        value = clean_value(value)
        if value is None:
            return None
        try:
            return int(float(value))  # Float orqali int qilish (1.0 -> 1)
        except (ValueError, TypeError):
            return None
    if isinstance(value, (float, Decimal)):
        return int(value)
    return None


def clean_decimal(value):
    """Decimal qiymatlarni tozalash va parse qilish"""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None
    if isinstance(value, str):
        value = clean_value(value)
        if value is None:
            return None
        try:
            return Decimal(value)
        except (InvalidOperation, ValueError):
            return None
    return None


def clean_date(value):
    """Date qiymatlarni tozalash va parse qilish"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        value = clean_value(value)
        if value is None:
            return None
        # Turli date formatlarni sinab ko'rish
        date_formats = [
            '%Y-%m-%d',
            '%d.%m.%Y',
            '%d/%m/%Y',
            '%Y.%m.%d',
            '%Y/%m/%d',
            '%d-%m-%Y',
        ]
        for fmt in date_formats:
            try:
                return datetime.strptime(value, fmt).date()
            except (ValueError, TypeError):
                continue
        return None
    return None


def clean_json(value):
    """JSON qiymatlarni tozalash va parse qilish"""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        value = clean_value(value)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None
    return None


def parse_client_item(item):
    """
    SOAP response'dan kelgan ClientItem'ni parse qilish
    Barcha mavjud fieldlarni dinamik tarzda parse qiladi
    """
    # Field mapping: SOAP field nomi -> DB field nomi
    field_mapping = {
        # Asosiy fieldlar
        'Code': 'client_code_1c',
        'Name': 'name',
        'Email': 'email',
        'Phone': 'phone',
        'Description': 'description',
        'is_delete': 'is_deleted',
        'is_active': 'is_active',
        
        # Company Information
        'CompanyName': 'company_name',
        'Company_Name': 'company_name',
        'TaxId': 'tax_id',
        'Tax_ID': 'tax_id',
        'INN': 'tax_id',
        'STIR': 'tax_id',
        'RegistrationNumber': 'registration_number',
        'Registration_Number': 'registration_number',
        'LegalAddress': 'legal_address',
        'Legal_Address': 'legal_address',
        'ActualAddress': 'actual_address',
        'Actual_Address': 'actual_address',
        
        # Contact Information
        'Fax': 'fax',
        'Website': 'website',
        'WebSite': 'website',
        'SocialMedia': 'social_media',
        'Social_Media': 'social_media',
        'AdditionalPhones': 'additional_phones',
        'Additional_Phones': 'additional_phones',
        
        # Business Information
        'Industry': 'industry',
        'BusinessType': 'business_type',
        'Business_Type': 'business_type',
        'EmployeeCount': 'employee_count',
        'Employee_Count': 'employee_count',
        'AnnualRevenue': 'annual_revenue',
        'Annual_Revenue': 'annual_revenue',
        'EstablishedDate': 'established_date',
        'Established_Date': 'established_date',
        
        # Financial Information
        'PaymentTerms': 'payment_terms',
        'Payment_Terms': 'payment_terms',
        'CreditLimit': 'credit_limit',
        'Credit_Limit': 'credit_limit',
        'Currency': 'currency',
        
        # Location Information
        'City': 'city',
        'Region': 'region',
        'Country': 'country',
        'PostalCode': 'postal_code',
        'Postal_Code': 'postal_code',
        
        # Contact Person
        'ContactPerson': 'contact_person',
        'Contact_Person': 'contact_person',
        'ContactPosition': 'contact_position',
        'Contact_Position': 'contact_position',
        'ContactEmail': 'contact_email',
        'Contact_Email': 'contact_email',
        'ContactPhone': 'contact_phone',
        'Contact_Phone': 'contact_phone',
        
        # Additional Information
        'Notes': 'notes',
        'Tags': 'tags',
        'Rating': 'rating',
        'Priority': 'priority',
        'Source': 'source',
        'Metadata': 'metadata',
    }
    
    # Field type mapping: qaysi fieldlar qanday type'ga convert qilinadi
    field_types = {
        # Boolean fields
        'is_deleted': clean_boolean,
        'is_active': clean_boolean,
        
        # Integer fields
        'employee_count': clean_integer,
        'priority': clean_integer,
        
        # Decimal fields
        'annual_revenue': clean_decimal,
        'credit_limit': clean_decimal,
        'rating': clean_decimal,
        
        # Date fields
        'established_date': clean_date,
        
        # JSON fields
        'social_media': clean_json,
        'additional_phones': clean_json,
        'tags': clean_json,
        'metadata': clean_json,
    }
    
    parsed_data = {}
    
    # Avval mapping'da belgilangan fieldlarni parse qilish
    for soap_field, db_field in field_mapping.items():
        try:
            # SOAP response'dan field'ni olish
            raw_value = getattr(item, soap_field, None)
            
            # Agar field mavjud bo'lsa
            if raw_value is not None:
                # Type conversion
                if db_field in field_types:
                    converted_value = field_types[db_field](raw_value)
                else:
                    # String fieldlar uchun
                    converted_value = clean_value(raw_value)
                
                if converted_value is not None:
                    parsed_data[db_field] = converted_value
        except Exception as e:
            logger.warning(f"Error parsing field {soap_field} -> {db_field}: {e}")
            continue
    
    # Qo'shimcha: SOAP response'dan kelgan barcha fieldlarni avtomatik aniqlash
    # (mapping'da bo'lmagan fieldlar uchun)
    try:
        # Zeep object'ning barcha attribute'larini olish
        if hasattr(item, '__dict__'):
            for attr_name in dir(item):
                # Private attribute'larni va mapping'da bo'lgan fieldlarni tashlab o'tish
                if attr_name.startswith('_') or attr_name in field_mapping:
                    continue
                
                try:
                    raw_value = getattr(item, attr_name, None)
                    
                    # Agar bu callable emas va None emas bo'lsa
                    if raw_value is not None and not callable(raw_value):
                        # DB field nomini aniqlash (snake_case ga o'tkazish)
                        db_field = attr_name.lower().replace(' ', '_')
                        
                        # Agar bu field Client modelida mavjud bo'lsa
                        if hasattr(Client, db_field):
                            # Type conversion
                            if db_field in field_types:
                                converted_value = field_types[db_field](raw_value)
                            else:
                                converted_value = clean_value(raw_value)
                            
                            if converted_value is not None:
                                parsed_data[db_field] = converted_value
                except Exception as e:
                    logger.debug(f"Error parsing additional field {attr_name}: {e}")
                    continue
    except Exception as e:
        logger.debug(f"Error getting additional fields from SOAP item: {e}")
    
    # Majburiy fieldlarni tekshirish
    if not parsed_data.get('client_code_1c') or not parsed_data.get('name'):
        return None
    
    return parsed_data


def get_zeep_client(wsdl_url):
    """1C Web Service client yaratish"""
    transport = Transport(cache=SqliteCache())
    zeep_settings = Settings(strict=False, xml_huge_tree=True)
    return ZeepClient(wsdl=wsdl_url, settings=zeep_settings, transport=transport)


def get_nomenklatura_from_1c(integration):
    """1C dan nomenklatura'lar ro'yxatini olish"""
    try:
        zeep_client = get_zeep_client(integration.wsdl_url)
        method = getattr(zeep_client.service, integration.method_nomenklatura)
        response = method()
        
        if hasattr(response, 'ProductItem'):
            return response.ProductItem
        elif isinstance(response, list):
            return response
        elif hasattr(response, 'TotalCount'):
            logger.info(f"TotalCount: {response.TotalCount}")
            return response.TotalCount
        else:
            return []
    except Exception as e:
        logger.error(f"Error fetching nomenklatura from 1C: {e}")
        return []


def get_clients_from_1c(integration):
    """1C dan client'lar ro'yxatini olish"""
    try:
        zeep_client = get_zeep_client(integration.wsdl_url)
        method = getattr(zeep_client.service, integration.method_clients)
        response = method()
        
        # SOAP response strukturasi: GetClientListResponse -> return -> ClientItem[]
        # Python'da 'return' reserved keyword, shuning uchun getattr ishlatamiz
        return_obj = getattr(response, 'return', None)
        if return_obj:
            if hasattr(return_obj, 'ClientItem'):
                items = return_obj.ClientItem
                # Agar bitta item bo'lsa, list qilamiz
                if not isinstance(items, list):
                    items = [items]
                return items
            elif isinstance(return_obj, list):
                return return_obj
        
        # Eski format uchun fallback
        if hasattr(response, 'ClientItem'):
            items = response.ClientItem
            if not isinstance(items, list):
                items = [items]
            return items
        elif isinstance(response, list):
            return response
        else:
            return []
    except Exception as e:
        logger.error(f"Error fetching clients from 1C: {e}")
        return []


def process_nomenklatura_chunk(items, integration, chunk_size=100, log_obj=None):
    """Nomenklatura chunk'larini batch qilib saqlash - bulk operations bilan optimallashtirilgan"""
    created_count = 0
    updated_count = 0
    error_count = 0
    
    from api.models import Project
    
    try:
        # Barcha itemlarni birinchi marta parse qilish
        parsed_items = []
        for item in items:
            try:
                code_1c = clean_value(getattr(item, 'Code', None))
                name = clean_value(getattr(item, 'Name', None))
                title = clean_value(getattr(item, 'Title', None))
                description = clean_value(getattr(item, 'Description', None))
                project_name = clean_value(getattr(item, 'Project', None))
                
                if not code_1c or not name:
                    error_count += 1
                    continue
                
                parsed_items.append({
                    'code_1c': code_1c,
                    'name': name,
                    'title': title,
                    'description': description,
                    'project_name': project_name,
                })
            except Exception as e:
                logger.error(f"Error parsing nomenklatura item: {e}")
                error_count += 1
                continue
        
        # Chunk'larga bo'lib ishlash - bulk operations bilan
        for i in range(0, len(parsed_items), chunk_size):
            chunk = parsed_items[i:i + chunk_size]
            
            try:
                with transaction.atomic():
                    # Barcha code_1c larni olish
                    codes_1c = [item['code_1c'] for item in chunk]
                    
                    # Mavjud nomenklatura'larni olish
                    existing_dict = {
                        obj.code_1c: obj 
                        for obj in Nomenklatura.objects.filter(
                            code_1c__in=codes_1c,
                            is_deleted=False
                        )
                    }
                    
                    # Project cache
                    project_cache = {}
                    default_project = integration.project
                    
                    to_create = []
                    to_update = []
                    
                    for item_data in chunk:
                        code_1c = item_data['code_1c']
                        project_name = item_data['project_name']
                        
                        # Project'ni topish yoki cache'dan olish
                        if project_name:
                            if project_name not in project_cache:
                                project_cache[project_name], _ = Project.objects.get_or_create(
                                    name=project_name,
                                    defaults={'code_1c': project_name, 'is_active': True, 'is_deleted': False}
                                )
                            project = project_cache[project_name]
                        else:
                            project = default_project
                        
                        if code_1c in existing_dict:
                            # Update
                            existing = existing_dict[code_1c]
                            existing.name = item_data['name']
                            existing.title = item_data['title']
                            existing.description = item_data['description']
                            existing.updated_at = timezone.now()
                            to_update.append(existing)
                        else:
                            # Create
                            to_create.append(Nomenklatura(
                                code_1c=code_1c,
                                name=item_data['name'],
                                title=item_data['title'],
                                description=item_data['description'],
                                is_active=True,
                                is_deleted=False
                            ))
                    
                    # Bulk operations
                    if to_create:
                        Nomenklatura.objects.bulk_create(to_create, ignore_conflicts=True)
                        created_count += len(to_create)
                    
                    if to_update:
                        Nomenklatura.objects.bulk_update(
                            to_update, 
                            ['name', 'title', 'description', 'updated_at'],
                            batch_size=chunk_size
                        )
                        updated_count += len(to_update)
                
                # Progress yangilash - har chunk'dan keyin
                if log_obj:
                    processed = min(i + chunk_size, len(parsed_items))
                    log_obj.processed_items = processed
                    log_obj.created_items = created_count
                    log_obj.updated_items = updated_count
                    log_obj.error_items = error_count
                    log_obj.status = 'processing'
                    # Retry mechanism bilan save
                    max_retries = 3
                    for retry in range(max_retries):
                        try:
                            log_obj.save(update_fields=['processed_items', 'created_items', 'updated_items', 'error_items', 'status'])
                            break
                        except Exception as save_error:
                            if retry == max_retries - 1:
                                logger.error(f"Failed to save log after {max_retries} retries: {save_error}")
                            else:
                                time_module.sleep(0.1 * (retry + 1))
                
            except Exception as e:
                logger.error(f"Error processing nomenklatura chunk batch: {e}")
                error_count += len(chunk)
                continue
    
    except Exception as e:
        logger.error(f"Error processing nomenklatura chunk: {e}")
        if log_obj:
            log_obj.status = 'error'
            log_obj.error_details = str(e)
            log_obj.end_time = timezone.now()
            try:
                log_obj.save(update_fields=['status', 'error_details', 'end_time'])
            except Exception:
                pass  # Ignore save errors in error handler
        raise
    
    return created_count, updated_count, error_count


def process_clients_chunk(items, integration, chunk_size=100, log_obj=None):
    """Client chunk'larini batch qilib saqlash - bulk operations bilan optimallashtirilgan"""
    created_count = 0
    updated_count = 0
    error_count = 0
    
    try:
        # Barcha itemlarni birinchi marta parse qilish
        parsed_items = []
        for item in items:
            try:
                # Barcha fieldlarni dinamik tarzda parse qilish
                parsed_data = parse_client_item(item)
                
                if not parsed_data:
                    error_count += 1
                    continue
                
                # Default qiymatlarni o'rnatish
                if 'is_deleted' not in parsed_data:
                    parsed_data['is_deleted'] = False
                if 'is_active' not in parsed_data:
                    parsed_data['is_active'] = True
                
                parsed_items.append(parsed_data)
            except Exception as e:
                logger.error(f"Error parsing client item: {e}")
                error_count += 1
                continue
        
        # Chunk'larga bo'lib ishlash - bulk operations bilan
        for i in range(0, len(parsed_items), chunk_size):
            chunk = parsed_items[i:i + chunk_size]
            
            try:
                with transaction.atomic():
                    # Barcha client_code_1c larni olish
                    codes_1c = [item['client_code_1c'] for item in chunk]
                    
                    # Mavjud client'larni olish - is_deleted=False bo'lganlarini ham olamiz
                    existing_dict = {
                        obj.client_code_1c: obj 
                        for obj in Client.objects.filter(
                            client_code_1c__in=codes_1c
                        )
                    }
                    
                    to_create = []
                    to_update = []
                    
                    for item_data in chunk:
                        client_code_1c = item_data['client_code_1c']
                        
                        if client_code_1c in existing_dict:
                            # Update - barcha fieldlarni yangilash
                            existing = existing_dict[client_code_1c]
                            
                            # Barcha fieldlarni yangilash
                            for field_name, field_value in item_data.items():
                                if hasattr(existing, field_name) and field_name not in ['id', 'created_at']:
                                    try:
                                        setattr(existing, field_name, field_value)
                                    except Exception as e:
                                        logger.warning(f"Error setting field {field_name} on client {client_code_1c}: {e}")
                            
                            existing.updated_at = timezone.now()
                            to_update.append(existing)
                        else:
                            # Create - barcha fieldlar bilan yaratish
                            try:
                                new_client = Client(**item_data)
                                to_create.append(new_client)
                            except Exception as e:
                                logger.error(f"Error creating client {client_code_1c}: {e}")
                                error_count += 1
                                continue
                    
                    # Bulk operations
                    if to_create:
                        Client.objects.bulk_create(to_create, ignore_conflicts=True)
                        created_count += len(to_create)
                    
                    if to_update:
                        # Barcha yangilanishi kerak bo'lgan fieldlarni aniqlash
                        # Client modelining barcha fieldlarini olish (auto fieldlar va foreign key'larni tashlab)
                        update_fields = set()
                        
                        # Birinchi client'dan barcha o'zgargan field nomlarini olish
                        sample_client = to_update[0]
                        for field in sample_client._meta.get_fields():
                            field_name = field.name
                            # Auto fieldlar, many-to-many va foreign key'larni tashlab o'tish
                            if (field_name not in ['id', 'created_at'] and 
                                not field.many_to_many and 
                                not (hasattr(field, 'related_model') and field.related_model)):
                                # Agar bu field Client modelida mavjud bo'lsa
                                if hasattr(Client, field_name):
                                    update_fields.add(field_name)
                        
                        # updated_at har doim qo'shiladi
                        update_fields.add('updated_at')
                        
                        # Agar update_fields bo'sh bo'lsa, default fieldlarni ishlatamiz
                        if not update_fields or len(update_fields) < 3:
                            update_fields = {
                                'name', 'email', 'phone', 'description', 
                                'is_deleted', 'is_active', 'updated_at',
                                'company_name', 'tax_id', 'registration_number',
                                'legal_address', 'actual_address', 'fax', 'website',
                                'social_media', 'additional_phones', 'industry',
                                'business_type', 'employee_count', 'annual_revenue',
                                'established_date', 'payment_terms', 'credit_limit',
                                'currency', 'city', 'region', 'country', 'postal_code',
                                'contact_person', 'contact_position', 'contact_email',
                                'contact_phone', 'notes', 'tags', 'rating', 'priority',
                                'source', 'metadata'
                            }
                        
                        Client.objects.bulk_update(
                            to_update, 
                            list(update_fields),
                            batch_size=chunk_size
                        )
                        updated_count += len(to_update)
                
                # Progress yangilash - har chunk'dan keyin
                if log_obj:
                    processed = min(i + chunk_size, len(parsed_items))
                    log_obj.processed_items = processed
                    log_obj.created_items = created_count
                    log_obj.updated_items = updated_count
                    log_obj.error_items = error_count
                    log_obj.status = 'processing'
                    # Retry mechanism bilan save
                    max_retries = 3
                    for retry in range(max_retries):
                        try:
                            log_obj.save(update_fields=['processed_items', 'created_items', 'updated_items', 'error_items', 'status'])
                            break
                        except Exception as save_error:
                            if retry == max_retries - 1:
                                logger.error(f"Failed to save log after {max_retries} retries: {save_error}")
                            else:
                                time_module.sleep(0.1 * (retry + 1))
                
            except Exception as e:
                logger.error(f"Error processing clients chunk batch: {e}")
                error_count += len(chunk)
                continue
    
    except Exception as e:
        logger.error(f"Error processing clients chunk: {e}")
        if log_obj:
            log_obj.status = 'error'
            log_obj.error_details = str(e)
            log_obj.end_time = timezone.now()
            try:
                log_obj.save(update_fields=['status', 'error_details', 'end_time'])
            except Exception:
                pass  # Ignore save errors in error handler
        raise
    
    return created_count, updated_count, error_count


def sync_nomenklatura_async(integration_id, task_id):
    """Nomenklatura'larni async tarzda yuklab olish"""
    integration = Integration.objects.get(id=integration_id)
    log_obj = IntegrationLog.objects.get(task_id=task_id)
    
    try:
        log_obj.status = 'fetching'
        log_obj.save(update_fields=['status'])
        
        # 1C dan ma'lumotlarni olish
        items = get_nomenklatura_from_1c(integration)
        
        if not items:
            log_obj.status = 'completed'
            log_obj.end_time = timezone.now()
            log_obj.message = 'No data found in 1C'
            log_obj.save(update_fields=['status', 'end_time', 'message'])
            return
        
        log_obj.total_items = len(items)
        log_obj.status = 'processing'
        log_obj.save(update_fields=['total_items', 'status'])
        
        # Chunk'larga bo'lib ishlash
        created, updated, errors = process_nomenklatura_chunk(
            items,
            integration,
            chunk_size=integration.chunk_size,
            log_obj=log_obj
        )
        
        log_obj.status = 'completed'
        log_obj.end_time = timezone.now()
        log_obj.processed_items = len(items)
        log_obj.created_items = created
        log_obj.updated_items = updated
        log_obj.error_items = errors
        log_obj.message = f'Completed: {created} created, {updated} updated, {errors} errors'
        log_obj.save(update_fields=['status', 'end_time', 'processed_items', 'created_items', 'updated_items', 'error_items', 'message'])
        
        # Invalidate cache after sync
        cache.clear()
    except Exception as e:
        logger.error(f"Error in sync_nomenklatura_async: {e}")
        log_obj.status = 'error'
        log_obj.error_details = str(e)
        log_obj.end_time = timezone.now()
        log_obj.save(update_fields=['status', 'error_details', 'end_time'])


def sync_clients_async(integration_id, task_id):
    """Client'larni async tarzda yuklab olish"""
    integration = Integration.objects.get(id=integration_id)
    log_obj = IntegrationLog.objects.get(task_id=task_id)
    
    try:
        log_obj.status = 'fetching'
        log_obj.save(update_fields=['status'])
        
        # 1C dan ma'lumotlarni olish
        items = get_clients_from_1c(integration)
        
        if not items:
            log_obj.status = 'completed'
            log_obj.end_time = timezone.now()
            log_obj.message = 'No data found in 1C'
            log_obj.save(update_fields=['status', 'end_time', 'message'])
            return
        
        log_obj.total_items = len(items)
        log_obj.status = 'processing'
        log_obj.save(update_fields=['total_items', 'status'])
        
        # Chunk'larga bo'lib ishlash
        created, updated, errors = process_clients_chunk(
            items,
            integration,
            chunk_size=integration.chunk_size,
            log_obj=log_obj
        )
        
        log_obj.status = 'completed'
        log_obj.end_time = timezone.now()
        log_obj.processed_items = len(items)
        log_obj.created_items = created
        log_obj.updated_items = updated
        log_obj.error_items = errors
        log_obj.message = f'Completed: {created} created, {updated} updated, {errors} errors'
        log_obj.save(update_fields=['status', 'end_time', 'processed_items', 'created_items', 'updated_items', 'error_items', 'message'])
        
        # Invalidate cache after sync
        cache.clear()
    except Exception as e:
        logger.error(f"Error in sync_clients_async: {e}")
        log_obj.status = 'error'
        log_obj.error_details = str(e)
        log_obj.end_time = timezone.now()
        log_obj.save(update_fields=['status', 'error_details', 'end_time'])


@extend_schema(
    tags=['Integration'],
    summary="1C dan nomenklatura ma'lumotlarini sync qilishni boshlash",
    description=(
        "Integration sozlamasidagi WSDL va method ma'lumotlari asosida 1C dan nomenklatura"
        " ma'lumotlarini fon rejimida yuklashni boshlaydi. Jarayon tugaguncha `task_id`"
        " orqali `GET /api/v1/integration/sync-status/{task_id}/` endpointiga murojaat qilib"
        " progressni kuzatish mumkin."
    ),
    request=None,
    responses={
        202: IntegrationSyncResponseSerializer,
        401: OpenApiResponse(description="Authentication talab qilinadi"),
        404: OpenApiResponse(description="Integration topilmadi yoki faol emas"),
    },
    examples=[
        OpenApiExample(
            name="Curl misoli",
            value="curl -X POST http://localhost:8000/api/v1/integration/1/sync-nomenklatura/ "
            "-H \"Authorization: Bearer <access_token>\"",
        )
    ],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_nomenklatura_from_1c(request, integration_id):
    """1C dan nomenklatura'larni yuklab olish (async)"""
    integration = get_object_or_404(Integration, id=integration_id, is_active=True, is_deleted=False)
    task_id = str(uuid.uuid4())
    
    # Log yaratish
    log_obj = IntegrationLog.objects.create(
        integration=integration,
        task_id=task_id,
        sync_type='nomenklatura',
        status='fetching'
    )
    
    # Background thread'da ishlash - threading (django-q2 Django 5.2 bilan mos kelmaydi)
    thread = threading.Thread(target=sync_nomenklatura_async, args=(integration.id, task_id))
    thread.daemon = True
    thread.start()
    
    return Response(
        {
            'task_id': task_id,
            'status': 'started',
            'message': f'Nomenklatura sync started for {integration.name}',
            'integration': {
                'id': integration.id,
                'name': integration.name,
                'project': integration.project.name,
            },
        },
        status=status.HTTP_202_ACCEPTED,
    )


@extend_schema(
    tags=['Integration'],
    summary="1C dan client ma'lumotlarini sync qilishni boshlash",
    description=(
        "Integration sozlamasidagi WSDL va method ma'lumotlari asosida 1C dan client"
        " ma'lumotlarini fon rejimida yuklashni boshlaydi. Jarayon tugaguncha `task_id`"
        " orqali `GET /api/v1/integration/sync-status/{task_id}/` endpointiga murojaat qilib"
        " progressni kuzatish mumkin."
    ),
    request=None,
    responses={
        202: IntegrationSyncResponseSerializer,
        401: OpenApiResponse(description="Authentication talab qilinadi"),
        404: OpenApiResponse(description="Integration topilmadi yoki faol emas"),
    },
    examples=[
        OpenApiExample(
            name="HTTPie misoli",
            value="http POST http://localhost:8000/api/v1/integration/1/sync-clients/ "
            "Authorization:\"Bearer <access_token>\"",
        )
    ],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_clients_from_1c(request, integration_id):
    """1C dan client'larni yuklab olish (async)"""
    integration = get_object_or_404(Integration, id=integration_id, is_active=True, is_deleted=False)
    task_id = str(uuid.uuid4())
    
    # Log yaratish
    log_obj = IntegrationLog.objects.create(
        integration=integration,
        task_id=task_id,
        sync_type='clients',
        status='fetching'
    )
    
    # Background thread'da ishlash - threading (django-q2 Django 5.2 bilan mos kelmaydi)
    thread = threading.Thread(target=sync_clients_async, args=(integration.id, task_id))
    thread.daemon = True
    thread.start()
    
    return Response(
        {
            'task_id': task_id,
            'status': 'started',
            'message': f'Clients sync started for {integration.name}',
            'integration': {
                'id': integration.id,
                'name': integration.name,
                'project': integration.project.name,
            },
        },
        status=status.HTTP_202_ACCEPTED,
    )


@extend_schema(
    tags=['Integration'],
    summary="1C sync jarayonining statusini olish",
    description=(
        "`task_id` bo'yicha fon sinxronizatsiya log'ini qaytaradi. Agar jarayon hali ham"
        " davom etayotgan bo'lsa, `progress_percent` maydoni orqali qancha qismi"
        " bajarilganini kuzatish mumkin."
    ),
    request=None,
    responses={
        200: IntegrationSyncStatusSerializer,
        401: OpenApiResponse(description="Authentication talab qilinadi"),
        404: OpenApiResponse(description="Berilgan task_id bo'yicha log topilmadi"),
    },
    examples=[
        OpenApiExample(
            name="Statusni olish",
            value="http GET http://localhost:8000/api/v1/integration/sync-status/afb9d96e-... "
            "Authorization:\"Bearer <access_token>\"",
        )
    ],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sync_status(request, task_id):
    """Sync progress'ni olish"""
    try:
        log_obj = IntegrationLog.objects.get(task_id=task_id)
        return Response(
            {
                'task_id': log_obj.task_id,
                'integration': {
                    'id': log_obj.integration.id,
                    'name': log_obj.integration.name,
                    'project': log_obj.integration.project.name,
                },
                'sync_type': log_obj.sync_type,
                'status': log_obj.status,
                'total': log_obj.total,
                'processed': log_obj.processed,
                'created': log_obj.created,
                'updated': log_obj.updated,
                'errors': log_obj.errors,
                'progress_percent': log_obj.progress_percent,
                'error_message': log_obj.error_details,
                'started_at': log_obj.start_time,
                'completed_at': log_obj.end_time,
            }
        )
    except IntegrationLog.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    tags=['Integration'],
    summary="Integration sozlamalarini ro'yxatini olish",
    description=(
        "Aktiv va o'chirilmagan integration yozuvlari ro'yxatini qaytaradi. Har bir integration"
        " project bilan bog'langan bo'lib, 1C web-servis parametrlari va sync konfiguratsiyasini"
        " o'z ichiga oladi."
    ),
    request=None,
    responses={
        200: IntegrationSerializer(many=True),
        401: OpenApiResponse(description="Authentication talab qilinadi"),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_integrations(request):
    """Integration'lar ro'yxatini olish"""
    integrations = Integration.objects.filter(
        is_deleted=False
    ).select_related('project').order_by('-created_at')
    
    serializer = IntegrationSerializer(integrations, many=True, context={'request': request})
    return Response(serializer.data)
