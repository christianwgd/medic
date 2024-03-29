from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView
from django.utils.translation import gettext as _

from prescription.forms import PrescriptionForm
from prescription.models import Prescription


class PrescriptionListView(LoginRequiredMixin, ListView):
    model = Prescription

    def get_queryset(self):
        return Prescription.objects.active(
            for_user=self.request.user,
        ).order_by('medicament__name', 'medicament__strength')


class PrescriptionDetailView(LoginRequiredMixin, DetailView):
    model = Prescription


class PrescriptionCreateView(LoginRequiredMixin, BSModalCreateView):
    model = Prescription
    form_class = PrescriptionForm
    success_message = _('Prescription saved')
    success_url = reverse_lazy('prescription:list')

    def form_valid(self, form):
        new_prescription = form.save(commit=False)
        new_prescription.owner = self.request.user
        return super().form_valid(form)


class PrescriptionUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Prescription
    form_class = PrescriptionForm
    success_message = _('Prescription saved')

    def get_success_url(self):
        return reverse('prescription:detail', kwargs={'pk': self.object.id})


class PrescriptionDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = Prescription
    success_url = reverse_lazy('prescription:list')
    success_message = _('Prescription deleted')
