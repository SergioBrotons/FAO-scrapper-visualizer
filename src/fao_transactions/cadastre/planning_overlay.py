"""Spatial Planning & Building Permit Overlay Engine for Geneva SITG Data."""

from typing import Dict, Any, List, Optional, Tuple
import httpx
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
from rich.console import Console

from fao_transactions.config import settings

console = Console()


class PlanningOverlayEngine:
    """Pre-caches spatial planning layers and evaluates spatial intersects on transactions."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.sitg.rest_base_url).rstrip("/")
        self.client = httpx.Client(timeout=45.0)

        self.plq_tree: Optional[STRtree] = None
        self.plq_props: List[Dict[str, Any]] = []

        self.dev_tree: Optional[STRtree] = None
        self.dev_props: List[Dict[str, Any]] = []

        self.urb_tree: Optional[STRtree] = None
        self.urb_props: List[Dict[str, Any]] = []

        self.bati_tree: Optional[STRtree] = None
        self.bati_props: List[Dict[str, Any]] = []

        self._initialized = False

    def load_layers(self) -> None:
        """Fetch all planning and project geometries from SITG REST in bulk."""
        if self._initialized:
            return

        console.print("[dim #C9A24D]Loading SITG Urban Planning & Building Permit Layers...[/dim #C9A24D]")

        # 1. RDPPF_PLQ
        self.plq_props, self.plq_tree = self._fetch_layer_tree(
            settings.sitg.layers.plq,
            "NO_PLAN,LIEU,STATUT_JUR,LIEN_PLAN,LIEN_REGLEMENT,LIEN_SAD",
        )

        # 2. RDPPF_ZONES_DEV
        self.dev_props, self.dev_tree = self._fetch_layer_tree(
            settings.sitg.layers.zones_dev,
            "NOM_ZONE,ABRV_ZONE,DESC_ZONE,NO_LOI,RESTRIC,LIEN_PLAN,LIEN_SAD",
        )

        # 3. PDCN_PROJET_URB
        self.urb_props, self.urb_tree = self._fetch_layer_tree(
            settings.sitg.layers.grands_projets,
            "NOM,TYPE,GP,LIEN_FICHE",
        )

        # 4. CAD_BATI_PROJET
        self.bati_props, self.bati_tree = self._fetch_layer_tree(
            settings.sitg.layers.projected_buildings,
            "NO_AUTOR,TYPE,DESTINATION,NIVEAUX_HORSOL,HAUTEUR,CATEGORIE_BATPRO,DATEDT",
        )

        self._initialized = True
        console.print("[green][OK] Planning and Building Permit layers cached successfully.[/green]")

    def _fetch_layer_tree(self, layer_subpath: str, out_fields: str) -> Tuple[List[Dict[str, Any]], Optional[STRtree]]:
        url = f"{self.base_url}/{layer_subpath}/query"
        params = {
            "where": "1=1",
            "outFields": out_fields,
            "f": "geojson",
            "returnGeometry": "true",
            "outSR": 2056,
        }
        try:
            r = self.client.get(url, params=params)
            r.raise_for_status()
            feats = r.json().get("features", [])
            geoms = []
            props = []
            for f in feats:
                g = f.get("geometry")
                if g:
                    try:
                        s = shape(g)
                        if s.is_valid:
                            geoms.append(s)
                            props.append(f.get("properties", {}))
                    except Exception:
                        pass
            if geoms:
                return props, STRtree(geoms)
        except Exception as e:
            console.print(f"[dim yellow]Warning fetching layer {layer_subpath}: {e}[/dim yellow]")
        return [], None

    def evaluate_point(self, lv95_e: float, lv95_n: float, wgs84_lon: Optional[float] = None, wgs84_lat: Optional[float] = None) -> Dict[str, Any]:
        """Evaluate all planning overlays and deep-links for a given coordinate pair."""
        if not self._initialized:
            self.load_layers()

        pt = Point(lv95_e, lv95_n)
        res: Dict[str, Any] = {
            "streetview_url": None,
            "sitg_aerial_url": f"https://map.sitg.ge.ch/?center={int(lv95_e)},{int(lv95_n)}&scale=1000&mapresources=CADASTRE,ORTHOPHOTO_2023",
            "plq_number": None,
            "plq_name": None,
            "plq_status": None,
            "plq_plan_url": None,
            "plq_reglement_url": None,
            "plq_sad_url": None,
            "zone_dev_name": None,
            "zone_dev_code": None,
            "zone_dev_restriction": None,
            "zone_dev_url": None,
            "zone_dev_sad_url": None,
            "grand_projet_name": None,
            "grand_projet_type": None,
            "grand_projet_url": None,
            "permit_number": None,
            "permit_type": None,
            "permit_destination": None,
            "permit_floors": None,
            "permit_height": None,
            "permit_sad_url": None,
        }

        if wgs84_lon and wgs84_lat:
            res["streetview_url"] = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={wgs84_lat},{wgs84_lon}"

        # 1. PLQ Check
        if self.plq_tree:
            matches = self.plq_tree.query(pt, predicate="intersects")
            if matches.size > 0:
                p = self.plq_props[matches[0]]
                res["plq_number"] = p.get("NO_PLAN")
                res["plq_name"] = p.get("LIEU")
                res["plq_status"] = p.get("STATUT_JUR")
                res["plq_plan_url"] = p.get("LIEN_PLAN")
                res["plq_reglement_url"] = p.get("LIEN_REGLEMENT")
                res["plq_sad_url"] = p.get("LIEN_SAD")

        # 2. Zone Dev Check
        if self.dev_tree:
            matches = self.dev_tree.query(pt, predicate="intersects")
            if matches.size > 0:
                p = self.dev_props[matches[0]]
                res["zone_dev_name"] = p.get("NOM_ZONE")
                res["zone_dev_code"] = p.get("ABRV_ZONE")
                res["zone_dev_restriction"] = p.get("RESTRIC")
                res["zone_dev_url"] = p.get("LIEN_PLAN")
                res["zone_dev_sad_url"] = p.get("LIEN_SAD")

        # 3. Grand Projet Check
        if self.urb_tree:
            matches = self.urb_tree.query(pt, predicate="intersects")
            if matches.size > 0:
                p = self.urb_props[matches[0]]
                res["grand_projet_name"] = p.get("NOM")
                res["grand_projet_type"] = p.get("TYPE")
                res["grand_projet_url"] = p.get("LIEN_FICHE")

        # 4. Building Permit (CAD_BATI_PROJET) within 15m buffer
        if self.bati_tree:
            buf = pt.buffer(15.0)
            matches = self.bati_tree.query(buf, predicate="intersects")
            if matches.size > 0:
                p = self.bati_props[matches[0]]
                no_autor = p.get("NO_AUTOR")
                res["permit_number"] = no_autor
                res["permit_type"] = p.get("TYPE")
                res["permit_destination"] = p.get("DESTINATION")
                res["permit_floors"] = p.get("NIVEAUX_HORSOL")
                res["permit_height"] = p.get("HAUTEUR")
                if no_autor and "APA" in str(no_autor).upper():
                    clean_num = str(no_autor).replace("APA", "").strip()
                    res["permit_sad_url"] = f"https://app2.ge.ch/sadconsult/dossier/APA/{clean_num}"

        return res
