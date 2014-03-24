from django import forms
from django.contrib.gis.forms import ModelForm as GeoModelForm, BaseGeometryWidget

from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
from georef.models import *


class GCPForm(GeoModelForm):
    class Meta:
        model = GCP
        widgets = {
            'ground': forms.HiddenInput(),
            'image': forms.HiddenInput(),
        }


class KuvaForm(forms.ModelForm):
    class Meta:
        model = Kuva
        fields = ['name', 'kuvaus', 'shootTime', 'shootHeight', 'tyyppi', 'tags']


GCPFormset = inlineformset_factory(Kuva, GCP, form=GCPForm, extra=0)
