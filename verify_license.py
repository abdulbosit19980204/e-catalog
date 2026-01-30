import os
import sys
import django
import uuid
from django.utils import timezone

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from license.models import AppLicense, AppVersionMetadata, AccessHistory
from django.test import Client
from django.urls import reverse

def verify_license_api():
    print("--- Verifying Mobile License API ---")
    
    # 1. Create dummy data
    license_key = f"TEST-LIC-{uuid.uuid4().hex[:8].upper()}"
    license = AppLicense.objects.create(
        license_key=license_key,
        entity_type='USER',
        entity_id=999,
        expires_at=timezone.now() + timezone.timedelta(days=30),
        status='ACTIVE'
    )
    
    AppVersionMetadata.objects.create(
        version_code="1.0.4",
        is_mandatory_update=False,
        release_notes="Initial release test"
    )
    
    # 2. Test API using Django Test Client
    client = Client()
    url = '/api/v1/license/status/'
    
    print(f"Checking status for license: {license_key}")
    response = client.get(url, HTTP_X_LICENSE_KEY=license_key, HTTP_X_APP_VERSION="1.0.4")
    
    if response.status_code == 200:
        data = response.json()
        print("API Response: SUCCESS")
        print(f"  Access allowed: {data['can_access']}")
        print(f"  Days remaining: {data['license_info']['days_remaining']}")
        print(f"  Latest version from server: {data['version_info']['latest']}")
    else:
        print(f"API Response: FAILED (Status {response.status_code})")
        print(response.content)
        return

    # 3. Check history
    history_count = AccessHistory.objects.filter(license=license).count()
    print(f"Access traces logged: {history_count}")
    
    if history_count > 0:
        print("VERIFICATION COMPLETE: Everything is working as designed.")
    else:
        print("VERIFICATION FAILED: Access trace was not logged.")

if __name__ == "__main__":
    verify_license_api()
