from django.db import models
from django.contrib.gis.db import models as gismodels
from django.conf import settings

import os, re
import datetime
import subprocess
from geoserver.catalog import Catalog
from sorl.thumbnail import ImageField
from taggit.managers import TaggableManager


class KuvaTyyppi(models.Model):
    VIISTO = 'vk'
    KOHDE = 'kk'
    ILMA = 'ik'
    KUVATYYPIT = (
        (VIISTO, 'Viistoilmakuva'),
        (KOHDE, 'Kohde'),
        (ILMA, 'Kohtisuora ilmakuva'),
    )
    tyyppi = models.CharField(max_length=2, choices=KUVATYYPIT)


def removeTabs(text):
    return ' '.join(text.split())

class KuvaManager(models.Manager):
    def create_kuva(self, filename):
        kuva = self.create()
        kuvaFolder = 'kuvat'

        pvmtimenamePattern = re.compile(r'(?P<yy>\d{2})(?P<mm>\d{2})(?P<dd>\d{2})\s(?P<hh>\d{2})(?P<min>\d{2})\s(?P<nimi>.*)\.tif')
        numnamePattern = re.compile(r'(?P<id>\d+)(?P<nimi>.*)\.tif')


        tif = os.path.basename(filename)
        kuva.orginalFilePath = u'alkuperaiset/' + tif

        result = re.match(pvmtimenamePattern, tif)
        if result:
            tiedot = result.groupdict()
            vuosi = 1900 + int(tiedot['yy'])
            kk = int(tiedot['mm'])
            pv = int(tiedot['dd'])
            d = datetime.datetime(vuosi, kk if kk else 1, pv if pv else 1, int(tiedot['hh']), int(tiedot['min']))
            kuva.shootTime = d
            kuva.name = removeTabs(tiedot['nimi'])
            jpgname = '19{yy}{mm}{dd}_{hh}{min}'.format(**tiedot)
        else:
            result = re.match(numnamePattern, tif)
            if result:
                tiedot = result.groupdict()
                kuva.name = removeTabs(tiedot['nimi'])
                jpgname = tiedot['id']

        jpgname += '.jpg'
        output = os.path.join(settings.MEDIA_ROOT, kuvaFolder, jpgname)
        if not os.path.exists(output):
            args = ['gdal_translate', '-of', 'JPEG', '-ot', 'Byte', '-scale', filename.encode('cp1252'), output.encode('cp1252')]
            translate = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = translate.communicate()
            print out
            if err:
                print 'VIRHE: ' + err
                return

        kuva.jpgImage = os.path.join(kuvaFolder, jpgname)

        kuva.save()

        return kuva

    def updateGs(self):
        gs = settings.GEOSERVER
        cat = Catalog(gs['host'], gs['user'], gs['password'])
        ws = cat.get_workspace(gs['workspace'])
        epsg = 'EPSG:404000'

        for kuva in self.all():
            image = kuva.jpgImage
            path = os.path.join(settings.MEDIA_ROOT, image.name)

            layerName = kuva.gsName()

            kuva.createWld()
            cs = cat.create_coveragestore2(layerName, workspace=ws)
            cs.url = 'file://' + path
            cs.type = 'WorldImage'
            cat.save(cs)

            coverage = cat.publish_coverage(layerName, cs, epsg)
            cat.addToGwc(coverage, 'kuva404000')


class Kuva(models.Model):
    name = models.CharField(max_length=256)
    kuvaus = models.TextField(blank=True, null=True)
    shootTime = models.DateTimeField(blank=True, null=True)
    shootHeight = models.PositiveIntegerField(blank=True, null=True)

    jpgImage = models.ImageField(upload_to="kuvat")
    orginalFilePath = models.ImageField(upload_to="alkuperaiset", blank=True)

    tyyppi = models.ForeignKey(KuvaTyyppi, blank=True, null=True)
    geom = gismodels.GeometryField(blank=True, null=True, srid=3067, dim=2)


    tags = TaggableManager(blank=True)

    objects = KuvaManager()
    geoObjects = gismodels.GeoManager()

    def __unicode__(self):
        return u'%s' % (self.name)

    def gsName(self):
        return os.path.splitext(os.path.basename(self.jpgImage.name))[0]

    def getOriginalFilePath(self):
        return os.path.join(settings.MEDIA_ROOT, self.orginalFilePath.name)

    def createWld(self):
        image = self.jpgImage

        wldPath = os.path.join(settings.MEDIA_ROOT, os.path.splitext(image.name)[0] + '.wld')
        with open(wldPath, 'w') as wld:
            wld.write(
                    '1.0\n' \
                    '0.0\n' \
                    '0.0\n' \
                    '-1.0\n' \
                    '0.5\n' \
                    '{:.1f}\n'.format(image.height - 0.5)
                    )

class GCP(models.Model):
    ground = gismodels.PointField(srid=4326, spatial_index=False)
    image = gismodels.PointField(spatial_index=False)

    kuva = models.ForeignKey(Kuva, related_name="gcps")

class Mosaic(models.Model):
    fid = models.IntegerField(primary_key=True)
    geom = gismodels.PolygonField(srid=3067)
    location = models.CharField(max_length=255)
    time = models.DateTimeField(blank=True, null=True)

    objects = gismodels.GeoManager()

    class Meta:
        managed = False
        db_table = 'tausta_mosaic'
