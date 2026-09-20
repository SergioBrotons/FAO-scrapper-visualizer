"""Official SITG (Système d'Information du Territoire à Genève) REST Client."""

import unicodedata
from typing import Any, Dict, List, Optional, Tuple
import httpx
from rich.console import Console

from fao_transactions.cadastre.coordinate_transform import (
    transform_geojson_geometry,
    lv95_to_wgs84,
)
from fao_transactions.config import settings

console = Console()

# The 4 cadastral sections composing the City of Geneva
GENEVA_CITY_SECTIONS = [
    "Genève-Cité",
    "Genève-Plainpalais",
    "Genève-Eaux-Vives",
    "Genève-Petit-Saconnex",
]


def normalize_string(s: str) -> str:
    """Normalize string by removing accents and converting to lowercase."""
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).strip().lower()


class SitgClient:
    """Client for SITG ArcGIS FeatureServer REST endpoints."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.sitg.rest_base_url).rstrip("/")
        self.client = httpx.Client(timeout=30.0)

    def _query_layer(
        self,
        layer_subpath: str,
        where_clause: str,
        out_fields: str = "*",
        return_geometry: bool = True,
        out_sr: int = 2056,
    ) -> List[Dict[str, Any]]:
        """Query a SITG FeatureServer layer using ArcGIS REST standard."""
        url = f"{self.base_url}/{layer_subpath}/query"
        params = {
            "where": where_clause,
            "outFields": out_fields,
            "f": "geojson",
            "returnGeometry": "true" if return_geometry else "false",
            "outSR": out_sr,
        }

        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("features", [])
        except Exception as e:
            console.print(f"[dim yellow]Warning during SITG query ({where_clause}): {e}[/dim yellow]")
            return []

    def _build_parcel_where(self, commune_str: str, parcel_number: str) -> str:
        """Construct SQL where clause for SITG parcel query."""
        clean_p = parcel_number.strip()
        # Escape single quotes
        safe_commune = commune_str.replace("'", "''")
        if clean_p.isdigit():
            return f"(COMMUNE='{safe_commune}' OR UPPER(COMMUNE)='{safe_commune.upper()}') AND NO_PARCELLE={clean_p}"
        else:
            safe_p = clean_p.replace("'", "''")
            return f"(COMMUNE='{safe_commune}' OR UPPER(COMMUNE)='{safe_commune.upper()}') AND NO_PARCELLE='{safe_p}'"

    def _compute_centroid(self, feature: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """Compute (east, north) centroid in LV95 from geometry coordinates."""
        geom = feature.get("geometry")
        if not geom:
            return None
        coords = geom.get("coordinates")
        if not coords:
            return None

        # Flatten coordinate rings to find average center
        pts: List[Tuple[float, float]] = []

        def extract_pts(c_list: Any) -> None:
            if not isinstance(c_list, list) or not c_list:
                return
            if isinstance(c_list[0], (int, float)) and len(c_list) >= 2:
                pts.append((float(c_list[0]), float(c_list[1])))
            else:
                for item in c_list:
                    extract_pts(item)

        extract_pts(coords)
        if not pts:
            return None
        avg_x = sum(p[0] for p in pts) / len(pts)
        avg_y = sum(p[1] for p in pts) / len(pts)
        return (avg_x, avg_y)

    def _process_feature(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Add LV95 & WGS84 geometries, centroids, and normalized properties."""
        geom_2056 = feature.get("geometry")
        if geom_2056:
            feature["geometry_2056"] = geom_2056
            feature["geometry_4326"] = transform_geojson_geometry(geom_2056, to_crs="EPSG:4326")

            centroid_lv95 = self._compute_centroid(feature)
            if centroid_lv95:
                feature["centroid_lv95"] = centroid_lv95
                lon, lat = lv95_to_wgs84(centroid_lv95[0], centroid_lv95[1])
                feature["centroid_wgs84"] = (lon, lat)

        return feature

    def query_parcel(
        self,
        commune: str,
        parcel_number: str,
        section: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Query the active cadastral parcel layer (CAD_PARCELLE_MENSU).
        Primary lookup: COMMUNE + NO_PARCELLE.
        Supports Geneva City 4 sections and accented commune resolution.
        """
        clean_commune = commune.strip()
        clean_parcel = parcel_number.strip()
        norm_commune = normalize_string(clean_commune)

        candidate_communes: List[str] = []

        # Check if query is for Geneva City or has a specific section
        if norm_commune in ("geneve", "ville de geneve", "geneva"):
            if section:
                norm_sec = normalize_string(section)
                matched_sec = [s for s in GENEVA_CITY_SECTIONS if norm_sec in normalize_string(s)]
                if matched_sec:
                    candidate_communes.extend(matched_sec)
            candidate_communes.extend([s for s in GENEVA_CITY_SECTIONS if s not in candidate_communes])
        else:
            candidate_communes.append(clean_commune)

        for comm in candidate_communes:
            where = self._build_parcel_where(comm, clean_parcel)
            features = self._query_layer(settings.sitg.layers.parcels, where)
            if features:
                return self._process_feature(features[0])

        return None

    def query_historical_parcel(
        self,
        commune: str,
        parcel_number: str,
    ) -> List[Dict[str, Any]]:
        """Query mutated or historical parcels from CAD_PARCELLE_MENSU_HISTO."""
        clean_commune = commune.strip()
        clean_parcel = parcel_number.strip()
        where = self._build_parcel_where(clean_commune, clean_parcel)
        features = self._query_layer(settings.sitg.layers.historical_parcels, where)
        return [self._process_feature(feat) for feat in features]

    def query_buildings_by_egrid(self, egrid: str) -> List[Dict[str, Any]]:
        """Query buildings associated with a parcel EGRID (CAD_BATIMENT_HORSOL)."""
        clean_egrid = egrid.strip()
        where = f"EGRID_LISTE LIKE '%{clean_egrid}%' OR EGRID_CENTROIDE='{clean_egrid}'"
        features = self._query_layer(settings.sitg.layers.buildings, where)
        return [self._process_feature(feat) for feat in features]

    def query_addresses(
        self,
        commune: Optional[str] = None,
        egid: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Query official addresses from CAD_ADRESSE by EGID or commune."""
        clauses = []
        if egid:
            clauses.append(f"EGID={egid}")
        if commune:
            safe_commune = commune.strip().replace("'", "''")
            clauses.append(f"(COMMUNE='{safe_commune}' OR UPPER(COMMUNE)='{safe_commune.upper()}')")

        if not clauses:
            return []

        where = " AND ".join(clauses)
        features = self._query_layer(settings.sitg.layers.addresses, where)
        return [self._process_feature(feat) for feat in features]

