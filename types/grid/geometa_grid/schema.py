from marshmallow import fields, Schema
from geometa.schema import BaseSchema, Type_
from geometa import from_bounds_to_geojson, CannotHandleError
import gdal
import osr


class SubDatasets(fields.Field):
    def _deserialize(self, value, attr, obj):
        # TODO: Validate subdatasets
        return value


class GridSchema(Schema):
    type_ = Type_(required=True)
    # Each subdataset must follow the base schema
    subDatasets = fields.Nested(BaseSchema, many=True, required=True)


def get_bounds(dataset):
    left, xres, xskew, top, yskew, yres = dataset.GetGeoTransform()
    right = left + (dataset.RasterXSize * xres)
    bottom = top + (dataset.RasterYSize * yres)

    bounds = {'left': left,
              'bottom': bottom,
              'right': right,
              'top': top}

    return bounds


def get_projection_as_proj4(dataset):
    projection = osr.SpatialReference()
    projection.ImportFromWkt(dataset.GetProjection())
    return projection.ExportToProj4()


def get_subdataset_info(subDataset):
    dataset = gdal.Open(subDataset)
    crs = get_projection_as_proj4(dataset) or '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs '
    metadata = {}
    bounds = get_bounds(dataset)
    metadata['crs'] = crs
    metadata['type_'] = 'grid'
    metadata['affine'] = list(dataset.GetGeoTransform())
    metadata['width'] = dataset.RasterXSize
    metadata['height'] = dataset.RasterYSize
    metadata['driver'] = dataset.GetDriver().LongName
    metadata['nativeBounds'] = bounds
    metadata['bounds'] = from_bounds_to_geojson(bounds, crs)

    return metadata


def get_subdatasets(dataset):
    return [get_subdataset_info(s[0]) for s in dataset.GetSubDatasets()]


def handler(path):
    try:
        # Returns metadata for girder to save it on the file model
        metadata = {}
        metadata['type_'] = 'grid'
        main_dataset = gdal.Open(path)
        try:
            gdal.Open(main_dataset.GetSubDatasets()[0][0])
        except IndexError:
            raise CannotHandleError('Does not have subdatasets')
        metadata['subDatasets'] = get_subdatasets(main_dataset)
        schema = GridSchema()
        return schema.load(metadata)
    except AttributeError:
        raise CannotHandleError('Gdal could not open dataset')
