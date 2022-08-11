from datetime import timedelta
from decimal import Decimal

from django.contrib import auth
from django.test import TestCase
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.translation import gettext as _
from faker import Faker

from medicament.forms import MedicamentForm, StockChangeForm
from medicament.models import Medicament, UNIT_CHOICES, StockChange
from prescription.models import Prescription
from usrprofile.models import UserProfile


class MedicamentTestCase(TestCase):
    def setUp(self):
        self.fake = Faker('de_DE')
        user_model = auth.get_user_model()
        self.user = user_model.objects.create(username=self.fake.user_name())
        self.profile = UserProfile.objects.create(ref_usr=self.user)
        self.medicament = Medicament.objects.create(
            name=self.fake.word(),
            producer=self.fake.word(),
            ingredient=self.fake.word(),
            package=self.fake.random_int(min=50, max=250, step=50),
            strength=self.fake.random_int(min=1, max=50, step=5),
            unit=UNIT_CHOICES[self.fake.random_int(min=0, max=3)][0],
            owner=self.user
        )


class MedicamentModelTest(MedicamentTestCase):

    def test_medicament_str(self):
        dose = formats.localize(self.medicament.strength, use_l10n=True)
        self.assertEqual(
            str(self.medicament),
            f'{self.medicament.name} {dose} {self.medicament.unit}'
        )

    def test_medicament_active_prescription_none(self):
        self.assertEqual(
            self.medicament.get_active_prescription(for_user=self.user),
            None
        )

    def test_medicament_active_prescription(self):
        today = timezone.now().date()
        Prescription.objects.create(
            medicament=self.medicament,
            morning=1.0,
            weekdays=17,  # Mo and Fr
            owner=self.user,
            valid_from=today-timedelta(days=90),
            valid_until=today-timedelta(days=61)
        )
        prescription_active = Prescription.objects.create(
            medicament=self.medicament,
            morning=2.0,
            weekdays=127,  # all weekdays
            owner=self.user,
            valid_from=today-timedelta(days=60),
        )
        active_prescription = self.medicament.get_active_prescription(for_user=self.user)
        self.assertEqual(active_prescription, prescription_active)
        self.assertEqual(active_prescription.morning, 2.0)
        self.assertTrue(active_prescription.weekdays.tu)
        self.assertTrue(active_prescription.weekdays.sa)

    def test_stock_change_str_and_update(self):
        med_stock = self.medicament.stock
        stock_change = StockChange.objects.create(
            medicament=self.medicament,
            date=timezone.now().date(),
            amount=self.medicament.package,
            reason='01',
            text=self.fake.paragraph(nb_sentences=1)[:49],
            owner=self.user
        )
        self.assertEqual(str(stock_change), str(self.medicament))
        self.medicament.refresh_from_db()
        self.assertEqual(self.medicament.stock, med_stock + self.medicament.package)

    def test_stock_change_update_negative(self):
        med_stock = self.medicament.stock
        StockChange.objects.create(
            medicament=self.medicament,
            date=timezone.now().date(),
            amount=5,
            reason='99',
            text=self.fake.paragraph(nb_sentences=1)[:49],
            owner=self.user
        )
        self.medicament.refresh_from_db()
        self.assertEqual(self.medicament.stock, med_stock - 5)


class MedicamentFormTests(MedicamentTestCase):

    def test_medicament_form_test_invalid(self):
        form = MedicamentForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)
        self.assertIn(_('This field is required.'), form.errors['name'])
        self.assertIn(_('This field is required.'), form.errors['strength'])
        self.assertIn(_('This field is required.'), form.errors['unit'])
        self.assertIn(_('This field is required.'), form.errors['package'])

    def test_medicament_form_test_valid(self):
        form = MedicamentForm({
            'name': self.fake.word(),
            'producer': self.fake.word(),
            'ingredient': self.fake.word(),
            'package': self.fake.random_int(min=50, max=250, step=50),
            'strength': self.fake.random_int(min=1, max=50, step=5),
            'unit': UNIT_CHOICES[self.fake.random_int(min=0, max=3)][0],
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

    def test_stock_change_form_test_invalid(self):
        form = StockChangeForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)
        self.assertIn(_('This field is required.'), form.errors['date'])
        self.assertIn(_('This field is required.'), form.errors['reason'])
        self.assertIn(_('This field is required.'), form.errors['amount'])

    def test_tock_change_form_test_valid(self):
        form = StockChangeForm({
            'date': self.fake.date_this_month(),
            'reason': '01',
            'amount': self.medicament.package,
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)


class MedicamentViewsTest(MedicamentTestCase):

    def test_medicament_list_view_no_user(self):
        list_url = reverse('medicament:list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={list_url}')

    def test_medicament_list_view(self):
        self.client.force_login(self.user)
        list_url = reverse('medicament:list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['medicament_list']), 1)
        self.assertIsInstance(response.context['medicament_list'][0], Medicament)

    def test_medicament_detail_view_no_user(self):
        detail_url = reverse('medicament:detail', kwargs={'pk': self.medicament.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={detail_url}')

    def test_medicament_detail_view(self):
        self.client.force_login(self.user)
        detail_url = reverse('medicament:detail', kwargs={'pk': self.medicament.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        medicament = response.context['medicament']
        self.assertIsInstance(medicament, Medicament)
        self.assertEqual(medicament, self.medicament)

    def test_medicament_update_view_no_user(self):
        update_url = reverse('medicament:update', kwargs={'pk': self.medicament.id})
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={update_url}')

    def test_medicament_update_view_get(self):
        self.client.force_login(self.user)
        update_url = reverse('medicament:update', kwargs={'pk': self.medicament.id})
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200)
        medicament = response.context['medicament']
        self.assertIsInstance(medicament, Medicament)
        self.assertEqual(medicament, self.medicament)

    def test_medicament_update_view_post(self):
        self.client.force_login(self.user)
        update_url = reverse('medicament:update', kwargs={'pk': self.medicament.id})
        form_data = {
            'name': 'new name',
            'package': 100,
            'strength': Decimal(2.0),
            'unit': 'mg',
        }
        response = self.client.post(update_url, form_data)
        self.assertEqual(response.status_code, 302)
        detail_url = reverse('medicament:detail', kwargs={'pk': self.medicament.id})
        self.assertEqual(response.url, detail_url)
        self.medicament.refresh_from_db()
        self.assertEqual(self.medicament.name, 'new name')
        self.assertEqual(self.medicament.package, 100)
        self.assertEqual(self.medicament.strength, Decimal(2.0))
        self.assertEqual(self.medicament.unit, 'mg')

    def test_medicament_delete_view_no_user(self):
        delete_url = reverse('medicament:delete', kwargs={'pk': self.medicament.id})
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={delete_url}')

    def test_medicament_delete_view_get(self):
        self.client.force_login(self.user)
        delete_url = reverse('medicament:delete', kwargs={'pk': self.medicament.id})
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)

    def test_medicament_delete_view_post(self):
        self.client.force_login(self.user)
        med_id = self.medicament.id
        delete_url = reverse('medicament:delete', kwargs={'pk': self.medicament.id})
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Medicament.DoesNotExist):  # pylint: disable=no-member
            Medicament.objects.get(pk=med_id)

    def test_stock_change_list_view_no_user(self):
        list_url = reverse('medicament:stock-history', kwargs={'med_id': self.medicament.id})
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={list_url}')

    def test_stock_change_list_view(self):
        stock_change = StockChange.objects.create(
            medicament=self.medicament,
            date=timezone.now().date(),
            amount=self.medicament.package,
            reason='01',
            text=self.fake.paragraph(nb_sentences=1)[:49],
            owner=self.user
        )
        self.client.force_login(self.user)
        list_url = reverse('medicament:stock-history', kwargs={'med_id': self.medicament.id})
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        stock_change_list = response.context['stockchange_list']
        self.assertEqual(len(stock_change_list), 1)
        stock_change_first = stock_change_list.first()
        self.assertIsInstance(stock_change_first, StockChange)
        self.assertEqual(stock_change_first, stock_change)

    def test_stock_change_create_view_no_user(self):
        create_url = reverse('medicament:stock-change', kwargs={'med_id': self.medicament.id})
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={create_url}')

    def test_stock_change_create_view_get(self):
        self.client.force_login(self.user)
        create_url = reverse('medicament:stock-change', kwargs={'med_id': self.medicament.id})
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 200)

    def test_stock_change_create_view_post(self):
        self.client.force_login(self.user)
        create_url = reverse('medicament:stock-change', kwargs={'med_id': self.medicament.id})
        stock_change_date = self.fake.date_time_this_month().date()
        form_data = {
            'medicament': self.medicament,
            'date': stock_change_date,
            'amount': self.medicament.package,
            'reason': '01',
            'text': self.fake.paragraph(nb_sentences=1),
        }
        response = self.client.post(create_url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('medicament:detail', kwargs={'pk': self.medicament.id})
        )
        new_stock_change = StockChange.objects.filter(
            medicament=self.medicament
        ).order_by('-date').first()
        self.assertEqual(new_stock_change.date, stock_change_date)
        self.assertEqual(new_stock_change.amount, self.medicament.package)
        self.assertEqual(new_stock_change.reason, '01')

    def test_calc_consumption_view_no_user(self):
        calc_url = reverse('medicament:stock-calc', kwargs={'med_id': self.medicament.id})
        response = self.client.get(calc_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={calc_url}')

    def test_calc_consumption_view(self):
        today = timezone.now().date()
        Prescription.objects.create(
            medicament=self.medicament,
            morning=2.0,
            weekdays=127,
            owner=self.user,
            valid_from=today - timedelta(days=60),
        )
        self.client.force_login(self.user)
        calc_url = reverse('medicament:stock-calc', kwargs={'med_id': self.medicament.id})
        response = self.client.get(calc_url)
        self.assertEqual(response.status_code, 200)
        consumption = response.json()['consumption']
        # 2.0 dose * 60 days -> 120
        self.assertEqual(consumption, f"{120.00:.2f}")
