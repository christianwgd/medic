# -*- coding: utf-8 -*-
import datetime
import logging

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import ProtectedError
from django_filters.views import FilterView

from mail_templated import send_mail

from usrprofile.models import UserProfile
from usrprofile.forms import MailForm
from medikamente.models import Verordnung, Medikament, Bestandsveraenderung, VrdFuture
from .filter import MedikamentFilter

from .forms import VrdForm, MedForm


logger = logging.getLogger('medic')


class MedListView(LoginRequiredMixin, FilterView):
    model = Medikament
    filterset_class = MedikamentFilter
    template_name = 'medikamente/medikamente.html'

    def get_paginate_by(self, queryset):
        return self.request.user.profile.medicaments_items_per_page

    def get_queryset(self):
        return Medikament.objects.filter(ref_usr=self.request.user)


class MedDetailView(LoginRequiredMixin, DetailView):
    model = Medikament


class MedCreateView(LoginRequiredMixin, BSModalCreateView):
    model = Medikament
    form_class = MedForm
    template_name = 'medikamente/med_form.html'
    success_message = _('New medicament saved.')
    success_url = reverse_lazy('medikamente:medikamente')

    def form_valid(self, form):
        new_med = form.save(commit=False)
        new_med.ref_usr = self.request.user
        new_med.bestand = 0
        new_med.bestand_vom = datetime.date.today()
        return super().form_valid(form)


class MedUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Medikament
    form_class = MedForm
    template_name = 'medikamente/med_form.html'
    success_message = _('Medicament saved.')

    def get_success_url(self):
        return reverse('medikamente:meddetail', kwargs={'pk': self.object.id})


class MedDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = Medikament
    template_name = 'medikamente/med_confirm_delete.html'
    success_url = reverse_lazy('medikamente:medikamente')
    success_message = _('Medicament deleted')

    def post(self, request, *args, **kwargs):
        try:
            super(MedDeleteView, self).post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, _('Could not delete medicament due to existing prescription.'))
        return redirect(self.success_url)


class VrdListView(LoginRequiredMixin, ListView):
    model = Verordnung
    template_name = 'medikamente/verordnungen.html'

    def get_queryset(self):
        qs = Verordnung.objects.active(
            for_user=self.request.user
        )
        print(qs)
        return qs


class VrdDetailView(LoginRequiredMixin, DetailView):
    model = Verordnung


class VrdCreateView(LoginRequiredMixin, BSModalCreateView):
    model = Verordnung
    form_class = VrdForm
    template_name = 'medikamente/vrd_form.html'
    success_message = _('New prescription saved.')
    success_url = reverse_lazy('medikamente:verordnungen')

    def form_valid(self, form):
        new_vrd = form.save(commit=False)
        new_vrd.ref_usr = self.request.user
        return super().form_valid(form)


class VrdUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Verordnung
    form_class = VrdForm
    template_name = 'medikamente/vrd_form.html'
    success_message = _('Prescription saved.')

    def get_success_url(self):
        return reverse('medikamente:vrddetail', kwargs={'pk': self.object.id})


class VerordnungDelete(LoginRequiredMixin, BSModalDeleteView):
    model = Verordnung
    template_name = 'medikamente/vrd_confirm_delete.html'
    success_url = reverse_lazy('medikamente:verordnungen')
    success_message = _('Prescription deleted')


@login_required(login_url='/login/')
def emailverordnungen(request):
    message = ''

    if 'cancel' in request.POST:
        messages.info(request, _('Function canceled.'))
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
                        messages.warning(request,
                            _('Sending emails requires email address in user settings.')
                        )
                    else:
                        mail_to.append(form.cleaned_data['mailadr'])
                        email_from = user.email
                        send_mail(
                            'medikamente/emailvrd.txt',
                            {
                                'user': user, 'text': form.cleaned_data['text'],
                                'verordnungen': volist, 'date': datetime.date.today()
                            },
                            email_from, mail_to
                        )
                        messages.success(request, _('Email sent.'))
                        return redirect(reverse_lazy('medikamente:verordnungen'))
                except Exception as e:
                    messages.error(request, _('Error sending email: {}.').format(e))
        else:
            form = MailForm(initial={
                'mailadr': up.email_arzt,
                'subject': 'Medikamentenplan für {} {}'.format(
                    request.user.first_name,
                    request.user.last_name
                )
            })

    except UserProfile.DoesNotExist:
        message = _('User {} has no user profile.'.format(user))
    except:
        message = _('Error in display of prescription')
        logger.exception(message)
        messages.error(request, message)

    return render(request, 'medikamente/emailvrd.html', {
        'verordnungen': volist,
        'form': form,
        'date': datetime.date.today()
    })


@login_required(login_url='/login/')
def getmed(request, med_id):
    med = Medikament.objects.get(id=med_id)
    serialized_med = serializers.serialize('json', [med, ])
    return HttpResponse(serialized_med, content_type='application/json')


# def berechne_tpt(vo):
#     tpt = 0.0
#     if vo.morgen is not None:
#         tpt = float(vo.morgen)
#     if vo.mittag is not None:
#         tpt += float(vo.mittag)
#     if vo.abend is not None:
#         tpt += float(vo.abend)
#     if vo.nacht is not None:
#         tpt += float(vo.nacht)
#
#     if vo.mo and vo.di and vo.mi and vo.do and vo.fr and vo.sa and vo.so:
#         zeitraum = _('Days')
#     else:
#         zeitraum = _('Week(s)')
#         # tage = 0
#         tpw = 0.0
#         if vo.mo:
#             tpw += float(tpt)
#         if vo.di:
#             tpw += float(tpt)
#         if vo.mi:
#             tpw += float(tpt)
#         if vo.do:
#             tpw += float(tpt)
#         if vo.fr:
#             tpw += float(tpt)
#         if vo.sa:
#             tpw += float(tpt)
#         if vo.so:
#             tpw += float(tpt)
#         tpt = tpw
#
#     return tpt, zeitraum

# @login_required(login_url='/login/')
# def bestandedit(request, med_id):
#     if 'cancel' in request.POST:
#         messages.info(request, _('Function canceled.'))
#         return redirect(reverse_lazy('medikamente:medikamente'))
#
#     try:
#         medikament = Medikament.objects.get(id=med_id)
#         vo = Verordnung.objects.get(ref_medikament=medikament, ref_usr=request.user)
#         if vo.morgen is not None:
#             defmenge = vo.morgen
#         elif vo.mittag is not None:
#             defmenge = vo.mittag
#         elif vo.abend is not None:
#             defmenge = vo.abend
#         elif vo.nacht is not None:
#             defmenge = vo.nacht
#         else:
#             defmenge = 0
#     except Medikament.DoesNotExist:
#         defmenge = 0
#     except Verordnung.DoesNotExist:
#         defmenge = 0
#
#     if request.method == 'POST':
#         form = bestEditForm(request.POST)
#         if form.is_valid():
#             try:
#                 delta = form.save(commit=False)
#                 if delta.menge == 0:
#                     messages.error(request, _('No amount provided.'))
#                 else:
#                     delta.ref_medikament = medikament
#                     delta.ref_usr = request.user
#                     if delta.grund in ['04', '05', '99']:  # Verfallsdatum erreicht, Dosiserhöhung oder sonstige -
#                         if delta.menge > 0:
#                             delta.menge = delta.menge * -1
#                     medikament.bestand += delta.menge
#                     medikament.save()
#                     delta.save()
#                     msg = _('Inventory change of {med} saved ({amount}).').format(
#                         med=delta.ref_medikament,
#                         amount=delta.menge
#                     )
#                     messages.success(request, msg)
#                     return redirect(reverse_lazy('medikamente:medikamente'))
#             except:
#                 message = _('Error saving {}.').format(delta.ref_medikament)
#                 logger.exception(message)
#                 messages.error(request, message)
#     else:  # GET
#         now = timezone.localtime()
#         form = bestEditForm(initial={
#             'ref_usr': request.user,
#             'ref_medikament': medikament,
#             'date': now
#         })
#
#     return render(request, 'medikamente/bestandedit.html', {
#         'form': form,
#         'medikament': medikament,
#         'defmenge': defmenge
#     })


# @login_required(login_url='/login/')
# def besthistory(request, med_id):
#     try:
#         medikament = Medikament.objects.get(id=med_id)
#         bestchangelist = Bestandsveraenderung.objects.filter(
#             ref_usr=request.user,
#             ref_medikament=medikament
#         ).order_by('-date')
#     except:
#         message = _('Error reading inventory history.')
#         logger.exception(message)
#         messages.error(request, message)
#
#     return render(request, 'medikamente/besthistory.html', {
#         'bestchangelist': bestchangelist,
#         'medikament': medikament
#     })


# @login_required(login_url='/login/')
# def vrdfutchange(request):
#     vrdfutlist = VrdFuture.objects.none()
#     user = None
#
#     try:
#         vrdfutlist = VrdFuture.objects.filter(ref_usr=request.user, erledigt=False)
#         user = User.objects.get(username=request.user.username)
#     except Exception as e:
#         message = 'Benutzer {} konnte nicht gelesen werden ({}).'.format(user.username, e)
#         messages.error(request, message)
#         logger.exception(message)
#
#     return render(request, 'medikamente/vrdfutchange.html', {'vrdfutlist': vrdfutlist, 'user': user})


# @login_required(login_url='/login/')
# def vrdfutnew(request):
#     if request.method == 'POST':
#         form = vrdFutForm(request.POST)
#         if form.is_valid():
#             try:
#                 new_vrdfut = form.save(commit=False)
#                 if new_vrdfut.morgen == None and new_vrdfut.mittag == None and new_vrdfut.abend == None and new_vrdfut.nacht == None:
#                     messages.warning(request, 'Die Verordnung enthält keine Werte.')
#                 else:
#                     med = Medikament.objects.get(id=new_vrdfut.ref_medikament.id)
#                     med.bestand_vom = timezone.now().date()
#                     med.save()
#                     new_vrdfut.ref_usr = request.user
#                     new_vrdfut.erledigt = False
#                     new_vrdfut.save()
#                     msg = u'%s gespeichert.' % new_vrdfut.ref_medikament
#                     messages.success(request, msg)
#                     return redirect(reverse_lazy('medikamente:vrdfutchange'))
#             except Exception as e:
#                 logger.exception('Fehler beim Speichern von Verordnungsänderung {} für Benutzer {} ({})'.format(
#                                  new_vrdfut.ref_medikament, request.user.username, e))
#                 messages.error(request, 'Fehler beim Speichern der Verordnungsänderung {}}: {}'.format(
#                                      new_vrdfut.ref_medikament, e))
#     else:  # GET
#         form = vrdFutForm(initial={'ref_usr': request.user, 'gueltig_ab': datetime.datetime.today(),
#                                    'mo': True, 'di': True, 'mi': True, 'do': True, 'fr': True, 'sa': True, 'so': True})
#
#     return render(request, 'medikamente/vrdfutedit.html', {'form': form})


# @login_required(login_url='/login/')
# def vrdfutedit(request, vrdfut_id):
#     form = None
#
#     try:
#         vrdfut = VrdFuture.objects.get(id=vrdfut_id, ref_usr=request.user)
#     except Exception as e:
#         message = 'Lesen Verordnung {} für Benutzer {} fehlgeschlagen: {}'.format(id, request.user, e)
#         messages.error(request, message)
#         logger.exception(message)
#
#     if request.method == 'POST':
#         form = vrdFutForm(request.POST, instance=vrdfut)
#         if form.is_valid():
#             try:
#                 form.save()
#                 msg = '{} gespeichert.'.format(vrdfut.ref_medikament)
#                 messages.success(request, msg)
#                 return redirect(reverse_lazy('medikamente:vrdfutchange'))
#             except Exception as e:
#                 logger.exception('Fehler beim Speichern von Verordnungsänderung {} für Benutzer {} ({})'.format(
#                                  vrdfut.ref_medikament, request.user.username, e))
#                 messages.error(request, 'Fehler beim Speichern der Verordnungsänderung {}: {}'.format(
#                                      vrdfut.ref_medikament, e))
#     else:  # GET
#         form = vrdFutForm(instance=vrdfut)
#
#     return render(request, 'medikamente/vrdfutedit.html', {'form': form, 'vrdfut': vrdfut})


# @login_required(login_url='/login/')
# def vrdfuthistory(request):
#     vrdfutlist = VrdFuture.objects.none()
#     user = None
#
#     try:
#         vrdfutlist = VrdFuture.objects.filter(ref_usr=request.user, erledigt=True)
#         user = User.objects.get(username=request.user.username)
#     except Exception as e:
#         message = 'Benutzer {} konnte nicht gelesen werden ({}).'.format(user.username, e)
#         messages.error(request, message)
#         logger.exception(message)
#
#     return render(request, 'medikamente/vrdfuthistory.html', {'vrdfutlist': vrdfutlist, 'user': user})
