from django.shortcuts import render
from nomenklatura.models import Nomenklatura, NomenklaturaImage
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .serializers import NomenklaturaSerializer, NomenklaturaImageSerializer

class NomenklaturaViewSet(viewsets.ModelViewSet):
    queryset = Nomenklatura.objects.filter(is_deleted=False)
    serializer_class = NomenklaturaSerializer
    lookup_field = 'code_1c'
    filterset_fields = ['code_1c', 'name']
    search_fields = ['code_1c', 'name']
    
    def get_queryset(self):
        """Optimizatsiya: prefetch_related bilan images yuklash - N+1 query muammosini hal qiladi"""
        return Nomenklatura.objects.filter(
            is_deleted=False
        ).prefetch_related('images').order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class NomenklaturaImageViewSet(viewsets.ModelViewSet):
    queryset = NomenklaturaImage.objects.filter(is_deleted=False)
    serializer_class = NomenklaturaImageSerializer
    filterset_fields = ['nomenklatura', 'is_main']
    search_fields = ['nomenklatura__code_1c', 'nomenklatura__name']
    
    def get_queryset(self):
        """Optimizatsiya: select_related bilan nomenklatura yuklash - N+1 query muammosini hal qiladi"""
        return NomenklaturaImage.objects.filter(
            is_deleted=False
        ).select_related('nomenklatura').order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['post'], url_path='bulk-upload')
    def bulk_upload(self, request):
        """Bir vaqtda bir nechta rasm yuklash"""
        nomenklatura_code = request.data.get('nomenklatura')
        if not nomenklatura_code:
            return Response(
                {'error': 'nomenklatura code_1c talab qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            nomenklatura = Nomenklatura.objects.get(code_1c=nomenklatura_code, is_deleted=False)
        except Nomenklatura.DoesNotExist:
            return Response(
                {'error': 'Nomenklatura topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        images = request.FILES.getlist('images')
        if not images:
            return Response(
                {'error': 'Rasmlar talab qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_images = []
        for image in images:
            image_obj = NomenklaturaImage.objects.create(
                nomenklatura=nomenklatura,
                image=image,
                is_main=False,
                is_active=True,
                is_deleted=False
            )
            serializer = NomenklaturaImageSerializer(image_obj, context={'request': request})
            created_images.append(serializer.data)
        
        return Response({
            'message': f'{len(created_images)} ta rasm muvaffaqiyatli yuklandi',
            'images': created_images
        }, status=status.HTTP_201_CREATED)
