from django.contrib import auth
from django.test import TestCase
from django.urls import reverse
from faker import Faker


User = auth.get_user_model()


class UserProfileModelTest(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.user = User.objects.create(
            username=self.fake.user_name(),
        )

    def test_profile_created(self):
        self.assertIsNotNone(self.user.profile)

    def test_profile_str(self):
        self.assertEqual(str(self.user.profile), self.user.username)


class UserProfileViewTest(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.user = User.objects.create(
            username=self.fake.user_name(),
        )

    def test_profile_update_get_anonymous(self):
        update_url = reverse('usrprofile:update')
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={update_url}')

    def test_profile_update_get(self):
        update_url = reverse('usrprofile:update')
        self.client.force_login(self.user)
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200)

    def test_profile_update_post(self):
        update_url = reverse('usrprofile:update')
        self.client.force_login(self.user)
        form_data = {
            'first_name': self.fake.first_name(),
            'last_name': self.fake.last_name(),
            'email': self.fake.email(),
            'warn_days_before': self.user.profile.warn_days_before,
            'medicaments_items_per_page': self.user.profile.medicaments_items_per_page,
            'show_measurement_days': self.user.profile.show_measurement_days,
            'measurements_items_per_page': self.user.profile.measurements_items_per_page,
        }
        response = self.client.post(update_url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('startpage'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, form_data['first_name'])
        self.assertEqual(self.user.last_name, form_data['last_name'])
        self.assertEqual(self.user.email, form_data['email'])