# -*- coding: utf-8 -*-
import datetime
import json
from decimal import Decimal
from logging import getLogger

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Avg, Max, Min
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone, formats, dateparse
from django.utils.translation import gettext_lazy as _

from mail_templated import send_mail

from medic.utils import getLocaleMonthNames

from usrprofile.models import UserProfile
from usrprofile.forms import MailForm

from werte.forms import TimeForm, MesswertForm
from werte.models import Wert

logger = getLogger('medic')


@login_required(login_url='/login/')
def werte(request):
    wertelist = Wert.objects.none()
    form = None
    message = ''

    try:
        up = UserProfile.objects.get(ref_usr=request.user)

        t = datetime.timedelta(days=up.werteLetzteTage)  # default from UserProfile
        bis = timezone.now()
        von = bis - t

        if request.method == 'POST':
            form = TimeForm(request.POST)
            if form.is_valid():
                von = form.cleaned_data['vonDate']
                bis = form.cleaned_data['bisDate']
                if von > bis:
                    messages.error(request, _('From date must be earlier than to date!'))
        else:
            form = TimeForm(initial={
                'vonDate': von,
                'bisDate': bis
            })

        wertelist = Wert.objects.filter(
            date__date__gte=von,
            date__date__lte=bis,
            ref_usr=request.user
        ).order_by('-date')
    except UserProfile.DoesNotExist:
        message = _('User {user} has no user profile.').format(user=request.user)
        messages.error(request, message)
        return redirect(reverse_lazy('startpage'))
    except Exception as e:
        message = _('Error in reading measurements.')
        logger.exception(message)
        messages.error(request, message)

    return render(request, 'werte/werte.html',
                  {'wertelist': wertelist, 'form': form, 'user': request.user, 'von': von, 'bis': bis})


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
                        messages.warning(request,
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


@login_required(login_url='/login/')
def minmax(request, von, bis):
    von_date = dateparse.parse_date(von)
    bis_date = dateparse.parse_date(bis)

    minrrsys = maxrrsys = medrrsys = None
    minrrdia = maxrrdia = medrrdia = None
    minpuls = maxpuls = medpuls = None
    mintemp = maxtemp = medtemp = None
    mingew = maxgew = medgew = None

    try:
        values = Wert.objects.filter(
            date__date__gte=von_date,
            date__date__lte=bis_date,
            ref_usr=request.user
        ).exclude(rrsys=None
                  ).aggregate(
            Avg('rrsys'), Max('rrsys'), Min('rrsys'),
            Avg('rrdia'), Max('rrdia'), Min('rrdia'),
            Avg('puls'), Max('puls'), Min('puls'),
            Avg('temp'), Max('temp'), Min('temp'),
            Avg('gew'), Max('gew'), Min('gew'),
        )

        minrrsys = values['rrsys__min']
        maxrrsys = values['rrsys__max']
        medrrsys = values['rrsys__avg']

        minrrdia = values['rrdia__min']
        maxrrdia = values['rrdia__max']
        medrrdia = values['rrdia__avg']

        minpuls = values['puls__min']
        maxpuls = values['puls__max']
        medpuls = values['puls__avg']

        mintemp = values['temp__min']
        maxtemp = values['temp__max']
        medtemp = values['temp__avg']

        mingew = values['gew__min']
        maxgew = values['gew__max']
        medgew = values['gew__avg']
    except:
        message = _('Error in calculating statistics')
        logger.exception(message)
        messages.error(request, message)

    return render(request, 'werte/minmax.html', {
        'minrrsys': minrrsys, 'maxrrsys': maxrrsys, 'medrrsys': medrrsys,
        'minrrdia': minrrdia, 'maxrrdia': maxrrdia, 'medrrdia': medrrdia,
        'minpuls': minpuls, 'maxpuls': maxpuls, 'medpuls': medpuls,
        'mintemp': mintemp, 'maxtemp': maxtemp, 'medtemp': medtemp,
        'mingew': mingew, 'maxgew': maxgew, 'medgew': medgew,
        'vonDate': von_date, 'bisDate': bis_date, 'user': request.user
    })


@login_required(login_url='/login/')
def delwert(request, delwert_id):
    try:
        Wert.objects.get(id=delwert_id).delete()
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse("ok")


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


class WertCreateView(LoginRequiredMixin, BSModalCreateView):
    model = Wert
    form_class = MesswertForm
    template_name = 'werte/measurments_form.html'
    success_message = _('New masurements saved.')
    success_url = reverse_lazy('werte:werte')

    def form_valid(self, form):
        new_val = form.save(commit=False)
        new_val.ref_usr = self.request.user
        new_val.save()
        return super().form_valid(form)


class WertUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Wert
    form_class = MesswertForm
    template_name = 'werte/measurments_form.html'
    success_message = _('Masurements saved.')
    success_url = reverse_lazy('werte:werte')
