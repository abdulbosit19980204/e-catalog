import requests
import json
import os
from urllib.parse import urljoin

# CONFIGURATION
BASE_URL = "http://localhost:8000"
LOGIN_URL = "/api/v1/auth/1c-login/"
LOGIN_DATA = {
    "login": "000000326",  # Correct 1C code from previous logs
    "password": "123", # Placeholder - USER MUST UPDATE IF CHANGED
    "project_name": "Evyap"
}

# ENDPOINTS TO CHECK (List endpoints are safest)
ENDPOINTS = [
    # Core
    "/api/v1/core/health/status/",
    
    # References (Public/Auth)
    "/api/v1/visit-types/",
    "/api/v1/visit-statuses/",
    "/api/v1/visit-priorities/",
    "/api/v1/visit-steps/",
    
    # Auth
    "/api/v1/auth/profile/",
    
    # Main Apps
    "/api/v1/client/",
    "/api/v1/project/",
    "/api/v1/nomenklatura/",
    "/api/v1/visits/",
    "/api/v1/visit-plans/",
]

def run_checks():
    print(f"🚀 Starting API Checker on {BASE_URL}")
    session = requests.Session()
    
    # 1. Login
    print(f"\n🔑 Authenticating...")
    try:
        login_resp = session.post(urljoin(BASE_URL, LOGIN_URL), json=LOGIN_DATA)
        if login_resp.status_code == 200:
            token = login_resp.json().get('tokens', {}).get('access')
            if token:
                session.headers.update({'Authorization': f'Bearer {token}'})
                print(f"✅ Login Successful! Token acquired.")
            else:
                print(f"❌ Login Failed: No token in response. {login_resp.text}")
                return
        else:
            print(f"❌ Login Failed: {login_resp.status_code} - {login_resp.text}")
            # Try continue for public endpoints
    except Exception as e:
        print(f"❌ Connection Error during login: {e}")
        return

    # 2. Check Endpoints
    print(f"\n📡 Checking Endpoints...")
    success_count = 0
    fail_count = 0
    
    for endpoint in ENDPOINTS:
        url = urljoin(BASE_URL, endpoint)
        try:
            resp = session.get(url)
            if resp.status_code == 200:
                print(f"✅ [200] {endpoint}")
                success_count += 1
            elif resp.status_code == 401:
                print(f"⛔ [401] {endpoint} (Unauthorized)")
                fail_count += 1
            elif resp.status_code == 403:
                print(f"🚫 [403] {endpoint} (Permission Denied)")
                fail_count += 1
            elif resp.status_code == 404:
                print(f"❓ [404] {endpoint} (Not Found)")
                fail_count += 1
            else:
                print(f"❌ [{resp.status_code}] {endpoint}")
                fail_count += 1
        except Exception as e:
            print(f"🔥 Error checking {endpoint}: {e}")
            fail_count += 1
            
    # 3. Summary
    print(f"\n📊 Summary")
    print(f"Total: {len(ENDPOINTS)}")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")

if __name__ == "__main__":
    run_checks()
