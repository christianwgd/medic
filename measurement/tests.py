from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.contrib import auth
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext as _
from faker import Faker

from measurement.forms import MeasurementForm
from measurement.models import Measurement, ValueType, Value
from measurement.templatetags.measurement_tags import format_value


user_model = auth.get_user_model()


class ValueTypeModelTest(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')

    def test_active_type_str(self):
        value_type = ValueType.objects.first()
        self.assertEqual(str(value_type), value_type.name)

    def test_active_type_manager(self):
        value_type = ValueType.objects.first()
        value_type.active = False
        value_type.save()
        value_types = ValueType.objects.all()
        active_value_types = ValueType.objects.active()
        self.assertEqual(value_types.count(), 5)
        self.assertEqual(active_value_types.count(), 4)


class MeasurementModelTests(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.user = user_model.objects.create(username=self.fake.user_name())
        self.today = timezone.now()
        self.measurement = Measurement.objects.create(
            owner=self.user,
            comment=self.fake.text(max_nb_chars=50),
            date=self.today,
        )
        self.value_type = ValueType.objects.last()
        self.value = Value.objects.create(
            value_type=self.value_type,
            value=54.3,
            measurement=self.measurement,
        )

    def test_measurement_str(self):
        self.assertEqual(str(self.measurement), date_format(self.today))

    def test_value_str(self):
        self.assertEqual(str(self.value), f'{self.value_type}-{self.measurement}')

    def test_active_value_manager(self):
        value_type_inactive = ValueType.objects.first()
        value_type_inactive.active = False
        value_type_inactive.save()
        value_type_active = ValueType.objects.last()
        Value.objects.create(
            value_type=value_type_inactive, value='55', measurement=self.measurement,
        )
        Value.objects.create(
            value_type=value_type_active, value='12.3', measurement=self.measurement,
        )
        active_values = Value.objects.active()
        self.assertEqual(active_values.count(), 2)
        self.assertEqual(Value.objects.count(), 3)


class MeasurementTemplateTagTests(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.user = user_model.objects.create(username=self.fake.user_name())
        self.today = timezone.now()
        self.measurement = Measurement.objects.create(
            owner=self.user,
            comment=self.fake.text(max_nb_chars=50),
            date=self.today,
        )
        self.value_type = ValueType.objects.last()
        self.value = Value.objects.create(
            value_type=self.value_type,
            value=54.3333,
            measurement=self.measurement,
        )

    def test_format_value_tag(self):
        formatted_value = format_value(self.measurement, self.value_type)
        self.assertEqual(formatted_value, '54.3')


class MeasurementFormTests(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')

    def test_measurement_form_fields(self):
        weight = ValueType.objects.get(slug='gewicht')
        weight.active = False
        weight.save()
        form = MeasurementForm()
        self.assertTrue('rrsys' in form.fields)
        self.assertTrue('rrdia' in form.fields)
        self.assertTrue('puls' in form.fields)
        self.assertFalse('gewicht' in form.fields)
        self.assertTrue('temp' in form.fields)

    def test_measurement_form_empty(self):
        form = MeasurementForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertIn(_('No values entered.'), form.errors['__all__'])

    def test_measurement_form_valid(self):
        form = MeasurementForm({'rrsys': 122, 'rrdia': 77, 'puls': 66})
        self.assertTrue(form.is_valid())


class MeasurementViewTests(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        self.user = user_model.objects.create(username=self.fake.user_name())
        self.today = timezone.now()
        self.measurement = Measurement.objects.create(
            owner=self.user,
            comment=self.fake.text(max_nb_chars=50),
            date=self.today,
        )
        self.value_type = ValueType.objects.last()
        self.value = Value.objects.create(
            value_type=self.value_type,
            value=54.3333,
            measurement=self.measurement,
        )

    def test_measurement_list_view_no_user(self):
        list_url = reverse('measurement:list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={list_url}')

    def test_measurement_list_view(self):
        self.client.force_login(self.user)
        list_url = reverse('measurement:list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), 1)
        self.assertIsInstance(page_obj[0], Measurement)

    def test_measurement_list_filter(self):
        last_week = self.today - timedelta(days=7)
        limit_date = self.today - timedelta(days=4)
        measurement = Measurement.objects.create(
            owner=self.user,
            comment=self.fake.text(max_nb_chars=50),
        )
        measurement.date = last_week
        measurement.save()
        value_type = ValueType.objects.last()
        Value.objects.create(
            value_type=value_type,
            value=88.1,
            measurement=measurement,
        )
        self.client.force_login(self.user)
        list_url = reverse('measurement:list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 2)

        response = self.client.get(
            f'{list_url}?date_min={date_format(limit_date, "Y-m-d")}',
        )
        self.assertEqual(response.status_code, 200)
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), 1)
        measurement = page_obj[0]
        self.assertEqual(measurement.values.first().value, Decimal('54.33'))

        response = self.client.get(
            f'{list_url}?date_max={date_format(limit_date, "Y-m-d")}',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 1)
        page_obj = response.context['page_obj']
        measurement = page_obj[0]
        self.assertEqual(measurement.values.first().value, Decimal('88.10'))

    def test_measurement_list_view_empty_qs(self):
        blank_user = user_model.objects.create(username=self.fake.user_name())
        self.client.force_login(blank_user)
        list_url = reverse('measurement:list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), 0)

    def test_measurement_print_view(self):
        measurements = Measurement.objects.all()
        date_min = date_format(
            measurements.first().date - timedelta(days=1), "Y-m-d",
        )
        date_max = date_format(
            measurements.last().date + timedelta(days=1), "Y-m-d",
        )
        self.client.force_login(self.user)
        list_url = reverse('measurement:print', kwargs={'von': date_min, 'bis': date_max})
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        measurements = response.context['measurement_list']
        self.assertEqual(len(measurements), 1)
        self.assertIsInstance(measurements[0], Measurement)

    def test_measurement_create_view_no_user(self):
        create_url = reverse('measurement:neu')
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={create_url}')

    def test_measurement_create_view(self):
        self.client.force_login(self.user)
        create_url = reverse('measurement:neu')
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 200)
        form_data = {
            'rrsys': 120,
            'rrdia': 80,
            'puls': 66,
        }
        measurements_count = Measurement.objects.count()
        response = self.client.post(create_url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('measurement:list'))
        self.assertEqual(Measurement.objects.count(), measurements_count + 1)
        # Get the newly created measurement, first because reverse ordering
        new_measurement = Measurement.objects.first()
        self.assertEqual(new_measurement.values.get(value_type__slug='rrsys').value, 120)
        self.assertEqual(new_measurement.values.get(value_type__slug='rrdia').value, 80)
        self.assertEqual(new_measurement.values.get(value_type__slug='puls').value, 66)

    def test_measurement_update_view_no_user(self):
        update_url = reverse('measurement:edit', kwargs={'pk': self.measurement.id})
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={update_url}')

    def test_measurement_update_view(self):
        self.client.force_login(self.user)
        update_url = reverse('measurement:edit', kwargs={'pk': self.measurement.id})
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200)
        form_data = {
            'rrsys': 120,
            'rrdia': 80,
            'puls': 66,
        }
        response = self.client.post(update_url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('measurement:list'))
        self.measurement.refresh_from_db()
        self.assertEqual(self.measurement.values.get(value_type__slug='rrsys').value, 120)
        self.assertEqual(self.measurement.values.get(value_type__slug='rrdia').value, 80)
        self.assertEqual(self.measurement.values.get(value_type__slug='puls').value, 66)

    def test_measurement_minmax_view(self):
        measurements = Measurement.objects.all()
        date_min = date_format(
            measurements.first().date - timedelta(days=1), "Y-m-d",
        )
        date_max = date_format(
            measurements.last().date + timedelta(days=1), "Y-m-d",
        )
        self.client.force_login(self.user)
        list_url = reverse('measurement:minmax', kwargs={'von': date_min, 'bis': date_max})
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        measurements = response.context['measurement_list']
        self.assertEqual(len(measurements), 1)
        self.assertIsInstance(measurements[0], Measurement)

    def test_measurement_chart_view(self):
        measurements = Measurement.objects.all()
        date_min = date_format(
            measurements.first().date - timedelta(days=1), "Y-m-d",
        )
        date_max = date_format(
            measurements.last().date + timedelta(days=1), "Y-m-d",
        )
        self.client.force_login(self.user)
        list_url = reverse('measurement:diagram', kwargs={'von': date_min, 'bis': date_max})
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)

    def test_measurement_chart_json(self):
        self.client.force_login(self.user)
        measurements = Measurement.objects.all()
        date_min = date_format(
            measurements.first().date - timedelta(days=1), "Y-m-d",
        )
        date_max = date_format(
            measurements.last().date + timedelta(days=1), "Y-m-d",
        )
        list_url = reverse(
            'measurement:json-values',
            kwargs={'type': 'gewicht', 'von': date_min, 'bis': date_max},
        )
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        resp = response.json()
        self.assertEqual(resp['type'], 'gewicht')
        self.assertEqual(resp['von'], date_min)
        self.assertEqual(resp['bis'], date_max)
        self.assertEqual(len(resp['datasets']), 1)
        self.assertEqual(
            Decimal(resp['datasets'][0]['data'][0]),
            round(measurements.first().values.get(value_type__slug='gewicht').value, 1),
        )
