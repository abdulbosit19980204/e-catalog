from rest_framework import serializers
from .models import Integration


class IntegrationSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_code_1c = serializers.CharField(source='project.code_1c', read_only=True)
    
    class Meta:
        model = Integration
        fields = [
            'id',
            'name',
            'project',
            'project_name',
            'project_code_1c',
            'wsdl_url',
            'method_nomenklatura',
            'method_clients',
            'chunk_size',
            'description',
            'is_active',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class IntegrationSummarySerializer(serializers.Serializer):
    """Integration uchun qisqa ma'lumot."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    project = serializers.CharField(read_only=True)


class IntegrationSyncResponseSerializer(serializers.Serializer):
    """Sync jarayonini boshlash response strukturasi."""

    task_id = serializers.CharField(help_text="Background task identifikatori")
    status = serializers.CharField(help_text="Jarayon holati (started yoki error)")
    message = serializers.CharField(help_text="Insonga o'qishga qulay xabar")
    integration = IntegrationSummarySerializer()


class IntegrationSyncStatusSerializer(serializers.Serializer):
    """Sync progress holatini ko'rsatuvchi schema."""

    task_id = serializers.CharField(help_text="Background task identifikatori")
    integration = IntegrationSummarySerializer()
    sync_type = serializers.ChoiceField(
        choices=['nomenklatura', 'clients'],
        help_text="Qaysi turdagi ma'lumot sync qilinmoqda",
    )
    status = serializers.ChoiceField(
        choices=['fetching', 'processing', 'completed', 'error'],
        help_text="Jarayonning joriy holati",
    )
    total = serializers.IntegerField(help_text="1C dan olingan umumiy elementlar soni", required=False)
    processed = serializers.IntegerField(help_text="Qayta ishlangan elementlar soni", required=False)
    created = serializers.IntegerField(help_text="Yangi yaratilgan elementlar soni", required=False)
    updated = serializers.IntegerField(help_text="Yangilangan elementlar soni", required=False)
    errors = serializers.IntegerField(help_text="Xato bo'lgan elementlar soni", required=False)
    progress_percent = serializers.IntegerField(
        help_text="Tugallanish foizi (0-100)", min_value=0, max_value=100, required=False
    )
    error_message = serializers.CharField(
        help_text="Xato tafsilotlari (agar mavjud bo'lsa)", allow_null=True, required=False
    )
    started_at = serializers.DateTimeField(help_text="Jarayon boshlangan vaqt", required=False)
    completed_at = serializers.DateTimeField(
        help_text="Jarayon tugagan vaqt (agar tugagan bo'lsa)", allow_null=True, required=False
    )

