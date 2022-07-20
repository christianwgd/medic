# -*- coding: utf-8 -*-
import json
from decimal import Decimal
from logging import getLogger

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.urls import reverse_lazy
from django.db.models import Avg, Max, Min, F, ExpressionWrapper, Func, CharField
from django.shortcuts import render, redirect
from django.utils import formats, dateparse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django_filters.views import FilterView

from medic.utils import getLocaleMonthNames

from werte.filters import MeasurementFilter

from werte.forms import MeasurementForm
from werte.models import Wert, Measurement, ValueType, Value

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


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


def date_to_str(date):
    return formats.date_format(date.date, 'c')


class MeasurementDiagramView(LoginRequiredMixin, ListView):
    model = Measurement
    template_name = 'werte/diagram.html'

    def get_queryset(self):
        measurements = Measurement.objects.filter(
            owner=self.request.user,
        ).order_by('date')
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
        diagram_data = {}
        for value_type in value_types:
            diagram_data[value_type.slug] = Value.objects.filter(
                value_type__slug=value_type.slug, measurement__in=self.get_queryset()
            ).values_list(
                'measurement__date', 'value'
            )
        print(diagram_data)
        return context


@login_required(login_url='/login/')
def diagram(request, von, bis):
    von_date = dateparse.parse_date(von)
    bis_date = dateparse.parse_date(bis)

    sys = []
    dia = []
    puls = []
    temp = []
    gew = []

    try:
        wertelist = Wert.objects.filter(
            date__date__gte=von_date,
            date__date__lte=bis_date,
            ref_usr=request.user
        ).order_by('date')

        if wertelist.count() == 0:
            messages.warning(request, _('No measurements found.'))
            return redirect(reverse_lazy('startpage'))

        for wert in wertelist:
            date = formats.date_format(wert.date, 'c')
            sys.append([date, wert.rrsys])
            dia.append([date, wert.rrdia])
            puls.append([date, wert.puls])
            temp.append([date, wert.temp])
            gew.append([date, wert.gew])

        js_sys = json.dumps(sys, cls=DecimalEncoder)
        js_dia = json.dumps(dia, cls=DecimalEncoder)
        js_puls = json.dumps(puls, cls=DecimalEncoder)
        js_temp = json.dumps(temp, cls=DecimalEncoder)
        js_gew = json.dumps(gew, cls=DecimalEncoder)
    except:
        message = _('Error in measurements')
        logger.exception(message)
        messages.error(request, message)

    loc_months = getLocaleMonthNames()
    return render(request, 'werte/diagram.html', {
        'user': request.user,
        'sys': js_sys,
        'dia': js_dia,
        'puls': js_puls,
        'tmp': js_temp,
        'gew': js_gew,
        'loc_months': loc_months,
    })
