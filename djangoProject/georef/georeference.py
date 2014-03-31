'''
Created on 1.3.2014

@author: lkajan
'''


from osgeo import gdal
from osgeo import osr
from osgeo import osr
import re, sys, os, traceback
from django.contrib.gis.geos import Polygon

import tempfile
from subprocess import Popen, PIPE
import threading

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

wgs84 = osr.SpatialReference()
wgs84.ImportFromEPSG(4326)
srs = osr.SpatialReference()
srs.ImportFromEPSG(3067)
tr = osr.CoordinateTransformation(wgs84, srs)

def transform_gcps(gcps, imageHeight, dst):
    src = osr.SpatialReference()
    src.ImportFromEPSG(4326)
    tr = osr.CoordinateTransformation(src, dst)
    ret = []
    for gcp in gcps:
        x, y, z = tr.TransformPoint(gcp.ground.get_x(), gcp.ground.get_y(), 0.0)
        ret.append(gdal.GCP(x, y, z, gcp.image.get_x(), imageHeight - gcp.image.get_y()))
    return ret

class NonBlockingStreamReader(object):
    def __init__(self, stream):
        '''
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''

        self._s = stream
        self._q = Queue()
        self._errQ = Queue()

        def _populateQueue(stream, queue, errQ):
            '''
            Collect lines from 'stream' and put them in 'quque'.
            '''

            while True:
                try:
                    line = stream.readline()
                    if line == '':
                        continue

                    if line:
                        queue.put(line)
                    else:
                        raise UnexpectedEndOfStream
                except Exception as e:
                    errQ.put(e)

        self._t = threading.Thread(target=_populateQueue,
                args=(self._s, self._q, self._errQ))
        self._t.daemon = True
        self._t.start()  # start collecting lines from the stream

    def readline(self, timeout=None):
        try:
            exc = self._errQ.get(block=False)
        except Empty:
            pass
        else:
            raise exc

        try:
            return self._q.get(block=timeout is not None,
                    timeout=timeout)
        except Empty:
            return None

class UnexpectedEndOfStream(Exception):
    pass

class GeoreferenceError(Exception):
    pass

class Georeferencer():
    def __init__(self, src, gcps, dst):
        if len(gcps) < 3:
            raise GeoreferenceError('Not enough GCPs')

        self.src = src
        self.gcps_list = []
        self.dst = dst

        self.poly = None

        srcDef = gdal.Open(self.src, gdal.GA_ReadOnly)
        self.srcHeight = srcDef.RasterYSize
        self.srcWidth = srcDef.RasterXSize
        srcDef = None



        for gcp in gcps:
            x, y, z = tr.TransformPoint(gcp.ground.get_x(), gcp.ground.get_y(), 0.0)
            self.gcps_list.extend([
                        '-gcp',
                        '{0}'.format(gcp.image.get_x()), '{0}'.format(self.srcHeight - gcp.image.get_y()),
                        '{0}'.format(x), '{0}'.format(y)])




    def getPoly(self):
        coordPattern = re.compile('\d+(?:\.\d*)?')
        gdaltransform = ['gdaltransform',
                         '-s_srs', 'EPSG:3067']
        gdaltransform.extend(self.gcps_list)
        transform = Popen(gdaltransform, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False)
        transFormOut = NonBlockingStreamReader(transform.stdout)
        transFormErr = NonBlockingStreamReader(transform.stderr)

        transform.stdin.write('{0} {1}\n'.format(0, self.srcHeight))
        transform.stdin.write('{0} {1}\n'.format(0, 0))
        transform.stdin.write('{0} {1}\n'.format(self.srcWidth, 0))
        transform.stdin.write('{0} {1}\n'.format(self.srcWidth, self.srcHeight))

        transform.stdin.flush()
        transform.stdin.close()
        coorList = []
        i = 0
        while i < 4:
            try:
                err = transFormErr.readline(0.1)
                if err:
                    print err
                    i += 1

                line = transFormOut.readline(0.1)
                if line:
                    print line
                    coords = coordPattern.findall(line)
                    coorList.append([float(coords[0]), float(coords[1])])
                    i += 1
                else:
                    print 'eei'
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)
                raise

        if len(coorList) == 4:
            coorList.append(coorList[0])
        else:
            return None

        t = tuple(coorList)
        polygon = Polygon(t)
        return polygon

    def createVrt(self):
        _t, vrtOutput = tempfile.mkstemp()

        gdal_translate = ['gdal_translate',
                          '-of', 'vrt',
                          '-ot', 'Byte',
                          '-scale' , '0', '65535', '1', '255',
                          '-a_nodata', '0',
                          '-a_srs', 'EPSG:3067']

        gdal_translate.extend(self.gcps_list)
        gdal_translate.append(self.src.encode('cp1252'))
        gdal_translate.append(vrtOutput.encode('cp1252'))

        translate = Popen(gdal_translate, stdout=PIPE, stderr=PIPE)
        out, err = translate.communicate()
        print out
        if err:
            raise GeoreferenceError(err)

        return vrtOutput

    def warp(self):
        vrtOutput = self.createVrt()
        gdalwarp = ['gdalwarp',
                    '-of', 'GTiff',
                    '-srcnodata', '0',
                    '-dstnodata', '0',
                    '-r', 'cubic',
                    '-co', 'COMPRESS=DEFLATE',
                    '-co', 'TILED=YES',
                    '-wo', 'NUM_THREADS=ALL_CPUS',
                    '-tr', '0.25', '0.25',
                    '-tap']
        gdalwarp.append(vrtOutput.encode('cp1252'))
        gdalwarp.append(self.dst.replace('\\', '/').encode('cp1252'))

        warp = Popen(gdalwarp, stdout=PIPE, stderr=PIPE)
        out, err = warp.communicate()
        print out
        if err:
            raise GeoreferenceError(err)

        return self.dst
