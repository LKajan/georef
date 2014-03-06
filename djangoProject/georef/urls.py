from django.conf.urls import *
from georef.views import *

urlpatterns = patterns('',
    url(r"^$", index),
    url(r'^kartta/', kartta),
    url(r'^kuva/(\d+)$', imageInfo),
    url(r'^georef/(\d+)$', georef),
    url(r'^images.geojson$', imagesGeojson),
    url(r'^images.json$', imagesJson)
)
