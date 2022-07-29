# -*- coding: utf-8 -*-
from django.core.management.base import CommandError, BaseCommand
from medicament.models import Medicament, Prescription
from django.contrib.auth.models import User
import datetime


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


def vrd_for_weekday(weekday, vrd):
    if weekday == 1 and vrd.mo:
        return True
    elif weekday == 2 and vrd.di:
        return True
    elif weekday == 3 and vrd.mi:
        return True
    elif weekday == 4 and vrd.do:
        return True
    elif weekday == 5 and vrd.fr:
        return True
    elif weekday == 6 and vrd.sa:
        return True
    elif weekday == 7 and vrd.so:
        return True
    else:
        return False


class Command(BaseCommand):
    help = u'Berechnet die aktuellen Bestaende der Medikamente.'

    def handle_noargs(self, **options):
        try:
            userlist = User.objects.filter(username='cwiegand')
            for usr in userlist:
                medikamente = Medicament.objects.all()
                for med in medikamente:
                    self.stdout.write('+++ Berechnung für Medicament {}'.format(med))
                    vo = Prescription.objects.filter(ref_usr=usr, ref_medikament=med)
                    tpt = 0
                    if vo.count() == 1:  # Gibt es eine Prescription für das Medicament?
                        vrd = vo[0]

                        today = datetime.date.today()

                        if vrd.morgen is not None:
                            tpt += vrd.morgen
                        if vrd.mittag is not None:
                            tpt += vrd.mittag
                        if vrd.abend is not None:
                            tpt += vrd.abend
                        if vrd.nacht is not None:
                            tpt += vrd.nacht

                        last_update = med.bestand_vom
                        # days = today - last_update

                        # Verbrauch berechnen
                        verbrauch = 0
                        for single_date in daterange(last_update, today):
                            # Gibt es eine Prescription für den Wochentag?
                            if vrd_for_weekday(single_date.isoweekday(), vrd):
                                verbrauch += tpt
                            #     self.stdout.write(u'Verbrauch am {}: {}' % (single_date.strftime("%A, %d.%m.%Y"),
                            #                                                                      verbrauch))
                            # else:
                            #     self.stdout.write(u'Keine Prescription am {}' % single_date.strftime("%A, %d.%m.%Y"))

                        if med.bestand >= verbrauch:
                            best_alt = med.bestand
                            med.bestand = best_alt - verbrauch
                            med.bestand_vom = today
                            med.save()
                            self.stdout.write('Bestand fuer {} {}{} neu berechnet:'.format(
                                med.name, med.staerke, med.einheit))
                            self.stdout.write('Bestand: {} - Verbrauch {} = {}'.format(
                                best_alt, verbrauch, med.bestand))
                        else:
                            self.stdout.write('Bestand fuer {} geringer als Verbrauch' % med.name)

                    else:
                        self.stdout.write('Medicament {} {}{} hat keine Prescription.'.format(
                            med.name, med.staerke, med.einheit))
                self.stdout.write('Medikamenten-Bestaende von Benutzer {} aktualisiert.'.format(usr.username))
        except Exception as e:
            raise CommandError('Fehler beim Berechnen der Medikamenten-Bestaende: {}.'.format(e))
