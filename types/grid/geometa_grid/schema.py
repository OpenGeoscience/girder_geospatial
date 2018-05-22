from marshmallow import fields
from geometa.schema import BaseSchema
from geometa import from_bounds_to_geojson, CannotHandleError
import gdal


class SubDatasets(fields.Field):
    def _deserialize(self, value, attr, obj):
        return value


class GridSchema(BaseSchema):
    driver = fields.String(required=True)
    width = fields.Integer(required=True)
    height = fields.Integer(required=True)
    affine = fields.List(fields.Float, required=True)
    subDatasets = SubDatasets(required=True)


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
        metadata['type_'] = 'grid'
        main_dataset = gdal.Open(path)
        try:
            dataset = gdal.Open(main_dataset.GetSubDatasets()[0][0])
        except IndexError:
            raise CannotHandleError('Does not have subdatasets')
        bounds = get_bounds(dataset)
        # 2 big assumptions
        # We get the metadata from the 1st subdataset
        # We assume crs is WGS84
        crs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs '
        metadata['crs'] = crs
        metadata['subDatasets'] = main_dataset.GetSubDatasets()
        metadata['affine'] = list(dataset.GetGeoTransform())
        metadata['width'] = dataset.RasterXSize
        metadata['height'] = dataset.RasterYSize
        metadata['driver'] = dataset.GetDriver().LongName
        metadata['nativeBounds'] = bounds
        metadata['bounds'] = from_bounds_to_geojson(bounds, crs)
        schema = GridSchema()
        return schema.load(metadata)
    except AttributeError:
        raise CannotHandleError('Gdal could not open dataset')
