from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Client, ClientImage
from .serializers import ClientSerializer, ClientImageSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.filter(is_deleted=False)
    serializer_class = ClientSerializer
    lookup_field = 'client_code_1c'
    filterset_fields = ['client_code_1c', 'name', 'email']
    search_fields = ['client_code_1c', 'name', 'email']
    permission_classes = [IsAuthenticated]  # Faqat authenticated user'lar uchun
    
    def get_queryset(self):
        """Optimizatsiya: prefetch_related bilan images yuklash - N+1 query muammosini hal qiladi"""
        return Client.objects.filter(
            is_deleted=False
        ).prefetch_related('images').order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ClientImageViewSet(viewsets.ModelViewSet):
    queryset = ClientImage.objects.filter(is_deleted=False)
    serializer_class = ClientImageSerializer
    filterset_fields = ['client', 'is_main']
    search_fields = ['client__client_code_1c', 'client__name']
    permission_classes = [IsAuthenticated]  # Faqat authenticated user'lar uchun
    
    def get_queryset(self):
        """Optimizatsiya: select_related bilan client yuklash - N+1 query muammosini hal qiladi"""
        return ClientImage.objects.filter(
            is_deleted=False
        ).select_related('client').order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['post'], url_path='bulk-upload')
    def bulk_upload(self, request):
        """Bir vaqtda bir nechta rasm yuklash"""
        client_code = request.data.get('client')
        if not client_code:
            return Response(
                {'error': 'client client_code_1c talab qilinadi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = Client.objects.get(client_code_1c=client_code, is_deleted=False)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client topilmadi'},
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
            image_obj = ClientImage.objects.create(
                client=client,
                image=image,
                is_main=False,
                is_active=True,
                is_deleted=False
            )
            serializer = ClientImageSerializer(image_obj, context={'request': request})
            created_images.append(serializer.data)
        
        return Response({
            'message': f'{len(created_images)} ta rasm muvaffaqiyatli yuklandi',
            'images': created_images
        }, status=status.HTTP_201_CREATED)
