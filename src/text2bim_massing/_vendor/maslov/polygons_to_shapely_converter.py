# Source: evgmaslov/massing-generation, commit 607ff1fcf80477787409522d93e18e42ac1436cf.
# Only base-class/import dependencies were removed; conversion methods are unchanged.
from typing import List, Tuple

import shapely
from shapely.geometry import Polygon, MultiPolygon

class PolygonsToShapelyConverter:
    def __call__(self, *, polygons: List[List[Tuple[float, float]]]) -> shapely.Geometry:
        shapely_cur_polygon = Polygon(polygons[0])
        for i in range(1, len(polygons)):
            poly = Polygon(polygons[i])
            if shapely_cur_polygon.equals(poly):
                continue
            elif shapely_cur_polygon.contains_properly(poly):
                shapely_cur_polygon = shapely_cur_polygon.difference(poly)
            elif poly.contains_properly(shapely_cur_polygon):
                shapely_cur_polygon = poly.difference(shapely_cur_polygon)
            else:
                shapely_cur_polygon = shapely_cur_polygon.union(poly)
        return shapely_cur_polygon