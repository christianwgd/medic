

from django.db import models
from django.contrib import auth
from django.dispatch import receiver
from django.utils import formats
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

from measurement.models import ValueType

User = auth.get_user_model()


class StartUrl(models.Model):

    class Meta:
        verbose_name = _("Home page")
        verbose_name_plural = _("Home pages")
        ordering = ['sort_order' ]

    def __str__(self):
        return self.name

    name = models.CharField(verbose_name=_('Name'), max_length=100)
    url = models.CharField(verbose_name=_('URL pattern'), max_length=100)
    sort_order = models.PositiveIntegerField(default=0, blank=False, null=False)


class UserProfile(models.Model):

    class Meta:
        verbose_name = _("User setting")
        verbose_name_plural = _("User settings")

    def __str__(self):
        return self.ref_usr.username

    gebdat = models.DateField(
        verbose_name=_("Date of birth"), null=True, blank=True,
    )
    warn_days_before = models.IntegerField(
        default=20, verbose_name=_("Hold medicaments inventory for at least"),
        validators=[MinValueValidator(2), MaxValueValidator(30)],
        help_text=_('days'),
    )
    show_measurement_days = models.IntegerField(
        default=30, verbose_name=_("Show readings for"),
        validators=[MinValueValidator(10), MaxValueValidator(365)],
        help_text=_('days'),
    )
    doc_can_see_msm = models.BooleanField(
        default=False, verbose_name=_("Doctor is allowed to see measurements"),
    )
    doc_can_see_med = models.BooleanField(
        default=False, verbose_name=_("Doctor is allowed to see prescription"),
    )
    ref_usr = models.OneToOneField(
        User, on_delete=models.CASCADE,
        verbose_name=_("User"), related_name='profile',
    )
    email_arzt = models.EmailField(
        verbose_name=_("Doctor's email address"), null=True, blank=True,
    )
    my_start_page = models.ForeignKey(
        StartUrl, on_delete=models.PROTECT,
        verbose_name=_("My home page"), blank=True, null=True,
    )
    measurements_items_per_page = models.PositiveSmallIntegerField(
        verbose_name=_('Items per page'), default=16,
    )
    medicaments_items_per_page = models.PositiveSmallIntegerField(
        verbose_name=_('Items per page'), default=16,
    )
    active_value_types = models.ManyToManyField(ValueType, verbose_name=_('Active types'), blank=True)

    @property
    def usr_inf(self):
        if self.gebdat is None:
            born = ''
        else:
            birth_date = formats.date_format(
                self.gebdat,
                format='SHORT_DATE_FORMAT',
                use_l10n=True,
            )
            born = f"{_('born')} {birth_date}"
        if self.ref_usr.first_name and self.ref_usr.last_name:
            user_full_name = self.ref_usr.get_full_name()
        else:
            user_full_name = self.ref_usr.username
        return f'{user_full_name} {born}'


@receiver(models.signals.post_save, sender=User)
def create_user_profile(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """
        Function to create user profile.
        sender is the model class that sends the signal,
        while instance is an actual instance of that class
    """

    user = instance
    try:
        UserProfile.objects.get(ref_usr=user)
    except UserProfile.DoesNotExist:  # pylint: disable=no-member
        profile = UserProfile()
        profile.ref_usr = user  # link the profile to the user
        profile.save()
