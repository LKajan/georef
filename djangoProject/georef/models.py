from django.db import models
from django.contrib.gis.db import models as gismodels
from django.conf import settings
import os

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


class GCP(models.Model):
    ground = gismodels.PointField()
    image = gismodels.PointField()


class Kuva(models.Model):
    name = models.CharField(max_length=256)
    kuvaus = models.TextField(blank=True, null=True)
    shootTime = models.DateTimeField(blank=True, null=True)
    shootHeight = models.IntegerField(blank=True, null=True)

    jpgImage = models.ImageField(upload_to="kuvat")
    orginalFilePath = models.FilePathField(blank=True)

    tyyppi = models.ForeignKey(KuvaTyyppi, blank=True, null=True)
    geom = gismodels.GeometryField(blank=True, null=True, srid=3067, dim=2)
    gcps = models.ManyToManyField(GCP, blank=True)
    objects = gismodels.GeoManager()
    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return u'%s' % (self.name)

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


class Mosaic(models.Model):
    fid = models.IntegerField(primary_key=True)
    geom = gismodels.PolygonField(srid=3067)
    location = models.CharField(max_length=255)
    time = models.DateTimeField(blank=True, null=True)

    objects = gismodels.GeoManager()

    class Meta:
        managed = False
        db_table = 'tausta_mosaic'
