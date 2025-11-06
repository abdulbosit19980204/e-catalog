from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Project, ProjectImage
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile

class ProjectAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_project(self):
        """Test project yaratish"""
        data = {
            'code_1c': 'PROJ001',
            'name': 'Test Project',
            'title': 'Test Title',
            'description': '<p>Test Description</p>'
        }
        response = self.client.post('/api/v1/project/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().code_1c, 'PROJ001')
        
    def test_list_projects(self):
        """Test project ro'yxatini olish"""
        Project.objects.create(
            code_1c='PROJ001',
            name='Test Project'
        )
        response = self.client.get('/api/v1/project/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_get_project_detail(self):
        """Test project tafsilotlarini olish"""
        project = Project.objects.create(
            code_1c='PROJ001',
            name='Test Project'
        )
        response = self.client.get(f'/api/v1/project/{project.code_1c}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code_1c'], 'PROJ001')
        
    def test_update_project(self):
        """Test project yangilash"""
        project = Project.objects.create(
            code_1c='PROJ001',
            name='Test Project'
        )
        data = {'name': 'Updated Project'}
        response = self.client.patch(f'/api/v1/project/{project.code_1c}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        self.assertEqual(project.name, 'Updated Project')
        
    def test_delete_project(self):
        """Test project o'chirish"""
        project = Project.objects.create(
            code_1c='PROJ001',
            name='Test Project'
        )
        response = self.client.delete(f'/api/v1/project/{project.code_1c}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Soft delete - project hali mavjud, lekin is_deleted=True
        # is_deleted=False filter tufayli oddiy get() ishlamaydi, shuning uchun all() dan foydalanamiz
        project = Project.objects.filter(code_1c='PROJ001').first()
        self.assertIsNotNone(project)
        self.assertTrue(project.is_deleted)
        
    def test_project_search(self):
        """Test project qidirish"""
        Project.objects.create(code_1c='PROJ001', name='Test Project')
        Project.objects.create(code_1c='PROJ002', name='Another Project')
        response = self.client.get('/api/v1/project/?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
