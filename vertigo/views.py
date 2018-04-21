from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage

import os

from .models import Equipment, EquipmentBorrowing
from .forms import EquipmentBorrowingForm
from .exports import ExportMaterial


def send_email(user, item, gender):
    """Methode called to send email to new borrower
    :param user: the User class instance
    :param item: the Equipment class instance
    :param gender: the current equipment gender
    """
    if settings.SEND_EMAIL:  # and not request.user.is_authenticated:
        subject = "{prefix} Emprunt {item}".format(prefix=settings.EMAIL_SUBJECT_PREFIX, item=item)
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user.email]
        text_content = """
                            Salut {user}, tu as emprunté {article} {item}.
                            Tu en es responsable pendant une semaine, jusqu'à son retour
                            entre les mains du référent matériel jeudi prochain.
                            """.format(user=user.first_name, article=gender, item=item)
        html_content = """
                            <p>Salut {user},</p>
                            <p>Tu as emprunté {article} <strong>{item}</strong>.<br \>
                            Tu en es responsable pendant une semaine,
                            jusqu'à son retour entre les mains du référent matériel <strong>jeudi prochain</strong>.</p>
                            <p>Bonne grimpe !</p>
                            <p>- - -</p>
                            <img src="cid:logo.png">
                            """.format(user=user.first_name, article=gender, item=item)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.mixed_subtype = 'related'

        with open(os.path.join(settings.STATICFILES_DIRS[0], 'img/logo_mail.png'), 'rb') as img:
            msg_image = MIMEImage(img.read())

        msg_image.add_header('Content-ID', '<logo.png>')
        msg.attach(msg_image)

        msg.send()


@permission_required('vertigo.add_equipmentborrowing')
def list_page(request, url_type):

    # Verify the user agreed to borrowing policy
    if request.user.profile.agreement:

        equipment = [obj for obj in Equipment.TYPE_LIST if obj.url == url_type][0]

        response = EquipmentBorrowing.objects.filter(item__type=equipment.url).order_by('item__ref', '-date', '-id') \
            .distinct('item__ref').exclude(item__status=False)

        context = {
            'types': Equipment.TYPE_LIST,
            'current_type': equipment,
            'data': response
        }
        return render(request, 'list.html', context)

    else:
        return redirect('agreement_url', url_type=url_type)  # , next=request.path


@permission_required('vertigo.add_equipmentborrowing')
def borrowing_page(request, url_type, equipment_id):

    equipment = [obj for obj in Equipment.TYPE_LIST if obj.url == url_type][0]

    # request.META.get('HTTP_REFERER')

    current_obj = Equipment.objects.get(id=equipment_id)

    # Process POST request
    if request.POST:
        form = EquipmentBorrowingForm(request.POST)
        if form.is_valid():
            item = current_obj
            user = form.cleaned_data['user']
            date = form.cleaned_data['date']
            EquipmentBorrowing.objects.create(item=item, user=user, date=date)

            send_email(user, item, equipment.gender)

            messages.success(request, "Le nouvel emprunt a bien été enregistré.")

            return redirect('list_url', url_type=url_type)

    # Process GET request as default
    form = EquipmentBorrowingForm(initial={'item': equipment_id, 'user': request.user.id})
    equipment_ref = current_obj.ref

    form.fields['user'].queryset = User.objects.filter(is_active=True).filter(profile__agreement=True)

    context = {
        'form': form,
        'current_type': equipment,
        'equipment_id': equipment_id,
        'equipment_ref': equipment_ref,
    }

    return render(request, 'borrowing.html', context)


@permission_required('vertigo.add_equipmentborrowing')
def agreement_page(request, url_type):

    if request.POST and request.user:
        user = User.objects.get(id=request.user.id)
        user.profile.agreement = True
        user.save()
        return redirect('list_url', url_type=url_type)

    if not request.user.profile.agreement:
        context = {
            'url_type': url_type
        }
        return render(request, 'agreement.html', context)


def logout_page(request):
    if request.user.is_authenticated:
        messages.success(
            request, mark_safe("A bientôt <span class=\"font-weight-bold\">{}</span> ! Tu as bien été déconnecté."
                               .format(request.user.first_name)))
        logout(request)
    return render(request, 'login.html')


def export_pdf(request):
    if request.user.is_authenticated:

        response = ExportMaterial()
        return response.pdf_material()
