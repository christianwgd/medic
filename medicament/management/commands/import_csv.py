import csv
import os
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from medicament.models import DosageForm, MedPznData


class Command(BaseCommand):
    help = 'Delete old uploads for chia firmware'

    # pylint: disable=too-many-locals
    def handle(self, *args, **options):
        base_dir = getattr(settings, "BASE_DIR", None)
        csv_dir = os.path.join(base_dir, 'medicament', 'pzn_data')

        # mport dosage forms
        # format: key;short;name
        with open(os.path.join(csv_dir, 'dar.csv'), encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                key, short, name = row[0].split(';')
                DosageForm.objects.get_or_create(
                    key=key,
                    defaults={'short': short, 'name': name}
                )
            file.close()

        # Import pzn data
        # Format: PZN;name;producer;Key_DAR;Referencedate;Verification
        with open(os.path.join(csv_dir, 'pzn.csv'), encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                pzn, name, producer, dosage_form, ref_date, verification = row[0].split(';')
                MedPznData.objects.get_or_create(
                    pzn=int(pzn),
                    defaults={
                        'name': name,
                        'producer': producer,
                        'dosage_form': DosageForm.objects.get(key=dosage_form),
                        'ref_date': datetime.strptime(ref_date, '%Y-%m-%d'),
                        'verification': verification
                    }
                )
            file.close()
