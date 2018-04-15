from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

import phonenumbers
from phonenumber_field.modelfields import PhoneNumberField


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Profile(models.Model):
    """
        Profil data liked to User model
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    license = models.CharField('licence', max_length=12, blank=True)  # 3401 2017 9039
    phone = PhoneNumberField('téléphone', null=True, blank=True)
    birth_date = models.DateField('date de naissance', null=True, blank=True)
    medical_date = models.DateField('date du certificat', null=True, blank=True)
    medical_file = models.FileField('certificat médical', upload_to='medical_certs/%Y/', null=True, blank=True)
    agreement = models.BooleanField('accord de responsabilité', default=False)
    forbidden = models.BooleanField('interdit d\'emprunt', default=False)

    def formatted_phone(self):
        if self.phone:
            return phonenumbers.format_number(self.phone, phonenumbers.PhoneNumberFormat.NATIONAL)
    formatted_phone.short_description = 'téléphone'

    def __str__(self):
        return self.user.first_name


class EquipmentType:
    """
        Simple class to handle Equipment type conjugation and reference
    """
    def __init__(self, singular, plural):
        self.singular = singular
        self.plural = plural
        self.url = slugify(plural)


class Equipment(models.Model):
    """
        Model data for all equipment gear
    """

    # Do not modify after database is initialized, only append to the end
    # TODO: add localization if needed
    ROPE = EquipmentType('corde', 'cordes')
    RAPPEL = EquipmentType('rappel', 'rappels')
    QUICKDRAW = EquipmentType('dégaines', 'dégaines')
    LANYARD = EquipmentType('longe', 'longes')
    HARNESS = EquipmentType('baudrier', 'baudriers')
    HELMET = EquipmentType('casque', 'casques')
    CRASHPAD = EquipmentType('crashpad', 'crashpads')

    TYPE_LIST = [ROPE, RAPPEL, QUICKDRAW, LANYARD, HARNESS, HELMET, CRASHPAD]  # Must be exact number as above

    # TYPES = {}
    # for item in TYPE_LIST:
    #     TYPES[item.ref] = {'singular': item.singular, 'plural': item.plural}

    TYPE_CHOICE = [(equipment.url, equipment.singular) for equipment in TYPE_LIST]

    YEAR_CHOICE = []
    now = timezone.now().year
    for n in range(now, now - 11, -1):
        YEAR_CHOICE.append((n, n))

    ref = models.IntegerField(
        'numéro', help_text='le numéro donné par l\'association', blank=True, null=True, db_index=True)
    type = models.CharField('type', max_length=20, choices=TYPE_CHOICE, default=ROPE.url)
    status = models.BooleanField('en usage', help_text='décocher si réformé', default=True, db_index=True)

    brand = models.CharField('marque', max_length=50, blank=True)
    model = models.CharField('model', max_length=50, blank=True)

    serial_number = models.CharField('numéro de série', max_length=50, blank=True)
    year_of_manufacture = models.IntegerField('date de fabrication', choices=YEAR_CHOICE, blank=True, null=True)
    date_of_purchase = models.DateField('date d\'achat', blank=True, null=True)
    date_of_first_use = models.DateField('date de première utilisation', blank=True, null=True)

    caution = models.CharField(
        'avertissement', help_text='un court text accolé au nom du matériel', max_length=50, blank=True)
    comment = models.TextField('commentaire', max_length=3, blank=True)

    class Meta:
        verbose_name = 'équipement'
        verbose_name_plural = 'équipements'
        ordering = ('-status', 'type', 'ref')

    def __str__(self):
        message = self.caution if self.caution else ''
        return '{type} n°{ref}{caution}'.format(type=self.get_type_display(), ref=self.ref, caution=message)

    def clean(self):

        now = timezone.now().date()

        if self.year_of_manufacture:
            if self.year_of_manufacture > now.year:
                raise ValidationError(
                    {'year_of_manufacture': 'la date de fabrication doit être antérieur à la date du jour'})

        if self.date_of_purchase:
            if self.date_of_purchase > now:
                raise ValidationError(
                    {'date_of_purchase': 'la date d\'achat doit être antérieur à la date du jour'})

        if self.date_of_first_use:
            if self.date_of_first_use > now:
                raise ValidationError(
                    {'date_of_first_use': 'la date de premier usage doit être antérieur à la date du jour'})

        if self.date_of_purchase and self.year_of_manufacture:
            if self.date_of_purchase.year < self.year_of_manufacture:
                raise ValidationError(
                    {'date_of_purchase': 'la date d\'achat doit être antérieur à la date de fabrication'})

        if self.date_of_purchase and self.date_of_first_use:
            if self.date_of_purchase > self.date_of_first_use:
                raise ValidationError(
                    {'date_of_first_use': 'la date de premier usage doit être postérieur à la date d\'achat'})

        # Don't allow creating an equipment when existing one with same ref and is in use
        if not self.pk:
            if Equipment.objects.filter(type=self.type, ref=self.ref, status=True).exists():
                raise ValidationError(
                    {'ref': 'un·e {} en cours d\'usage existe déjà avec ce numéro'.format(self.get_type_display())})


class EquipmentBorrowing(models.Model):
    """
    Borrowing model linking an Equipment to a User
    """

    item = models.ForeignKey(Equipment, on_delete=models.PROTECT, verbose_name='équipement')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='par', blank=True, null=True)
    date = models.DateField('emprunté le', default=timezone.now, db_index=True)

    class Meta:
        verbose_name = 'emprunt'
        verbose_name_plural = 'emprunts de matériel'
        ordering = ('-date', '-id')

    def __str__(self):
        return 'Emprunt {item} par {user}'.format(item=self.item, user=self.user.first_name)

    @property
    def color(self):
        diff = timezone.now().date() - self.date
        d = int(diff.days)
        color = 'dark'
        if d < 2:
            color = 'success'
        elif d < 7:
            color = 'secondary'
        elif d < 14:
            color = 'warning'
        elif d < 21:
            color = 'danger'
        return color
