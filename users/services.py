import requests
import xml.etree.ElementTree as ET
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import AuthProject, UserProfile, AgentBusinessRegion

User = get_user_model()

class OneCAuthService:
    @staticmethod
    def get_soap_body(login, password):
        return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:sam="http://www.sample-package.org">
   <soap:Header/>
   <soap:Body>
      <sam:GetUser>
         <sam:Login>{login}</sam:Login>
         <sam:Password>{password}</sam:Password>
      </sam:GetUser>
   </soap:Body>
</soap:Envelope>"""

    @staticmethod
    def get_business_regions_soap_body(user_code):
        return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:sam="http://www.sample-package.org">
   <soap:Header/>
   <soap:Body>
      <sam:GetBusinessRegions>
         <sam:UserCode>{user_code}</sam:UserCode>
      </sam:GetBusinessRegions>
   </soap:Body>
</soap:Envelope>"""

    @staticmethod
    def parse_response(response_content):
        """
        Parses the SOAP response in a namespace-agnostic way.
        """
        try:
            root = ET.fromstring(response_content)
            
            # Helper to check tag name ignoring namespace
            def is_tag(element, name):
                return element.tag.endswith(f"}}{name}") or element.tag == name

            # 1. Find Body
            body = None
            for child in root:
                if is_tag(child, 'Body'):
                    body = child
                    break
            if body is None:
                print("DEBUG: Body not found")
                return None
            
            # 2. Find GetUserResponse
            response_xml = None
            for child in body:
                if is_tag(child, 'GetUserResponse'):
                    response_xml = child
                    break
            if response_xml is None:
                print("DEBUG: GetUserResponse not found")
                return None
            
            # 3. Find return
            ret_data = None
            for child in response_xml:
                if is_tag(child, 'return'):
                    ret_data = child
                    break
            if ret_data is None:
                print("DEBUG: return element not found")
                return None
            
            # 4. Extract data into a dictionary
            data_map = {}
            for child in ret_data:
                # Remove namespace from tag
                tag_name = child.tag.split('}', 1)[1] if '}' in child.tag else child.tag
                data_map[tag_name] = child.text

            return {
                'code': data_map.get('Code'),
                'name': data_map.get('Name'),
                'type': data_map.get('Type'),
                'code_project': data_map.get('CodeProject'),
                'code_error': data_map.get('CodeError'),
                'message': data_map.get('Message'),
                'code_sklad': data_map.get('CodeSklad'),
                'business_region_code': data_map.get('BussinesRegionCode'),
                'business_region_name': data_map.get('BussinesRegionName'),
            }
        except Exception as e:
            print(f"XML Parse Error: {e}")
            return None

    @staticmethod
    def parse_business_regions(response_content):
        """
        Parses the GetBusinessRegions SOAP response.
        """
        try:
            root = ET.fromstring(response_content)
            def is_tag(element, name):
                return element.tag.endswith(f"}}{name}") or element.tag == name

            body = None
            for child in root:
                if is_tag(child, 'Body'):
                    body = child
                    break
            if body is None: return []
            
            resp_node = None
            for child in body:
                if is_tag(child, 'GetBusinessRegionsResponse'):
                    resp_node = child
                    break
            if resp_node is None: return []
            
            ret_node = None
            for child in resp_node:
                if is_tag(child, 'return'):
                    ret_node = child
                    break
            if ret_node is None: return []
            
            regions = []
            for child in ret_node:
                if is_tag(child, 'Rows'):
                    region_data = {}
                    for row_child in child:
                        tag_name = row_child.tag.split('}', 1)[1] if '}' in row_child.tag else row_child.tag
                        region_data[tag_name] = row_child.text
                    if region_data.get('Code'):
                        regions.append({
                            'code': region_data.get('Code'),
                            'name': region_data.get('Name')
                        })
            return regions
        except Exception as e:
            print(f"Business Region Parse Error: {e}")
            return []

    @classmethod
    def authenticate(cls, project_name, login, password):
        try:
            # Helper: name bo'yicha qidirish (case-insensitive qulay bo'lishi mumkin, lekin hozir exact match)
            # filter().first() duplicate bo'lsa xato bermasligi uchun
            project = AuthProject.objects.filter(name=project_name, is_active=True).first()
            if not project:
                return None, f"Project '{project_name}' not found or inactive"
        except Exception as e:
            return None, f"Project lookup error: {str(e)}"

        urls_to_try = []
        primary_url = project.service_url or project.wsdl_url
        if primary_url:
            urls_to_try.append(primary_url)
        if project.wsdl_url_alt:
            urls_to_try.append(project.wsdl_url_alt)

        last_error = "No URLs configured for project"
        payload = cls.get_soap_body(login, password)
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8', 
        }

        for url in urls_to_try:
            # Clean URL: remove ?wsdl or ?WSDL if present
            if url.lower().endswith('?wsdl'):
                url = url[:-5]
                
            print(f"DEBUG: Attempting 1C Auth at: {url}")

            try:
                response = requests.post(url, data=payload.encode('utf-8'), headers=headers, timeout=10)
                
                if response.status_code != 200:
                    last_error = f"1C Service Error at {url}: {response.status_code}"
                    print(f"ERROR: {last_error}")
                    continue # Try next URL
                    
                data = cls.parse_response(response.content)
                
                if not data:
                    last_error = f"Invalid XML from {url}"
                    print(f"ERROR: {last_error}")
                    continue
                    
                if data.get('code_error') != '1': 
                    return None, data.get('message', 'Authorization failed')
                    
                # Success - Create or Update User
                user = cls.update_or_create_user(project, login, data)
                
                # NEW: Fetch and sync Business Regions
                cls.sync_agent_regions(project, url, data.get('code'), user.profile, headers)
                
                tokens = cls.get_tokens_for_user(user)
                
                return {
                    'user': {
                        'username': user.username,
                        'full_name': user.first_name,
                        'code_1c': data['code'],
                    },
                    'tokens': tokens,
                    'message': data['message']
                }, None

            except requests.RequestException as e:
                last_error = f"Connection Error at {url}: {str(e)}"
                print(f"ERROR: {last_error}")
                continue # Try next URL

        return None, last_error

    @staticmethod
    def update_or_create_user(project, login, data):
        # User logic
        # Collision prevention: different projects can have same login (e.g. TP-3)
        # Strategy: Scoped username = "{project_code}_{login}"
        
        scoped_username = f"{project.project_code}_{login}"
        
        # We use the scoped username for Django User.
        user, created = User.objects.get_or_create(username=scoped_username)
        
        # Update user fields
        # Store original "Name" from 1C in first_name (e.g. "XOLIQOV MIRKOMIL")
        user.first_name = data.get('name', '')[:30] 
        if not user.is_active:
            user.is_active = True
        user.save()
        
        # Update or Create UserProfile
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'project': project,
                'code_1c': data.get('code'),
                'code_project': data.get('code_project'),
                'code_sklad': data.get('code_sklad'),
                'type_1c': data.get('type'),
                'business_region_code': data.get('business_region_code'),
                'business_region_name': data.get('business_region_name'),
            }
        )
        return user

    @classmethod
    def sync_agent_regions(cls, project, url, user_code, profile, headers):
        """
        Fetches business regions from 1C and updates the AgentBusinessRegion model.
        """
        if not user_code or not profile:
            return

        payload = cls.get_business_regions_soap_body(user_code)
        try:
            response = requests.post(url, data=payload.encode('utf-8'), headers=headers, timeout=10)
            if response.status_code == 200:
                regions_data = cls.parse_business_regions(response.content)
                if regions_data:
                    # Remove old regions and add new ones
                    AgentBusinessRegion.objects.filter(profile=profile).delete()
                    for reg in regions_data:
                        AgentBusinessRegion.objects.create(
                            profile=profile,
                            code=reg['code'],
                            name=reg['name'] or f"Region {reg['code']}"
                        )
                    print(f"DEBUG: Synced {len(regions_data)} business regions for agent {user_code}")
        except Exception as e:
            print(f"ERROR: Failed to sync business regions: {e}")

    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        
        # Calculate expiry times based on settings (or token payload)
        # refresh.access_token.payload['exp'] is a timestamp
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'access_expires_at': refresh.access_token['exp'],
            'refresh_expires_at': refresh['exp'],
        }
