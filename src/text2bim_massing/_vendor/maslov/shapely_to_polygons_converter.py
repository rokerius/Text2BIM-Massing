# Source: evgmaslov/massing-generation, commit 607ff1fcf80477787409522d93e18e42ac1436cf.
# Only base-class/import dependencies were removed; conversion methods are unchanged.
from typing import List, Tuple

import shapely
from shapely.geometry import Polygon, MultiPolygon

class ShapelyToPolygonsConverter:
    def __call__(self, *, polygons: shapely.Geometry) -> List[List[Tuple[float, float]]]:     
        def convert_polygon(polygon):
            exterior_coords = list(polygon.exterior.coords)
            if exterior_coords[0] == exterior_coords[-1]:
                exterior_coords = exterior_coords[:-1]
            exterior_coords = [(p[0], p[1]) for p in exterior_coords]

            holes_coords = []
            for interior in polygon.interiors:
                interior_coords = list(interior.coords)
                if interior_coords[0] == interior_coords[-1]:
                    interior_coords = interior_coords[:-1]
                interior_coords = [(p[0], p[1]) for p in interior_coords]
                holes_coords.append(interior_coords)

            total_coords = [exterior_coords] + holes_coords
            return total_coords
        output_polygons = []
        if isinstance(polygons, MultiPolygon):
            for poly in polygons.geoms:
                local_polys = convert_polygon(poly)
                output_polygons.extend(local_polys)
        elif isinstance(polygons, Polygon):
            local_polys = convert_polygon(polygons)
            output_polygons.extend(local_polys)
        return output_polygons