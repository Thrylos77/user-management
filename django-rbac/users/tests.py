from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User

class UserAPITests(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )

    def test_get_user_details_unauthenticated(self):
        """
        Ensure unauthenticated users cannot access the 'me' endpoint.
        """
        url = reverse('user-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_details_authenticated(self):
        """
        Ensure authenticated users can access their own details.
        """
        url = reverse('user-detail')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
