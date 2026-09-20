"""Configuration management using Pydantic and YAML."""

from pathlib import Path
from typing import Any, Dict
import yaml
from pydantic import BaseModel, Field


class FaoSettings(BaseModel):
    base_url: str = "https://fao.ge.ch"
    timeout_seconds: int = 30
    rate_limit_delay_min_seconds: float = 2.0
    rate_limit_delay_max_seconds: float = 4.0


class BrowserSettings(BaseModel):
    headless: bool = False
    profile_dir: str = "data/browser_profile"
    viewport_width: int = 1400
    viewport_height: int = 900
    slow_mo: int = 100


class SitgLayers(BaseModel):
    parcels: str = "CAD_PARCELLE_MENSU/FeatureServer/0"
    historical_parcels: str = "CAD_PARCELLE_MENSU_HISTO/FeatureServer/0"
    ddp: str = "CAD_DDP/FeatureServer/0"
    ppe: str = "CAD_PPE/FeatureServer/0"
    buildings: str = "CAD_BATIMENT_HORSOL/FeatureServer/0"
    addresses: str = "CAD_ADRESSE/FeatureServer/0"
    zoning: str = "SIT_ZONE_AMENAG/FeatureServer/0"


class SitgSettings(BaseModel):
    rest_base_url: str = "https://vector.sitg.ge.ch/arcgis/rest/services"
    layers: SitgLayers = Field(default_factory=SitgLayers)


class StorageSettings(BaseModel):
    database_path: str = "data/state/state.sqlite"
    raw_pdf_dir: str = "data/raw/fao"
    discovery_dir: str = "data/discovery"
    exports_dir: str = "data/exports"


class Settings(BaseModel):
    fao: FaoSettings = Field(default_factory=FaoSettings)
    browser: BrowserSettings = Field(default_factory=BrowserSettings)
    sitg: SitgSettings = Field(default_factory=SitgSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)

    @classmethod
    def load(cls, config_path: str = "config/settings.yaml") -> "Settings":
        path = Path(config_path)
        if not path.exists():
            return cls()
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        browser_dict = data.get("browser", {})
        if "viewport" in browser_dict:
            vp = browser_dict.pop("viewport")
            browser_dict["viewport_width"] = vp.get("width", 1400)
            browser_dict["viewport_height"] = vp.get("height", 900)

        return cls(
            fao=FaoSettings(**data.get("fao", {})),
            browser=BrowserSettings(**browser_dict),
            sitg=SitgSettings(**data.get("sitg", {})),
            storage=StorageSettings(**data.get("storage", {})),
        )


settings = Settings.load()
