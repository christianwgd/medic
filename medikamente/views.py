# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from past.utils import old_div
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic.edit import DeleteView
from mail_templated import send_mail
from medikamente.models import Verordnung, Medikament, Bestandsveraenderung, VrdFuture
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone
from usrprofile.models import UserProfile
import datetime
import logging
from django.core import serializers
from .forms import vrdForm, vrdFutForm, medForm, bestEditForm
from usrprofile.forms import MailForm

logger = logging.getLogger('medic')


def berechne_tpt(vo):
    tpt = 0.0
    if vo.morgen is not None:
        tpt = float(vo.morgen)
    if vo.mittag is not None:
        tpt += float(vo.mittag)
    if vo.abend is not None:
        tpt += float(vo.abend)
    if vo.nacht is not None:
        tpt += float(vo.nacht)

    if vo.mo and vo.di and vo.mi and vo.do and vo.fr and vo.sa and vo.so:
        zeitraum = 'Tage'
    else:
        zeitraum = 'Woche(n)'
        # tage = 0
        tpw = 0.0
        if vo.mo:
            tpw += float(tpt)
        if vo.di:
            tpw += float(tpt)
        if vo.mi:
            tpw += float(tpt)
        if vo.do:
            tpw += float(tpt)
        if vo.fr:
            tpw += float(tpt)
        if vo.sa:
            tpw += float(tpt)
        if vo.so:
            tpw += float(tpt)
        tpt = tpw

    return tpt, zeitraum


@login_required(login_url='/login/')
def verordnungen(request):
    mintg = 0
    minw = 0
    volist = None

    try:
        user = User.objects.get(username=request.user.username)
        up = UserProfile.objects.get(ref_usr=request.user)
    except User.DoesNotExist:
        message = 'Benutzer existiert nicht.'
        messages.error(request, message)
        return redirect(reverse_lazy('startpage'))
    except UserProfile.DoesNotExist:
        message = 'Der Benutzer %s hat kein Benutzerprofil.' % request.user
        messages.error(request, message)
        return redirect(reverse_lazy('startpage'))

    try:
        volist = Verordnung.objects.filter(ref_usr=request.user).order_by('ref_medikament__name',
                                                                          'ref_medikament__staerke')

        mintg = up.warnenTageVorher
        minw = old_div(mintg, 7)

        for vo in volist:
            m = vo.ref_medikament
            tpt, zeitraum = berechne_tpt(vo)
            if tpt > 0:
                vo.days = old_div(float(m.bestand), float(tpt))
            else:
                vo.days = 0.0
    except Exception as e:
        message = "Fehler beim Anzeigen der Verordnungsliste: {}.".format(e)
        messages.error(request, message)
        logger.exception(message)

    return render(request, 'medikamente/verordnungen.html',
                  {'verordnungen': volist, 'user': user, 'mindays': mintg, 'minweeks': minw})


@login_required(login_url='/login/')
def emailverordnungen(request):
    message = ''

    if 'cancel' in request.POST:
        messages.info(request, 'Funktion abgebrochen.')
        return redirect(reverse_lazy('medikamente:verordnungen'))

    try:
        user = request.user
        volist = Verordnung.objects.filter(ref_usr=user)
        up = UserProfile.objects.get(ref_usr=user)

        if request.method == 'POST':
            form = MailForm(request.POST)
            if form.is_valid():
                try:
                    mail_to = []
                    if user.email is None or user.email == '':
                        messages.warning(
                            request,
                            'emails können nicht gesendet werden, da keine eigene email-Adresse \
                            angegeben wurde(s.a. Einstellungen).'
                        )
                    else:
                        mail_to.append(form.cleaned_data['mailadr'])
                        email_from = user.email
                        send_mail('medikamente/emailvrd.txt',
                                  {'user': user, 'text': form.cleaned_data['text'],
                                   'verordnungen': volist, 'date': datetime.date.today()},
                                  email_from, mail_to)
                        messages.success(request, 'Email gesendet.')
                        return redirect(reverse_lazy('medikamente:verordnungen'))
                except Exception as e:
                    messages.error(request, 'Fehler beim Senden: {}.'.format(e))
        else:
            form = MailForm(initial={'mailadr': up.email_arzt,
                                     'subject': 'Medikamentenplan für {} {}'.format(request.user.first_name,
                                                                                    request.user.last_name)
                                     })

    except UserProfile.DoesNotExist:
        message = 'Der Benutzer {} hat kein Benutzerprofil.'.format(request.user)
    except Exception as e:
        message = 'Fehler beim Anzeigen des Medikamentenplans: {}'.format(e)
    if message:
        logger.exception(message)
        messages.error(request, message)

    return render(request, 'medikamente/emailvrd.html',
                  {'verordnungen': volist, 'form': form, 'date': datetime.date.today()})


@login_required(login_url='/login/')
def vrdnew(request):
    if 'cancel' in request.POST:
        messages.info(request, 'Änderung abgebrochen.')
        return redirect(reverse_lazy('medikamente:verordnungen'))

    if request.method == 'POST':
        form = vrdForm(request.POST)
        if form.is_valid():
            try:
                new_vrd = form.save(commit=False)
                if new_vrd.morgen == None and new_vrd.mittag == None and new_vrd.abend == None and new_vrd.nacht == None:
                    messages.warning(request, 'Die Verordnung enthält keine Werte.')
                else:
                    med = Medikament.objects.get(id=new_vrd.ref_medikament.id)
                    med.bestand_vom = datetime.date.today()
                    med.save()
                    new_vrd.ref_usr = request.user
                    new_vrd.save()
                    msg = u'%s gespeichert.' % new_vrd.ref_medikament
                    messages.success(request, msg)
                    return redirect(reverse_lazy('medikamente:verordnungen'))
            except Exception as e:
                logger.exception('Fehler beim Speichern von Verordnung {} für Benutzer {} ({})'.format(
                                 new_vrd.ref_medikament, request.user.username, e))
                messages.error(request,
                    'Fehler beim Speichern der Verordnung %s: %s' % (new_vrd.ref_medikament, e)
                )
    else:  # GET
        form = vrdForm(initial={'ref_usr': request.user, 'mo': True, 'di': True, 'mi': True,
                                'do': True, 'fr': True, 'sa': True, 'so': True})

    return render(request, 'medikamente/vrdedit.html', {'form': form})


@login_required(login_url='/login/')
def vrdedit(request, vrd_id):
    if 'cancel' in request.POST:
        messages.info(request, 'Änderung abgebrochen.')
        return redirect(reverse_lazy('medikamente:verordnungen'))

    try:
        vrd = Verordnung.objects.get(id=vrd_id, ref_usr=request.user)
    except Exception as e:
        message = 'Lesen Verordnung {} für Benutzer {} fehlgeschlagen: {}'.format(id, request.user, e)
        messages.error(request, message)
        logger.exception(message)

    if request.method == 'POST':
        form = vrdForm(request.POST, instance=vrd)
        if form.is_valid():
            try:
                form.save()
                msg = '{} gespeichert.'.format(vrd.ref_medikament)
                messages.success(request, msg)
                return redirect(reverse_lazy('medikamente:verordnungen'))
            except Exception as e:
                logger.exception('Fehler beim Speichern von Verordnung {} für Benutzer {} ({})'.format(
                                 vrd.ref_medikament, request.user.username, e))
                messages.error(request, 'Fehler beim Speichern der Verordnung {}: {}'.format(vrd.ref_medikament, e))
    else:  # GET
        form = vrdForm(instance=vrd)

    return render(request, 'medikamente/vrdedit.html', {'form': form, 'vrd': vrd})


@login_required(login_url='/login/')
def vrdfutchange(request):
    vrdfutlist = VrdFuture.objects.none()
    user = None

    try:
        vrdfutlist = VrdFuture.objects.filter(ref_usr=request.user, erledigt=False)
        user = User.objects.get(username=request.user.username)
    except Exception as e:
        message = 'Benutzer {} konnte nicht gelesen werden ({}).'.format(user.username, e)
        messages.error(request, message)
        logger.exception(message)

    return render(request, 'medikamente/vrdfutchange.html', {'vrdfutlist': vrdfutlist, 'user': user})


@login_required(login_url='/login/')
def vrdfutnew(request):
    if request.method == 'POST':
        form = vrdFutForm(request.POST)
        if form.is_valid():
            try:
                new_vrdfut = form.save(commit=False)
                if new_vrdfut.morgen == None and new_vrdfut.mittag == None and new_vrdfut.abend == None and new_vrdfut.nacht == None:
                    messages.warning(request, 'Die Verordnung enthält keine Werte.')
                else:
                    med = Medikament.objects.get(id=new_vrdfut.ref_medikament.id)
                    med.bestand_vom = datetime.date.today()
                    med.save()
                    new_vrdfut.ref_usr = request.user
                    new_vrdfut.erledigt = False
                    new_vrdfut.save()
                    msg = u'%s gespeichert.' % new_vrdfut.ref_medikament
                    messages.success(request, msg)
                    return redirect(reverse_lazy('medikamente:vrdfutchange'))
            except Exception as e:
                logger.exception('Fehler beim Speichern von Verordnungsänderung {} für Benutzer {} ({})'.format(
                                 new_vrdfut.ref_medikament, request.user.username, e))
                messages.error(request, 'Fehler beim Speichern der Verordnungsänderung {}}: {}'.format(
                                     new_vrdfut.ref_medikament, e))
    else:  # GET
        form = vrdFutForm(initial={'ref_usr': request.user, 'gueltig_ab': datetime.datetime.today(),
                                   'mo': True, 'di': True, 'mi': True, 'do': True, 'fr': True, 'sa': True, 'so': True})

    return render(request, 'medikamente/vrdfutedit.html', {'form': form})


@login_required(login_url='/login/')
def vrdfutedit(request, vrdfut_id):
    form = None

    try:
        vrdfut = VrdFuture.objects.get(id=vrdfut_id, ref_usr=request.user)
    except Exception as e:
        message = 'Lesen Verordnung {} für Benutzer {} fehlgeschlagen: {}'.format(id, request.user, e)
        messages.error(request, message)
        logger.exception(message)

    if request.method == 'POST':
        form = vrdFutForm(request.POST, instance=vrdfut)
        if form.is_valid():
            try:
                form.save()
                msg = '{} gespeichert.'.format(vrdfut.ref_medikament)
                messages.success(request, msg)
                return redirect(reverse_lazy('medikamente:vrdfutchange'))
            except Exception as e:
                logger.exception('Fehler beim Speichern von Verordnungsänderung {} für Benutzer {} ({})'.format(
                                 vrdfut.ref_medikament, request.user.username, e))
                messages.error(request, 'Fehler beim Speichern der Verordnungsänderung {}: {}'.format(
                                     vrdfut.ref_medikament, e))
    else:  # GET
        form = vrdFutForm(instance=vrdfut)

    return render(request, 'medikamente/vrdfutedit.html', {'form': form, 'vrdfut': vrdfut})


@login_required(login_url='/login/')
def vrdfuthistory(request):
    vrdfutlist = VrdFuture.objects.none()
    user = None

    try:
        vrdfutlist = VrdFuture.objects.filter(ref_usr=request.user, erledigt=True)
        user = User.objects.get(username=request.user.username)
    except Exception as e:
        message = 'Benutzer {} konnte nicht gelesen werden ({}).'.format(user.username, e)
        messages.error(request, message)
        logger.exception(message)

    return render(request, 'medikamente/vrdfuthistory.html', {'vrdfutlist': vrdfutlist, 'user': user})


@login_required(login_url='/login/')
def getmed(request, med_id):
    med = Medikament.objects.get(id=med_id)
    serialized_med = serializers.serialize('json', [med, ])
    return HttpResponse(serialized_med, content_type='application/json')


class VerordnungDelete(DeleteView):
    model = Verordnung
    template_name = 'medikamente/verordnung_delete_confirm.html'
    success_url = reverse_lazy('medikamente:verordnungen')

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return redirect(reverse_lazy('medikamente:vrdedit',
                                                     kwargs = {'vrd_id': self.kwargs['pk']}))
        messages.success(request, "Verordnung gelöscht.")
        return super(VerordnungDelete, self).post(request, args, kwargs)


@login_required(login_url='/login/')
def medikamente(request):
    message = ''

    try:
        user = User.objects.get(username=request.user.username)
        up = UserProfile.objects.get(ref_usr=user)
        mintg = up.warnenTageVorher
        medikamente = Medikament.objects.filter(ref_usr=request.user).order_by('name', 'staerke')
    except User.DoesNotExist:
        message = 'Benutzer existiert nicht.'
        messages.error(request, message)
        return redirect(reverse_lazy('startpage'))
    except UserProfile.DoesNotExist:
        message = 'Der Benutzer {} hat kein Benutzerprofil.'.format(user)
        messages.error(request, message)
        return redirect(reverse_lazy('startpage'))
    except Exception as e:
        message = 'Fehler beim Anzeigen der Medikantenliste: {}'.format(e)
    if message != '':
        logger.exception(message)
        messages.error(request, message)

    return render(request, 'medikamente/medikamente.html',
                  {'medikamente': medikamente, 'user': user, 'min': mintg})


@login_required(login_url='/login/')
def mednew(request):
    if 'cancel' in request.POST:
        messages.info(request, u'Änderung abgebrochen.')
        return redirect(reverse_lazy('medikamente:medikamente'))

    if request.method == 'POST':
        form = medForm(request.POST)
        if form.is_valid():
            try:
                new_med = form.save(commit=False)
                new_med.ref_usr = request.user
                new_med.bestand = 0
                new_med.bestand_vom = datetime.date.today()
                new_med.save()
                msg = '{} {} {} gespeichert.'.format(new_med.name, new_med.staerke, new_med.einheit)
                messages.success(request, msg)
                return redirect(reverse_lazy('medikamente:medikamente'))
            except Exception as e:
                message = 'Fehler beim Speichern von {}: {}'.format(new_med.name, e)
                logger.exception(message)
                messages.error(request, message)
    else:  # GET
        form = medForm(initial={'ref_usr': request.user})

    return render(request, 'medikamente/mededit.html', {'form': form})


@login_required(login_url='/login/')
def mededit(request, med_id):
    if 'cancel' in request.POST:
        messages.info(request, 'Änderung abgebrochen.')
        return redirect(reverse_lazy('medikamente:medikamente'))

    med = Medikament.objects.get(id=med_id)

    if request.method == 'POST':
        form = medForm(request.POST, instance=med)
        if form.is_valid():
            try:
                form.save()
                msg = '{} {} {} gespeichert.'.format(med.name, med.staerke, med.einheit)
                messages.success(request, msg)
                return redirect(reverse_lazy('medikamente:medikamente'))
            except Exception as e:
                message = 'Fehler beim Speichern von {}: {}'.fomat(med.name, e)
                logger.exception(message)
                messages.error(request, message)
    else:  # GET
        form = medForm(instance=med)

    return render(request, 'medikamente/mededit.html', {'form': form, 'med_id': med_id})


class MedDelete(DeleteView):
    model = Medikament
    template_name = 'medikamente/med_delete_confirm.html'
    success_url = reverse_lazy('medikamente:medikamente')

    def post(self, request, *args, **kwargs):
        if 'cancel' in request.POST:
            return redirect(reverse_lazy('medikamente:mededit',
                                                     kwargs = {'med_id': self.kwargs['pk']}))
        messages.success(request, "Medikament gelöscht.")
        return super(MedDelete, self).post(request, args, kwargs)


@login_required(login_url='/login/')
def bestandedit(request, med_id):
    if 'cancel' in request.POST:
        messages.info(request, u'Änderung abgebrochen.')
        return redirect(reverse_lazy('medikamente:medikamente'))

    try:
        medikament = Medikament.objects.get(id=med_id)
        vo = Verordnung.objects.get(ref_medikament=medikament, ref_usr=request.user)
        if vo.morgen is not None:
            defmenge = vo.morgen
        elif vo.mittag is not None:
            defmenge = vo.mittag
        elif vo.abend is not None:
            defmenge = vo.abend
        elif vo.nacht is not None:
            defmenge = vo.nacht
        else:
            defmenge = 0
    except Medikament.DoesNotExist:
        defmenge = 0
    except Verordnung.DoesNotExist:
        defmenge = 0

    if request.method == 'POST':
        form = bestEditForm(request.POST)
        if form.is_valid():
            try:
                delta = form.save(commit=False)
                if delta.menge == 0:
                    messages.error(request, 'Keine Menge angegeben!')
                else:
                    delta.ref_medikament = medikament
                    delta.ref_usr = request.user
                    if delta.grund in ['04', '05', '99']:  # Verfallsdatum erreicht, Dosiserhöhung oder sonstige -
                        if delta.menge > 0:
                            delta.menge = delta.menge * -1
                    medikament.bestand += delta.menge
                    medikament.save()
                    delta.save()
                    msg = 'Bestand von {} übernommen ({}).'.format(delta.ref_medikament, delta.menge)
                    messages.success(request, msg)
                    return redirect(reverse_lazy('medikamente:medikamente'))
            except Exception as e:
                message = 'Fehler beim Speichern von {}: {}'.format(delta.ref_medikament, e)
                logger.exception(message)
                messages.error(request, message)
    else:  # GET
        now = timezone.localtime()
        form = bestEditForm(initial={'ref_usr': request.user, 'ref_medikament': medikament, 'date': now})

    return render(request, 'medikamente/bestandedit.html',
                  {'form': form, 'medikament': medikament, 'defmenge': defmenge})


@login_required(login_url='/login/')
def besthistory(request, med_id):
    try:
        medikament = Medikament.objects.get(id=med_id)
        bestchangelist = Bestandsveraenderung.objects.filter(ref_usr=request.user,
                                                             ref_medikament=medikament).order_by('-date')
    except Exception as e:
        message = 'Fehler beim Anhzeigen der Bestandshistorie für Benutzer {}: {}'.format(request.user, e)
        logger.exception(message)
        messages.error(request, message)

    return render(request, 'medikamente/besthistory.html',
                  {'bestchangelist': bestchangelist, 'medikament': medikament})