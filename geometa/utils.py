from shapely.geometry import Polygon, mapping
from pyproj import Proj, transform


def clamp(number, lowerBound, upperBound):
    return max(lowerBound, min(number, upperBound))


def from_bounds_to_geojson(bounds, crs):
    try:
        in_proj = Proj(crs)
        out_proj = Proj(init='epsg:4326')
        xmin, ymin = transform(in_proj, out_proj,
                               bounds['left'], bounds['bottom'])
        xmax, ymax = transform(in_proj, out_proj,
                               bounds['right'], bounds['top'])
        # Index creation fails for layers that
        # exceeds lat long limits in mongo
        wgs84_bounds = Polygon.from_bounds(clamp(xmin, -180.0, 180.0),
                                           clamp(ymin, -90.0, 90.0),
                                           clamp(xmax, -180.0, 180.0),
                                           clamp(ymax, -90.0, 90.0))
        return mapping(wgs84_bounds)
    except RuntimeError:
        return ''
