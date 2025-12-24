import requests
import xml.etree.ElementTree as ET
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import AuthProject, UserProfile

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
    def parse_response(response_content):
        """
        Parses the SOAP response and returns a dictionary of user data.
        """
        try:
            # Remove namespaces for easier parsing or handle them
            # This is a naive parser based on the example provided
            root = ET.fromstring(response_content)
            
            # Namespaces map (based on provided XML)
            ns = {
                'soap': 'http://www.w3.org/2003/05/soap-envelope',
                'm': 'http://www.sample-package.org'
            }
            
            # Find return element
            # Path: Body -> GetUserResponse -> return
            body = root.find('soap:Body', ns)
            if body is None: return None
            
            response = body.find('m:GetUserResponse', ns)
            if response is None: return None
            
            data = response.find('m:return', ns)
            if data is None: return None
            
            return {
                'code': data.find('m:Code', ns).text,
                'name': data.find('m:Name', ns).text,
                'type': data.find('m:Type', ns).text,
                'code_project': data.find('m:CodeProject', ns).text,
                'code_error': data.find('m:CodeError', ns).text,
                'message': data.find('m:Message', ns).text,
                'code_sklad': data.find('m:CodeSklad', ns).text,
            }
        except Exception as e:
            print(f"XML Parse Error: {e}")
            return None

    @classmethod
    def authenticate(cls, project_code, login, password):
        try:
            project = AuthProject.objects.get(project_code=project_code, is_active=True)
        except AuthProject.DoesNotExist:
            return None, "Project not found or inactive"

        url = project.service_url or project.wsdl_url
        payload = cls.get_soap_body(login, password)
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8', # SOAP 1.2 content type
            # 'SOAPAction': 'http://www.sample-package.org/GetUser' # May be needed
        }

        try:
            response = requests.post(url, data=payload.encode('utf-8'), headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"1C Error Status: {response.status_code}, Body: {response.text}")
                return None, f"1C Service Error: {response.status_code}"
                
            data = cls.parse_response(response.content)
            
            if not data:
                return None, "Invalid XML response from 1C"
                
            if data.get('code_error') != '1': # Assuming 1 is success based on example "Авторизация прошла успешно!!!"
                return None, data.get('message', 'Authorization failed')
                
            # Success - Create or Update User
            user = cls.update_or_create_user(login, data)
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
            return None, f"Connection Error: {str(e)}"

    @staticmethod
    def update_or_create_user(login, data):
        # User logic
        # Should we assume 'login' from client is the username? Or define username from 1C data?
        # User request says: "userni oldin royxatdan otmagan bolsa userlistga register qilish kerak"
        
        # We use the provided 'login' as username.
        user, created = User.objects.get_or_create(username=login)
        
        # Update user fields
        user.first_name = data.get('name', '')[:30] # Truncate if too long (max 150 usually)
        if not user.is_active:
            user.is_active = True
        user.save()
        
        # Update or Create UserProfile
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'code_1c': data.get('code'),
                'code_project': data.get('code_project'),
                'code_sklad': data.get('code_sklad'),
                'type_1c': data.get('type')
            }
        )
        return user

    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
