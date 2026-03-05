from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from .models import Student


class OnboardingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('onboarding.services.IDCardService.generate_card')
    def test_register_student(self, mock_id_card):
        mock_id_card.return_value = {'card_id': 'CARD-123', 'raw_response': {'cardId': 'CARD-123'}}

        payload = {
            'first_name': 'Ava',
            'last_name': 'Stone',
            'email': 'ava@example.com',
            'phone': '1234567890',
            'home_country': 'India',
            'campus_city': 'Melbourne',
            'course': 'Cloud Computing',
        }
        response = self.client.post('/api/register-student', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['student']['card_id'], 'CARD-123')
        self.assertEqual(Student.objects.count(), 1)

    def test_country_info_requires_country_param(self):
        response = self.client.get('/api/country-info')
        self.assertEqual(response.status_code, 400)

    @patch('onboarding.views.WelcomePackQueueService.enqueue')
    def test_trigger_welcome_pack(self, mock_enqueue):
        student = Student.objects.create(
            first_name='Ava',
            last_name='Stone',
            email='ava2@example.com',
            phone='1234567890',
            home_country='India',
            campus_city='Melbourne',
            course='Cloud Computing',
            card_id='CARD-123',
        )
        mock_enqueue.return_value = {'queued': True, 'message_id': 'msg-1', 'note': 'ok'}

        response = self.client.post('/api/generate-welcome-pack', {'student_id': student.id}, format='json')

        self.assertEqual(response.status_code, 202)
        self.assertTrue(response.data['queued'])
        self.assertEqual(response.data['message_id'], 'msg-1')
