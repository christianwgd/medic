from datetime import timedelta

from django.contrib import auth
from django.test import TestCase
from django.utils import formats, timezone
from faker import Faker

from medicament.models import Medicament, UNIT_CHOICES, StockChange
from prescription.models import Prescription


class MedicamentTestCase(TestCase):
    def setUp(self):
        self.fake = Faker('de_DE')
        user_model = auth.get_user_model()
        self.user = user_model.objects.create(username=self.fake.user_name())
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
            text=self.fake.paragraph(nb_sentences=1),
            owner=self.user
        )
        self.assertEqual(str(stock_change), str(self.medicament))
        self.medicament.refresh_from_db()
        self.assertEqual(self.medicament.stock, med_stock + self.medicament.package)
