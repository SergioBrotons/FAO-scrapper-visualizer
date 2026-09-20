"""Pydantic data models for transaction records."""

import hashlib
from typing import Optional
from pydantic import BaseModel, Field


class TransactionRecord(BaseModel):
    """Normalized model representing a property transaction extracted from FAO."""

    source_category: str = Field(default="Registre_Foncier", description="Source: 'Registre_Foncier' (art. 157 LaCC) or 'LDTR_Appartement' (art. 39 LDTR)")
    commune: str = Field(description="Geneva commune name")
    commune_section: Optional[str] = Field(default=None, description="Section within Geneva (e.g. Cité, Plainpalais, Eaux-Vives)")
    parcel_number: Optional[str] = Field(default=None, description="Cadastral parcel number or ID (if known)")
    transaction_type: Optional[str] = Field(default="Vente", description="Type of transaction (Vente, Héritage, Partage, Donation, etc.)")
    property_type: Optional[str] = Field(default=None, description="Property category (Bien-fonds/B-F, PPE/Appartement, DDP, COP)")
    nature: Optional[str] = Field(default=None, description="Description of the property (e.g. villa, maison, appartement, garage)")
    address: Optional[str] = Field(default=None, description="Street address or location of property")
    rooms: Optional[float] = Field(default=None, description="Number of rooms for apartments (e.g. 5 pièces)")
    floor: Optional[str] = Field(default=None, description="Floor level (e.g. 2ème étage)")
    unit_number: Optional[str] = Field(default=None, description="Apartment or lot number (e.g. 4.01)")
    case_number: Optional[str] = Field(default=None, description="Official registry case number (Affaire YYYY/NNNNN/N or VA XXXXX)")
    surface_m2: Optional[float] = Field(default=None, description="Land or building surface in m²")
    seller: Optional[str] = Field(default=None, description="Ancien(s) / Requérant / Aliénateur / Vendeur")
    buyer: Optional[str] = Field(default=None, description="Nouveau(x) / Acquéreur / Buyer")
    price_raw: Optional[str] = Field(default=None, description="Raw text of the price / consideration")
    price_chf: Optional[float] = Field(default=None, description="Parsed numeric amount in CHF")
    notice_date: Optional[str] = Field(default=None, description="Date of notice or transaction")
    file_source: Optional[str] = Field(default=None, description="Source PDF filename")
    raw_text: str = Field(description="Full raw text of the notice block")
    transaction_hash: Optional[str] = Field(default=None, description="Unique SHA256 identifier")

    def model_post_init(self, __context) -> None:
        """Compute unique deterministic transaction hash if not provided."""
        if not self.transaction_hash:
            # Hash incorporates normalized key identification attributes
            norm_addr = (self.address or "").lower().replace(" ", "")
            norm_seller = (self.seller or "").lower().replace(" ", "")
            norm_buyer = (self.buyer or "").lower().replace(" ", "")
            norm_commune = (self.commune or "").lower().strip()
            norm_case = (self.case_number or "").lower().replace(" ", "")

            seed = f"{self.source_category}_{norm_commune}_{norm_case}_{norm_addr}_{norm_seller}_{norm_buyer}_{self.price_chf or ''}"
            self.transaction_hash = hashlib.sha256(seed.encode("utf-8")).hexdigest()
