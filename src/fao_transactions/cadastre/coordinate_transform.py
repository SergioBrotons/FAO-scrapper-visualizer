"""Swiss Coordinate Transformation between EPSG:2056 (CH1903+ / LV95) and EPSG:4326 (WGS84)."""

from typing import Any, Dict, List, Tuple, Union
from pyproj import Transformer
from shapely.geometry import shape, mapping
from shapely.ops import transform

# Transformer from EPSG:2056 (E, N) -> EPSG:4326 (Lat, Lon) or (Lon, Lat)
# Note: In GIS GeoJSON standard, coordinates are [longitude, latitude].
_transformer_2056_to_4326 = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)
_transformer_4326_to_2056 = Transformer.from_crs("EPSG:4326", "EPSG:2056", always_xy=True)


def lv95_to_wgs84(east: float, north: float) -> Tuple[float, float]:
    """Convert Swiss LV95 (E, N) coordinates to WGS84 (longitude, latitude)."""
    lon, lat = _transformer_2056_to_4326.transform(east, north)
    return lon, lat


def wgs84_to_lv95(lon: float, lat: float) -> Tuple[float, float]:
    """Convert WGS84 (longitude, latitude) to Swiss LV95 (E, N)."""
    east, north = _transformer_4326_to_2056.transform(lon, lat)
    return east, north


def transform_geojson_geometry(geometry: Dict[str, Any], to_crs: str = "EPSG:4326") -> Dict[str, Any]:
    """
    Transform a GeoJSON geometry dictionary between EPSG:2056 and EPSG:4326.
    Default converts from EPSG:2056 to EPSG:4326.
    """
    if not geometry:
        return {}

    geom_obj = shape(geometry)
    if to_crs == "EPSG:4326":
        transformed = transform(_transformer_2056_to_4326.transform, geom_obj)
    elif to_crs == "EPSG:2056":
        transformed = transform(_transformer_4326_to_2056.transform, geom_obj)
    else:
        raise ValueError(f"Unsupported target CRS: {to_crs}")

    return mapping(transformed)
