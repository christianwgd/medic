# encoding: utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from usrprofile.forms import UsrProfForm
from usrprofile.models import UserProfile

from logging import getLogger

logger = getLogger('medic')


class UserProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserProfile
    form_class = UsrProfForm
    success_url = reverse_lazy('startpage')

    def get_object(self):
        user, created = UserProfile.objects.get_or_create(
            ref_usr=self.request.user, defaults={'email': self.request.user.email}
        )
        return user

    def get_success_message(self, cleaned_data):
        return _(f'Settings for user {self.object.ref_usr.username} saved.')

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


@login_required(login_url='/login/')
def userprof(request):
    if 'cancel' in request.POST:
        messages.info(request, _('Edit cancelled.'))
        return redirect(reverse_lazy('startpage'))

    try:
        usr = User.objects.get(username=request.user.username)
        usrProf = UserProfile.objects.get(ref_usr = usr)
    except User.DoesNotExist:
        message = _('User does not exist.')
        messages.error(request, message)
        return redirect(reverse_lazy('startpage'))
    except UserProfile.DoesNotExist:
        message = _('User {user} has no user profile.').format(user=usr)
        messages.error(request, message)
        usrProf = UserProfile.objects.create(ref_usr_id=usr.id)

    if request.method == 'POST':
        form = UsrProfForm(request.POST, instance=usrProf)
        if form.is_valid():
            try:
                form.save()
                if form.cleaned_data['email'] != usr.email:
                    usr.email = form.cleaned_data['email']
                    usr.save()
                messages.success(request,
                    _('Settings for user {user} saved.').format(
                        user=usrProf.ref_usr.username
                    )
                )
                return redirect(reverse_lazy('startpage'))
            except Exception:
                msg = _('Error saving settings for user {user}').format(
                    user=usr.username
                )
                logger.exception(msg)
                messages.error(request, msg)
    else:  # GET
        form = UsrProfForm(instance=usrProf, initial={'email': usr.email})

    return render(request, 'usrprofile/usrprof.html', {'form': form})
