from django.shortcuts import render, render_to_response, get_object_or_404, RequestContext
from django.contrib.gis.geos import Polygon, GEOSGeometry, fromstr
from django.http import Http404, HttpResponse, HttpRequest, HttpResponseBadRequest

from georef.models import Kuva
from sorl.thumbnail import get_thumbnail

import json

# Create your views here.

def index(request):
    return render_to_response("kuvat/index.html")

def kartta(request):
    return render_to_response("kuvat/kartta.html")

def edit(request, kuva):
    pass

def imageInfo(request, kuva):
    kuva = get_object_or_404(Kuva, pk=kuva)

    return render_to_response('kuvat/kuvaInfo.html',
                              {'kuva': kuva},
                              context_instance=RequestContext(request))

def imagesGeojson(request):
    bbox = request.GET.get('bbox', None)
    if bbox:
        try:
            envelope = tuple([float(i) for i in bbox.split(',')])
            bboxGeom = Polygon.from_bbox(envelope)
        except:
            return HttpResponseBadRequest()

        kuvat = Kuva.objects.filter(geom__intersects=bboxGeom)
    else:
        kuvat = Kuva.objects.all()

    data = {'type': 'FeatureCollection',
            'crs': {
                'type': 'name',
                'properties': {
                    'name': 'urn:ogc:def:crs:EPSG::3067'
                  }
                },
            'features' : []}
    for kuva in kuvat:
        data['features'].append({'type': 'Feature',
                                 'geometry' : json.loads(kuva.geom.json),
                                 'properties': {
                                                'id': kuva.id,
                                                'thumbnail': get_thumbnail(kuva.jpgImage, 'x125').url
                                                }
                                 })

    jsondata = json.dumps(data)

    return HttpResponse(jsondata, content_type="application/json")

def updateImageGeom(request, kuva):
    image = get_object_or_404(Kuva, pk=kuva)


