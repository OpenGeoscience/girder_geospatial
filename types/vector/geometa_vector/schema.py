from marshmallow import fields
from geometa.schema import BaseSchema
from geometa.utils import from_bounds_to_geojson
from geometa.exceptions import CannotHandleError
from osgeo import ogr
from shapely.geometry import Polygon
from shapely.ops import unary_union


class Layers(fields.Field):
    def _deserialize(self, value, attr, obj):
        # TODO: Validate subdatasets
        return value


class VectorLayerSchema(BaseSchema):
    featureCount = fields.Int()
    layerFields = fields.List(fields.Str)
    geomType = fields.Str()


class VectorSchema(BaseSchema):
    # Each subdataset must follow the base schema
    driver = fields.String(required=True)
    layers = fields.Int(required=True)
    layerInfo = fields.Nested(VectorLayerSchema, many=True, required=True)


def get_field_info(definition):
    fieldName = definition.GetName()
    fieldTypeCode = definition.GetType()
    fieldType = definition.GetFieldTypeName(fieldTypeCode)
    precision = definition.GetPrecision()
    return '{}: {}:{}'.format(fieldName, fieldType, precision)


def get_layer_info(layer):
    metadata = {}
    extent = layer.GetExtent()
    crs = layer.GetSpatialRef().ExportToProj4()
    bounds = {'left': extent[0], 'right': extent[1],
              'bottom': extent[2], 'top': extent[3]}
    metadata['crs'] = crs
    metadata['nativeBounds'] = bounds
    metadata['type_'] = 'vector'
    metadata['bounds'] = from_bounds_to_geojson(bounds, crs)
    metadata['featureCount'] = layer.GetFeatureCount()
    definition = layer.GetLayerDefn()
    count = definition.GetFieldCount()
    metadata['geomType'] = ogr.GeometryTypeToName(definition.GetGeomType())
    metadata['layerFields'] = [get_field_info(definition.GetFieldDefn(i))
                               for i in range(count)]
    return metadata


def get_layers(dataset):
    return [get_layer_info(dataset.GetLayer(i))
            for i in range(dataset.GetLayerCount())]


def handler(path):
    try:
        # Returns metadata for girder to save it on the file model
        metadata = {}
        metadata['type_'] = 'vector'
        dataset = ogr.Open(path)
        if not dataset:
            raise CannotHandleError()
        metadata['driver'] = dataset.GetDriver().GetName()
        metadata['layers'] = dataset.GetLayerCount()
        metadata['layerInfo'] = get_layers(dataset)
        layerBounds = [Polygon.from_bounds(i['nativeBounds']['left'],
                                           i['nativeBounds']['bottom'],
                                           i['nativeBounds']['right'],
                                           i['nativeBounds']['top'])
                       for i in metadata['layerInfo']]
        union = unary_union(layerBounds)
        layer = dataset.GetLayer(0)
        crs = layer.GetSpatialRef().ExportToProj4()
        bounds = {'left': union.bounds[0], 'right': union.bounds[2],
                  'bottom': union.bounds[1], 'top': union.bounds[3]}
        metadata['crs'] = crs
        metadata['nativeBounds'] = bounds
        metadata['type_'] = 'vector'
        metadata['bounds'] = from_bounds_to_geojson(bounds, crs)

        schema = VectorSchema()
        return schema.load(metadata)
    except AttributeError:
        raise CannotHandleError('Ogr could not open dataset')
