![Logo vertigo-django](https://raw.githubusercontent.com/linuxipho/vertigo-django/master/static/img/vertigodjango.png)

# vertigo-django
Decentralized equipment &amp; borrowing management app for climbing clubs

## Installation
Cloner le dépot:
```bash
git clone https://github.com/linuxipho/vertigo-django.git
```

Créer un fichier de configuration `.env` à la racine du projet:
```bash
cd vertigo-django
touch .env
```

Renseigner les variables suivantes dans ce fichier:
```bash
SECRET_KEY = %aVerY!difFicU&lTs#eCr@eTk~ey
ALLOWED_HOSTS = cloud.doe.com
DB_NAME = dbname
DB_USER = dbuser
DB_PASSWORD = dbpass
SEND_EMAIL = True
EMAIL_HOST = smtp.doe.com
EMAIL_PORT = 587
EMAIL_HOST_USER = john@doe.com
EMAIL_HOST_PASSWORD = password
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = John Doe <john@doe.com>
EMAIL_SUBJECT_PREFIX = [Subject]
```