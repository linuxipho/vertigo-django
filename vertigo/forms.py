from django import forms
from django.forms import ModelForm
from django.utils import timezone

from vertigo.models import EquipmentBorrowing, TopoBorrowing
from django.contrib.auth.models import User


class BorrowingForm(ModelForm):

    def clean(self):
        cleaned_data = super(BorrowingForm, self).clean()
        date = cleaned_data.get("date")
        print(date)
        print(timezone.now().date())
        if date > timezone.now().date():
            print(True)
            self.add_error('date', "Tu ne peux pas emrunter dans le futur !")
            # raise forms.ValidationError("Tu ne peux pas emrunter dans le futur !", code='invalid')
        return cleaned_data

    class Meta:
        fields = ['date', 'user']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
        }


class EquipmentBorrowingForm(BorrowingForm):
    class Meta(BorrowingForm.Meta):
        model = EquipmentBorrowing


class TopoBorrowingForm(BorrowingForm):
    class Meta(BorrowingForm.Meta):
        model = TopoBorrowing


class UploadFileForm(forms.Form):

    file = forms.FileField(label='Fichier \'export.txt\'')

    class Meta:
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
