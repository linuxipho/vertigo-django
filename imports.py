#!/usr/bin/env python
import os
import csv
import django
import phonenumbers
import pytz
from datetime import datetime

from django.core.exceptions import ValidationError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vertigodjango.settings")
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.utils.timezone import make_aware
from django.core.validators import validate_email


GROUP, created = Group.objects.get_or_create(name='adherents')


def create_user(login, full=True):
    new_user = User.objects.create(username=login)
    new_user.profile.license = ffcam
    new_user.profile.phone = phone
    new_user.set_password(naissance)
    new_user.groups.add(GROUP)
    new_user.first_name = prenom
    new_user.last_name = nom
    if full:
        new_user.email = login
    new_user.date_joined = joined_date

    return new_user


# On ouvre le csv provenant de l'intranet FFCAM
with open('export.txt', encoding='latin-1') as f:

    reader = csv.DictReader(f, delimiter='\t')

    # On boucle sur chaque ligne
    for line in reader:

        # On récupère les colonnes
        prenom = line['PRENOM']
        nom = line['NOM']
        email = line['MEL'].lower()
        ffcam = line['ID']
        phone = phonenumbers.parse(line['POR'], "FR") if len(line['POR']) >= 9 else None
        naissance = ''.join(reversed(line['DATNAISS'].split('-')))
        date_adh_fede = line['DATADHFEDE']
        has_paid = True if line['RC'] else False
        joined_date = make_aware(datetime.strptime(date_adh_fede, '%Y-%m-%d'), pytz.timezone("Europe/Paris"))

        print("Itération --> " + nom)

        try:
            # Sélectionne l'adhérent en fonction de son numéro de licence
            user = User.objects.get(profile__license=ffcam)
            print("User with license {} exists".format(ffcam))

        except User.DoesNotExist:
            print("User with license {} does not exists".format(ffcam))

            try:
                validate_email(email)
                user = User.objects.get(email=email)
                print("User with email {} exists".format(email))

            except User.DoesNotExist:
                print("Creating new user")
                user = create_user(email)

            except ValidationError:
                user = create_user(ffcam, False)

        # Met à jour ne numéro de licence
        if user.date_joined < joined_date:
            print("Update profile with new license number")
            user.date_joined = joined_date
            user.profile.license = ffcam

        # Active ou pas le membre
        user.is_active = has_paid
        user.is_staff = has_paid

        # On sauve l'utilisateur
        user.save()

# Set superuser
superuser = User.objects.get(profile__license='340120179003')  # Me !
superuser.is_superuser = True
superuser.is_staff = True
superuser.is_active = True
superuser.save()
