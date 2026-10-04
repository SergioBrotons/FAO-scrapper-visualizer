"""Swiss Federal Register of Buildings and Dwellings (RegBL / GWR) Client.

Queries official Federal Office of Topography (swisstopo / geo.admin.ch)
and Federal Statistical Office (BFS) open APIs to retrieve EGID, EGRID,
construction year, building footprint, total dwelling units, number of floors,
and heating systems without API keys.
"""

import ssl
import json
import logging
import urllib.parse
import urllib.request
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# BFS / RegBL Heating system code definitions
BFS_HEATING_SYSTEMS: Dict[int, str] = {
    7500: "Pas de chauffage",
    7501: "Mazout (Fioul)",
    7510: "Charbon",
    7511: "Gaz naturel",
    7512: "Électricité",
    7513: "Bois / Pellets",
    7520: "Chauffage à distance (CAD Genève / SIG)",
    7530: "Pompe à chaleur (PAC)",
    7540: "Solaire thermique",
    7560: "Biomasse / Autre",
}

# BFS Building construction periods
BFS_CONSTRUCTION_PERIODS: Dict[int, str] = {
    8011: "Avant 1919",
    8012: "1919 - 1945",
    8013: "1946 - 1960",
    8014: "1961 - 1970",
    8015: "1971 - 1980",
    8016: "1981 - 1990",
    8017: "1991 - 2000",
    8018: "2001 - 2005",
    8019: "2006 - 2010",
    8020: "2011 - 2015",
    8021: "2016 - 2020",
    8022: "Après 2020",
}


class RegblClient:
    """Client for Swiss Federal Building Register (RegBL/GWR) via geo.admin.ch."""

    def __init__(self):
        self.search_url = "https://api3.geo.admin.ch/rest/services/api/SearchServer"
        self.detail_base = "https://api3.geo.admin.ch/rest/services/ech/MapServer/ch.bfs.gebaeude_wohnungs_register"
        self.cache: Dict[str, Optional[Dict[str, Any]]] = {}
        self.ssl_context = self._get_ssl_context()

    def _get_ssl_context(self) -> ssl.SSLContext:
        try:
            return ssl.create_default_context()
        except Exception:
            return ssl._create_unverified_context()

    def query_building_by_address(self, address: str, commune: str) -> Optional[Dict[str, Any]]:
        """
        Search RegBL by address and commune.
        Returns detailed building characteristics and federal identifiers.
        """
        if not address:
            return None

        # Clean address string
        clean_addr = address.strip()
        clean_comm = (commune or "Genève").strip()
        cache_key = f"{clean_comm.lower()}_{clean_addr.lower()}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        search_query = f"{clean_addr} {clean_comm}"
        encoded_query = urllib.parse.quote_plus(search_query)
        url = f"{self.search_url}?type=locations&origins=address&searchText={encoded_query}"

        req = urllib.request.Request(url, headers={"User-Agent": "Cytria-Intelligence-Cadastre/2.0"})
        try:
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.debug(f"RegBL search error for '{search_query}': {e}")
            self.cache[cache_key] = None
            return None

        results = data.get("results", [])
        if not results:
            self.cache[cache_key] = None
            return None

        top = results[0].get("attrs", {})
        feat_id = top.get("featureId")
        if not feat_id:
            self.cache[cache_key] = None
            return None

        lat = top.get("lat")
        lon = top.get("lon")
        y = top.get("y")  # LV95 Easting (approx 2.5M)
        x = top.get("x")  # LV95 Northing (approx 1.1M)

        # Retrieve RegBL building attribute record
        detail_url = f"{self.detail_base}/{feat_id}"
        req_d = urllib.request.Request(detail_url, headers={"User-Agent": "Cytria-Intelligence-Cadastre/2.0"})
        try:
            with urllib.request.urlopen(req_d, context=self.ssl_context, timeout=8) as resp_d:
                d_data = json.loads(resp_d.read().decode("utf-8"))
        except Exception as err:
            logger.debug(f"RegBL detail fetch error for feat {feat_id}: {err}")
            self.cache[cache_key] = None
            return None

        attrs = d_data.get("feature", {}).get("attributes", {})
        if not attrs:
            self.cache[cache_key] = None
            return None

        # Resolve heating system
        genh1 = attrs.get("genh1")
        heating = BFS_HEATING_SYSTEMS.get(genh1, f"Code BFS {genh1}" if genh1 else None)

        # Resolve construction year (prioritize wbauj array, fallback to gbauj)
        year = attrs.get("gbauj")
        wbauj = attrs.get("wbauj", [])
        if not year and isinstance(wbauj, list) and wbauj:
            valid_years = [int(y) for y in wbauj if y and str(y).isdigit()]
            if valid_years:
                year = max(valid_years)

        # Resolve construction period
        gbaup = attrs.get("gbaup")
        period = BFS_CONSTRUCTION_PERIODS.get(gbaup) if gbaup else None

        result = {
            "egid": str(attrs.get("egid")) if attrs.get("egid") else None,
            "egrid": attrs.get("egrid"),
            "parcel_number": str(attrs.get("lparz")) if attrs.get("lparz") else None,
            "construction_year": int(year) if year else None,
            "construction_period": period,
            "building_floors": int(attrs.get("gastw")) if attrs.get("gastw") else None,
            "apartments_count": int(attrs.get("ganzwhg")) if attrs.get("ganzwhg") else None,
            "surface_ground_m2": float(attrs.get("garea")) if attrs.get("garea") else None,
            "heating_system": heating,
            "lat": float(lat) if lat else None,
            "lon": float(lon) if lon else None,
            "lv95_e": float(y) if y else None,
            "lv95_n": float(x) if x else None,
            "official_street": attrs.get("strname_deinr") or top.get("label"),
            "postal_code": attrs.get("dplz4"),
        }

        self.cache[cache_key] = result
        return result
