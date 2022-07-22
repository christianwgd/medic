# -*- coding: utf-8 -*-
import datetime
from django.core.management.base import CommandError, BaseCommand
from medikamente.models import Prescription, VrdFuture


class Command(BaseCommand):
    help = 'Aktiviert eingegebene, fällige Verordnungsänderungen.'

    def handle(self, **options):
        try:
            vrdfutlist = VrdFuture.objects.filter(erledigt=False)
            if vrdfutlist.count() == 0:
                self.stdout.write('Keine aktiven Änderungen.')
            else:
                today = datetime.datetime.today()
                for vrdfut in vrdfutlist:
                    if vrdfut.gueltig_ab == today.date():
                        self.stdout.write('+++ Aktiviere Änderung für Medicament {} für Benutzer {}'.format(
                                          vrdfut.ref_medikament, vrdfut.ref_usr))
                        vrd, created = Prescription.objects.get_or_create(ref_medikament=vrdfut.ref_medikament,
                                                                          ref_usr=vrdfut.ref_usr,
                                                                          defaults={'morgen': vrdfut.morgen,
                                                                                  'mittag': vrdfut.mittag,
                                                                                  'abend': vrdfut.abend,
                                                                                  'nacht': vrdfut.nacht,
                                                                                  'mo': vrdfut.mo,
                                                                                  'di': vrdfut.di,
                                                                                  'mi': vrdfut.mi,
                                                                                  'do': vrdfut.do,
                                                                                  'fr': vrdfut.fr,
                                                                                  'sa': vrdfut.sa,
                                                                                  'so': vrdfut.so})
                        if not created:
                            vrd.morgen = vrdfut.morgen
                            vrd.mittag = vrdfut.mittag
                            vrd.abend = vrdfut.abend
                            vrd.nacht = vrdfut.nacht
                            vrd.mo = vrdfut.mo
                            vrd.di = vrdfut.di
                            vrd.mi = vrdfut.mi
                            vrd.do = vrdfut.do
                            vrd.fr = vrdfut.fr
                            vrd.sa = vrdfut.sa
                            vrd.so = vrdfut.so
                            vrd.save()
                            self.stdout.write('Prescription {} für Benutzer {} geändert.'.format(
                                vrd.ref_medikament, vrd.ref_usr))
                        else:
                            self.stdout.write('Prescription {} für Benutzer {} erstellt.'.format(
                                vrd.ref_medikament, vrd.ref_usr))

                        vrdfut.erledigt = True
                        vrdfut.save()
                    else:
                        self.stdout.write('Heute keine aktiven Änderungen für {}.'.format(vrdfut.ref_medikament))

        except Exception as e:
            raise CommandError('Fehler beim Aktivieren einer geplanten Prescription: {}'.format(e))
