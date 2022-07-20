# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from logging import getLogger

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from chartjs.views.lines import BaseLineChartView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Avg, Max, Min
from django.utils import formats, timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, TemplateView
from django_filters.views import FilterView

from werte.filters import MeasurementFilter

from werte.forms import MeasurementForm
from werte.models import Measurement, ValueType, Value

logger = getLogger('medic')


class MeasurementListView(LoginRequiredMixin, FilterView):
    model = Measurement
    filterset_class = MeasurementFilter
    paginate_by = 16

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['value_types'] = ValueType.objects.active()
        return ctx

    def get_queryset(self):
        return Measurement.objects.filter(
            owner=self.request.user
        ).prefetch_related('values').all()


class MeasurementCreateView(LoginRequiredMixin, BSModalCreateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = 'werte/measurment_form.html'
    success_message = _('New masurements saved.')
    success_url = reverse_lazy('werte:werte')

    def form_valid(self, form):
        measurement = form.save(commit=False)
        measurement.owner = self.request.user
        measurement.save()
        for value_type in ValueType.objects.active():
            if value_type.slug in form.cleaned_data:
                Value.objects.create(
                    value_type=value_type,
                    measurement=measurement,
                    value=form.cleaned_data[value_type.slug]
                )
        return super().form_valid(form)


class MeasurementUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = 'werte/measurment_form.html'
    success_message = _('Masurements saved.')
    success_url = reverse_lazy('werte:werte')

    def get_initial(self):
        initial = super().get_initial()
        for value_type in ValueType.objects.active():
            try:
                value = Value.objects.get(
                    value_type=value_type,
                    measurement=self.object,
                )
                initial[value_type.slug] = f'{value.value:.{value_type.format}f}'
            except Value.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        measurement = form.save(commit=False)
        for value_type in ValueType.objects.active():
            if value_type.slug in form.cleaned_data and value_type.slug in form.changed_data:
                value = Value.objects.get(
                    value_type=value_type,
                    measurement=measurement,
                )
                value.value = form.cleaned_data[value_type.slug]
                value.save()
        return super().form_valid(form)


class MeasurementMinMaxView(LoginRequiredMixin, ListView):
    model = Measurement
    template_name = 'werte/minmax.html'

    def get_queryset(self):
        measurements = Measurement.objects.filter(
            owner=self.request.user,
        )
        von = self.kwargs.get('von', None)
        if von:
            measurements = measurements.filter(date__date__gte=von)
        bis = self.kwargs.get('bis', None)
        if bis:
            measurements = measurements.filter(date__date__lte=bis)
        return measurements.prefetch_related('values').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        value_types = ValueType.objects.active().order_by('sort_order')
        values = self.get_queryset()
        stats = {}
        for value_type in value_types:
            stats[value_type.slug] = Value.objects.filter(
                value_type__slug=value_type.slug, measurement__in=values
            ).aggregate(Avg('value'), Max('value'), Min('value'))
            stats[value_type.slug]['unit'] = value_type.unit
            stats[value_type.slug]['name'] = value_type.name
            stats[value_type.slug]['format'] = value_type.format
        context['stats'] = stats
        context['von'] = values.last()
        context['bis'] = values.first()
        return context


class MeasurementDiagramView(LoginRequiredMixin, TemplateView):
    template_name = 'werte/diagram.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['value_types'] = ValueType.objects.active()
        context['von'] = self.kwargs.get('von', None)
        context['bis'] = self.kwargs.get('bis', None)
        if context['von'] == '':
            context['first'] = Measurement.objects.order_by('date').first().date
        else:
            context['first'] = datetime.strptime(context['von'], '%Y-%m-%d')
        if context['bis'] == '':
            context['last'] = Measurement.objects.order_by('date').last().date
        else:
            context['last'] = datetime.strptime(context['bis'], '%Y-%m-%d')
        return context


class ValuesJSONView(BaseLineChartView):
    value_type = None
    queryset = None

    def get(self, request, *args, **kwargs):
        typus = kwargs.get('type')
        date_from = timezone.now() - timedelta(days=4*365)
        self.value_type = ValueType.objects.get(slug=typus)
        self.queryset = Value.objects.filter(
            value_type__slug=typus, measurement__date__gte=date_from
        ).order_by('measurement__date')
        return super().get(request, *args, **kwargs)

    def get_providers(self):
        return [self.value_type.name]

    def get_labels(self):
        return [formats.date_format(item.measurement.date, 'd.m.y') for item in self.queryset]

    def get_data(self):
        return [[int(item.value) for item in self.queryset]]
