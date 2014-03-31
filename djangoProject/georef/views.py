from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.gis.geos import Polygon, GEOSGeometry, fromstr
from django.http import Http404, HttpResponse, HttpRequest, HttpResponseBadRequest

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from georef.models import Kuva, KuvaTyyppi, GCP, Mosaic
from georef.forms import KuvaForm, GCPFormset
from sorl.thumbnail import get_thumbnail
import json
from georef.georeference import Georeferencer

import os
from django.conf import settings
from osgeo import gdal
# Create your views here.

def index(request):
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('pageSize', 12))

    kuvalista = Kuva.objects.all()
    paginator = Paginator(kuvalista, size)

    try:
        kuvat = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        kuvat = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        kuvat = paginator.page(paginator.num_pages)

    return render(request, "georef/index.html", {'kuvat': kuvat
                                                 })

def kartta(request):
    return render(request, "georef/kartta.html")

def georef(request, kuvaId):
    kuva = get_object_or_404(Kuva, pk=kuvaId)

    ik = KuvaTyyppi.objects.get(tyyppi='ik')

    if request.method == 'POST':
        kuvaForm = KuvaForm(request.POST, instance=kuva)
        gcpFormSet = GCPFormset(request.POST, request.FILES, instance=kuva)
        if kuvaForm.is_valid() and gcpFormSet.is_valid():
            kuva = kuvaForm.save(commit=False)
            gcpFormSet.save()

            gcps = kuva.gcps.all()
            src = os.path.join(settings.MEDIA_ROOT, kuva.orginalFilePath.name).replace('\\', '/')
            dst = os.path.join(settings.TAUSTA_MOSAIC, u'images', kuva.name + u'.tif').replace('\\', '/')

            poly = None
            try:
                gr = Georeferencer(src, gcps, dst)
                poly = gr.getPoly()
                kuva.geom = poly

                if kuva.tyyppi == ik and poly is not None:
                    gr.warp()
                    mosaic = Mosaic(geom=poly,
                                    location='images\\' + kuva.name + '.tif',
                                    time=kuva.shootTime)
                    mosaic.save()

            except Exception as e:
                print e

            kuva.save()

            return redirect('georef.views.kartta')
    else:
        kuvaForm = KuvaForm(instance=kuva)
        gcpFormSet = GCPFormset(instance=kuva)

    return render(request, 'georef/georef.html',
                              {'kuva': kuva,
                               'form': kuvaForm,
                               'gcpFormSet': gcpFormSet})


def imageInfo(request, kuva):
    kuva = get_object_or_404(Kuva, pk=kuva)

    return render(request, 'georef/kuvaInfo.html',
                              {'kuva': kuva})

def imagesJson(request):
    height = int(request.GET.get('height', 200))
    page = int(request.GET.get('page', 0))

    kuvalista = Kuva.objects.all()
    paginator = Paginator(kuvalista, 12)

    try:
        kuvat = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        kuvat = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        kuvat = paginator.page(paginator.num_pages)

    data = []
    for kuva in kuvat:
        data.append({
                    'id': kuva.id,
                    'thumbnail': get_thumbnail(kuva.jpgImage, 'x{0:d}'.format(height)).url
                    })

    jsondata = json.dumps(data)
    return HttpResponse(jsondata, content_type="application/json")

def imagesGeojson(request):
    bbox = request.GET.get('bbox', None)
    if bbox:
        try:
            envelope = tuple([float(i) for i in bbox.split(',')])
            bboxGeom = Polygon.from_bbox(envelope)
        except:
            return HttpResponseBadRequest()

        kuvat = Kuva.geoObjects.filter(geom__intersects=bboxGeom)
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


