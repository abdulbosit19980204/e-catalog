from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, OperationalError
import random
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


def get_zeep_client(wsdl_url, username=None, password=None):
    """1C Web Service client yaratish"""
    import requests
    from requests.auth import HTTPBasicAuth
    
    session = requests.Session()
    if username and password:
        session.auth = HTTPBasicAuth(username, password)
    
    transport = Transport(cache=SqliteCache(), session=session)
    zeep_settings = Settings(strict=False, xml_huge_tree=True)
    return ZeepClient(wsdl=wsdl_url, settings=zeep_settings, transport=transport)


def get_nomenklatura_from_1c(integration):
    """1C dan nomenklatura'lar ro'yxatini olish"""
    try:
        zeep_client = get_zeep_client(
            integration.wsdl_url, 
            username=integration.username, 
            password=integration.password
        )
        method = getattr(zeep_client.service, integration.method_nomenklatura)
        response = method()
        
        # SOAP response strukturasi: GetProductListResponse -> return -> ProductItem[]
        return_obj = getattr(response, 'return', None)
        if return_obj:
            if hasattr(return_obj, 'ProductItem'):
                return return_obj.ProductItem
            elif isinstance(return_obj, list):
                return return_obj
        
        # Fallback formatlar
        if hasattr(response, 'ProductItem'):
            return response.ProductItem
        elif isinstance(response, list):
            return response
        elif hasattr(response, 'TotalCount'):
            logger.info(f"Nomenklatura TotalCount from 1C: {response.TotalCount}")
            return []
        else:
            logger.warning(f"Unexpected nomenklatura response structure: {type(response)}")
            return []
    except Exception as e:
        logger.error(f"Error fetching nomenklatura from 1C: {e}")
        return []


def get_clients_from_1c(integration):
    """1C dan client'lar ro'yxatini olish"""
    try:
        zeep_client = get_zeep_client(
            integration.wsdl_url, 
            username=integration.username, 
            password=integration.password
        )
        method = getattr(zeep_client.service, integration.method_clients)
        response = method()
        
        # SOAP response strukturasi: GetClientListResponse -> return -> ClientItem[]
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
        elif hasattr(response, 'TotalCount'):
            logger.info(f"Clients TotalCount from 1C: {response.TotalCount}")
            return []
        else:
            logger.warning(f"Unexpected client response structure: {type(response)}")
            return []
    except Exception as e:
        logger.error(f"Error fetching clients from 1C: {e}")
        return []


def process_nomenklatura_chunk(items, integration, chunk_size=50, log_obj=None):
    """Nomenklatura chunk'larini project-scoped unique constraint bilan saqlash
    
    Optimized for concurrency:
    - Small chunk_size (50) to reduce lock duration
    - Delays between chunks to allow other queries
    - Aggressive retry with exponential backoff
    """
    created_count = 0
    updated_count = 0
    error_count = 0
    
    try:
        # Barcha itemlarni parse qilish
        parsed_items = []
        for item in items:
            try:
                code_1c = clean_value(getattr(item, 'Code', None))
                name = clean_value(getattr(item, 'Name', None))
                title = clean_value(getattr(item, 'Title', None))
                description = clean_value(getattr(item, 'Description', None))
                
                if not code_1c or not name:
                    error_count += 1
                    continue
                
                parsed_items.append({
                    'code_1c': code_1c,
                    'name': name,
                    'title': title,
                    'description': description,
                })
            except Exception as e:
                logger.error(f"Error parsing nomenklatura item: {e}")
                error_count += 1
                continue
        
        # Chunk'larga bo'lib ishlash - kichik chunk'lar
        for i in range(0, len(parsed_items), chunk_size):
            chunk = parsed_items[i:i + chunk_size]
            
            # Har bir chunk'dan oldin kichik delay - user API'larga imkon berish
            if i > 0:
                time_module.sleep(0.05)  # 50ms delay between chunks
            
            try:
                # Retry logic for database locks
                max_db_retries = 10  # Ko'proq retry
                for db_retry in range(max_db_retries):
                    try:
                        # Har bir item uchun update_or_create
                        for item_data in chunk:
                            try:
                                # update_or_create - atomic operation
                                obj, created = Nomenklatura.objects.update_or_create(
                                    project=integration.project,
                                    code_1c=item_data['code_1c'],
                                    defaults={
                                        'name': item_data['name'],
                                        'title': item_data['title'],
                                        'description': item_data['description'],
                                        'is_active': True,
                                        'is_deleted': False,
                                    }
                                )
                                if created:
                                    created_count += 1
                                else:
                                    updated_count += 1
                                    
                                # Micro-delay har 10 itemdan keyin - concurrency uchun
                                if (created_count + updated_count) % 10 == 0:
                                    time_module.sleep(0.01)  # 10ms
                                    
                            except Exception as e:
                                logger.error(f"Error processing nomenklatura {item_data.get('code_1c')}: {e}")
                                error_count += 1
                        
                        # Muvaffaqiyatli - retry loop'dan chiqish
                        break
                        
                    except OperationalError as e:
                        if "database is locked" in str(e).lower() and db_retry < max_db_retries - 1:
                            # Exponential backoff - har retry'da ko'proq kutish
                            wait_time = random.uniform(0.1, 0.5) * (2 ** db_retry)
                            logger.warning(f"Database locked, retrying in {wait_time:.2f}s (attempt {db_retry+1}/{max_db_retries})")
                            time_module.sleep(wait_time)
                            continue
                        else:
                            raise e
                
                # Progress yangilash
                if log_obj:
                    processed = min(i + chunk_size, len(parsed_items))
                    log_obj.processed_items = processed
                    log_obj.created_items = created_count
                    log_obj.updated_items = updated_count
                    log_obj.error_items = error_count
                    log_obj.status = 'processing'
                    
                    # Retry bilan save
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
                pass
        raise
    
    return created_count, updated_count, error_count


def process_clients_chunk(items, integration, chunk_size=50, log_obj=None):
    """Client chunk'larini project-scoped unique constraint bilan saqlash
    
    Optimized for concurrency:
    - Small chunk_size (50) to reduce lock duration
    - Delays between chunks to allow other queries
    - Aggressive retry with exponential backoff
    """
    created_count = 0
    updated_count = 0
    error_count = 0
    
    try:
        # Barcha itemlarni parse qilish
        parsed_items = []
        for item in items:
            try:
                parsed_data = parse_client_item(item)
                
                if not parsed_data:
                    error_count += 1
                    continue
                
                if 'is_deleted' not in parsed_data:
                    parsed_data['is_deleted'] = False
                if 'is_active' not in parsed_data:
                    parsed_data['is_active'] = True
                
                parsed_items.append(parsed_data)
            except Exception as e:
                logger.error(f"Error parsing client item: {e}")
                error_count += 1
                continue
        
        # Chunk'larga bo'lib ishlash - kichik chunk'lar
        for i in range(0, len(parsed_items), chunk_size):
            chunk = parsed_items[i:i + chunk_size]
            
            # Har bir chunk'dan oldin kichik delay - user API'larga imkon berish
            if i > 0:
                time_module.sleep(0.05)  # 50ms delay between chunks
            
            try:
                # Retry logic for database locks
                max_db_retries = 10  # Ko'proq retry
                for db_retry in range(max_db_retries):
                    try:
                        # Har bir item uchun update_or_create
                        for item_data in chunk:
                            try:
                                client_code_1c = item_data.pop('client_code_1c')
                                
                                # update_or_create - atomic operation
                                obj, created = Client.objects.update_or_create(
                                    project=integration.project,
                                    client_code_1c=client_code_1c,
                                    defaults=item_data
                                )
                                if created:
                                    created_count += 1
                                else:
                                    updated_count += 1
                                    
                                # Micro-delay har 10 itemdan keyin - concurrency uchun
                                if (created_count + updated_count) % 10 == 0:
                                    time_module.sleep(0.01)  # 10ms
                                    
                            except Exception as e:
                                logger.error(f"Error processing client {item_data.get('client_code_1c', 'Unknown')}: {e}")
                                error_count += 1
                        
                        # Muvaffaqiyatli - retry loop'dan chiqish
                        break
                        
                    except OperationalError as e:
                        if "database is locked" in str(e).lower() and db_retry < max_db_retries - 1:
                            # Exponential backoff - har retry'da ko'proq kutish
                            wait_time = random.uniform(0.1, 0.5) * (2 ** db_retry)
                            logger.warning(f"Database locked, retrying in {wait_time:.2f}s (attempt {db_retry+1}/{max_db_retries})")
                            time_module.sleep(wait_time)
                            continue
                        else:
                            raise e
                
                # Progress yangilash
                if log_obj:
                    processed = min(i + chunk_size, len(parsed_items))
                    log_obj.processed_items = processed
                    log_obj.created_items = created_count
                    log_obj.updated_items = updated_count
                    log_obj.error_items = error_count
                    log_obj.status = 'processing'
                    
                    # Retry bilan save
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
