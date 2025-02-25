from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib import auth
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone, formats
from django.utils.translation import gettext as _
from faker import Faker

from medicament.models import Medicament, UNIT_CHOICES
from prescription.forms import PrescriptionForm
from prescription.models import Prescription
from prescription.templatetags.prescription_tags import calc_dosis, weekday_disp, calc_days

user_model = auth.get_user_model()


class PrescriptionTestCase(TestCase):
    def setUp(self):
        self.fake = Faker('de_DE')
        self.user = user_model.objects.create(username=self.fake.user_name())
        self.medicament = Medicament.objects.create(
            name=self.fake.word(),
            producer=self.fake.word(),
            ingredient=self.fake.word(),
            package=self.fake.random_int(min=50, max=250, step=50),
            strength=self.fake.random_int(min=1, max=50, step=5),
            unit=UNIT_CHOICES[self.fake.random_int(min=0, max=3)][0],
            owner=self.user,
        )
        today = timezone.now().date()
        self.prescription = Prescription.objects.create(
            medicament=self.medicament,
            morning=1.0,
            weekdays=127,  # All days a week
            owner=self.user,
            valid_from=today - timedelta(days=90),
            valid_until=today - timedelta(days=61),
        )
        self.active_prescription = Prescription.objects.create(
            medicament=self.medicament,
            morning=1.0,
            weekdays=127,  # All days a week
            owner=self.user,
            valid_from=today - timedelta(days=29),
            valid_until=None,
        )


class PrescriptionModelTest(PrescriptionTestCase):

    def test_prescription_str(self):
        self.assertEqual(str(self.prescription), str(self.medicament))

    def test_prescription_active_false(self):
        today = timezone.now().date()
        self.assertFalse(self.prescription.active(today, self.user))

    def test_prescription_active_true(self):
        day = timezone.now().date() - timedelta(days=80)
        self.assertTrue(self.prescription.active(day, self.user))

    def test_prescription_get_dose_per_day(self):
        day = timezone.now().date() - timedelta(days=80)
        self.assertEqual(self.prescription.get_dose_per_day(day, self.user), 1.0)

    def test_prescription_get_dose_per_day_inactive_prescription(self):
        day = timezone.now().date() - timedelta(days=20)
        self.assertEqual(self.prescription.get_dose_per_day(day, self.user), 0.0)

    def test_prescription_get_default_dose_none(self):
        self.prescription.noon = self.prescription.evening = self.prescription.night = 0
        self.prescription.morning = 0
        self.prescription.save()
        self.assertEqual(self.prescription.get_default_dose(), None)

    def test_prescription_get_default_dose_night(self):
        self.prescription.morning = self.prescription.noon = self.prescription.evening = 0
        self.prescription.night = 1.0
        self.prescription.save()
        self.assertEqual(self.prescription.get_default_dose(), 1.0)

    def test_prescription_get_default_dose_evening(self):
        self.prescription.morning = self.prescription.noon = self.prescription.night = 0
        self.prescription.evening = 1.0
        self.prescription.save()
        self.assertEqual(self.prescription.get_default_dose(), 1.0)

    def test_prescription_get_default_dose_noon(self):
        self.prescription.morning = self.prescription.evening = self.prescription.night = 0
        self.prescription.noon = 1.0
        self.prescription.save()
        self.assertEqual(self.prescription.get_default_dose(), 1.0)

    def test_prescription_get_default_dose_morning(self):
        self.prescription.noon = self.prescription.evening = self.prescription.night = 0
        self.prescription.morning = 1.0
        self.prescription.save()
        self.assertEqual(self.prescription.get_default_dose(), 1.0)

    def test_prescription_get_amount_for_time(self):
        start = timezone.now().date() - timedelta(days=80)
        end = timezone.now().date() - timedelta(days=70)
        self.assertEqual(
            self.prescription.get_amount_for_time(start, end, self.user),
            Decimal('10'),
        )

    def test_prescription_get_days_before_empty(self):
        self.assertEqual(
            self.prescription.get_days_before_empty(self.user),
            self.prescription.medicament.stock,
        )

    def test_prescription_active_manager(self):
        self.assertEqual(
            Prescription.objects.active(for_user=self.user).count(), 1,
        )


class PrescriptionFormTests(PrescriptionTestCase):

    def test_medicament_form_test_invalid(self):
        form = PrescriptionForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
        self.assertIn(_('This field is required.'), form.errors['medicament'])
        self.assertIn(_('No values entered.'), form.errors['__all__'])

    def test_medicament_form_test_valid(self):
        form_data = {
            'medicament': self.medicament.pk,
            'morning': 1.5,
            'weekdays': ['mo', 'we', 'fr'],
        }
        form = PrescriptionForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)


class PrescriptionTagTest(PrescriptionTestCase):

    def test_calc_dosis(self):
        value = Decimal('2.00')
        result = calc_dosis(value, self.prescription.id)
        dose = formats.localize(round(self.prescription.medicament.strength * value, 2), use_l10n=True)
        self.assertEqual(result, f'{dose}{self.prescription.medicament.unit}')

    def test_weekday_disp(self):
        result = weekday_disp(self.prescription.weekdays)
        self.assertEqual(
            result,
            {
                'weekdays': [
                    (_('Mo'), self.prescription.weekdays.mo),
                    (_('Tu'), self.prescription.weekdays.tu),
                    (_('We'), self.prescription.weekdays.we),
                    (_('Th'), self.prescription.weekdays.th),
                    (_('Fr'), self.prescription.weekdays.fr),
                    (_('Sa'), self.prescription.weekdays.sa),
                    (_('Su'), self.prescription.weekdays.su),
                ],
            },
        )

    def test_calc_days_danger(self):
        result = calc_days(self.active_prescription, self.user)
        self.assertEqual(result, '<span class="badge bg-danger">0</span>')

    def test_calc_days_warning(self):
        self.active_prescription.medicament.stock = 20
        self.active_prescription.medicament.save()
        result = calc_days(self.active_prescription, self.user)
        self.assertEqual(result, '<span class="badge bg-warning">20</span>')

    def test_calc_days_success(self):
        self.active_prescription.medicament.stock = 40
        self.active_prescription.medicament.save()
        result = calc_days(self.active_prescription, self.user)
        self.assertEqual(result, '<span class="badge bg-success">40</span>')


class PrescriptionViewsTest(PrescriptionTestCase):

    def test_prescription_list_view_no_user(self):
        list_url = reverse('prescription:list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={list_url}')

    def test_prescription_list_view(self):
        self.client.force_login(self.user)
        list_url = reverse('prescription:list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['prescription_list']), 1)
        self.assertIsInstance(response.context['prescription_list'][0], Prescription)

    def test_prescription_detail_view_no_user(self):
        detail_url = reverse(
            'prescription:detail',
            kwargs={'pk': self.active_prescription.id},
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={detail_url}')

    def test_prescription_detail_view(self):
        self.client.force_login(self.user)
        detail_url = reverse(
            'prescription:detail',
            kwargs={'pk': self.active_prescription.id},
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        prescription = response.context['prescription']
        self.assertIsInstance(prescription, Prescription)
        self.assertEqual(prescription, self.active_prescription)

    def test_prescription_create_view_no_user(self):
        create_url = reverse('prescription:create')
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={create_url}')

    def test_prescription_create_view_get(self):
        self.client.force_login(self.user)
        create_url = reverse('prescription:create')
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "prescription/prescription_form.html")

    def test_prescription_create_view_post(self):
        self.client.force_login(self.user)
        update_url = reverse('prescription:create')
        form_data = {
            'medicament': self.medicament.pk,
            'morning': 1.5,
            'weekdays': ['mo', 'we', 'fr'],
        }
        response = self.client.post(update_url, form_data)
        self.assertEqual(response.status_code, 302)
        list_url = reverse('prescription:list')
        self.assertEqual(response.url, list_url)
        new_prescription = Prescription.objects.get(morning=1.5)
        self.assertEqual(new_prescription.medicament, self.medicament)
        self.assertEqual(new_prescription.morning, Decimal('1.5'))
        self.assertTrue(new_prescription.weekdays.mo)
        self.assertFalse(new_prescription.weekdays.tu)
        self.assertTrue(new_prescription.weekdays.we)
        self.assertFalse(new_prescription.weekdays.th)
        self.assertTrue(new_prescription.weekdays.fr)
        self.assertFalse(new_prescription.weekdays.sa)
        self.assertFalse(new_prescription.weekdays.su)

    def test_prescription_update_view_no_user(self):
        update_url = reverse('prescription:update', kwargs={'pk': self.prescription.id})
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={update_url}')

    def test_prescription_update_view_get(self):
        self.client.force_login(self.user)
        update_url = reverse('prescription:update', kwargs={'pk': self.prescription.id})
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200)
        prescription = response.context['prescription']
        self.assertIsInstance(prescription, Prescription)
        self.assertEqual(prescription, self.prescription)

    def test_prescription_update_view_post(self):
        self.client.force_login(self.user)
        update_url = reverse('prescription:update', kwargs={'pk': self.prescription.id})
        form_data = {
            'medicament': self.medicament.pk,
            'morning': 2.5,
            'weekdays': ['tu', 'th', 'sa'],
        }
        response = self.client.post(update_url, form_data)
        self.assertEqual(response.status_code, 302)
        detail_url = reverse('prescription:detail', kwargs={'pk': self.prescription.id})
        self.assertEqual(response.url, detail_url)
        self.prescription.refresh_from_db()
        self.assertEqual(self.prescription.medicament, self.medicament)
        self.assertEqual(self.prescription.morning, Decimal('2.5'))
        self.assertFalse(self.prescription.weekdays.mo)
        self.assertTrue(self.prescription.weekdays.tu)
        self.assertFalse(self.prescription.weekdays.we)
        self.assertTrue(self.prescription.weekdays.th)
        self.assertFalse(self.prescription.weekdays.fr)
        self.assertTrue(self.prescription.weekdays.sa)
        self.assertFalse(self.prescription.weekdays.su)

    def test_prescription_delete_view_no_user(self):
        delete_url = reverse('prescription:delete', kwargs={'pk': self.prescription.id})
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={delete_url}')

    def test_prescription_delete_view_get(self):
        self.client.force_login(self.user)
        delete_url = reverse('prescription:delete', kwargs={'pk': self.prescription.id})
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)

    def test_prescription_delete_view_post(self):
        self.client.force_login(self.user)
        prescription_id = self.medicament.id
        delete_url = reverse('prescription:delete', kwargs={'pk': self.prescription.id})
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        with pytest.raises(Prescription.DoesNotExist):  # pylint: disable=no-member
            Prescription.objects.get(pk=prescription_id)
