
from datetime import datetime
from logging import getLogger

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from bootstrap_modal_forms.mixins import is_ajax
from chartjs.views.lines import BaseLineChartView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db.models import Avg, Max, Min
from django.utils import formats, timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, TemplateView
from django_filters.views import FilterView

from measurement.filters import MeasurementFilter

from measurement.forms import MeasurementForm
from measurement.models import Measurement, ValueType, Value

logger = getLogger('medic')


class MeasurementListView(LoginRequiredMixin, FilterView):
    model = Measurement
    filterset_class = MeasurementFilter

    def get_paginate_by(self, queryset):
        return self.request.user.profile.measurements_items_per_page

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['value_types'] = self.request.user.profile.active_value_types.all()
        # change dates because of reversed ordering!
        if self.filterset.qs.all():
            ctx['max_date'] = formats.date_format(self.filterset.qs.first().date, 'Y-m-d')
            ctx['min_date'] = formats.date_format(self.filterset.qs.last().date, 'Y-m-d')
        else:
            today = formats.date_format(timezone.now().date())
            ctx['max_date'] = ctx['min_date'] = today
        return ctx

    def get_queryset(self):
        return Measurement.objects.filter(
            owner=self.request.user,
        ).prefetch_related('values').all()


class MeasurementPrintView(LoginRequiredMixin, ListView):
    model = Measurement
    template_name = 'measurement/measurement_print.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['value_types'] = self.request.user.profile.active_value_types.all()
        ctx['min_date'] = datetime.strptime(self.kwargs['von'], '%Y-%m-%d').astimezone()
        ctx['max_date'] = datetime.strptime(self.kwargs['bis'], '%Y-%m-%d').astimezone()
        return ctx

    def get_queryset(self):
        measurements = Measurement.objects.filter(
            owner=self.request.user,
            date__date__gte=self.kwargs['von'],
            date__date__lte=self.kwargs['bis'],
        )
        return measurements.prefetch_related('values').all()


class MeasurementCreateView(LoginRequiredMixin, BSModalCreateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = 'measurement/measurment_form.html'
    success_message = _('New masurements saved.')
    success_url = reverse_lazy('measurement:list')

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        form_kwargs['user'] = self.request.user
        return form_kwargs

    def form_valid(self, form):
        if not is_ajax(self.request.META):
            measurement = form.save(commit=False)
            measurement.owner = self.request.user
            measurement.save()
            for value_type in self.request.user.profile.active_value_types.all():
                if form.cleaned_data.get(value_type.slug):
                    Value.objects.create(
                        value_type=value_type,
                        measurement=measurement,
                        value=form.cleaned_data[value_type.slug],
                    )
            return redirect(self.success_url)
        return super().form_valid(form)


class MeasurementUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = 'measurement/measurment_form.html'
    success_message = _('Masurements saved.')
    success_url = reverse_lazy('measurement:list')

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        form_kwargs['user'] = self.request.user
        return form_kwargs

    def get_initial(self):
        initial = super().get_initial()
        for value_type in self.request.user.profile.active_value_types.all():
            try:
                value = Value.objects.get(
                    value_type=value_type,
                    measurement=self.object,
                )
                if value.value is not None:
                    initial[value_type.slug] = f'{value.value:.{value_type.decimals}f}'
            except Value.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        measurement = form.save(commit=False)
        for value_type in self.request.user.profile.active_value_types.all():
            if value_type.slug in form.cleaned_data and value_type.slug in form.changed_data:
                value, _created = Value.objects.get_or_create(
                    value_type=value_type,
                    measurement=measurement,
                )
                value.value = form.cleaned_data[value_type.slug]
                value.save()
        return super().form_valid(form)


class MeasurementMinMaxView(LoginRequiredMixin, ListView):
    model = Measurement
    template_name = 'measurement/minmax.html'

    def get_queryset(self):
        measurements = Measurement.objects.filter(
            owner=self.request.user,
            date__date__gte=self.kwargs['von'],
            date__date__lte=self.kwargs['bis'],
        )
        return measurements.prefetch_related('values').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        value_types = self.request.user.profile.active_value_types.all()
        values = self.get_queryset()
        stats = {}
        for value_type in value_types:
            stats[value_type.slug] = Value.objects.filter(
                value_type__slug=value_type.slug, measurement__in=values,
            ).aggregate(Avg('value'), Max('value'), Min('value'))
            stats[value_type.slug]['unit'] = value_type.unit
            stats[value_type.slug]['name'] = value_type.name
            stats[value_type.slug]['decimals'] = value_type.decimals
        context['stats'] = stats
        context['von'] = values.last()
        context['bis'] = values.first()
        return context


class MeasurementDiagramView(LoginRequiredMixin, TemplateView):
    template_name = 'measurement/diagram.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['value_types'] = self.request.user.profile.active_value_types.all()
        context['von'] = self.kwargs.get('von', '')
        context['bis'] = self.kwargs.get('bis', '')
        context['first'] = datetime.strptime(context['von'], '%Y-%m-%d').astimezone()
        context['last'] = datetime.strptime(context['bis'], '%Y-%m-%d').astimezone()
        return context


class ValuesJSONView(BaseLineChartView):
    value_type = None
    queryset = None

    def get(self, request, *args, **kwargs):
        typus = kwargs.get('type')
        low_date = timezone.make_aware(datetime.strptime(self.kwargs['von'], '%Y-%m-%d'))
        high_date = timezone.make_aware(datetime.strptime(self.kwargs['bis'], '%Y-%m-%d'))
        self.value_type = ValueType.objects.get(slug=typus)
        self.queryset = Value.objects.filter(
            measurement__owner=self.request.user,
            value_type__slug=typus,
            measurement__date__gte=low_date,
            measurement__date__lte=high_date,
        ).order_by('measurement__date')
        return super().get(request, *args, **kwargs)

    def get_providers(self):
        return [self.value_type.name]

    def get_labels(self):
        return [formats.date_format(item.measurement.date, 'd.m.y') for item in self.queryset]

    def get_data(self):
        return [[round(item.value, self.value_type.decimals) for item in self.queryset]]
