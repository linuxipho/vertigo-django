from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage

import os

from .models import Equipment, Topo, EquipmentBorrowing, TopoBorrowing
from .forms import UploadFileForm, EquipmentBorrowingForm, TopoBorrowingForm
from .exports import ExportMaterial
from .imports import ImportUsers


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
                            <p>- - -<br />
                            https://matos.vertigo-montpellier.fr</p>
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

        context = {'types': Equipment.TYPE_LIST + Topo.TYPE_LIST}

        if url_type in [item.url for item in Topo.TYPE_LIST]:
            context['current_type'] = [obj for obj in Topo.TYPE_LIST if obj.url == url_type][0]
            context['data'] = TopoBorrowing.objects.filter(item__type=context['current_type'].url) \
                .order_by('item__ref', '-date', '-id').distinct('item__ref').exclude(item__status=False)
            template = 'list_topo.html'

        else:  # elif url_type in [item.url for item in Equipment.TYPE_LIST]:
            context['current_type'] = [obj for obj in Equipment.TYPE_LIST if obj.url == url_type][0]
            context['data'] = EquipmentBorrowing.objects.filter(item__type=context['current_type'].url)\
                .order_by('item__ref', '-date', '-id').distinct('item__ref').exclude(item__status=False)
            template = 'list.html'

        return render(request, template, context)

    else:
        return redirect('agreement_url', url_type=url_type)  # , next=request.path


@permission_required(('vertigo.add_equipmentborrowing', 'vertigo.add_topoborrowing'))
def borrowing_page(request, url_type, item_id):

    # request.META.get('HTTP_REFERER')
    if url_type in [item.url for item in Equipment.TYPE_LIST]:
        object_type = [obj for obj in Equipment.TYPE_LIST if obj.url == url_type][0]
        current_obj = Equipment.objects.get(id=item_id)
    else:
        object_type = [obj for obj in Topo.TYPE_LIST if obj.url == url_type][0]
        current_obj = Topo.objects.get(id=item_id)

    # Process POST request
    if request.POST:
        if not request.POST.get("cancel"):

            if issubclass(type(current_obj), Equipment):
                form = EquipmentBorrowingForm(request.POST)
            else:
                form = TopoBorrowingForm(request.POST)

            if form.is_valid():
                user = form.cleaned_data['user']
                date = form.cleaned_data['date']

                if issubclass(type(current_obj), Equipment):
                    EquipmentBorrowing.objects.create(item=current_obj, user=user, date=date)
                else:
                    TopoBorrowing.objects.create(item=current_obj, user=user, date=date)

                send_email(user, current_obj, object_type.gender)
                messages.success(request, "Le nouvel emprunt a bien été enregistré.")

                return redirect('list_url', url_type=url_type)
        else:
            return redirect('list_url', url_type=url_type)

    # Process GET request as default

    if issubclass(type(current_obj), Equipment):
        form = EquipmentBorrowingForm()
    else:
        form = TopoBorrowingForm()

    form.initial = {'date': timezone.now().date().strftime('%Y-%m-%d'),
                    'item': item_id,
                    'user': request.user.id}

    form.fields['user'].queryset = User.objects.filter(is_active=True).filter(profile__agreement=True)
    form.fields['date'].label = "Empruntée le" if object_type.gender == 'la' else "Emprunté le"

    context = {
        'form': form,
        'current_type': object_type,
        'equipment_id': current_obj.id,
        'equipment_ref': current_obj.ref,
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


@permission_required('vertigo.add_user')
def import_page(request):

    if request.POST:
        print("Form")
        if not request.POST.get("cancel"):
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                print("Process file")
                import_users = ImportUsers(request.FILES['file'])
                created = import_users.run()
                print("{} users created".format(created))
                messages.success(request, "{} adhérents on été ajoutés".format(created))
                return HttpResponseRedirect('/admin/auth/user/')

        # else:
        #     return redirect('list_url', url_type=url_type)

    # Process GET request as default
    return render(request, 'import.html', {'form': UploadFileForm()})
