from marshmallow import fields
from geometa.schema import BaseSchema
from geometa import from_bounds_to_geojson, CannotHandleError
import gdal
import osr


class GeotiffSchema(BaseSchema):
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
        colorInterp = gdal.GetColorInterpretationName(band.GetColorInterpretation())
        band_info['dataType'] = gdal.GetDataTypeName(band.DataType)
        band_info['colorInterpretation'] = colorInterp
        band_info['scale'] = band.GetScale()
        band_info['offset'] = band.GetOffset()
        band_info['noData'] = band.GetNoDataValue()
        band_info['units'] = band.GetUnitType()
        bands.append(band_info)

    return bands


def get_bounds(dataset):
    left, xres, xskew, top, yskew, yres = dataset.GetGeoTransform()
    right = left + (dataset.RasterXSize * xres)
    bottom = top + (dataset.RasterYSize * yres)

    bounds = {'left': left,
              'bottom': bottom,
              'right': right,
              'top': top}

    return bounds


def handler(path):
    try:
        # Returns metadata for girder to save it on the file model
        metadata = {}
        metadata['type_'] = 'raster'

        dataset = gdal.Open(path)

        crs = get_projection_as_proj4(dataset)
        bounds = get_bounds(dataset)

        metadata['crs'] = crs
        metadata['bands'] = dataset.RasterCount
        metadata['bandInfo'] = get_band_info(dataset)
        metadata['affine'] = list(dataset.GetGeoTransform())
        metadata['width'] = dataset.RasterXSize
        metadata['height'] = dataset.RasterYSize
        metadata['driver'] = dataset.GetDriver().LongName
        metadata['nativeBounds'] = bounds
        metadata['bounds'] = from_bounds_to_geojson(bounds, crs)
        schema = GeotiffSchema()
        return schema.load(metadata)
    except AttributeError:
        raise CannotHandleError('Gdal could not open dataset')
