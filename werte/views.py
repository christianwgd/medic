# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import calendar
import datetime
import json
from decimal import Decimal
from logging import getLogger

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Avg, Max, Min
from django.forms import ModelForm
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from mail_templated import send_mail

from usrprofile.models import UserProfile
from werte.forms import TimeForm
from werte.models import Wert


logger = getLogger('medic')


def utc_to_local(utc_dt):
    # get integer timestamp to avoid precision lost
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= datetime.timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_dt.microsecond)


@login_required(login_url='/login/')
def werte(request):
    wertelist = Wert.objects.none()
    form = None
    message = ''
    
    try:
        up = UserProfile.objects.get(ref_usr=request.user)
        
        t = datetime.timedelta(days=up.werteLetzteTage)  # default aus UserProfile
        bis = timezone.now()
        von = bis - t
        von = von.replace(hour=23, minute=59)

        if request.method == 'POST':
            form = TimeForm(request.POST)
            if form.is_valid():
                von = datetime.datetime.combine(form.cleaned_data['vonDate'],
                                                datetime.time(00, 00))
                von = timezone.make_aware(von)
                bis = datetime.datetime.combine(form.cleaned_data['bisDate'],
                                                datetime.time(23, 59))
                bis = timezone.make_aware(bis)
                if von > bis:
                    messages.error(request, 'von-Datum muss kleiner als bis-Datum sein!')
        else:
            form = TimeForm(initial={
                'vonDate': von.strftime("%d.%m.%Y"),
                'bisDate': bis.strftime("%d.%m.%Y")
            })
            
        wertelist = Wert.objects.filter(date__gte=von, date__lte=bis, ref_usr=request.user).order_by('-date')
    except UserProfile.DoesNotExist:
        message = u'Der Benutzer %s hat kein Benutzerprofil.' % request.user
        messages.error(request, message)
        return redirect(reverse_lazy('startpage'))
    except Exception as e:
        message = 'Fehler beim Anzeigen der Messwerte: %s' % e
    if message != '':
        logger.exception(message)
        messages.error(request, message)
    
    return render(request, 'werte/werte.html',
                  {'wertelist': wertelist, 'form': form, 'user': request.user})


class MailForm(forms.Form):
    mailadr = forms.EmailField(label="an")
    subject = forms.CharField(max_length=80, label="Betreff")
    text = forms.CharField(max_length=500, required=False,
                           label="Text", widget=forms.Textarea(attrs={'cols': 80, 'rows': 4}))


@login_required(login_url='/login/')
def emailwerte(request, von, bis):
    message = ''

    if 'cancel' in request.POST:
        messages.info(request, 'Funktion abgebrochen.')
        return redirect(reverse_lazy('werte:werte'))

    von_date = timezone.make_aware(datetime.datetime.strptime(von, "%d.%m.%Y"))
    bis_date = timezone.make_aware(datetime.datetime.strptime(bis, "%d.%m.%Y"))

    wertelist = Wert.objects.filter(date__gte=von_date, date__lte=bis_date, ref_usr=request.user).order_by('-date')

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
                             'emails können nicht gesendet werden, da keine eigene email-Adresse angegeben wurde(s.a. Einstellungen).')
                    else:
                        mail_to.append(form.cleaned_data['mailadr'])
                        email_from = user.email
                        send_mail('werte/emailwerte.txt',
                                  {'user': user, 'text': form.cleaned_data['text'], 'wertelist': wertelist, 'von': von, 'bis': bis},
                                  email_from, mail_to)
                        messages.success(request, 'Email gesendet.')
                        return redirect(reverse_lazy('werte:werte'))
                except Exception as e:
                    messages.error(request, 'Fehler beim Senden: {}.'.format(e))
        else:
            form = MailForm(initial={'mailadr': up.email_arzt,
                            'subject': 'Werte %s %s vom %s bis %s' % (request.user.first_name,
                                                                      request.user.last_name, von, bis)})

    except UserProfile.DoesNotExist:
        message = 'Der Benutzer {} hat kein Benutzerprofil.'.format(request.user)
        messages.error(request, message)
        return redirect(reverse_lazy('startpage'))
    except Exception as e:
        message = 'Fehler beim Anzeigen der Messwerte: {}'.format(e)
    if message != '':
        logger.exception(message)
        messages.error(request, message)

    return render(request, 'werte/emailwerte.html',
                  {'wertelist': wertelist, 'form': form, 'von': von, 'bis': bis})


@login_required(login_url='/login/')
def minmax(request, von, bis):
    von_date = datetime.date.today()
    bis_date = datetime.date.today()
    minrrsys = maxrrsys = medrrsys = None
    minrrdia = maxrrdia = medrrdia = None
    minpuls  = maxpuls  = medpuls  = None
    mintemp  = maxtemp  = medtemp  = None
    mingew   = maxgew   = medgew   = None
    
    try:
        von_date = timezone.make_aware(
            datetime.datetime.combine(datetime.datetime.strptime(von, "%d.%m.%Y"),
                                             datetime.time(00, 00))
        )
        bis_date = timezone.make_aware(
            datetime.datetime.combine(datetime.datetime.strptime(bis, "%d.%m.%Y"),
                                             datetime.time(23, 59))
        )
        
        values = (Wert.objects.filter(date__gte=von_date, date__lte=bis_date,
                                      ref_usr=request.user).exclude(rrsys=None)
                                        .aggregate(Avg('rrsys'), Max('rrsys'), Min('rrsys'),
                                                   Avg('rrdia'), Max('rrdia'), Min('rrdia'),
                                                   Avg('puls'), Max('puls'), Min('puls'),
                                                   Avg('temp'), Max('temp'), Min('temp'),
                                                   Avg('gew'), Max('gew'), Min('gew'),))

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
    except Exception as e:
        message = 'Fehler beim Anzeigen der Statistik-Werte: %s' % e
        logger.exception(message)
        messages.error(request, message)
    
    return render(request, 'werte/minmax.html',
                  {'minrrsys': minrrsys, 'maxrrsys': maxrrsys, 'medrrsys': medrrsys,
                   'minrrdia': minrrdia, 'maxrrdia': maxrrdia, 'medrrdia': medrrdia,
                   'minpuls': minpuls, 'maxpuls': maxpuls, 'medpuls': medpuls,
                   'mintemp': mintemp, 'maxtemp': maxtemp, 'medtemp': medtemp,
                   'mingew': mingew, 'maxgew': maxgew, 'medgew': medgew,
                   'vonDate': von_date, 'bisDate': bis_date, 'user': request.user})


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

    sys = []
    dia = []
    puls = []
    temp = []
    gew = []
    
    try:
        von_date = timezone.make_aware(
            datetime.datetime.combine(datetime.datetime.strptime(von, "%d.%m.%Y"),
                                      datetime.time(00, 00))
        )
        bis_date = timezone.make_aware(
            datetime.datetime.combine(datetime.datetime.strptime(bis, "%d.%m.%Y"),
                                      datetime.time(23, 59))
        )

        werte_list = Wert.objects.filter(date__gte=von_date, date__lte=bis_date,
                                         ref_usr=request.user).order_by('date')

        if werte_list.count() == 0:
            messages.error(request, 'Keine Werte in diesem Zeitraum.')
            return redirect(reverse_lazy('startpage'))

        mindate = werte_list.aggregate(Min('date'))
        maxdate = werte_list.aggregate(Max('date'))
        
        vondate = mindate['date__min'].strftime('%Y-%m-%dT%H:%M:%S')
        bisdate = maxdate['date__max'].strftime('%Y-%m-%dT%H:%M:%S')
        
        for wert in werte_list:
            date = wert.date.strftime('%Y-%m-%dT%H:%M:%S')
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
    except Exception as e:
        message = u'Fehler beim Anzeigen der Messwerte: %s' % e
        logger.exception(message)
        messages.error(request, message)
    
    return render(request, 'werte/diagram.html',
                  {'von': von, 'bis': bis, 'vondate': vondate, 'bisdate': bisdate, 'user': request.user,
                   'sys': js_sys, 'dia': js_dia, 'puls': js_puls, 'tmp': js_temp, 'gew': js_gew})


class MesswertForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(MesswertForm, self).__init__(*args, **kwargs)
        self.fields['gew'].localize = True
        self.fields['temp'].localize = True
    
    class Meta:
        model = Wert
        fields = ['rrsys', 'rrdia', 'puls', 'temp', 'gew', 'bemerkung']
        widgets = { 
            'rrsys': forms.NumberInput(attrs={'min': 0, "autofocus": "autofocus"}),
            'rrdia': forms.NumberInput(attrs={'min': 0}),
            'puls': forms.NumberInput(attrs={'min': 0}),
            'temp': forms.NumberInput(attrs={'min': 0}),
            'gew': forms.NumberInput(attrs={'min': 0}),
        }  


@login_required(login_url='/login/')
def new(request):

    if 'cancel' in request.POST:
        messages.info(request, u'Änderung abgebrochen.')
        return redirect(reverse_lazy('werte:werte'))

    try:
        UserProfile.objects.get(ref_usr=request.user)
    except Exception as e:
        message = 'Der Benutzer %s hat kein Benutzerprofil.' % request.user
        messages.error(request, message)
        return redirect(reverse_lazy('startpage'))

    if request.method == 'POST':
        form = MesswertForm(request.POST)
        if form.is_valid():
            try:
                new_wert = form.save(commit=False)
                if (new_wert.rrsys is None and new_wert.rrdia is None and new_wert.puls is None
                    and new_wert.temp is None and new_wert.gew is None):
                    messages.warning(request, 'Keine Werte eingegeben.')
                else:
                    new_wert.ref_usr = request.user
                    new_wert.save()
                    loc_date = utc_to_local(new_wert.date)
                    msg = 'Werte vom %s in die Datenbank übernommen.' % loc_date.strftime("%d.%m.%Y %H:%M")
                    messages.success(request, msg)
                    return redirect(reverse_lazy('werte:werte'))
            except Exception as e:
                logger.exception(u'Fehler beim Speichern der Werte für Benutzer %s: %s' % (request.user, e))
                messages.error(request, u'Fehler beim Speichern der Werte: %s' % e)
    else:  # GET
        form = MesswertForm(initial={'ref_usr': request.user})
    return render(request, 'werte/new.html', {'form': form})


@login_required(login_url='/login/')
def edit(request, wert_id):

    if 'cancel' in request.POST:
        messages.info(request, u'Änderung abgebrochen.')
        return redirect(reverse_lazy('werte:werte'))

    wert = Wert.objects.get(id=wert_id)
    
    if request.method == 'POST':
        form = MesswertForm(request.POST, instance=wert)
        if form.is_valid():
            try:
                wert.ref_usr = request.user
                wert.save()
                loc_date = utc_to_local(wert.date)
                msg = 'Werte vom %s in die Datenbank übernommen.' % loc_date.strftime("%d.%m.%Y %H:%M")
                messages.success(request, msg)
                return redirect(reverse_lazy('werte:werte'))
            except Exception as e:
                logger.exception(u'Fehler beim Speichern der Werte für Benutzer %s: %s' % (request.user, e))
                messages.error(request, u'Fehler beim Speichern der Werte: %s' % e)
    else:  # GET
        form = MesswertForm(instance=wert)
        
    return render(request, 'werte/new.html', {'form': form})