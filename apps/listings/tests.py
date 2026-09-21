from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import Group
from apps.users.models import User
from datetime import date, timedelta
import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.listings.models import Listing, ListingPhoto
from apps.bookings.models import Booking
from apps.reviews.models import Review
from apps.analytics.models import SearchQuery
from apps.core.models import BookingStatus


class ListingPermissionsTests(APITestCase):
    def setUp(self):
        self.landlord = User.objects.create_user(email='landlord@test.com', password='TestPass123!')
        landlord_group, _ = Group.objects.get_or_create(name='Landlords')
        self.landlord.groups.add(landlord_group)

        self.other_landlord = User.objects.create_user(email='other@test.com', password='TestPass123!')
        self.other_landlord.groups.add(landlord_group)

        self.listing = Listing.objects.create(
            owner=self.landlord, title='Test Listing', description='desc',
            country='Germany', city='Köln', district='Test', street='Test', house_number='1',
            price=500, rooms=2, housing_type='apartment'
        )

    def test_anonymous_cant_create_listing(self):
        response = self.client.post('/api/listings/', {
            'title': 'New Listing', 'description': 'desc', 'country': 'Germany',
            'city': 'Köln', 'district': 'Test', 'street': 'Test', 'house_number': '1',
            'price': 500, 'rooms': 2, 'housing_type': 'apartment'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_other_user_cant_edit_listing(self):
        self.client.force_authenticate(user=self.other_landlord)
        response = self.client.patch(f'/api/listings/{self.listing.id}/', {'title': 'Hacked'})
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


class SoftDeleteTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='softdelete@test.com', password='TestPass123!')
        self.listing = Listing.objects.create(
            owner=self.owner, title='To Delete', description='desc',
            country='Germany', city='Köln', district='Test', street='Test', house_number='1',
            price=500, rooms=2, housing_type='apartment'
        )

    def test_soft_delete_hides_from_default_manager(self):
        listing_id = self.listing.id
        self.listing.delete()

        self.assertFalse(Listing.objects.filter(id=listing_id).exists())
        self.assertTrue(Listing.all_objects.filter(id=listing_id).exists())


def make_listing(owner, **kwargs):
    data = dict(
        owner=owner, title='Test Listing', description='desc',
        country='Germany', city='Köln', district='Test', street='Test', house_number='1',
        price=500, rooms=2, housing_type='apartment'
    )
    data.update(kwargs)
    return Listing.objects.create(**data)


def make_image():
    buffer = io.BytesIO()
    Image.new('RGB', (1, 1)).save(buffer, format='PNG')
    return SimpleUploadedFile('photo.png', buffer.getvalue(), content_type='image/png')


class ListingPhotoTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='TestPass123!')
        self.stranger = User.objects.create_user(email='stranger@test.com', password='TestPass123!')
        self.listing = make_listing(self.owner)

    def test_invalid_listing_id_returns_400(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/listings/photos/', {'listing': 'abc', 'image': make_image()},
                                    format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_photo_to_foreign_listing_returns_403(self):
        self.client.force_authenticate(user=self.stranger)
        response = self.client.post('/api/listings/photos/',
                                    {'listing': str(self.listing.id), 'image': make_image()},
                                    format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_photos_of_inactive_listing_hidden(self):
        hidden = make_listing(self.owner, is_active=False)
        ListingPhoto.objects.create(listing=hidden, image='listings/photos/hidden.png')
        ListingPhoto.objects.create(listing=self.listing, image='listings/photos/visible.png')

        response = self.client.get('/api/listings/photos/')
        self.assertEqual(len(response.data), 1)

        self.client.force_authenticate(user=self.owner)
        response = self.client.get('/api/listings/photos/')
        self.assertEqual(len(response.data), 2)


class ListingDeleteTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='TestPass123!')
        landlord_group, _ = Group.objects.get_or_create(name='Landlords')
        self.owner.groups.add(landlord_group)
        self.tenant = User.objects.create_user(email='tenant@test.com', password='TestPass123!')
        self.listing = make_listing(self.owner)
        self.client.force_authenticate(user=self.owner)

    def test_cant_delete_with_active_booking(self):
        Booking.objects.create(listing=self.listing, tenant=self.tenant,
                               date_start=date.today() + timedelta(days=5),
                               date_end=date.today() + timedelta(days=10))
        response = self.client.delete(f'/api/listings/{self.listing.id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Listing.objects.filter(id=self.listing.id).exists())

    def test_delete_without_active_bookings(self):
        response = self.client.delete(f'/api/listings/{self.listing.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Listing.objects.filter(id=self.listing.id).exists())


class ListingRatingTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@test.com', password='TestPass123!')
        self.listing = make_listing(self.owner)
        for i, rating in enumerate([4, 5]):
            tenant = User.objects.create_user(email=f'tenant{i}@test.com', password='TestPass123!')
            booking = Booking.objects.create(
                listing=self.listing, tenant=tenant,
                date_start=date.today() - timedelta(days=20 - i * 5),
                date_end=date.today() - timedelta(days=17 - i * 5),
                status=BookingStatus.COMPLETED,
            )
            Review.objects.create(booking=booking, rating=rating)

    def test_rating_in_listing_detail(self):
        response = self.client.get(f'/api/listings/{self.listing.id}/')
        self.assertEqual(response.data['average_rating'], 4.5)
        self.assertEqual(response.data['reviews_count'], 2)

    def test_rating_in_list_with_price_stats(self):
        response = self.client.get('/api/listings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['average_rating'], 4.5)
        self.assertIsNotNone(response.data['price_stats']['average_price'])

    def test_reviews_filter_by_listing(self):
        other_listing = make_listing(self.owner)
        response = self.client.get(f'/api/reviews/?listing={self.listing.id}')
        self.assertEqual(len(response.data), 2)
        response = self.client.get(f'/api/reviews/?listing={other_listing.id}')
        self.assertEqual(len(response.data), 0)


class SearchAnalyticsTests(APITestCase):
    def test_search_logged_once_and_normalized(self):
        self.client.get('/api/listings/?search=  Berlin ')
        self.client.get('/api/listings/?search=Berlin&page=2')
        self.assertEqual(SearchQuery.objects.count(), 1)
        self.assertEqual(SearchQuery.objects.first().query, 'berlin')
