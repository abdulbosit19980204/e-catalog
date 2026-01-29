import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from utils.ai.puter import PuterService
from utils.settings import get_system_setting

def verify():
    u = get_system_setting('PUTER_USERNAME')
    p = get_system_setting('PUTER_PASSWORD')
    
    if not u or not p:
        print("ERROR: Puter credentials are not set in the database.")
        from core.models import SystemSettings
        print(f"Current settings count: {SystemSettings.objects.count()}")
        for s in SystemSettings.objects.filter(key__icontains='PUTER'):
            print(f"- {s.key}: {'[PRESENT]' if s.value else '[EMPTY]'}")
        return

    service = PuterService()
    print(f"Testing PuterService with user: {u}")
    
    try:
        # Test Text
        print("\n[1/2] Testing Text Generation...")
        res = service.generate_sync("Bitta mahsulot uchun tavsif yoz: Olma", model="gpt-4o")
        print(f"Result (first 100 chars): {res[:100]}...")
        
        # Test Image
        print("\n[2/2] Testing Image Generation...")
        img_data = service.generate_image_sync("A high quality product photo of a red apple on a white background")
        if img_data and isinstance(img_data, bytes) and len(img_data) > 100:
            print(f"SUCCESS: Received image data ({len(img_data)} bytes)")
        else:
            print(f"FAILED: Received invalid image data: {type(img_data)}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    verify()
