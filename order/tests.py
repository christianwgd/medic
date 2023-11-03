import pytest
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.translation import gettext as _

from medicament.models import Medicament
from medicament.tests import MedicamentTestCase
from order.forms import OrderForm
from order.models import Order
from prescription.models import Prescription


class OrderModelTests(MedicamentTestCase):

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            owner=self.user,
        )
        self.order.medicaments.add(self.medicament)

    def test_order_str(self):
        date_str = formats.date_format(
            timezone.localtime(self.order.date),
            format='SHORT_DATETIME_FORMAT',
        )
        self.assertEqual(f"{date_str}", str(self.order))


class OrderFormTests(MedicamentTestCase):

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            owner=self.user,
        )
        self.order.medicaments.add(self.medicament)
        Prescription.objects.create(
            medicament=self.medicament,
            morning=1.0,
            weekdays=127,  # All days a week
            owner=self.user,
        )

    def test_order_form_test_invalid(self):
        form = OrderForm({}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertIn(_('This field is required.'), form.errors['medicaments'])

    def test_medicament_form_test_valid(self):
        form = OrderForm({'medicaments': [self.medicament.id]}, user=self.user)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.errors), 0)

    def test_medicament_form_queryset(self):
        form = OrderForm({}, user=self.user)
        self.assertQuerySetEqual(
            form.fields['medicaments'].queryset,
            Medicament.objects.all()
        )

class OrderViewTests(MedicamentTestCase):

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            owner=self.user,
        )
        self.order.medicaments.add(self.medicament)
        Prescription.objects.create(
            medicament=self.medicament,
            morning=1.0,
            weekdays=127,  # All days a week
            owner=self.user,
        )

    def test_order_list_view_no_user(self):
        list_url = reverse('order:list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={list_url}')

    def test_order_list_view(self):
        self.client.force_login(self.user)
        list_url = reverse('order:list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['order_list']), 1)
        self.assertIsInstance(response.context['order_list'][0], Order)

    def test_order_detail_view_no_user(self):
        detail_url = reverse('order:detail', kwargs={'pk': self.order.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={detail_url}')

    def test_order_detail_view(self):
        self.client.force_login(self.user)
        detail_url = reverse('order:detail', kwargs={'pk': self.order.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['order'], Order)

    def test_order_create_view_no_user(self):
        create_url = reverse('order:create')
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/accounts/login/?next={create_url}')

    def test_order_create_view_get(self):
        self.client.force_login(self.user)
        create_url = reverse('order:create')
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "order/order_form.html")

    def test_order_create_view_post(self):
        self.client.force_login(self.user)
        update_url = reverse('order:create')
        form_data = {'medicaments': [self.medicament.id]}
        response = self.client.post(update_url, form_data, user=self.user)
        self.assertEqual(response.status_code, 302)
        list_url = reverse('order:list')
        self.assertEqual(response.url, list_url)
        new_order = Order.objects.latest('date')
        self.assertEqual(new_order.medicaments.first(), self.medicament)

    def test_order_update_view_get(self):
        self.client.force_login(self.user)
        update_url = reverse('order:update', kwargs={'pk': self.order.id})
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200)
        order = response.context['order']
        self.assertIsInstance(order, Order)
        self.assertEqual(order, self.order)

    def test_order_update_view_post(self):
        self.client.force_login(self.user)
        update_url = reverse('order:update', kwargs={'pk': self.order.id})
        form_data = {'medicaments': [self.medicament.id]}
        response = self.client.post(update_url, form_data, user=self.user)
        self.assertEqual(response.status_code, 302)
        detail_url = reverse('order:detail', kwargs={'pk': self.order.id})
        self.assertEqual(response.url, detail_url)
        self.order.refresh_from_db()
        self.assertEqual(self.order.medicaments.first(), self.medicament)

    def test_order_delete_view_get(self):
        self.client.force_login(self.user)
        delete_url = reverse('order:delete', kwargs={'pk': self.order.id})
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)

    def test_order_delete_view_post(self):
        self.client.force_login(self.user)
        order_id = self.order.id
        delete_url = reverse('order:delete', kwargs={'pk': self.order.id})
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        with pytest.raises(Order.DoesNotExist):  # pylint: disable=no-member
            Order.objects.get(pk=order_id)

    def test_order_close(self):
        self.client.force_login(self.user)
        close_url = reverse('order:close', kwargs={'order_id': self.order.id})
        response = self.client.post(close_url)
        self.assertEqual(response.status_code, 302)
        detail_url = reverse('order:detail', kwargs={'pk': self.order.id})
        self.assertEqual(response.url, detail_url)
        self.order.refresh_from_db()
        self.assertTrue(self.order.done)
