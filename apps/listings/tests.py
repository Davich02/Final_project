from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import Group
from apps.users.models import User
from apps.listings.models import Listing


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