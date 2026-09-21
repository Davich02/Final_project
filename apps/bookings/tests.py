from datetime import date, timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User
from apps.listings.models import Listing
from apps.bookings.models import Booking
from apps.core.models import BookingStatus


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

    def test_past_dates_rejected(self):
        response = self.client.post('/api/bookings/', {
            'listing': str(self.listing.id),
            'date_start': str(date.today() - timedelta(days=5)),
            'date_end': str(date.today() + timedelta(days=2)),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_own_listing_rejected(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/bookings/', {
            'listing': str(self.listing.id),
            'date_start': str(date.today() + timedelta(days=5)),
            'date_end': str(date.today() + timedelta(days=10)),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_listing_rejected(self):
        self.listing.is_active = False
        self.listing.save()
        response = self.client.post('/api/bookings/', {
            'listing': str(self.listing.id),
            'date_start': str(date.today() + timedelta(days=5)),
            'date_end': str(date.today() + timedelta(days=10)),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BookingStatusTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='TestPass123!')
        self.tenant = User.objects.create_user(email='tenant@test.com', password='TestPass123!')
        self.listing = Listing.objects.create(
            owner=self.owner, title='Test Listing', description='desc',
            country='Germany', city='Köln', district='Test', street='Test', house_number='1',
            price=500, rooms=2, housing_type='apartment'
        )

    def make_booking(self, start_offset, end_offset, booking_status=BookingStatus.PENDING):
        return Booking.objects.create(
            listing=self.listing, tenant=self.tenant,
            date_start=date.today() + timedelta(days=start_offset),
            date_end=date.today() + timedelta(days=end_offset),
            status=booking_status,
        )

    def test_update_and_delete_not_allowed(self):
        booking = self.make_booking(5, 10)
        self.client.force_authenticate(user=self.owner)
        url = f'/api/bookings/{booking.id}/'
        self.assertEqual(self.client.patch(url, {'date_end': str(date.today() + timedelta(days=20))}).status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_tenant_can_cancel(self):
        booking = self.make_booking(5, 10, BookingStatus.CONFIRMED)
        self.client.force_authenticate(user=self.tenant)
        response = self.client.post(f'/api/bookings/{booking.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        booking.refresh_from_db()
        self.assertEqual(booking.status, BookingStatus.CANCELLED)

    def test_owner_cannot_cancel(self):
        booking = self.make_booking(5, 10)
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/bookings/{booking.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_complete_before_end_rejected(self):
        booking = self.make_booking(5, 10, BookingStatus.CONFIRMED)
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/bookings/{booking.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_complete_after_end_allowed(self):
        booking = self.make_booking(-10, -2, BookingStatus.CONFIRMED)
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/bookings/{booking.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
