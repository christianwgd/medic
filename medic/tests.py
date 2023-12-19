from django.contrib import auth
from django.test import TestCase
from django.urls import reverse
from faker import Faker

from usrprofile.models import StartUrl

User = auth.get_user_model()


class MedicViewTest(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.user = User.objects.create(
            username=self.fake.user_name(),
        )

    def test_index_view_anonymous(self):
        index_url = reverse('index')
        response = self.client.get(index_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/login/?next={index_url}')

    def test_index_view(self):
        self.client.force_login(self.user)
        index_url = reverse('index')
        response = self.client.get(index_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "index.html")

    def test_start_view_anonymous(self):
        start_url = reverse('startpage')
        response = self.client.get(start_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/login/?next={start_url}')

    def test_start_view_no_start_page(self):
        self.client.force_login(self.user)
        start_url = reverse('startpage')
        response = self.client.get(start_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))

    def test_start_view_startpage_set(self):
        profile = self.user.profile
        profile.my_start_page = StartUrl.objects.create(
            name='measurements list',
            url='measurement:list',
        )
        profile.save()
        self.client.force_login(self.user)
        start_url = reverse('startpage')
        response = self.client.get(start_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse(profile.my_start_page.url))

    def test_start_view(self):
        self.client.force_login(self.user)
        logoff_url = reverse('logoff')
        response = self.client.post(logoff_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('medic_login'))
