import requests
import xml.etree.ElementTree as ET
from django.conf import settings
from .models import Visit
import logging

logger = logging.getLogger(__name__)

class VisitSyncService:
    @staticmethod
    def get_soap_body(visit, status_type):
        """
        status_type: 'check_in' or 'check_out'
        """
        agent_code = visit.agent_code or ""
        client_code = visit.client_code_1c or ""
        date_str = visit.planned_date.strftime('%Y-%m-%d') if visit.planned_date else ""
        time_str = ""
        
        if status_type == 'check_in' and visit.check_in_time:
            time_str = visit.check_in_time.strftime('%H:%M:%S')
        elif status_type == 'check_out' and visit.check_out_time:
            time_str = visit.check_out_time.strftime('%H:%M:%S')

        return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:sam="http://www.sample-package.org">
   <soap:Header/>
   <soap:Body>
      <sam:SyncVisit>
         <sam:AgentCode>{agent_code}</sam:AgentCode>
         <sam:ClientCode>{client_code}</sam:ClientCode>
         <sam:Type>{status_type}</sam:Type>
         <sam:Date>{date_str}</sam:Date>
         <sam:Time>{time_str}</sam:Time>
         <sam:Lat>{visit.latitude or 0}</sam:Lat>
         <sam:Lon>{visit.longitude or 0}</sam:Lon>
      </sam:SyncVisit>
   </soap:Body>
</soap:Envelope>"""

    @staticmethod
    def parse_response(response_content):
        try:
            root = ET.fromstring(response_content)
            def is_tag(element, name):
                return element.tag.endswith(f"}}{name}") or element.tag == name

            # Search for SyncVisitResponse
            for body in root:
                if is_tag(body, 'Body'):
                    for resp in body:
                        if is_tag(resp, 'SyncVisitResponse'):
                            for ret in resp:
                                if is_tag(ret, 'return'):
                                    data_map = {}
                                    for child in ret:
                                        tag_name = child.tag.split('}', 1)[1] if '}' in child.tag else child.tag
                                        data_map[tag_name] = child.text
                                    return data_map
            return None
        except Exception as e:
            logger.error(f"VisitSync parse error: {e}")
            return None

    @classmethod
    def sync_visit(cls, visit, status_type):
        project = visit.project
        if not project:
            logger.warning(f"Visit {visit.pk} has no project assigned. Skipping sync.")
            return False

        # Try primary then alternative URL
        urls_to_try = []
        primary_url = project.service_url or project.wsdl_url
        if primary_url:
            urls_to_try.append(primary_url)
        if project.wsdl_url_alt:
            urls_to_try.append(project.wsdl_url_alt)

        if not urls_to_try:
            visit.sync_status = 'failed'
            visit.sync_error = "No WSDL URL configured for project"
            visit.save()
            return False

        payload = cls.get_soap_body(visit, status_type)
        headers = {'Content-Type': 'application/soap+xml; charset=utf-8'}
        
        last_error = ""
        for url in urls_to_try:
            if url.lower().endswith('?wsdl'):
                url = url[:-5]
            
            try:
                response = requests.post(url, data=payload.encode('utf-8'), headers=headers, timeout=10)
                if response.status_code != 200:
                    last_error = f"1C Error {response.status_code}"
                    continue
                
                data = cls.parse_response(response.content)
                if not data:
                    last_error = "Invalid XML response"
                    continue
                
                # Check for success based on the data_map from 1C
                # Assuming 'Code' or 'Status' field from 1C
                if data.get('CodeError') == '1' or data.get('Status') == 'Success':
                    visit.sync_status = 'synced'
                    visit.sync_error = ""
                    visit.save()
                    return True
                else:
                    last_error = data.get('Message', 'Unknown error from 1C')
                    continue

            except requests.RequestException as e:
                last_error = f"Connection failed: {str(e)}"
                continue

        visit.sync_status = 'failed'
        visit.sync_error = last_error
        visit.save()
        return False
