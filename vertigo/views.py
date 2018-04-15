from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from .models import Equipment, EquipmentBorrowing
from .forms import EquipmentBorrowingForm


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


def borrowing_page(request, url_type, equipment_id):

    # request.META.get('HTTP_REFERER')

    # Verify tha user agreed to borrowing policy
    # if request.user.profile.responsibility:
    current_obj = Equipment.objects.get(id=equipment_id)

    # Process POST request
    if request.POST:
        form = EquipmentBorrowingForm(request.POST)
        if form.is_valid():
            item = current_obj
            user = form.cleaned_data['user']
            date = form.cleaned_data['date']
            EquipmentBorrowing.objects.create(item=item, user=user, date=date)

            return redirect('list_url', url_type=url_type)

    # Process GET request as default
    form = EquipmentBorrowingForm(initial={'item': equipment_id, 'user': request.user.id})
    equipment_ref = current_obj.ref

    form.fields['user'].queryset = User.objects.filter(is_active=True).filter(profile__responsibility=True)

    context = {
        'form': form,
        'url_type': url_type,
        'equipment_id': equipment_id,
        'equipment_ref': equipment_ref,
    }

    return render(request, 'borrowing.html', context)

    # else:
    #     return redirect('agreement_url', next=request.path)
