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
            
            # Support nested field paths (e.g. 'client__project')
            parts = self.project_field_name.split('__')
            model_class = queryset.model
            
            # Special case: If the model itself is AuthProject or Project
            if model_class.__name__ == 'AuthProject':
                return queryset.filter(id=user_auth_project.id)
            elif model_class.__name__ == 'Project':
                return queryset.filter(code_1c=user_auth_project.project_code, is_deleted=False)

            # Resolve the target model of the project field
            current_model = model_class
            target_model = None
            for i, part in enumerate(parts):
                field = current_model._meta.get_field(part)
                if i < len(parts) - 1:
                    current_model = field.related_model
                else:
                    target_model = field.related_model
            
            # Case 1: Model uses users.AuthProject
            if target_model and target_model.__name__ == 'AuthProject':
                return queryset.filter(**{self.project_field_name: user_auth_project})
            
            # Case 2: Model uses api.Project
            elif target_model and target_model.__name__ == 'Project':
                # Map AuthProject (project_code) to Project (code_1c)
                from api.models import Project
                try:
                    target_project = Project.objects.get(code_1c=user_auth_project.project_code, is_deleted=False)
                    return queryset.filter(**{self.project_field_name: target_project})
                except Project.DoesNotExist:
                    import logging
                    logging.warning(f"ProjectScopedMixin: Project with code {user_auth_project.project_code} not found.")
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
                # If project_field_name is nested, we can't easily auto-assign it during save
                # Child models usually inherit project via parent (e.g. ClientImage -> Client)
                if '__' in self.project_field_name:
                    serializer.save()
                    return

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
                        import logging
                        logging.warning(f"ProjectScopedMixin perform_create: Project with code {user_auth_project.project_code} not found for mapping.")
                        serializer.save()
                else:
                    serializer.save()
            except (AttributeError, Exception):
                serializer.save()
        else:
            serializer.save()
