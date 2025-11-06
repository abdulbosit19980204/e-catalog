from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
import threading
from zeep import Client as ZeepClient, Settings
from zeep.cache import SqliteCache
from zeep.transports import Transport

from nomenklatura.models import Nomenklatura
from client.models import Client
from .models import Integration, IntegrationLog
from .serializers import IntegrationSerializer
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
    """Nomenklatura chunk'larini batch qilib saqlash - project'ga tegishli"""
    created_count = 0
    updated_count = 0
    error_count = 0
    
    try:
        with transaction.atomic():
            for i in range(0, len(items), chunk_size):
                chunk = items[i:i + chunk_size]
                
                for item in chunk:
                    try:
                        code_1c = clean_value(getattr(item, 'Code', None))
                        name = clean_value(getattr(item, 'Name', None))
                        title = clean_value(getattr(item, 'Title', None))
                        description = clean_value(getattr(item, 'Description', None))
                        project_name = clean_value(getattr(item, 'Project', None))
                        
                        if not code_1c or not name:
                            error_count += 1
                            continue
                        
                        # Project'ga tegishli ekanligini tekshirish
                        # Agar 1C dan project nomi kelsa, uni tekshirish
                        # Yoki integration'ning project'iga tegishli deb belgilash
                        from api.models import Project
                        
                        # 1C dan project nomi kelsa, uni topish yoki integration project'ini ishlatish
                        if project_name:
                            project, _ = Project.objects.get_or_create(
                                name=project_name,
                                defaults={'code_1c': project_name, 'is_active': True, 'is_deleted': False}
                            )
                        else:
                            # Integration'ning project'ini ishlatish
                            project = integration.project
                        
                        # Nomenklatura'ni saqlash yoki yangilash
                        existing = Nomenklatura.objects.filter(
                            code_1c=code_1c,
                            is_deleted=False
                        ).first()
                        
                        if existing:
                            existing.name = name
                            existing.title = title
                            existing.description = description
                            existing.updated_at = timezone.now()
                            existing.save(update_fields=['name', 'title', 'description', 'updated_at'])
                            updated_count += 1
                        else:
                            Nomenklatura.objects.create(
                                code_1c=code_1c,
                                name=name,
                                title=title,
                                description=description,
                                is_active=True,
                                is_deleted=False
                            )
                            created_count += 1
                    except Exception as e:
                        logger.error(f"Error processing nomenklatura item: {e}")
                        error_count += 1
                        continue
                
                # Progress yangilash
                if log_obj:
                    processed = min(i + chunk_size, len(items))
                    log_obj.processed_items = processed
                    log_obj.created_items = created_count
                    log_obj.updated_items = updated_count
                    log_obj.error_items = error_count
                    log_obj.status = 'processing'
                    log_obj.save(update_fields=['processed_items', 'created_items', 'updated_items', 'error_items', 'status'])
                
                # Kichik pauza - database yukini kamaytirish
                time_module.sleep(0.1)
    
    except Exception as e:
        logger.error(f"Error processing nomenklatura chunk: {e}")
        if log_obj:
            log_obj.status = 'error'
            log_obj.error_details = str(e)
            log_obj.end_time = timezone.now()
            log_obj.save(update_fields=['status', 'error_details', 'end_time'])
        raise
    
    return created_count, updated_count, error_count


def process_clients_chunk(items, integration, chunk_size=100, log_obj=None):
    """Client chunk'larini batch qilib saqlash - project'ga tegishli"""
    created_count = 0
    updated_count = 0
    error_count = 0
    
    try:
        with transaction.atomic():
            for i in range(0, len(items), chunk_size):
                chunk = items[i:i + chunk_size]
                
                for item in chunk:
                    try:
                        client_code_1c = clean_value(getattr(item, 'Code', None))
                        name = clean_value(getattr(item, 'Name', None))
                        email = clean_value(getattr(item, 'Email', None))
                        phone = clean_value(getattr(item, 'Phone', None))
                        description = clean_value(getattr(item, 'Description', None))
                        project_name = clean_value(getattr(item, 'Project', None))
                        
                        if not client_code_1c or not name:
                            error_count += 1
                            continue
                        
                        # Client'ni saqlash yoki yangilash
                        existing = Client.objects.filter(
                            client_code_1c=client_code_1c,
                            is_deleted=False
                        ).first()
                        
                        if existing:
                            existing.name = name
                            existing.email = email
                            existing.phone = phone
                            existing.description = description
                            existing.updated_at = timezone.now()
                            existing.save(update_fields=['name', 'email', 'phone', 'description', 'updated_at'])
                            updated_count += 1
                        else:
                            Client.objects.create(
                                client_code_1c=client_code_1c,
                                name=name,
                                email=email,
                                phone=phone,
                                description=description,
                                is_active=True,
                                is_deleted=False
                            )
                            created_count += 1
                    except Exception as e:
                        logger.error(f"Error processing client item: {e}")
                        error_count += 1
                        continue
                
                # Progress yangilash
                if log_obj:
                    processed = min(i + chunk_size, len(items))
                    log_obj.processed_items = processed
                    log_obj.created_items = created_count
                    log_obj.updated_items = updated_count
                    log_obj.error_items = error_count
                    log_obj.status = 'processing'
                    log_obj.save(update_fields=['processed_items', 'created_items', 'updated_items', 'error_items', 'status'])
                
                # Kichik pauza - database yukini kamaytirish
                time_module.sleep(0.1)
    
    except Exception as e:
        logger.error(f"Error processing clients chunk: {e}")
        if log_obj:
            log_obj.status = 'error'
            log_obj.error_details = str(e)
            log_obj.end_time = timezone.now()
            log_obj.save(update_fields=['status', 'error_details', 'end_time'])
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
    
    return Response({
        'task_id': task_id,
        'status': 'started',
        'message': f'Nomenklatura sync started for {integration.name}',
        'integration': {
            'id': integration.id,
            'name': integration.name,
            'project': integration.project.name
        }
    }, status=status.HTTP_202_ACCEPTED)


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
    
    return Response({
        'task_id': task_id,
        'status': 'started',
        'message': f'Clients sync started for {integration.name}',
        'integration': {
            'id': integration.id,
            'name': integration.name,
            'project': integration.project.name
        }
    }, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sync_status(request, task_id):
    """Sync progress'ni olish"""
    try:
        log_obj = IntegrationLog.objects.get(task_id=task_id)
        return Response({
            'task_id': log_obj.task_id,
            'integration': {
                'id': log_obj.integration.id,
                'name': log_obj.integration.name,
                'project': log_obj.integration.project.name
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
            'completed_at': log_obj.end_time
        })
    except IntegrationLog.DoesNotExist:
        return Response({
            'error': 'Task not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_integrations(request):
    """Integration'lar ro'yxatini olish"""
    integrations = Integration.objects.filter(
        is_deleted=False
    ).select_related('project').order_by('-created_at')
    
    serializer = IntegrationSerializer(integrations, many=True)
    return Response(serializer.data)
