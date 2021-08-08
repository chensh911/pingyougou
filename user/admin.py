from django.contrib import admin

# Register your models here.
from user.models import Address


class ControlAddress(admin.ModelAdmin):
    list_display = ('user', "receiver", "addr", "zip_code", "phone", "is_default",)


admin.site.register(Address, ControlAddress)
