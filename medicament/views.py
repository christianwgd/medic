# -*- coding: utf-8 -*-
import logging

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalReadView
from bootstrap_modal_forms.utils import is_ajax
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, DeleteView
from django.contrib import messages
from django.db.models import ProtectedError
from django_filters.views import FilterView

from medicament.models import Medicament, StockChange
from medicament.filter import MedicamentFilter, StockChangeFilter
from medicament.forms import MedicamentForm, StockChangeForm

logger = logging.getLogger('medic')


class MedicamentListView(LoginRequiredMixin, FilterView):
    model = Medicament
    filterset_class = MedicamentFilter

    def get_paginate_by(self, queryset):
        return self.request.user.profile.medicaments_items_per_page

    def get_queryset(self):
        return Medicament.objects.filter(owner=self.request.user)


class MedicamentDetailView(LoginRequiredMixin, DetailView):
    model = Medicament


class MedicamentReadView(LoginRequiredMixin, BSModalReadView):
    model = Medicament
    template_name = 'medicament/medicament_detail_modal.html'


class MedicamentCreateView(LoginRequiredMixin, BSModalCreateView):
    model = Medicament
    form_class = MedicamentForm
    success_message = _('New medicament saved.')
    success_url = reverse_lazy('medicament:list')

    def form_valid(self, form):
        new_med = form.save(commit=False)
        new_med.owner = self.request.user
        return super().form_valid(form)


class MedicamentUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Medicament
    form_class = MedicamentForm
    success_message = _('Medicament saved.')

    def get_success_url(self):
        return reverse('medicament:detail', kwargs={'pk': self.object.id})


class MedicamentDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Medicament
    success_url = reverse_lazy('medicament:list')
    success_message = _('Medicament deleted')

    def form_valid(self, form):
        try:
            if not is_ajax(self.request.META):
                super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, _('Could not delete medicament due to existing prescription.'))
        return redirect(self.success_url)


class StockChangeCreateView(LoginRequiredMixin, BSModalCreateView):
    model = StockChange
    form_class = StockChangeForm
    success_message = _('Stock update saved.')

    def get_success_url(self):
        return reverse('medicament:detail', kwargs={'pk': self.kwargs['med_id']})

    def get_initial(self):
        initial = super().get_initial()
        initial['medicament'] = Medicament.objects.get(id=self.kwargs['med_id'])
        initial['date'] = timezone.now()
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        med = Medicament.objects.get(id=self.kwargs['med_id'])
        context['medicament'] = med
        context['package'] = med.package
        prescription = med.get_active_prescription(for_user=self.request.user)
        if prescription is None:
            context['dose'] = 1.0
        else:
            context['dose'] = prescription.get_default_dose()
        return context

    def form_valid(self, form):
        if form.cleaned_data['amount'] > 0.0:
            stock_change = form.save(commit=False)
            stock_change.owner = self.request.user
            stock_change.medicament = Medicament.objects.get(id=self.kwargs['med_id'])
            if form.cleaned_data['reason'] == '00':
                stock_change.medicament.last_calc = timezone.now()
                stock_change.medicament.save()
            return super().form_valid(form)
        return redirect(self.get_success_url())


class StockChangeHistoryView(LoginRequiredMixin, FilterView):
    model = StockChange
    filterset_class = StockChangeFilter
    template_name = 'medicament/stockchange_filter.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context['medicament'] = Medicament.objects.get(id=self.kwargs['med_id'])
        return context

    def get_paginate_by(self, queryset):
        return self.request.user.profile.medicaments_items_per_page

    def get_queryset(self):
        return StockChange.objects.filter(
            owner=self.request.user,
            medicament=Medicament.objects.get(id=self.kwargs['med_id'])
        )


@require_http_methods(['GET'])
@login_required
def calc_consumption(request, med_id):
    medicament = Medicament.objects.get(id=med_id)
    today = timezone.now().date()
    if medicament.last_calc is None or medicament.last_calc < today:
        prescription = medicament.get_active_prescription(for_user=request.user)
        if medicament.last_calc is None:
            last_calc = prescription.valid_from
        else:
            last_calc = medicament.last_calc
        consumption = prescription.get_amount_for_time(
            start_date=last_calc,
            end_date=today,
            user=request.user
        )
    else:
        consumption = 0
    return JsonResponse({'consumption': consumption})
