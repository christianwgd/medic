# -*- coding: utf-8 -*-
import datetime
import logging

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from bootstrap_modal_forms.utils import is_ajax
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core import serializers
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.views.generic import DetailView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import ProtectedError
from django_filters.views import FilterView

from medic.mixins import ModalDeleteMessageMixin
from medicament.models import Medicament, StockChange
from medicament.filter import MedicamentFilter
from medicament.forms import MedicamentForm


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


@login_required(login_url='/login/')
def getmed(request, med_id):
    med = Medicament.objects.get(id=med_id)
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
#         medikament = Medicament.objects.get(id=med_id)
#         vo = Prescription.objects.get(ref_medikament=medikament, ref_usr=request.user)
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
#     except Medicament.DoesNotExist:
#         defmenge = 0
#     except Prescription.DoesNotExist:
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
#         medikament = Medicament.objects.get(id=med_id)
#         bestchangelist = StockChange.objects.filter(
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
#                     messages.warning(request, 'Die Prescription enthält keine Werte.')
#                 else:
#                     med = Medicament.objects.get(id=new_vrdfut.ref_medikament.id)
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
#         message = 'Lesen Prescription {} für Benutzer {} fehlgeschlagen: {}'.format(id, request.user, e)
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
