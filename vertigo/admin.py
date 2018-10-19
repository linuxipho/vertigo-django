from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from import_export import resources
from import_export.admin import ExportMixin

from .models import Profile, Equipment, Topo, EquipmentBorrowing, TopoBorrowing


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserResource(resources.ModelResource):

    queryset = User.objects.exclude(is_active=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class CustomUserAdmin(ExportMixin, UserAdmin):

    resource_class = UserResource

    inlines = (ProfileInline,)
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


class TopoAdmin(admin.ModelAdmin):
    model = Topo

    list_display = ('__str__', 'type', 'title', 'ref', 'status')
    list_filter = ('type', 'status')
    search_fields = ('ref', 'type')


class EquipmentBorrowingAdmin(admin.ModelAdmin):
    model = EquipmentBorrowing

    list_display = ('item', 'user', 'date')
    list_filter = ('item__type', 'item__status')
    search_fields = ('item__type', '=item__ref')


class TopoBorrowingAdmin(admin.ModelAdmin):
    model = TopoBorrowing

    list_display = ('item', 'user', 'date')
    list_filter = ('item__type', 'item__status')
    search_fields = ('item__type', '=item__ref')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Topo, TopoAdmin)
admin.site.register(EquipmentBorrowing, EquipmentBorrowingAdmin)
admin.site.register(TopoBorrowing, TopoBorrowingAdmin)
