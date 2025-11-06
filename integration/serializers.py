from rest_framework import serializers
from .models import Integration


class IntegrationSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_code_1c = serializers.CharField(source='project.code_1c', read_only=True)
    
    class Meta:
        model = Integration
        fields = ['id', 'name', 'project', 'project_name', 'project_code_1c', 'wsdl_url', 
                  'method_nomenklatura', 'method_clients', 'chunk_size', 'description',
                  'is_active', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

