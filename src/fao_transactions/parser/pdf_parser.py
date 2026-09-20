"""Deterministic parser for Geneva FAO real-estate transaction notices (rubrique 133 / art. 157 LaCC)."""

import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
try:
    import pymupdf
except ImportError:
    pymupdf = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None
from rich.console import Console

from fao_transactions.parser.models import TransactionRecord

console = Console(legacy_windows=False)

# Official Geneva communes for robust matching
GENEVA_COMMUNES = [
    "Aire-la-Ville", "Anières", "Avully", "Avusy", "Bardonnex", "Bellevue",
    "Bernex", "Carouge", "Cartigny", "Chancy", "Chêne-Bougeries", "Chêne-Bourg",
    "Choulex", "Collex-Bossy", "Collonge-Bellerive", "Cologny", "Confignon",
    "Corsier", "Dardagny", "Genthod", "Grand-Saconnex", "Le Grand-Saconnex",
    "Gy", "Hermance", "Jussy", "Laconnex", "Lancy", "Meinier", "Meyrin",
    "Onex", "Perly-Certoux", "Plan-les-Ouates", "Pregny-Chambésy", "Presinge",
    "Puplinge", "Russin", "Satigny", "Soral", "Thônex", "Troinex",
    "Vandœuvres", "Vandoeuvres", "Vernier", "Versoix", "Veyrier",
    "Genève", "Geneve", "Ville de Genève",
]

GENEVA_SECTIONS = ["Cité", "Plainpalais", "Eaux-Vives", "Petit-Saconnex"]

# Non-real-estate notice indicators to reject immediately
EXCLUDED_NOTICE_PATTERNS = [
    re.compile(r"autorisation(?:s)?\s+de\s+construire", re.IGNORECASE),
    re.compile(r"enqu[eê]te(?:s)?\s+publique(?:s)?", re.IGNORECASE),
    re.compile(r"abattage\s+d['’]arbre", re.IGNORECASE),
    re.compile(r"office\s+cantonal\s+des\s+v[eé]hicules", re.IGNORECASE),
    re.compile(r"service\s+des\s+contraventions", re.IGNORECASE),
    re.compile(r"proc[eé]dure\s+de\s+faillite", re.IGNORECASE),
    re.compile(r"commandement\s+de\s+payer", re.IGNORECASE),
    re.compile(r"avis\s+de\s+saisie", re.IGNORECASE),
    re.compile(r"d[eé]frichement", re.IGNORECASE),
    re.compile(r"exploitation\s+pr[eé]judiciable", re.IGNORECASE),
    re.compile(r"ordonnance\s+p[eé]nale", re.IGNORECASE),
]

TRANSACTION_INDICATORS = [
    "art. 157 lacc",
    "transaction immobilière",
    "transaction immobiliere",
    "b-f",
    "bien-fonds",
    "ppe",
    "ddp",
    "copropriété",
    "copropriete",
    "ancien(s)",
    "nouveau(x)",
    "aliénateur",
    "alienateur",
    "acquéreur",
    "acquereur",
    "mutation de propriété",
    "mutation de propriete",
]


def clean_spaces(text: str) -> str:
    """Normalize irregular whitespaces and line breaks."""
    text = re.sub(r"[\r\n]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_price(price_str: Optional[str]) -> Tuple[Optional[str], Optional[float]]:
    """Clean raw price text and parse numeric CHF value."""
    if not price_str:
        return None, None
    raw = clean_spaces(price_str)
    lower = raw.lower()
    if any(k in lower for k in ["non communiqué", "sans indication", "donation", "partage", "gratuit", "héritage"]):
        return raw, None

    match = re.search(r"(?:Fr\.?|CHF)?\s*([0-9][0-9\s'’.,]*[0-9])", raw)
    if match:
        num_str = match.group(1)
        cleaned_num = re.sub(r"[\s'’._-]", "", num_str).replace(",", ".")
        try:
            val = float(cleaned_num)
            return raw, val
        except ValueError:
            pass
    return raw, None


def parse_surface(surface_str: Optional[str]) -> Optional[float]:
    """Parse numeric square meters from surface string."""
    if not surface_str:
        return None
    cleaned = re.sub(r"[\s'’_]", "", surface_str).replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def is_real_estate_transaction(text: str) -> bool:
    """Validate that text is genuinely a real-estate transaction and not administrative noise."""
    lower = text.lower()
    for pat in EXCLUDED_NOTICE_PATTERNS:
        if pat.search(text):
            return False
    return any(ind in lower for ind in TRANSACTION_INDICATORS)


class FaoPdfParser:
    """Extracts Geneva real-estate transactions from FAO PDF publications."""

    def __init__(self):
        escaped_communes = [re.escape(c) for c in sorted(GENEVA_COMMUNES, key=len, reverse=True)]
        self.commune_regex = re.compile(
            rf"(?:Commune\s+(?:de\s+|d['’])?)?(?P<commune>{'|'.join(escaped_communes)})",
            re.IGNORECASE,
        )

    def extract_text_pymupdf(self, pdf_path: Path) -> str:
        """Extract continuous text using PyMuPDF."""
        doc = pymupdf.open(pdf_path)
        pages_text = [page.get_text("text") for page in doc]
        doc.close()
        return "\n\n".join(pages_text)

    def extract_text_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber layout awareness."""
        pages_text = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text(layout=True)
                if text:
                    pages_text.append(text)
        return "\n\n".join(pages_text)

    def parse_notice_block(
        self,
        block_text: str,
        current_commune: Optional[str] = None,
        notice_date: Optional[str] = None,
    ) -> Optional[TransactionRecord]:
        """Parse an individual notice paragraph into a TransactionRecord."""
        text = clean_spaces(block_text)
        if len(text) < 15:
            return None

        # Strictly verify this is a real-estate transaction
        if not is_real_estate_transaction(text):
            return None

        # Strip standard publication banner to avoid false "Genève" commune matches
        content_text = re.sub(
            r"Feuille\s+d'avis\s+officielle\s+de\s+la\s+R[eé]publique\s+et\s+canton\s+de\s+Gen[eè]ve\s*-\s*[^Page]+Page\s+\d+(?:\s*/\s*\d+)?",
            "",
            text,
            flags=re.IGNORECASE,
        )

        # Case number (Affaire YYYY/NNNNN/N)
        case_match = re.search(r"Affaire\s+([0-9]{4}/[0-9]+/[0-9]+)", text, re.IGNORECASE)
        case_number = case_match.group(1) if case_match else None

        # Transaction type (Vente, Héritage, Partage, Donation, Echange)
        trans_match = re.search(r"\b(Vente|Héritage|Heritage|Partage|Donation|Echange|Cession)\b", text, re.IGNORECASE)
        transaction_type = trans_match.group(1).capitalize() if trans_match else None

        # Commune detection (prefer commune in notice body, e.g. "Versoix, 47" or "B-F Versoix")
        commune = current_commune
        commune_body_match = re.search(
            rf"(?:(?:B-F|PPE|DDP|COP)\s+|-\s*)(?P<commune>{'|'.join([re.escape(c) for c in GENEVA_COMMUNES if c.lower() != 'genève'])})\b",
            content_text,
            re.IGNORECASE,
        )
        if commune_body_match:
            commune = commune_body_match.group("commune")
        else:
            comm_match = self.commune_regex.search(content_text)
            if comm_match:
                commune = comm_match.group("commune")

        if not commune:
            return None

        if commune.lower() in ("geneve", "ville de genève", "ville de geneve"):
            commune = "Genève"

        # Section detection (for Genève)
        section = None
        for sec in GENEVA_SECTIONS:
            if re.search(rf"\bsection\s+{re.escape(sec)}\b", text, re.IGNORECASE):
                section = sec
                break

        # Property type (B-F, PPE, DDP, COP)
        prop_type = None
        if re.search(r"\bB-F\b", text, re.IGNORECASE):
            prop_type = "Bien-fonds"
        elif re.search(r"\bPPE\b", text, re.IGNORECASE):
            prop_type = "PPE"
        elif re.search(r"\bDDP\b", text, re.IGNORECASE):
            prop_type = "DDP"
        elif re.search(r"\bCOP\b", text, re.IGNORECASE):
            prop_type = "Copropriété"

        # Parcel number detection (prioritize parcel right after property designation, avoid 1/2 fractions and /1000 PPE shares)
        parcel_number = None
        prop_parcel_match = re.search(
            r"(?:PPE|B-F|DDP|COP|parcelle(?:s)?)\s+[^,;]*?(?:,\s*)?(?:[0-9]{1,2}/)?([0-9]{1,6}(?:-[0-9]+)?)",
            text,
            re.IGNORECASE,
        )
        if prop_parcel_match:
            parcel_number = prop_parcel_match.group(1).replace(" ", "")
        else:
            # Fallback: scan slash parcel excluding coproperty fractions and thousandths
            slash_matches = re.finditer(r"\b([0-9]{1,2})/([0-9]+(?:\s*[-/]\s*[0-9]+)?)\b", text)
            for sm in slash_matches:
                prefix = sm.group(1)
                body = sm.group(2).replace(" ", "")
                if prefix in ("1", "2", "3", "4") and body in ("2", "3", "4", "5", "6", "1000"):
                    continue
                parcel_number = body
                break

            if not parcel_number:
                parcel_match = re.search(
                    r"(?:parcelle(?:s)?|ddp|ppe|immeuble|b-f)?\s*(?:n[o°]\s*)?([0-9]+(?:\s*[-/]\s*[0-9]+)?)",
                    text,
                    re.IGNORECASE,
                )
                if parcel_match:
                    parcel_number = parcel_match.group(1).replace(" ", "")

        if not parcel_number:
            return None

        # Surface detection (isolated surface in m2, avoid parcel number preceding comma)
        surface_m2 = None
        surf_match = re.search(r"(?:,\s*|\b)([0-9][0-9\s'’.]*)\s*m[2²]", text, re.IGNORECASE)
        if surf_match:
            surface_m2 = parse_surface(surf_match.group(1))

        # Parties detection
        # Seller / Ancien(s)
        seller = None
        seller_match = re.search(
            r"(?:Ancien\(s\)|Aliénateur|alienateur|vendeur|cédant)\s*:\s*([^.;]+?)(?=(?:Nouveau\(x\)|Acquéreur|acquereur|acheteur|prix|d’une|avec|\.|$))",
            text,
            re.IGNORECASE,
        )
        if seller_match:
            seller = clean_spaces(seller_match.group(1))

        # Buyer / Nouveau(x)
        buyer = None
        buyer_match = re.search(
            r"(?:Nouveau\(x\)|Acquéreur|acquereur|acheteur|cessionnaire)\s*:\s*([^.;]+?)(?=(?:B-F|PPE|DDP|COP|parcelle|prix|valeur|\.|$))",
            text,
            re.IGNORECASE,
        )
        if buyer_match:
            buyer = clean_spaces(buyer_match.group(1))

        # Price detection (support "Prix total de l'affaire: 1'620'000.-.", "Prix: ...", "Montant: ...", etc.)
        price_raw = None
        price_chf = None
        price_match = re.search(
            r"(?:Prix(?:\s+total(?:\s+de\s+l['’]affaire)?)?|Prix\s+de\s+vente|Montant(?:\s+de\s+l['’]affaire)?|Valeur(?:\s+totale)?|contreprestation)\s*:\s*([^.;]+)",
            text,
            re.IGNORECASE,
        )
        if price_match:
            price_raw, price_chf = parse_price(price_match.group(1))

        # Nature of property (e.g. Garage privé, Habitation à un seul logement, Appartement, Villa)
        nature = None
        nature_match = re.search(
            r"\b(?:Habitation|Maison|Villa|Appartement|Garage|Terrain|Immeuble|Bâtiment)[^,.;]*(?:,[^,.;]*){0,2}",
            text,
            re.IGNORECASE,
        )
        if nature_match:
            nature = clean_spaces(nature_match.group(0))

        # Address detection (e.g. Route de Saint-Loup 30A, 1290 Versoix)
        address = None
        addr_match = re.search(
            r"\b(?:Route|Rue|Chemin|Avenue|Boulevard|Place|Quai|Allée)\s+[^,;]+,\s*[0-9]{4}\s+[A-Za-zÀ-ÿ\-]+",
            text,
            re.IGNORECASE,
        )
        if addr_match:
            address = clean_spaces(addr_match.group(0))

        return TransactionRecord(
            commune=commune,
            commune_section=section,
            parcel_number=parcel_number,
            transaction_type=transaction_type,
            property_type=prop_type,
            nature=nature,
            address=address,
            case_number=case_number,
            surface_m2=surface_m2,
            seller=seller,
            buyer=buyer,
            price_raw=price_raw,
            price_chf=price_chf,
            notice_date=notice_date,
            raw_text=text,
        )

    def parse_ldtr_block(
        self,
        block_text: str,
        notice_date: Optional[str] = None,
        file_source: Optional[str] = None,
    ) -> Optional[TransactionRecord]:
        """Parse an LDTR apartment sale notice (article 39 LDTR)."""
        text = clean_spaces(block_text)
        if "ldtr" not in text.lower() and "va " not in text.lower() and "ventes d'appartements" not in text.lower():
            return None

        # Standard label lookahead to prevent cutting on abbreviations like M. or decimal dots in unit 4.01
        label_lookahead = r"(?=\s*(?:Requ[eê]te\s+n[o°]|Requ[eé]rant|Commune\s+et\s+lieu|Objet|Acqu[eé]reur|Prix|LDTR\s*=|Les\s+d[eé]cisions|$))"

        # Case / Requête number (e.g. VA 15177 or VA 14950/2)
        case_match = re.search(r"Requ[eê]te\s+n[o°]\s*:\s*(VA\s*[0-9]+(?:[/-][0-9]+)?)", text, re.IGNORECASE)
        case_number = clean_spaces(case_match.group(1)) if case_match else None

        # Seller: "Requérant et propriétaire de l'appartement: M. Nicolas HOFFMANN"
        seller = None
        seller_match = re.search(rf"Requ[eé]rant[^\n:]*:\s*(.+?)\s*{label_lookahead}", text, re.IGNORECASE)
        if seller_match:
            seller = clean_spaces(seller_match.group(1))

        # Buyer: "Acquéreur de l'appartement: M. Gonzalo MAGNASCO"
        buyer = None
        buyer_match = re.search(rf"Acqu[eé]reur[^\n:]*:\s*(.+?)\s*{label_lookahead}", text, re.IGNORECASE)
        if buyer_match:
            buyer = clean_spaces(buyer_match.group(1))

        # Commune & lieu: "Commune et lieu: Genève, section Eaux-Vives - 11, chemin de la Florence"
        commune = "Genève"
        section = None
        address = None
        loc_match = re.search(rf"Commune\s+et\s+lieu\s*:\s*(.+?)\s*{label_lookahead}", text, re.IGNORECASE)
        if loc_match:
            loc_str = clean_spaces(loc_match.group(1))
            for c in GENEVA_COMMUNES:
                if re.search(rf"\b{re.escape(c)}\b", loc_str, re.IGNORECASE):
                    commune = c
                    break
            for sec in GENEVA_SECTIONS:
                if re.search(rf"\b{re.escape(sec)}\b", loc_str, re.IGNORECASE):
                    section = sec
                    break

            # Extract address cleanly (after the dash separator)
            if " - " in loc_str:
                address = clean_spaces(loc_str.split(" - ", 1)[1])
            elif " – " in loc_str:
                address = clean_spaces(loc_str.split(" – ", 1)[1])
            elif " — " in loc_str:
                address = clean_spaces(loc_str.split(" — ", 1)[1])
            else:
                addr_m = re.search(r"(?:\b(?:Route|Rue|Chemin|Avenue|Boulevard|Place|Quai|Allée|Esplanade|Promenade)\b.+)$", loc_str, re.IGNORECASE)
                address = clean_spaces(addr_m.group(0)) if addr_m else loc_str

        # Objet: "Objet: appartement n° 4.01 de 5 pièces au 2ème étage"
        nature = "Appartement"
        unit_num = None
        rooms = None
        floor = None
        obj_match = re.search(rf"Objet\s*:\s*(.+?)\s*{label_lookahead}", text, re.IGNORECASE)
        if obj_match:
            nature = clean_spaces(obj_match.group(1))
            unit_m = re.search(r"(?:appartement|lot)?\s*n[o°]\s*([0-9A-Za-z.\-_]+)", nature, re.IGNORECASE)
            if unit_m:
                unit_num = unit_m.group(1)
            rooms_m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*pi[eè]ces", nature, re.IGNORECASE)
            if rooms_m:
                try:
                    rooms = float(rooms_m.group(1))
                except ValueError:
                    pass
            floor_m = re.search(
                r"\b(?:au\s+)?([0-9]+(?:er|ème|eme)?\s+[eé]tage|rez(?:-de-chauss[eé]e)?|attique|combles)\b",
                nature,
                re.IGNORECASE,
            )
            if floor_m:
                floor = clean_spaces(floor_m.group(0))

        # Prix de vente: "Prix de vente: Frs 2'770'000.--"
        price_raw = None
        price_chf = None
        price_match = re.search(rf"Prix[^\n:]*:\s*(.+?)\s*{label_lookahead}", text, re.IGNORECASE)
        if price_match:
            price_raw, price_chf = parse_price(price_match.group(1))

        return TransactionRecord(
            source_category="LDTR_Appartement",
            commune=commune,
            commune_section=section,
            parcel_number=None,
            transaction_type="Vente",
            property_type="PPE / Appartement",
            nature=nature,
            address=address,
            rooms=rooms,
            floor=floor,
            unit_number=unit_num,
            case_number=case_number,
            seller=seller,
            buyer=buyer,
            price_raw=price_raw,
            price_chf=price_chf,
            notice_date=notice_date,
            file_source=file_source,
            raw_text=text,
        )

    def parse_text(
        self,
        full_text: str,
        default_date: Optional[str] = None,
        file_source: Optional[str] = None,
    ) -> List[TransactionRecord]:
        """Parse document text into individual real-estate transaction records."""
        date_match = re.search(
            r"(\b\d{1,2}\s+(?:janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s+\d{4}\b)",
            full_text,
            re.IGNORECASE,
        )
        doc_date = default_date
        if date_match and not doc_date:
            doc_date = date_match.group(1)

        # Check if this entire PDF is an LDTR apartment sale
        if "article 39 ldtr" in full_text.lower() or "ventes d'appartements" in full_text.lower() or "requête n°: va" in full_text.lower():
            record = self.parse_ldtr_block(full_text, notice_date=doc_date, file_source=file_source)
            return [record] if record else []

        # Split into notice blocks for Registre Foncier
        raw_blocks = re.split(r"(?:\n\s*[-—•*]\s*|\n\s*\n+)", full_text)
        transactions: List[TransactionRecord] = []
        current_commune = None

        for block in raw_blocks:
            cleaned = block.strip()
            if not cleaned:
                continue

            record = self.parse_notice_block(
                block_text=cleaned,
                current_commune=current_commune,
                notice_date=doc_date,
            )
            if record:
                if file_source:
                    record.file_source = file_source
                transactions.append(record)

        return transactions

    def parse_pdf(self, pdf_path: Path, default_date: Optional[str] = None) -> List[TransactionRecord]:
        """Parse a PDF file from disk using PyMuPDF and pdfplumber fallback."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        filename = pdf_path.name
        text = self.extract_text_pymupdf(pdf_path)
        results = self.parse_text(text, default_date=default_date, file_source=filename)

        if len(results) == 0:
            plumber_text = self.extract_text_pdfplumber(pdf_path)
            results = self.parse_text(plumber_text, default_date=default_date, file_source=filename)

        return results

