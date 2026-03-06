from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient


class OperationsApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_demo')

    def setUp(self):
        self.client = APIClient()

    def test_patient_can_get_triage_preview(self):
        login = self.client.post(
            '/api/auth/login/',
            {'username': 'patient.asha', 'password': 'Patient@123'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        response = self.client.post(
            '/api/triage/preview/',
            {
                'concern': 'Shortness of breath',
                'symptoms': 'Cough and breathlessness after walking',
                'notes': 'Started yesterday',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('triage_score', response.data)
        self.assertIn('suggestedSlots', response.data)

    def test_doctor_can_load_dashboard(self):
        login = self.client.post(
            '/api/auth/login/',
            {'username': 'doctor.rao', 'password': 'Doctor@123'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        response = self.client.get('/api/doctor/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('appointments', response.data)
        self.assertIn('slots', response.data)
