from datetime import datetime
import csv
import pytz

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.utils.timezone import make_aware


class ImportUsers:

    def __init__(self, filename):
        self.file = filename
        self.created = 0
        self.members = 0

    def run(self):

        # On ouvre le csv provenant de l'intranet FFCAM
        with open(self.file.name, encoding='latin-1') as f:

            reader = csv.DictReader(f, delimiter='\t')
            group = Group.objects.get(name='adherents')

            # On boucle sur chaque ligne
            for line in reader:

                # On récupère les colonnes
                prenom = line['PRENOM']
                nom = line['NOM']
                email = line['MEL'].lower()
                ffcam = line['ID']
                # phone = line['POR']
                naissance = ''.join(reversed(line['DATNAISS'].split('-')))
                date_adh_fede = line['DATADHFEDE']
                has_paid = True if line['RC'] else False

                # On récupère l'utilisateur s'il existe, sinon on le créé
                user, created = User.objects.get_or_create(username=ffcam)

                # Si c'est une création
                if created:
                    # Créé le mot de base et le groupe
                    user.set_password(naissance)
                    user.groups.add(group)
                    # Ajoute la date d'adhésion
                    joined_date = datetime.strptime(date_adh_fede, '%Y-%m-%d')
                    user.date_joined = make_aware(joined_date, pytz.timezone("Europe/Paris"))
                    user.profile.license = ffcam
                    user.first_name = prenom
                    user.last_name = nom
                    user.email = email
                    self.created += 1
                    print("{license} {user} créé".format(user=user, license=user.profile.license))

                # Active ou pas le membre
                if has_paid:
                    user.is_active = True
                    user.is_staff = True
                    self.members += 1
                else:
                    user.is_active = False
                    user.is_staff = False

                # On sauve l'utilisateur
                user.save()

            print("Il y a {} adhérents dont {} qui viennent d'être rajoutés".format(self.members, self.created))

        return self.created
