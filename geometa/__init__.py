from shapely.geometry import Polygon, mapping
from pyproj import Proj, transform
import json


def from_bounds_to_geojson(left, bottom, right, top, crs):
    in_proj = Proj(init=crs)
    out_proj = Proj(init='epsg:4326')
    xmin, ymin = transform(in_proj, out_proj, left, bottom)
    xmax, ymax = transform(in_proj, out_proj, right, top)
    wgs84_bounds = Polygon.from_bounds(xmin, ymin, xmax, ymax)
    return json.dumps(mapping(wgs84_bounds))
