'''
Created on 1.3.2014

@author: lkajan
'''


from osgeo import gdal as _gdal
from osgeo import osr as _osr
from osgeo import osr as _ogr
import tempfile, os


def transform_gcps(gcps, srs):
    src = _osr.SpatialReference()
    src.ImportFromEPSG(4326)
    dst = _osr.SpatialReference()
    dst.ImportFromWkt(srs)
    tr = _osr.CoordinateTransformation(src, dst)
    ret = []
    for gcp in gcps:
        x, y, z = tr.TransformPoint(gcp['longitude'], gcp['latitude'], 0.0)
        ret.append(_gdal.GCP(x, y, z, gcp['pixel_x'], gcp['pixel_y']))
    return ret


def georeference(imagepath, gcps):
    src = _gdal.Open(imagepath)
    dst_path = ''
    if src is None:
        raise Exception("Can't open " + imagepath)

    srs = _osr.SpatialReference()
    srs.ImportFromEPSG(3067)

    dst_driver = _gdal.GetDriverByName('GTiff')

    gcps = transform_gcps(gcps, srs)
    if len(gcps) < 3:
        raise Exception('Not enough GCPs')

    georefed_path = tempfile.mktemp()

    vrt_driver = _gdal.GetDriverByName('VRT')
    georefed = vrt_driver.CreateCopy(georefed_path, src)
    georefed.SetProjection(srs)
    georefed.SetGCPs(gcps, srs)

    warped_path = tempfile.mktemp()
    warped = _gdal.AutoCreateWarpedVRT(georefed, srs, srs)
    if warped is None:
        raise Exception("Can't warp")
    warped.SetDescription(warped_path)

    # This is necessary, because otherwise we won't
    # be able to interrupt the process.
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    print "Warping ..."
    dst = dst_driver.CreateCopy(dst_path, warped, callback=_gdal.TermProgress)

    os.remove(warped_path)
    os.remove(georefed_path)

georeference.delay()  # Enqueue function in "default" queue

