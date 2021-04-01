from marshmallow import fields
from geometa.schema import BaseSchema
from geometa.utils import from_bounds_to_geojson
from geometa.exceptions import CannotHandleError
from osgeo import gdal, osr
from shapely.geometry import Polygon
from shapely.ops import unary_union


class SubDatasets(fields.Field):
    def _deserialize(self, value, attr, obj):
        # TODO: Validate subdatasets
        return value


class GridSubdatasetSchema(BaseSchema):
    name = fields.Str(required=True)
    driver = fields.String(required=True)
    width = fields.Integer(required=True)
    height = fields.Integer(required=True)
    affine = fields.List(fields.Float, required=True)


class GridSchema(BaseSchema):
    # Each subdataset must follow the base schema
    subDatasets = fields.Nested(GridSubdatasetSchema, many=True, required=True)


def get_bounds(dataset):
    left, xres, xskew, top, yskew, yres = dataset.GetGeoTransform()
    right = left + (dataset.RasterXSize * xres)
    bottom = top + (dataset.RasterYSize * yres)

    bounds = {'left': left,
              'bottom': bottom,
              'right': right,
              'top': top}

    return bounds


def get_bounds_from_gcp(dataset):
    upper_left = [i for i in dataset.GetGCPs() if i.Id == 'UpperLeft'][0]
    lower_right = [i for i in dataset.GetGCPs() if i.Id == 'LowerRight'][0]
    bounds = {'left': upper_left.GCPX,
              'bottom': lower_right.GCPY,
              'right': lower_right.GCPX,
              'top': upper_left.GCPY}

    return bounds


def get_projection_as_proj4(dataset):
    projection = osr.SpatialReference()
    projection.ImportFromWkt(dataset.GetProjection())
    return projection.ExportToProj4()


def get_subdataset_info(subDataset):
    dataset = gdal.Open(subDataset)
    wgs84 = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs '
    crs = get_projection_as_proj4(dataset) or wgs84
    metadata = {}
    if dataset.GetGCPCount() > 0:
        bounds = get_bounds_from_gcp(dataset)
    else:
        bounds = get_bounds(dataset)
    metadata['crs'] = crs
    metadata['type_'] = 'grid'
    metadata['name'] = dataset.GetDescription()
    metadata['driver'] = dataset.GetDriver().LongName
    metadata['nativeBounds'] = bounds
    metadata['bounds'] = from_bounds_to_geojson(bounds, crs)
    metadata['affine'] = list(dataset.GetGeoTransform())
    metadata['width'] = dataset.RasterXSize
    metadata['height'] = dataset.RasterYSize

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
        dataset = gdal.Open(main_dataset.GetSubDatasets()[0][0])
        wgs84 = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs '
        crs = get_projection_as_proj4(dataset) or wgs84
        metadata = {}
        metadata['subDatasets'] = get_subdatasets(main_dataset)
        subDatasetBounds = [Polygon.from_bounds(i['nativeBounds']['left'],
                                                i['nativeBounds']['bottom'],
                                                i['nativeBounds']['right'],
                                                i['nativeBounds']['top'])
                            for i in metadata['subDatasets']]
        union = unary_union(subDatasetBounds)
        bounds = {'left': union.bounds[0], 'right': union.bounds[2],
                  'bottom': union.bounds[1], 'top': union.bounds[3]}
        metadata['crs'] = crs
        metadata['type_'] = 'grid'
        metadata['driver'] = dataset.GetDriver().LongName
        metadata['nativeBounds'] = bounds
        metadata['bounds'] = from_bounds_to_geojson(bounds, crs)

        schema = GridSchema()
        return schema.load(metadata)
    except AttributeError:
        raise CannotHandleError('Gdal could not open dataset')
