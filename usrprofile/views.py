# encoding: utf-8
from logging import getLogger

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from usrprofile.forms import UsrProfForm
from usrprofile.models import UserProfile

logger = getLogger('medic')


class UserProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserProfile
    form_class = UsrProfForm
    success_url = reverse_lazy('startpage')

    def get_object(self, queryset=None):
        # pylint: disable=unused-variable
        user, created = UserProfile.objects.get_or_create(
            ref_usr=self.request.user, defaults={'email': self.request.user.email}
        )
        return user

    def get_success_message(self, cleaned_data):
        return _('Settings for user {user} saved.').format(user=self.object.ref_usr.username)

    def get_initial(self):
        initial = super().get_initial()
        initial['email'] = self.object.ref_usr.email
        return initial

    def form_valid(self, form):
        profile = form.save(commit=False)
        if 'email' in form.changed_data:
            profile.user.email = form.cleaned_data['email']
            profile.user.save()
        return super().form_valid(form)
