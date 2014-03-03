from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin
from georef.models import Kuva

# Register your models here.

class KuvaAdmin(AdminImageMixin, admin.ModelAdmin):
    pass

admin.site.register(Kuva, KuvaAdmin)