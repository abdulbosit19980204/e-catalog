import os
import sys
import django

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
import json

def test_activation_apis():
    client = Client()
    
    print("=== Testing License Activation API ===\n")
    
    # Test 1: Activate new device
    print("1. Activating new device...")
    response = client.post(
        '/api/v1/license/activate/',
        data=json.dumps({
            "device_id": "TEST-DEVICE-001",
            "device_info": {
                "model": "iPhone 14",
                "os": "iOS 17.2",
                "app_version": "1.0.4"
            },
            "organization_name": "Gloriya"
        }),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: License created")
        print(f"   License Key: {data['license_info']['license_key']}")
        print(f"   Days Remaining: {data['license_info']['days_remaining']}")
        license_key = data['license_info']['license_key']
    else:
        print(f"❌ FAILED: {response.status_code}")
        print(response.content)
        return
    
    # Test 2: Activate same device again (should return existing)
    print("\n2. Re-activating same device...")
    response = client.post(
        '/api/v1/license/activate/',
        data=json.dumps({
            "device_id": "TEST-DEVICE-001",
            "device_info": {
                "model": "iPhone 14",
                "os": "iOS 17.2",
                "app_version": "1.0.4"
            }
        }),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: Returned existing license")
        print(f"   Same License Key: {data['license_info']['license_key'] == license_key}")
    else:
        print(f"❌ FAILED: {response.status_code}")
    
    # Test 3: Version Activation
    print("\n3. Testing Version Activation...")
    response = client.post(
        '/api/v1/license/version-activate/',
        data=json.dumps({
            "version": "1.0.5",
            "device_id": "TEST-DEVICE-002",
            "device_info": {
                "model": "Samsung Galaxy S23",
                "os": "Android 14"
            }
        }),
        content_type='application/json'
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: Version activated")
        print(f"   Current Version: {data['version_info']['current']}")
        print(f"   Latest Version: {data['version_info']['latest']}")
        print(f"   License Key: {data['license_info']['license_key']}")
    else:
        print(f"❌ FAILED: {response.status_code}")
        print(response.content)
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    test_activation_apis()
