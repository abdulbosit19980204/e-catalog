from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Client, ClientImage

class ClientAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_client(self):
        """Test client yaratish"""
        data = {
            'client_code_1c': 'CLI001',
            'name': 'Test Client',
            'email': 'test@example.com',
            'phone': '+998901234567'
        }
        response = self.client.post('/api/v1/client/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Client.objects.count(), 1)
        
    def test_list_clients(self):
        """Test client ro'yxatini olish"""
        Client.objects.create(
            client_code_1c='CLI001',
            name='Test Client'
        )
        response = self.client.get('/api/v1/client/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
