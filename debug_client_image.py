import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS = ['*']

from client.models import ClientImage
from client.serializers import ClientImageSerializer
from rest_framework.request import Request
from django.test import RequestFactory

def test_serialization():
    factory = RequestFactory()
    request = factory.get('/api/v1/client-image/')
    drf_request = Request(request)
    
    print("Fetching images...")
    images = ClientImage.objects.filter(is_deleted=False)
    print(f"Found {images.count()} images.")
    
    serializer = ClientImageSerializer(images, many=True, context={'request': drf_request})
    
    try:
        print("Starting serialization...")
        data = serializer.data
        print(f"Successfully serialized {len(data)} images.")
    except Exception as e:
        print(f"ERROR during serialization: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_serialization()
