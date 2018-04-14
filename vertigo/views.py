from django.shortcuts import render

from .models import Equipment, EquipmentBorrowing


def list_page(request, url_type):

    equipment = [obj for obj in Equipment.TYPE_LIST if obj.ref == url_type][0]

    response = EquipmentBorrowing.objects.filter(item__type=equipment.ref).order_by('item__ref', '-date', '-id') \
        .distinct('item__ref').exclude(item__status=False)

    context = {
        'types': Equipment.TYPE_LIST,
        'current_type': equipment,
        'data': response
    }

    return render(request, 'list.html', context)


# def borrowing_page(request, equipment, equipment_id):
#     if request.user.agreement:
#
#         current_obj = Equipment.objects.get(id=equipment_id)
#         if request.POST:
#             form = EquipmentBorrowingForm(request.POST)
#             if form.is_valid():
#                 item = current_obj
#                 # user = User.objects.get(id=form.data['user'])
#                 user = form.cleaned_data['user']
#                 date = form.cleaned_data['date']
#                 EquipmentBorrowing.objects.create(item=item, user=user, date=date)
#
#                 if settings.SEND_BORROWING_EMAIL:  # and not request.user.is_authenticated:
#                     if user.email == 'remidechazelles@gmail.com':
#                         subject = "{prefix} Emprunt {item}".format(prefix=settings.EMAIL_SUBJECT_PREFIX, item=item)
#                         from_email = settings.DEFAULT_FROM_EMAIL
#                         to = [user.email]
#
#                         text_content = """
#                             Salut {user}, tu as emprunté {article} {item}.
#                             Tu en es responsable pendant une semaine, jusqu'à son retour
#                             entre les mains du référent matériel jeudi prochain.
#                             """.format(user=user.first_name, article=item.article, item=item)
#
#                         html_content = """
#                             <p>Salut {user},</p>
#                             <p>Tu as emprunté {article} <strong>{item}</strong>.<br \>
#                             Tu en es responsable pendant une semaine,
#                             jusqu'à son retour entre les mains du référent matériel <strong>jeudi prochain</strong>.</p>
#                             <p>- - -</p>
#                             <img src="cid:logo.png">
#                             """.format(user=user.first_name, article=item.article, item=item)
#
#                         msg = EmailMultiAlternatives(subject, text_content, from_email, to)
#
#                         msg.attach_alternative(html_content, "text/html")
#
#                         msg.mixed_subtype = 'related'
#
#                         with open(settings.STATICFILES_DIRS[0] + '/img/logo_mail.png', 'rb') as img:
#                             msg_image = MIMEImage(img.read())
#
#                         msg_image.add_header('Content-ID', '<logo.png>')
#                         msg.attach(msg_image)
#
#                         msg.send()
#
#                 messages.success(request, "Le nouvel emprunt a bien été enregistré.")
#                 return HttpResponseRedirect('/' + item.TYPE_GRAMMAR[item.type]['url'])
#
#         # Default GET actions
#         form = EquipmentBorrowingForm(initial={'item': equipment_id, 'user': request.user.id})
#         type_singular = Equipment.GRAMMAR[current_obj.type]['singular']
#         equipment_ref = current_obj.ref
#
#         form.fields['user'].queryset = User.objects.filter(is_active=True).filter(agreement=True)
#
#         context = {
#             'form': form,
#             'type_url': type_slug,
#             'equipment_id': equipment_id,
#             'type_singular': type_singular,
#             'equipment_ref': equipment_ref,
#         }
#
#         return render(request, 'app/borrowing.html', context)
#
#     else:
#         return redirect('agreement_url', next=request.path)
