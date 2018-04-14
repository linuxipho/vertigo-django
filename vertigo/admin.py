from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile, Equipment, EquipmentBorrowing


class ProfileInline(admin.StackedInline):

    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):

    inlines = (ProfileInline, )
    list_display = ('first_name', 'last_name', 'get_phone', 'email', 'get_medical_date')
    list_select_related = ('profile',)

    def get_medical_date(self, instance):
        return instance.profile.medical_date
    get_medical_date.short_description = 'Date du certificat'

    def get_phone(self, instance):
        return instance.profile.formatted_phone()
    get_phone.short_description = 'Téléphone'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


class EquipmentAdmin(admin.ModelAdmin):
    model = Equipment

    list_display = ('__str__', 'brand', 'model', 'serial_number', 'status')
    list_filter = ('type', 'status')
    search_fields = ('ref', 'type')


class EquipmentBorrowingAdmin(admin.ModelAdmin):
    model = EquipmentBorrowing

    list_display = ('item', 'user', 'date')
    list_filter = ('item__type', 'item__status')
    search_fields = ('item__type', '=item__ref')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(EquipmentBorrowing, EquipmentBorrowingAdmin)
