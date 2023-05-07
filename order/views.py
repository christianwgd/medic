from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.utils.translation import gettext as _

from order.forms import OrderForm
from order.models import Order


class OrderListView(LoginRequiredMixin, ListView):
    model = Order


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order


class OrderCreateView(LoginRequiredMixin, BSModalCreateView):
    model = Order
    form_class = OrderForm
    success_message = _('Order created.')
    success_url = reverse_lazy('order:list')

    # def get_success_url(self):
    #     return reverse('order:list')

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['user'] = self.request.user
        return form_kwargs

    def form_valid(self, form):
        new_order = form.save(commit=False)
        new_order.owner = self.request.user
        return super().form_valid(form)


class OrderUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Order
    form_class = OrderForm
    success_message = _('Order saved.')

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['user'] = self.request.user
        return form_kwargs


class OrderDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = Order
    success_message = _('Order deleted.')

    def get_success_url(self):
        return reverse('order:list')


@login_required
def close_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.done = True
    order.save()
    messages.success(request, _('Order closed'))
    return redirect(reverse('order:detail', kwargs={'pk': order_id}))
