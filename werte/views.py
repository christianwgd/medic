# -*- coding: utf-8 -*-
import json
from decimal import Decimal
from logging import getLogger

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Avg, Max, Min, F
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.utils import formats, dateparse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django_filters.views import FilterView

from mail_templated import send_mail

from medic.utils import getLocaleMonthNames

from usrprofile.models import UserProfile
from usrprofile.forms import MailForm
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



@login_required(login_url='/login/')
def emailwerte(request, von, bis):
    message = ''

    if 'cancel' in request.POST:
        messages.info(request, _('Function canceled.'))
        return redirect(reverse_lazy('werte:werte'))

    von = dateparse.parse_date(von)
    bis = dateparse.parse_date(bis)

    wertelist = Wert.objects.filter(
        date__date__gte=von,
        date__date__lte=bis,
        ref_usr=request.user
    ).order_by('-date')

    min_date = wertelist.earliest('date').date
    max_date = wertelist.latest('date').date

    try:
        user = request.user
        up = UserProfile.objects.get(ref_usr=user)

        if request.method == 'POST':
            form = MailForm(request.POST)
            if form.is_valid():
                try:
                    mail_to = []
                    if user.email is None or user.email == '':
                        messages.warning(
                            request,
                            _('Sending emails requires email address in user settings.')
                        )
                    else:
                        mail_to.append(form.cleaned_data['mailadr'])
                        email_from = user.email
                        send_mail(
                            'werte/emailwerte.txt',
                            {
                                'user': user, 'text': form.cleaned_data['text'],
                                'wertelist': wertelist, 'von': von, 'bis': bis
                            },
                            email_from, mail_to
                        )
                        messages.success(request, _('Email sent.'))
                        return redirect(reverse_lazy('werte:werte'))
                except Exception as e:
                    messages.error(request, _('Error sending email: {}.').format(e))
        else:
            form = MailForm(initial={
                'mailadr': up.email_arzt,
                'subject': _('Measurements {name} from {von} to {bis}').format(
                    name=request.user.get_full_name(),
                    von=formats.date_format(min_date, 'SHORT_DATE_FORMAT'),
                    bis=formats.date_format(max_date, 'SHORT_DATE_FORMAT')
                )}
            )

    except UserProfile.DoesNotExist:
        message = _('User {user} has no user profile.').format(user=request.user)
        messages.error(request, message)
        return redirect(reverse_lazy('startpage'))
    except Exception:
        message = _('Error in reading measurements.')
        logger.exception(message)
        messages.error(request, message)

    return render(request, 'werte/emailwerte.html',
                  {'wertelist': wertelist, 'form': form, 'von': min_date, 'bis': max_date})


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
