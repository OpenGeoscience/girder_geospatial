from marshmallow import fields, ValidationError
from geometa.schema import BaseSchema
from geometa.utils import from_bounds_to_geojson
from geometa.exceptions import CannotHandleError
from osgeo import gdal, osr
import rasterio
from rasterio.errors import RasterioIOError


class RasterSchema(BaseSchema):
    driver = fields.String(required=True)
    width = fields.Integer(required=True)
    height = fields.Integer(required=True)
    bands = fields.Integer(required=True)
    affine = fields.List(fields.Float, required=True)
    bandInfo = fields.List(fields.Dict, required=True)


def get_projection_as_proj4(dataset):
    projection = osr.SpatialReference()
    projection.ImportFromWkt(dataset.GetProjection())
    return projection.ExportToProj4()


def get_band_info(dataset):
    bands = []
    for i in range(dataset.RasterCount):
        band_info = {}
        band = dataset.GetRasterBand(i+1)
        color = band.GetColorInterpretation()
        colorInterp = gdal.GetColorInterpretationName(color)
        band_info['dataType'] = gdal.GetDataTypeName(band.DataType)
        band_info['colorInterpretation'] = colorInterp
        band_info['scale'] = band.GetScale()
        band_info['offset'] = band.GetOffset()
        band_info['noData'] = band.GetNoDataValue()
        band_info['units'] = band.GetUnitType()
        bands.append(band_info)

    return bands


def get_bounds(rasterio_dataset):

    bounds = rasterio_dataset.bounds

    return {'left': bounds.left,
            'bottom': bounds.bottom,
            'right': bounds.right,
            'top': bounds.top}


def handler(path):
    try:
        # Returns metadata for girder to save it on the file model
        metadata = {}
        metadata['type_'] = 'raster'

        dataset = gdal.Open(path)

        if dataset.GetSubDatasets():
            raise CannotHandleError('Cannot handle this data type')

        try:
            with rasterio.open(path) as src:
                bounds = get_bounds(src)
        except RasterioIOError:
            raise CannotHandleError('Cannot handle this data type')

        crs = get_projection_as_proj4(dataset)

        metadata['crs'] = crs
        metadata['bands'] = dataset.RasterCount
        metadata['bandInfo'] = get_band_info(dataset)
        metadata['affine'] = list(dataset.GetGeoTransform())
        metadata['width'] = dataset.RasterXSize
        metadata['height'] = dataset.RasterYSize
        metadata['driver'] = dataset.GetDriver().LongName
        metadata['nativeBounds'] = bounds
        metadata['bounds'] = from_bounds_to_geojson(bounds, crs)
        schema = RasterSchema()
        try:
            return schema.load(metadata)
        except ValidationError as e:
            raise CannotHandleError(e.messages)
    except AttributeError:
        raise CannotHandleError('Gdal could not open dataset')
