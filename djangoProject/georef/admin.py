from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin
from georef.models import Kuva, GCP

# Register your models here.

class GCPInline(admin.TabularInline):
    model = GCP
    fk_name = "kuva"

class KuvaAdmin(AdminImageMixin, admin.ModelAdmin):
    inlines = [GCPInline]

admin.site.register(Kuva, KuvaAdmin)
