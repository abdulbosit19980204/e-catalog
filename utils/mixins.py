from rest_framework import serializers

class ProjectScopedMixin:
    """
    Mixin to automatically filter querysets by the user's project.
    Intelligently handles both users.AuthProject and api.Project models.
    """
    project_field_name = 'project'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Superusers can see everything
        if user.is_superuser:
            return queryset
            
        try:
            # Get AuthProject from user profile
            user_auth_project = user.profile.project
            if not user_auth_project:
                return queryset.none()
            
            # Check the model's project field type
            model_class = queryset.model
            project_field = model_class._meta.get_field(self.project_field_name)
            target_model = project_field.related_model
            
            # Case 1: Model uses users.AuthProject
            if target_model.__name__ == 'AuthProject':
                return queryset.filter(**{self.project_field_name: user_auth_project})
            
            # Case 2: Model uses api.Project
            elif target_model.__name__ == 'Project':
                # Map AuthProject (project_code) to Project (code_1c)
                from api.models import Project
                try:
                    target_project = Project.objects.get(code_1c=user_auth_project.project_code, is_deleted=False)
                    return queryset.filter(**{self.project_field_name: target_project})
                except Project.DoesNotExist:
                    return queryset.none()
            
            # Fallback (exact Match)
            return queryset.filter(**{self.project_field_name: user_auth_project})
            
        except (AttributeError, Exception):
            # Fallback if profile doesn't exist or other error
            return queryset.none()

    def perform_create(self, serializer):
        """Automatically assign user's project on creation"""
        user = self.request.user
        if not user.is_superuser:
            try:
                user_auth_project = user.profile.project
                if not user_auth_project:
                    serializer.save()
                    return

                # Determine target project based on serializer model
                model_class = serializer.Meta.model
                project_field = model_class._meta.get_field(self.project_field_name)
                target_model = project_field.related_model

                if target_model.__name__ == 'AuthProject':
                    serializer.save(**{self.project_field_name: user_auth_project})
                elif target_model.__name__ == 'Project':
                    from api.models import Project
                    target_project = Project.objects.filter(code_1c=user_auth_project.project_code, is_deleted=False).first()
                    if target_project:
                        serializer.save(**{self.project_field_name: target_project})
                    else:
                        serializer.save()
                else:
                    serializer.save()
            except (AttributeError, Exception):
                serializer.save()
        else:
            serializer.save()
