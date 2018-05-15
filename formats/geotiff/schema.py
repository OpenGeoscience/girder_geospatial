from marshmallow import fields
from geometa.schema import BaseSchema
from geometa import from_bounds_to_geojson
import rasterio

EXTENSIONS = ['TIFF', 'TIF', 'tiff', 'tif']


class GeotiffSchema(BaseSchema):
    driver = fields.String(required=True)
    dtype = fields.String(required=True)
    width = fields.Integer(required=True)
    height = fields.Integer(required=True)
    bands = fields.Integer(required=True)
    affine = fields.List(fields.Float, required=True)
    bandInfo = fields.List(fields.String, required=True)
    noData = fields.Float()


def handler(path):
    # Returns metadata for girder to save it on the file model
    metadata = {}
    metadata['type_'] = 'raster'

    with rasterio.open(path) as src:
        crs = src.crs.values()[0]
        bounds = src.bounds
        affine = src.affine
        metadata['bands'] = src.count
        metadata['dtype'] = src.dtypes[0]
        metadata['width'] = src.width
        metadata['height'] = src.height
        metadata['driver'] = src.driver
        metadata['crs'] = crs
        metadata['affine'] = (affine.a, affine.b, affine.c,
                              affine.d, affine.e, affine.f)
        metadata['bandInfo'] = [src.colorinterp(i+1).name for i in range(src.count)]

    if src.nodata:
        metadata['noData'] = src.nodata
    metadata['nativeBounds'] = {'left': bounds.left,
                                'right': bounds.right,
                                'bottom': bounds.bottom,
                                'top': bounds.top}
    metadata['bounds'] = from_bounds_to_geojson(bounds.left,
                                                bounds.bottom,
                                                bounds.right,
                                                bounds.top,
                                                crs)
    schema = GeotiffSchema()
    return schema.load(metadata)
