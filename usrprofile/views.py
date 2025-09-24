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
        user, _created = UserProfile.objects.get_or_create(
            ref_usr=self.request.user, defaults={'email': self.request.user.email},
        )
        return user

    def get_success_message(self, cleaned_data):
        return _('Settings for user {user} saved.').format(user=self.object.ref_usr.username)

    def get_initial(self):
        initial = super().get_initial()
        initial['first_name'] = self.object.ref_usr.first_name
        initial['last_name'] = self.object.ref_usr.last_name
        initial['email'] = self.object.ref_usr.email
        return initial

    def form_valid(self, form):
        profile = form.save(commit=False)
        user_changed = False
        if 'first_name' in form.changed_data:
            profile.ref_usr.first_name = form.cleaned_data['first_name']
            user_changed = True
        if 'last_name' in form.changed_data:
            profile.ref_usr.last_name = form.cleaned_data['last_name']
            user_changed = True
        if 'email' in form.changed_data:
            profile.ref_usr.email = form.cleaned_data['email']
            user_changed = True
        if user_changed:
            profile.ref_usr.save()
        return super().form_valid(form)
