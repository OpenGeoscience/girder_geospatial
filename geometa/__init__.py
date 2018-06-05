from shapely.geometry import Polygon, mapping
from pyproj import Proj, transform


class CannotHandleError(Exception):
    pass


def from_bounds_to_geojson(bounds, crs):
    try:
        in_proj = Proj(crs)
        out_proj = Proj(init='epsg:4326')
        xmin, ymin = transform(in_proj, out_proj,
                               bounds['left'], bounds['bottom'])
        xmax, ymax = transform(in_proj, out_proj,
                               bounds['right'], bounds['top'])
        wgs84_bounds = Polygon.from_bounds(xmin, ymin, xmax, ymax)
        return mapping(wgs84_bounds)
    except RuntimeError:
        return ''
