from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
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

logger = logging.getLogger(__name__)


def clean_value(value):
    """Ma'lumotlarni tozalash"""
    if not value or value in ["NULL", "None", "null", ""]:
        return None
    return str(value).strip()


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
        
        if hasattr(response, 'ClientItem'):
            return response.ClientItem
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
                client_code_1c = clean_value(getattr(item, 'Code', None))
                name = clean_value(getattr(item, 'Name', None))
                email = clean_value(getattr(item, 'Email', None))
                phone = clean_value(getattr(item, 'Phone', None))
                description = clean_value(getattr(item, 'Description', None))
                
                if not client_code_1c or not name:
                    error_count += 1
                    continue
                
                parsed_items.append({
                    'client_code_1c': client_code_1c,
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'description': description,
                })
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
                    
                    # Mavjud client'larni olish
                    existing_dict = {
                        obj.client_code_1c: obj 
                        for obj in Client.objects.filter(
                            client_code_1c__in=codes_1c,
                            is_deleted=False
                        )
                    }
                    
                    to_create = []
                    to_update = []
                    
                    for item_data in chunk:
                        client_code_1c = item_data['client_code_1c']
                        
                        if client_code_1c in existing_dict:
                            # Update
                            existing = existing_dict[client_code_1c]
                            existing.name = item_data['name']
                            existing.email = item_data['email']
                            existing.phone = item_data['phone']
                            existing.description = item_data['description']
                            existing.updated_at = timezone.now()
                            to_update.append(existing)
                        else:
                            # Create
                            to_create.append(Client(
                                client_code_1c=client_code_1c,
                                name=item_data['name'],
                                email=item_data['email'],
                                phone=item_data['phone'],
                                description=item_data['description'],
                                is_active=True,
                                is_deleted=False
                            ))
                    
                    # Bulk operations
                    if to_create:
                        Client.objects.bulk_create(to_create, ignore_conflicts=True)
                        created_count += len(to_create)
                    
                    if to_update:
                        Client.objects.bulk_update(
                            to_update, 
                            ['name', 'email', 'phone', 'description', 'updated_at'],
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
    
    # Background thread'da ishlash
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
    
    # Background thread'da ishlash
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
