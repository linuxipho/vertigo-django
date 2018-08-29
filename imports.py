#!/usr/bin/env python
import django
from django.db.models import Q
from django.utils.dateparse import parse_date

django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

import csv


GROUP, created = Group.objects.get_or_create(name='adherents')


with open('export.txt', encoding='latin-1') as f:

    reader = csv.DictReader(f, delimiter='\t')

    for line in reader:  # phone

        prenom = line['PRENOM']
        nom = line['NOM']
        email = line['MEL'].lower()
        ffcam = line['ID']
        naissance = ''.join(reversed(line['DATNAISS'].split('-')))
        date_adh_fede = line['DATADHFEDE']
        is_current_member = True if line['RC'] else False

        try:
            user = User.objects.get(Q(profile__license=ffcam) | Q(username=email))

            if user.date_joined.date() < parse_date(date_adh_fede):
                print("Updating " + user.__str__())
                user.is_active = is_current_member
                user.is_staff = True if is_current_member else False
                user.profile.license = ffcam
                user.date_joined = parse_date(date_adh_fede)
                user.email = email
                user.save()

        except User.DoesNotExist as e:
            user = User.objects.create_user(username=email, first_name=prenom, last_name=nom, email=email)
            user.set_password(naissance)
            user.groups.add(GROUP)
            user.is_active = is_current_member
            user.is_staff = True if is_current_member else False
            user.date_joined = parse_date(date_adh_fede)
            user.profile.license = ffcam
            user.save()
            print("User {} created :".format(user))

# Set superuser
superuser = User.objects.get(profile__license='340120179003')
superuser.is_superuser = True
superuser.save()
