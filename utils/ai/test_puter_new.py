import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from utils.ai.puter import PuterService

def test_puter():
    service = PuterService()
    print("Testing PuterService...")
    
    try:
        # Test content generation
        print("\n1. Testing Text Generation (GPT-4o)...")
        text = service.generate_sync("Say hello in Uzbek")
        print(f"Response: {text}")
        
        # Test image generation
        print("\n2. Testing Image Generation (gpt-image-1.5)...")
        img_data = service.generate_image_sync("A simple red apple on white background")
        if img_data and len(img_data) > 100:
            print(f"Success! Received {len(img_data)} bytes of image data.")
        else:
            print(f"Failed or empty image data received: {img_data}")
            
    except Exception as e:
        print(f"\nError during testing: {e}")

if __name__ == "__main__":
    test_puter()
