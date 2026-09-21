from datetime import date, timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.listings.models import Listing


class BookingValidationTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='TestPass123!')
        self.tenant = User.objects.create_user(email='tenant@test.com', password='TestPass123!')
        self.listing = Listing.objects.create(
            owner=self.owner, title='Test Listing', description='desc',
            country='Germany', city='Köln', district='Test', street='Test', house_number='1',
            price=500, rooms=2, housing_type='apartment'
        )
        self.client.force_authenticate(user=self.tenant)

    def test_date_end_before_date_start_rejected(self):
        response = self.client.post('/api/bookings/', {
            'listing': str(self.listing.id),
            'date_start': str(date.today() + timedelta(days=10)),
            'date_end': str(date.today() + timedelta(days=5)),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_overlapping_booking_rejected(self):
        self.client.post('/api/bookings/', {
            'listing': str(self.listing.id),
            'date_start': str(date.today() + timedelta(days=5)),
            'date_end': str(date.today() + timedelta(days=10)),
        })
        response = self.client.post('/api/bookings/', {
            'listing': str(self.listing.id),
            'date_start': str(date.today() + timedelta(days=7)),
            'date_end': str(date.today() + timedelta(days=12)),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)