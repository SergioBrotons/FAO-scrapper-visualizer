"""Geneva Real Estate Agencies & Brokers Dataset, Geolocation, and Ranking Engine.

Includes geocoded headquarters coordinates, territorial radius of action, social media profiles
(LinkedIn Company Page, Instagram, Website), and individual broker LinkedIn profiles.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

GENEVA_AGENCIES_DATA: List[Dict[str, Any]] = [
    {
        "id": "barnes-suisse",
        "name": "BARNES Suisse SA - Genève",
        "address": "Rue du Rhône 23, 1204 Genève",
        "headquarters_commune": "Genève",
        "lat": 46.2045,
        "lon": 6.1495,
        "radius_meters": 6500,
        "website": "https://barnes-suisse.com/",
        "linkedin_url": "https://www.linkedin.com/company/barnes-suisse-sa/",
        "instagram_url": "https://www.instagram.com/barnes_suisse/",
        "phone": "+41 22 849 88 88",
        "email": "geneve@barnes-suisse.com",
        "specialties": ["Résidentiel Haut de Gamme", "Gestion de Fortune Immobilière", "Ventes Privées"],
        "sold_24m_count": 52,
        "sold_volume_chf_m": 210.0,
        "median_price_chf": 3950000,
        "median_house_chf": 6800000,
        "median_apartment_chf": 2300000,
        "rating": 4.70,
        "reviews_count": 89,
        "primary_territory": "Cologny / Genève / Vandœuvres / Rive Gauche",
        "top_communes": ["Cologny", "Genève", "Vandœuvres", "Collonge-Bellerive", "Pregny-Chambésy"],
        "discount_rate_est": 5.8,
        "agents": [
            {
                "name": "Jérôme Félicité",
                "role": "Président & Directeur Général",
                "specialty": "Propriétés Internationales & Hôtels Particuliers",
                "deals_count": 16,
                "rating": 4.80,
                "reviews_count": 27,
                "top_communes": ["Genève", "Cologny", "Pregny-Chambésy"],
                "linkedin_profile_url": "https://www.linkedin.com/in/jerome-felicite/",
                "phone": "+41 22 849 88 80",
                "email": "j.felicite@barnes-suisse.com"
            },
            {
                "name": "Marie-Christine de Saint-Affrique",
                "role": "Courtière Associée Senior",
                "specialty": "Villas & Terrains Cologny",
                "deals_count": 12,
                "rating": 4.90,
                "reviews_count": 19,
                "top_communes": ["Cologny", "Vandœuvres", "Collonge-Bellerive"],
                "linkedin_profile_url": "https://www.linkedin.com/in/marie-christine-de-saint-affrique/",
                "phone": "+41 22 849 88 82",
                "email": "mc.saintaffrique@barnes-suisse.com"
            },
            {
                "name": "Alexandre de Senarclens",
                "role": "Courtier Spécialiste Rive Droite",
                "specialty": "Résidences d'Ambassades & Propriétés de Maître",
                "deals_count": 10,
                "rating": 4.75,
                "reviews_count": 14,
                "top_communes": ["Pregny-Chambésy", "Bellevue", "Genthod"],
                "linkedin_profile_url": "https://www.linkedin.com/in/alexandre-de-senarclens/",
                "phone": "+41 22 849 88 85",
                "email": "a.senarclens@barnes-suisse.com"
            }
        ]
    },
    {
        "id": "cardis-sothebys",
        "name": "Cardis | Sotheby's International Realty Genève",
        "address": "Rue François-Bellot 2, 1206 Genève",
        "headquarters_commune": "Genève",
        "lat": 46.1975,
        "lon": 6.1550,
        "radius_meters": 7000,
        "website": "https://cardis.ch/",
        "linkedin_url": "https://www.linkedin.com/company/cardis-sotheby-s-international-realty/",
        "instagram_url": "https://www.instagram.com/cardissothebysrealty/",
        "phone": "+41 22 789 20 00",
        "email": "geneve@cardis.ch",
        "specialties": ["Ultra-Luxe", "Réseau International Sotheby's", "Immeubles & Domaines"],
        "sold_24m_count": 45,
        "sold_volume_chf_m": 185.0,
        "median_price_chf": 4100000,
        "median_house_chf": 7500000,
        "median_apartment_chf": 2400000,
        "rating": 4.75,
        "reviews_count": 72,
        "primary_territory": "Canton de Genève Entier (Cologny, Florissant, Russin)",
        "top_communes": ["Cologny", "Genève", "Vandœuvres", "Chêne-Bougeries", "Russin", "Satigny"],
        "discount_rate_est": 5.4,
        "agents": [
            {
                "name": "Sébastien Rohner",
                "role": "Directeur d'Agence Genève",
                "specialty": "Propriétés d'Exception",
                "deals_count": 18,
                "rating": 4.85,
                "reviews_count": 31,
                "top_communes": ["Cologny", "Genève", "Vandœuvres"],
                "linkedin_profile_url": "https://www.linkedin.com/in/sebastien-rohner/",
                "phone": "+41 22 789 20 01",
                "email": "s.rohner@cardis.ch"
            },
            {
                "name": "Arnaud Boissier",
                "role": "Courtier Senior",
                "specialty": "Appartements de Standing Champel",
                "deals_count": 11,
                "rating": 4.80,
                "reviews_count": 16,
                "top_communes": ["Genève", "Chêne-Bougeries"],
                "linkedin_profile_url": "https://www.linkedin.com/in/arnaud-boissier/",
                "phone": "+41 22 789 20 04",
                "email": "a.boissier@cardis.ch"
            },
            {
                "name": "Camille Dutoit",
                "role": "Courtière Spécialiste Campagne",
                "specialty": "Domaines Agricoles & Châteaux",
                "deals_count": 8,
                "rating": 4.90,
                "reviews_count": 12,
                "top_communes": ["Russin", "Satigny", "Dardagny"],
                "linkedin_profile_url": "https://www.linkedin.com/in/camille-dutoit-immo/",
                "phone": "+41 22 789 20 08",
                "email": "c.dutoit@cardis.ch"
            }
        ]
    },
    {
        "id": "comptoir-immobilier",
        "name": "Comptoir Immobilier SA",
        "address": "Rue de la Tertasse 2, 1204 Genève",
        "headquarters_commune": "Genève",
        "lat": 46.2012,
        "lon": 6.1455,
        "radius_meters": 5500,
        "website": "https://comptoir-immo.ch/",
        "linkedin_url": "https://www.linkedin.com/company/comptoir-immobilier-sa/",
        "instagram_url": "https://www.instagram.com/comptoir_immobilier/",
        "phone": "+41 22 319 88 88",
        "email": "ventes@comptoir-immo.ch",
        "specialties": ["Régie Historique", "Immeubles de Rendement", "Villas Rive Gauche & Droite"],
        "sold_24m_count": 48,
        "sold_volume_chf_m": 165.0,
        "median_price_chf": 2650000,
        "median_house_chf": 4200000,
        "median_apartment_chf": 1400000,
        "rating": 4.65,
        "reviews_count": 94,
        "primary_territory": "Genève Ville / Carouge / Rive Gauche",
        "top_communes": ["Genève", "Carouge", "Lancy", "Chêne-Bougeries", "Veyrier", "Thônex"],
        "discount_rate_est": 4.8,
        "agents": [
            {
                "name": "Quentin Epiney",
                "role": "Directeur Commercial Ventes",
                "specialty": "Immeubles Résidentiels & Rendement",
                "deals_count": 14,
                "rating": 4.75,
                "reviews_count": 25,
                "top_communes": ["Genève", "Carouge", "Lancy"],
                "linkedin_profile_url": "https://www.linkedin.com/in/quentin-epiney/",
                "phone": "+41 22 319 88 90",
                "email": "q.epiney@comptoir-immo.ch"
            },
            {
                "name": "Sophie Martin-Pache",
                "role": "Courtière Senior Résidentiel",
                "specialty": "Villas Familiales & Successions",
                "deals_count": 11,
                "rating": 4.85,
                "reviews_count": 18,
                "top_communes": ["Chêne-Bougeries", "Veyrier", "Thônex"],
                "linkedin_profile_url": "https://www.linkedin.com/in/sophie-martin-pache/",
                "phone": "+41 22 319 88 92",
                "email": "s.martinpache@comptoir-immo.ch"
            },
            {
                "name": "Julien Bourgnon",
                "role": "Courtier PPE & Promotions",
                "specialty": "Appartements Neufs & Rénovés",
                "deals_count": 9,
                "rating": 4.70,
                "reviews_count": 12,
                "top_communes": ["Plan-les-Ouates", "Bernex", "Onex"],
                "linkedin_profile_url": "https://www.linkedin.com/in/julien-bourgnon/",
                "phone": "+41 22 319 88 95",
                "email": "j.bourgnon@comptoir-immo.ch"
            }
        ]
    },
    {
        "id": "spg-groupe",
        "name": "SPG Société Privée de Gérance",
        "address": "Route de Chêne 36, 1208 Genève",
        "headquarters_commune": "Genève",
        "lat": 46.2025,
        "lon": 6.1665,
        "radius_meters": 5500,
        "website": "https://spg.ch/",
        "linkedin_url": "https://www.linkedin.com/company/spg-societe-privee-de-gerance/",
        "instagram_url": "https://www.instagram.com/spg_immobilier/",
        "phone": "+41 22 707 46 00",
        "email": "info@spg.ch",
        "specialties": ["Institutionnels", "Gestion de Patrimoine", "Promotions Immobilières"],
        "sold_24m_count": 42,
        "sold_volume_chf_m": 155.0,
        "median_price_chf": 2750000,
        "median_house_chf": 4500000,
        "median_apartment_chf": 1550000,
        "rating": 4.60,
        "reviews_count": 86,
        "primary_territory": "Chêne-Bougeries / Malagnou / Florissant",
        "top_communes": ["Genève", "Chêne-Bougeries", "Cologny", "Chêne-Bourg", "Vandœuvres"],
        "discount_rate_est": 5.0,
        "agents": [
            {
                "name": "Thierry Barbier-Mueller",
                "role": "Administrateur Délégué",
                "specialty": "Portefeuilles Institutionnels & Hoiries",
                "deals_count": 13,
                "rating": 4.80,
                "reviews_count": 21,
                "top_communes": ["Genève", "Chêne-Bougeries", "Cologny"],
                "linkedin_profile_url": "https://www.linkedin.com/in/thierry-barbier-mueller/",
                "phone": "+41 22 707 46 10",
                "email": "t.barbiermueller@spg.ch"
            },
            {
                "name": "Béatrice de Riedmatten",
                "role": "Courtière Partenaire",
                "specialty": "Appartements de Charme & PPE",
                "deals_count": 10,
                "rating": 4.70,
                "reviews_count": 15,
                "top_communes": ["Genève", "Chêne-Bourg", "Vandœuvres"],
                "linkedin_profile_url": "https://www.linkedin.com/in/beatrice-de-riedmatten/",
                "phone": "+41 22 707 46 15",
                "email": "b.riedmatten@spg.ch"
            }
        ]
    },
    {
        "id": "naef-immobilier",
        "name": "Naef Immobilier Genève",
        "address": "Avenue Eugène-Pittard 14-16, 1206 Genève",
        "headquarters_commune": "Genève",
        "lat": 46.1925,
        "lon": 6.1605,
        "radius_meters": 5200,
        "website": "https://naef.ch/",
        "linkedin_url": "https://www.linkedin.com/company/naef-immobilier/",
        "instagram_url": "https://www.instagram.com/naefimmobilier/",
        "phone": "+41 22 839 39 39",
        "email": "geneve@naef.ch",
        "specialties": ["Courtage Résidentiel", "Knight Frank Partner", "Promotions Neuves"],
        "sold_24m_count": 40,
        "sold_volume_chf_m": 140.0,
        "median_price_chf": 2500000,
        "median_house_chf": 4100000,
        "median_apartment_chf": 1350000,
        "rating": 4.68,
        "reviews_count": 78,
        "primary_territory": "Florissant / Champel / Conches",
        "top_communes": ["Genève", "Chêne-Bougeries", "Veyrier", "Troinex", "Vandœuvres"],
        "discount_rate_est": 4.9,
        "agents": [
            {
                "name": "Étienne Nagy",
                "role": "Directeur Général",
                "specialty": "Vente de Prestige & Partenariats",
                "deals_count": 12,
                "rating": 4.82,
                "reviews_count": 20,
                "top_communes": ["Genève", "Vandœuvres"],
                "linkedin_profile_url": "https://www.linkedin.com/in/etienne-nagy/",
                "phone": "+41 22 839 39 40",
                "email": "e.nagy@naef.ch"
            },
            {
                "name": "Isabelle Fiaux",
                "role": "Courtière Senior Rive Gauche",
                "specialty": "Villas Individuelles & Terrains",
                "deals_count": 10,
                "rating": 4.90,
                "reviews_count": 17,
                "top_communes": ["Chêne-Bougeries", "Veyrier", "Troinex"],
                "linkedin_profile_url": "https://www.linkedin.com/in/isabelle-fiaux/",
                "phone": "+41 22 839 39 45",
                "email": "i.fiaux@naef.ch"
            }
        ]
    },
    {
        "id": "moser-vernet",
        "name": "Moser Vernet & Cie (Move Properties)",
        "address": "Rue du Rhône 118, 1204 Genève",
        "headquarters_commune": "Genève",
        "lat": 46.2055,
        "lon": 6.1570,
        "radius_meters": 4800,
        "website": "https://moservernet.ch/",
        "linkedin_url": "https://www.linkedin.com/company/moser-vernet-&-cie/",
        "instagram_url": "https://www.instagram.com/moservernet_cie/",
        "phone": "+41 22 839 29 29",
        "email": "courtage@moservernet.ch",
        "specialties": ["Régie Familiale", "Courtage Move Properties", "Gestion Locative & Vente"],
        "sold_24m_count": 35,
        "sold_volume_chf_m": 115.0,
        "median_price_chf": 2350000,
        "median_house_chf": 3800000,
        "median_apartment_chf": 1280000,
        "rating": 4.72,
        "reviews_count": 64,
        "primary_territory": "Genève Centre / Eaux-Vives / Champel",
        "top_communes": ["Genève", "Chêne-Bougeries", "Cologny", "Collonge-Bellerive", "Carouge"],
        "discount_rate_est": 4.5,
        "agents": [
            {
                "name": "Nicolas Teissier",
                "role": "Responsable du Pôle Courtage",
                "specialty": "Villas & Immeubles Familiaux",
                "deals_count": 12,
                "rating": 4.85,
                "reviews_count": 19,
                "top_communes": ["Genève", "Chêne-Bougeries", "Cologny"],
                "linkedin_profile_url": "https://www.linkedin.com/in/nicolas-teissier-immo/",
                "phone": "+41 22 839 29 30",
                "email": "n.teissier@moservernet.ch"
            },
            {
                "name": "Théry Schir",
                "role": "Courtier Spécialiste PPE",
                "specialty": "Appartements & Résidences Récentes",
                "deals_count": 9,
                "rating": 4.78,
                "reviews_count": 13,
                "top_communes": ["Genève", "Collonge-Bellerive", "Carouge"],
                "linkedin_profile_url": "https://www.linkedin.com/in/thery-schir/",
                "phone": "+41 22 839 29 35",
                "email": "t.schir@moveproperties.ch"
            }
        ]
    },
    {
        "id": "leonard-properties",
        "name": "Leonard Properties Luxury Real Estate",
        "address": "Avenue de Champel 31, 1206 Genève",
        "headquarters_commune": "Genève",
        "lat": 46.1915,
        "lon": 6.1540,
        "radius_meters": 4500,
        "website": "https://leonard-properties.com/",
        "linkedin_url": "https://www.linkedin.com/company/leonard-properties/",
        "instagram_url": "https://www.instagram.com/leonardproperties/",
        "phone": "+41 22 718 70 70",
        "email": "info@leonard-properties.com",
        "specialties": ["Immobilier de Prestige", "Champel & Florissant", "Pieds-dans-l'eau"],
        "sold_24m_count": 28,
        "sold_volume_chf_m": 98.4,
        "median_price_chf": 3800000,
        "median_house_chf": 6200000,
        "median_apartment_chf": 2200000,
        "rating": 4.92,
        "reviews_count": 46,
        "primary_territory": "Champel / Cologny / Vandœuvres",
        "top_communes": ["Genève", "Cologny", "Vandœuvres", "Chêne-Bougeries", "Collonge-Bellerive"],
        "discount_rate_est": 3.8,
        "agents": [
            {
                "name": "Léonard Cohen",
                "role": "Fondateur & Directeur",
                "specialty": "Trophy Assets & Rive Gauche",
                "deals_count": 14,
                "rating": 4.96,
                "reviews_count": 28,
                "top_communes": ["Cologny", "Genève", "Vandœuvres"],
                "linkedin_profile_url": "https://www.linkedin.com/in/leonard-cohen-properties/",
                "phone": "+41 22 718 70 71",
                "email": "lc@leonard-properties.com"
            },
            {
                "name": "Audrey Caveng",
                "role": "Courtière Senior",
                "specialty": "Appartements de Maître & Champel",
                "deals_count": 8,
                "rating": 4.88,
                "reviews_count": 11,
                "top_communes": ["Genève", "Chêne-Bougeries"],
                "linkedin_profile_url": "https://www.linkedin.com/in/audrey-caveng/",
                "phone": "+41 22 718 70 73",
                "email": "ac@leonard-properties.com"
            },
            {
                "name": "Belfin Lips",
                "role": "Courtière Associée",
                "specialty": "Villas Contemporaines",
                "deals_count": 6,
                "rating": 4.80,
                "reviews_count": 7,
                "top_communes": ["Collonge-Bellerive", "Anières"],
                "linkedin_profile_url": "https://www.linkedin.com/in/belfin-lips/",
                "phone": "+41 22 718 70 75",
                "email": "bl@leonard-properties.com"
            }
        ]
    },
    {
        "id": "jouan-de-rham",
        "name": "Jouan - de Rham SA",
        "address": "Route de Thonon 60, 1222 Vésenaz",
        "headquarters_commune": "Collonge-Bellerive",
        "lat": 46.2395,
        "lon": 6.1880,
        "radius_meters": 4800,
        "website": "https://jouan-derham.ch/",
        "linkedin_url": "https://www.linkedin.com/company/jouan-de-rham/",
        "instagram_url": "https://www.instagram.com/jouanderham/",
        "phone": "+41 22 752 40 40",
        "email": "info@jouan-derham.ch",
        "specialties": ["Villas Rive Gauche", "Vésenaz & Anières", "Propriétés Familiales"],
        "sold_24m_count": 24,
        "sold_volume_chf_m": 76.0,
        "median_price_chf": 3100000,
        "median_house_chf": 4100000,
        "median_apartment_chf": 1450000,
        "rating": 5.0,
        "reviews_count": 18,
        "primary_territory": "Collonge-Bellerive / Vésenaz / Cologny",
        "top_communes": ["Collonge-Bellerive", "Anières", "Cologny", "Meinier", "Corsier", "Hermance"],
        "discount_rate_est": 3.5,
        "agents": [
            {
                "name": "Thomas Bergerat",
                "role": "Directeur Commercial",
                "specialty": "Villas & Terrains Vésenaz",
                "deals_count": 11,
                "rating": 5.0,
                "reviews_count": 10,
                "top_communes": ["Collonge-Bellerive", "Anières", "Cologny"],
                "linkedin_profile_url": "https://www.linkedin.com/in/thomas-bergerat/",
                "phone": "+41 22 752 40 42",
                "email": "t.bergerat@jouan-derham.ch"
            },
            {
                "name": "Léonard de Rham",
                "role": "Administrateur & Courtier",
                "specialty": "Patrimoine & Successions Rive Gauche",
                "deals_count": 8,
                "rating": 5.0,
                "reviews_count": 5,
                "top_communes": ["Collonge-Bellerive", "Meinier", "Corsier"],
                "linkedin_profile_url": "https://www.linkedin.com/in/leonard-de-rham/",
                "phone": "+41 22 752 40 45",
                "email": "l.derham@jouan-derham.ch"
            },
            {
                "name": "Maximilien de Stadelhofen",
                "role": "Courtier Expert",
                "specialty": "Propriétés au Bord de l'Eau",
                "deals_count": 5,
                "rating": 5.0,
                "reviews_count": 3,
                "top_communes": ["Hermance", "Anières", "Cologny"],
                "linkedin_profile_url": "https://www.linkedin.com/in/maximilien-stadelhofen/",
                "phone": "+41 22 752 40 48",
                "email": "m.stadelhofen@jouan-derham.ch"
            }
        ]
    },
    {
        "id": "stone-invest",
        "name": "Stone Invest Genève",
        "address": "Chemin de la Seymaz 14, 1253 Vandœuvres",
        "headquarters_commune": "Vandœuvres",
        "lat": 46.2215,
        "lon": 6.1990,
        "radius_meters": 5500,
        "website": "https://stone-invest.ch/",
        "linkedin_url": "https://www.linkedin.com/company/stone-invest/",
        "instagram_url": "https://www.instagram.com/stoneinvest_geneva/",
        "phone": "+41 22 342 70 70",
        "email": "contact@stone-invest.ch",
        "specialties": ["Rive Droite & Grand-Saconnex", "Villas & PPE Neuves", "Conseil Foncier"],
        "sold_24m_count": 22,
        "sold_volume_chf_m": 48.0,
        "median_price_chf": 1950000,
        "median_house_chf": 2900000,
        "median_apartment_chf": 1250000,
        "rating": 4.95,
        "reviews_count": 58,
        "primary_territory": "Le Grand-Saconnex / Meyrin / Vandœuvres",
        "top_communes": ["Le Grand-Saconnex", "Pregny-Chambésy", "Meyrin", "Bellevue", "Genthod", "Versoix"],
        "discount_rate_est": 4.6,
        "agents": [
            {
                "name": "Daniela Ghiandai",
                "role": "Courtière Partenaire Senior",
                "specialty": "Rive Droite & Ventes Express",
                "deals_count": 15,
                "rating": 5.0,
                "reviews_count": 39,
                "top_communes": ["Le Grand-Saconnex", "Pregny-Chambésy", "Meyrin"],
                "linkedin_profile_url": "https://www.linkedin.com/in/daniela-ghiandai/",
                "phone": "+41 22 342 70 72",
                "email": "d.ghiandai@stone-invest.ch"
            },
            {
                "name": "Marcello Della Torre",
                "role": "Courtier Associé",
                "specialty": "Villas & Terrains Rive Droite",
                "deals_count": 7,
                "rating": 4.90,
                "reviews_count": 19,
                "top_communes": ["Bellevue", "Genthod", "Versoix"],
                "linkedin_profile_url": "https://www.linkedin.com/in/marcello-dellatorre/",
                "phone": "+41 22 342 70 75",
                "email": "m.dellatorre@stone-invest.ch"
            }
        ]
    },
    {
        "id": "desormiere-vanhalst",
        "name": "Désormière & Vanhalst - Immobilier Genève",
        "address": "Chemin de Drize 34, 1256 Troinex",
        "headquarters_commune": "Troinex",
        "lat": 46.1685,
        "lon": 6.1480,
        "radius_meters": 4000,
        "website": "https://desormiere-vanhalst.ch/",
        "linkedin_url": "https://www.linkedin.com/company/desormiere-vanhalst/",
        "instagram_url": "https://www.instagram.com/desormiere_vanhalst/",
        "phone": "+41 22 794 80 80",
        "email": "info@desormiere-vanhalst.ch",
        "specialties": ["Villas & Propriétés de Maître", "Troinex & Veyrier", "Campagne Genevoise"],
        "sold_24m_count": 16,
        "sold_volume_chf_m": 42.5,
        "median_price_chf": 2400000,
        "median_house_chf": 3400000,
        "median_apartment_chf": 1100000,
        "rating": 4.87,
        "reviews_count": 31,
        "primary_territory": "Troinex / Veyrier / Rive Gauche",
        "top_communes": ["Troinex", "Veyrier", "Chêne-Bougeries", "Plan-les-Ouates", "Genève"],
        "discount_rate_est": 4.2,
        "agents": [
            {
                "name": "Sandra Bleeckx Vanhalst",
                "role": "Associée & Directrice de Courtage",
                "specialty": "Villas & Hoiries Rive Gauche",
                "deals_count": 9,
                "rating": 4.95,
                "reviews_count": 22,
                "top_communes": ["Troinex", "Veyrier", "Chêne-Bougeries"],
                "linkedin_profile_url": "https://www.linkedin.com/in/sandra-bleeckx-vanhalst/",
                "phone": "+41 22 794 80 82",
                "email": "sandra@desormiere-vanhalst.ch"
            },
            {
                "name": "Adrien Désormière",
                "role": "Associé & Courtier Expert",
                "specialty": "Villas Haut de Gamme & Terrains",
                "deals_count": 7,
                "rating": 4.80,
                "reviews_count": 9,
                "top_communes": ["Troinex", "Plan-les-Ouates", "Genève"],
                "linkedin_profile_url": "https://www.linkedin.com/in/adrien-desormiere/",
                "phone": "+41 22 794 80 84",
                "email": "adrien@desormiere-vanhalst.ch"
            }
        ]
    },
    {
        "id": "nessell-real-estate",
        "name": "NESSELL Real Estate SA",
        "address": "Rue Peillonnex 37, 1225 Chêne-Bourg",
        "legal_address": "Route de Chancy 59, 1213 Petit-Lancy",
        "headquarters_commune": "Chêne-Bourg",
        "lat": 46.1956,
        "lon": 6.1983,
        "radius_meters": 5500,
        "website": "https://www.nessell.ch/",
        "linkedin_url": "https://www.linkedin.com/company/nessell-real-estate/",
        "instagram_url": "https://www.instagram.com/nessell_realestate/",
        "phone": "+41 22 741 26 26",
        "email": "info@nessell.ch",
        "specialties": ["Trois-Chêne & Rive Gauche", "Maisons Individuelles", "Successions"],
        "sold_24m_count": 19,
        "sold_volume_chf_m": 39.2,
        "median_price_chf": 1850000,
        "median_house_chf": 2600000,
        "median_apartment_chf": 1050000,
        "rating": 4.90,
        "reviews_count": 34,
        "primary_territory": "Chêne-Bourg / Chêne-Bougeries / Thônex / Rive Gauche",
        "top_communes": ["Chêne-Bourg", "Chêne-Bougeries", "Thônex", "Vandœuvres", "Cologny"],
        "discount_rate_est": 5.1,
        "agents": [
            {
                "name": "David Knafo",
                "role": "Directeur Associé",
                "specialty": "Maisons Familiales & Onex",
                "deals_count": 12,
                "rating": 4.92,
                "reviews_count": 24,
                "top_communes": ["Onex", "Lancy", "Bernex"],
                "linkedin_profile_url": "https://www.linkedin.com/in/david-knafo-nessell/",
                "phone": "+41 22 792 50 52",
                "email": "d.knafo@nessell.ch"
            },
            {
                "name": "Corinne Guillo",
                "role": "Courtière Partenaire",
                "specialty": "Appartements & PPE Ouest Genevois",
                "deals_count": 7,
                "rating": 4.86,
                "reviews_count": 10,
                "top_communes": ["Onex", "Confignon", "Plan-les-Ouates"],
                "linkedin_profile_url": "https://www.linkedin.com/in/corinne-guillo/",
                "phone": "+41 22 792 50 55",
                "email": "c.guillo@nessell.ch"
            }
        ]
    },
    {
        "id": "beaulieu-immobilier",
        "name": "Beaulieu Immobilier Genève",
        "address": "Route de Pregny 12, 1292 Chambésy",
        "headquarters_commune": "Pregny-Chambésy",
        "lat": 46.2380,
        "lon": 6.1435,
        "radius_meters": 4500,
        "website": "https://beaulieu-immo.ch/",
        "linkedin_url": "https://www.linkedin.com/company/beaulieu-immobilier/",
        "instagram_url": "https://www.instagram.com/beaulieu_immo_geneve/",
        "phone": "+41 22 758 10 10",
        "email": "info@beaulieu-immo.ch",
        "specialties": ["Rive Droite Lac", "Pregny-Chambésy & Bellevue", "Villas Diplomatiques"],
        "sold_24m_count": 14,
        "sold_volume_chf_m": 44.2,
        "median_price_chf": 2850000,
        "median_house_chf": 3900000,
        "median_apartment_chf": 1300000,
        "rating": 4.95,
        "reviews_count": 21,
        "primary_territory": "Pregny-Chambésy / Chambésy / Bellevue",
        "top_communes": ["Pregny-Chambésy", "Bellevue", "Genthod", "Versoix"],
        "discount_rate_est": 3.9,
        "agents": [
            {
                "name": "Gabriela Turcatti",
                "role": "Courtière Associée",
                "specialty": "Villas Diplomatiques & Rive Droite",
                "deals_count": 10,
                "rating": 5.0,
                "reviews_count": 18,
                "top_communes": ["Pregny-Chambésy", "Bellevue", "Genthod"],
                "linkedin_profile_url": "https://www.linkedin.com/in/gabriela-turcatti/",
                "phone": "+41 22 758 10 12",
                "email": "g.turcatti@beaulieu-immo.ch"
            },
            {
                "name": "Philippe Beaulieu",
                "role": "Fondateur",
                "specialty": "Domaines Lacustres",
                "deals_count": 4,
                "rating": 4.85,
                "reviews_count": 3,
                "top_communes": ["Pregny-Chambésy", "Versoix"],
                "linkedin_profile_url": "https://www.linkedin.com/in/philippe-beaulieu-immo/",
                "phone": "+41 22 758 10 15",
                "email": "p.beaulieu@beaulieu-immo.ch"
            }
        ]
    },
    {
        "id": "swissroc-group",
        "name": "Swissroc Real Estate",
        "address": "Rue Jacques-Dalphin 36, 1227 Carouge",
        "headquarters_commune": "Carouge",
        "lat": 46.1835,
        "lon": 6.1390,
        "radius_meters": 4200,
        "website": "https://swissroc.com/",
        "linkedin_url": "https://www.linkedin.com/company/swissroc-group/",
        "instagram_url": "https://www.instagram.com/swissroc_group/",
        "phone": "+41 22 552 05 55",
        "email": "contact@swissroc.com",
        "specialties": ["Développement & Foncier", "Promotions Clé en Main", "Carouge & Plainpalais"],
        "sold_24m_count": 26,
        "sold_volume_chf_m": 82.0,
        "median_price_chf": 2700000,
        "median_house_chf": 3500000,
        "median_apartment_chf": 1500000,
        "rating": 4.78,
        "reviews_count": 39,
        "primary_territory": "Carouge / Genève / Vessy",
        "top_communes": ["Carouge", "Lancy", "Genève", "Veyrier"],
        "discount_rate_est": 4.4,
        "agents": [
            {
                "name": "Cyril de Bavier",
                "role": "CEO & Associé",
                "specialty": "Développement Urbain & Terrains",
                "deals_count": 11,
                "rating": 4.85,
                "reviews_count": 15,
                "top_communes": ["Carouge", "Lancy", "Genève"],
                "linkedin_profile_url": "https://www.linkedin.com/in/cyril-de-bavier/",
                "phone": "+41 22 552 05 56",
                "email": "c.debavier@swissroc.com"
            },
            {
                "name": "Guillaume Basile",
                "role": "Directeur des Ventes",
                "specialty": "Vente sur Plan & Rénovations",
                "deals_count": 9,
                "rating": 4.75,
                "reviews_count": 12,
                "top_communes": ["Carouge", "Veyrier"],
                "linkedin_profile_url": "https://www.linkedin.com/in/guillaume-basile/",
                "phone": "+41 22 552 05 58",
                "email": "g.basile@swissroc.com"
            }
        ]
    },
    {
        "id": "engel-voelkers-geneve",
        "name": "Engel & Völkers Genève",
        "address": "Quai Gustave-Ador 2, 1207 Genève",
        "headquarters_commune": "Genève",
        "lat": 46.2065,
        "lon": 6.1555,
        "radius_meters": 5200,
        "website": "https://engelvoelkers.com/geneva",
        "linkedin_url": "https://www.linkedin.com/company/engel-&-v%C3%B6lkers-switzerland/",
        "instagram_url": "https://www.instagram.com/evgeneva/",
        "phone": "+41 22 552 29 29",
        "email": "geneva@engelvoelkers.com",
        "specialties": ["Réseau International", "Appartements Quai Gustave-Ador", "Cologny & Anières"],
        "sold_24m_count": 25,
        "sold_volume_chf_m": 79.5,
        "median_price_chf": 2900000,
        "median_house_chf": 4500000,
        "median_apartment_chf": 1800000,
        "rating": 4.70,
        "reviews_count": 42,
        "primary_territory": "Eaux-Vives / Cologny / Vésenaz",
        "top_communes": ["Genève", "Cologny", "Anières", "Vandœuvres", "Choulex", "Meinier"],
        "discount_rate_est": 5.2,
        "agents": [
            {
                "name": "Alain Schaller",
                "role": "Managing Director",
                "specialty": "Résidences Lacustres & Prestige",
                "deals_count": 10,
                "rating": 4.75,
                "reviews_count": 18,
                "top_communes": ["Cologny", "Genève", "Anières"],
                "linkedin_profile_url": "https://www.linkedin.com/in/alain-schaller/",
                "phone": "+41 22 552 29 30",
                "email": "alain.schaller@engelvoelkers.com"
            },
            {
                "name": "Nathalie Guichard",
                "role": "Courtière Spécialiste Rive Gauche",
                "specialty": "Villas & Terrains Équestres",
                "deals_count": 8,
                "rating": 4.82,
                "reviews_count": 14,
                "top_communes": ["Vandœuvres", "Choulex", "Meinier"],
                "linkedin_profile_url": "https://www.linkedin.com/in/nathalie-guichard-ev/",
                "phone": "+41 22 552 29 32",
                "email": "nathalie.guichard@engelvoelkers.com"
            }
        ]
    },
    {
        "id": "geneva-homes",
        "name": "Geneva Homes Real Estate",
        "address": "Route de Malagnou 40A, 1208 Genève",
        "headquarters_commune": "Genève",
        "lat": 46.1985,
        "lon": 6.1645,
        "radius_meters": 4800,
        "website": "https://genevahomes.ch/",
        "linkedin_url": "https://www.linkedin.com/company/geneva-homes/",
        "instagram_url": "https://www.instagram.com/genevahomes_realty/",
        "phone": "+41 22 735 25 25",
        "email": "info@genevahomes.ch",
        "specialties": ["Clientèle Expatriée & Multilingue", "Florissant & Malagnou", "Investissements"],
        "sold_24m_count": 21,
        "sold_volume_chf_m": 56.4,
        "median_price_chf": 2200000,
        "median_house_chf": 3400000,
        "median_apartment_chf": 1400000,
        "rating": 5.0,
        "reviews_count": 75,
        "primary_territory": "Malagnou / Florissant / Champel",
        "top_communes": ["Genève", "Chêne-Bougeries", "Vandœuvres", "Pregny-Chambésy", "Versoix"],
        "discount_rate_est": 4.1,
        "agents": [
            {
                "name": "Silvia Mandracho",
                "role": "Fondatrice & Directrice",
                "specialty": "Ventes Résidentielles Internationales",
                "deals_count": 11,
                "rating": 5.0,
                "reviews_count": 42,
                "top_communes": ["Genève", "Chêne-Bougeries", "Vandœuvres"],
                "linkedin_profile_url": "https://www.linkedin.com/in/silvia-mandracho/",
                "phone": "+41 22 735 25 26",
                "email": "s.mandracho@genevahomes.ch"
            },
            {
                "name": "Colin Woolcock",
                "role": "Senior Broker",
                "specialty": "Expat Housing & Relocation Sales",
                "deals_count": 7,
                "rating": 5.0,
                "reviews_count": 21,
                "top_communes": ["Genève", "Pregny-Chambésy", "Versoix"],
                "linkedin_profile_url": "https://www.linkedin.com/in/colin-woolcock/",
                "phone": "+41 22 735 25 28",
                "email": "c.woolcock@genevahomes.ch"
            }
        ]
    },
    {
        "id": "agci-immobilier",
        "name": "AGCI Immobilier",
        "address": "Avenue Vibert 13, 1227 Carouge",
        "headquarters_commune": "Carouge",
        "lat": 46.1820,
        "lon": 6.1340,
        "radius_meters": 3800,
        "website": "https://agci.ch/",
        "linkedin_url": "https://www.linkedin.com/company/agci-immobilier/",
        "instagram_url": "https://www.instagram.com/agci_immobilier/",
        "phone": "+41 22 301 22 22",
        "email": "contact@agci.ch",
        "specialties": ["Carouge & Environs", "Évaluations Précises", "Vente Appartements"],
        "sold_24m_count": 18,
        "sold_volume_chf_m": 37.8,
        "median_price_chf": 1750000,
        "median_house_chf": 2500000,
        "median_apartment_chf": 1150000,
        "rating": 4.91,
        "reviews_count": 48,
        "primary_territory": "Carouge / Lancy / Acacias",
        "top_communes": ["Carouge", "Genève", "Lancy"],
        "discount_rate_est": 4.3,
        "agents": [
            {
                "name": "Alexandre Gallo",
                "role": "Directeur Général",
                "specialty": "Immobilier Urbain & Carougeois",
                "deals_count": 12,
                "rating": 4.95,
                "reviews_count": 35,
                "top_communes": ["Carouge", "Genève", "Lancy"],
                "linkedin_profile_url": "https://www.linkedin.com/in/alexandre-gallo-agci/",
                "phone": "+41 22 301 22 24",
                "email": "a.gallo@agci.ch"
            }
        ]
    },
    {
        "id": "ci-leman",
        "name": "CI Léman Immobilier",
        "address": "Route du Grand-Lancy 50, 1212 Grand-Lancy",
        "headquarters_commune": "Lancy",
        "lat": 46.1810,
        "lon": 6.1260,
        "radius_meters": 4000,
        "website": "https://ci-leman.ch/",
        "linkedin_url": "https://www.linkedin.com/company/ci-leman-immobilier/",
        "instagram_url": "https://www.instagram.com/cilemanimmo/",
        "phone": "+41 22 793 40 40",
        "email": "info@ci-leman.ch",
        "specialties": ["Grand-Lancy & Bachet", "PPE Récentes", "Accompagnement Financement"],
        "sold_24m_count": 20,
        "sold_volume_chf_m": 41.0,
        "median_price_chf": 1800000,
        "median_house_chf": 2400000,
        "median_apartment_chf": 1100000,
        "rating": 4.60,
        "reviews_count": 52,
        "primary_territory": "Lancy / Plan-les-Ouates / Carouge",
        "top_communes": ["Lancy", "Plan-les-Ouates", "Onex", "Bernex", "Confignon"],
        "discount_rate_est": 4.7,
        "agents": [
            {
                "name": "Lionel Chandy",
                "role": "Directeur Associé",
                "specialty": "Vente de Logements & Financement",
                "deals_count": 10,
                "rating": 4.70,
                "reviews_count": 28,
                "top_communes": ["Lancy", "Plan-les-Ouates", "Onex"],
                "linkedin_profile_url": "https://www.linkedin.com/in/lionel-chandy/",
                "phone": "+41 22 793 40 42",
                "email": "l.chandy@ci-leman.ch"
            },
            {
                "name": "Adrien Billaux",
                "role": "Courtier Spécialiste",
                "specialty": "Villas Mitoyennes & PPE",
                "deals_count": 7,
                "rating": 4.65,
                "reviews_count": 14,
                "top_communes": ["Lancy", "Bernex", "Confignon"],
                "linkedin_profile_url": "https://www.linkedin.com/in/adrien-billaux/",
                "phone": "+41 22 793 40 45",
                "email": "a.billaux@ci-leman.ch"
            }
        ]
    },
    {
        "id": "oakswell-group",
        "name": "OAKSWELL BY OAKS GROUP",
        "address": "Route de Malagnou 26, 1208 Genève",
        "headquarters_commune": "Genève",
        "lat": 46.2000,
        "lon": 6.1610,
        "radius_meters": 4500,
        "website": "https://oakswell.ch/",
        "linkedin_url": "https://www.linkedin.com/company/oaks-group-sa/",
        "instagram_url": "https://www.instagram.com/oakswell_geneva/",
        "phone": "+41 22 736 12 12",
        "email": "contact@oakswell.ch",
        "specialties": ["Immobilier Contemporain", "Conseil Patrimonial", "Malagnou & Florissant"],
        "sold_24m_count": 16,
        "sold_volume_chf_m": 43.5,
        "median_price_chf": 2300000,
        "median_house_chf": 3600000,
        "median_apartment_chf": 1450000,
        "rating": 5.0,
        "reviews_count": 18,
        "primary_territory": "Malagnou / Genève / Cologny",
        "top_communes": ["Genève", "Chêne-Bougeries", "Vandœuvres", "Cologny", "Collonge-Bellerive"],
        "discount_rate_est": 3.7,
        "agents": [
            {
                "name": "Joëlle Ordon",
                "role": "Courtière Associée Senior",
                "specialty": "Négociation Stratégique & Off-Market",
                "deals_count": 9,
                "rating": 5.0,
                "reviews_count": 12,
                "top_communes": ["Genève", "Chêne-Bougeries", "Vandœuvres"],
                "linkedin_profile_url": "https://www.linkedin.com/in/joelle-ordon/",
                "phone": "+41 22 736 12 14",
                "email": "j.ordon@oakswell.ch"
            },
            {
                "name": "Luca Copercini",
                "role": "Directeur Associé",
                "specialty": "Villas Contemporaines",
                "deals_count": 5,
                "rating": 5.0,
                "reviews_count": 6,
                "top_communes": ["Cologny", "Collonge-Bellerive"],
                "linkedin_profile_url": "https://www.linkedin.com/in/luca-copercini/",
                "phone": "+41 22 736 12 16",
                "email": "l.copercini@oakswell.ch"
            }
        ]
    },
    {
        "id": "swixim-plan-les-ouates",
        "name": "Swixim International - Plan-les-Ouates",
        "address": "Route de Saint-Julien 129, 1228 Plan-les-Ouates",
        "headquarters_commune": "Plan-les-Ouates",
        "lat": 46.1650,
        "lon": 6.1170,
        "radius_meters": 4500,
        "website": "https://swixim.ch/",
        "linkedin_url": "https://www.linkedin.com/company/swixim-international/",
        "instagram_url": "https://www.instagram.com/swixim_switzerland/",
        "phone": "+41 22 794 15 15",
        "email": "plan-les-ouates@swixim.ch",
        "specialties": ["Réseau International", "Plan-les-Ouates & Perly", "Maisons Familiales"],
        "sold_24m_count": 15,
        "sold_volume_chf_m": 31.5,
        "median_price_chf": 1750000,
        "median_house_chf": 2400000,
        "median_apartment_chf": 1050000,
        "rating": 4.90,
        "reviews_count": 22,
        "primary_territory": "Plan-les-Ouates / Perly-Certoux / Bardonnex",
        "top_communes": ["Plan-les-Ouates", "Perly-Certoux", "Bardonnex"],
        "discount_rate_est": 4.9,
        "agents": [
            {
                "name": "Laure Monney",
                "role": "Directrice d'Agence",
                "specialty": "Maisons Villageoises & Terrains",
                "deals_count": 9,
                "rating": 5.0,
                "reviews_count": 14,
                "top_communes": ["Plan-les-Ouates", "Perly-Certoux", "Bardonnex"],
                "linkedin_profile_url": "https://www.linkedin.com/in/laure-monney/",
                "phone": "+41 22 794 15 17",
                "email": "l.monney@swixim.ch"
            }
        ]
    },
    {
        "id": "omnia-geneve",
        "name": "Omnia Immobilier Genève",
        "address": "Rue Charles-Bonnet 3, 1206 Genève",
        "headquarters_commune": "Genève",
        "lat": 46.1970,
        "lon": 6.1530,
        "radius_meters": 5000,
        "website": "https://omnia.ch/",
        "linkedin_url": "https://www.linkedin.com/company/omnia-immobilier/",
        "instagram_url": "https://www.instagram.com/omniaimmobilier/",
        "phone": "+41 22 700 80 80",
        "email": "geneve@omnia.ch",
        "specialties": ["Courtage Romand", "Genève & Vaud", "Appartements & Villas"],
        "sold_24m_count": 22,
        "sold_volume_chf_m": 58.0,
        "median_price_chf": 2150000,
        "median_house_chf": 3200000,
        "median_apartment_chf": 1300000,
        "rating": 5.0,
        "reviews_count": 24,
        "primary_territory": "Genève / Florissant / Champel",
        "top_communes": ["Genève", "Chêne-Bougeries", "Veyrier", "Troinex", "Satigny"],
        "discount_rate_est": 4.4,
        "agents": [
            {
                "name": "Alexandre Gallina",
                "role": "Directeur Genève",
                "specialty": "Vente Résidentielle Haut de Gamme",
                "deals_count": 10,
                "rating": 5.0,
                "reviews_count": 16,
                "top_communes": ["Genève", "Chêne-Bougeries"],
                "linkedin_profile_url": "https://www.linkedin.com/in/alexandre-gallina/",
                "phone": "+41 22 700 80 82",
                "email": "a.gallina@omnia.ch"
            },
            {
                "name": "Grégory Marchand",
                "role": "Courtier Expert",
                "specialty": "Villas & Terrains Campagne",
                "deals_count": 7,
                "rating": 5.0,
                "reviews_count": 8,
                "top_communes": ["Veyrier", "Troinex", "Satigny"],
                "linkedin_profile_url": "https://www.linkedin.com/in/gregory-marchand-immo/",
                "phone": "+41 22 700 80 85",
                "email": "g.marchand@omnia.ch"
            }
        ]
    },
    {
        "id": "105-immo",
        "name": "105 Immo - Immobilier & Architecture",
        "address": "Route d'Hermance 105, 1245 Collonge-Bellerive",
        "headquarters_commune": "Collonge-Bellerive",
        "lat": 46.2520,
        "lon": 6.2015,
        "radius_meters": 4500,
        "website": "https://105immo.ch/",
        "linkedin_url": "https://www.linkedin.com/company/105immo/",
        "instagram_url": "https://www.instagram.com/105immo/",
        "phone": "+41 22 751 05 05",
        "email": "info@105immo.ch",
        "specialties": ["Rive Gauche Bord du Lac", "Hermance & Anières", "Maisons d'Architecte"],
        "sold_24m_count": 13,
        "sold_volume_chf_m": 41.2,
        "median_price_chf": 2950000,
        "median_house_chf": 3800000,
        "median_apartment_chf": 1400000,
        "rating": 4.95,
        "reviews_count": 19,
        "primary_territory": "Collonge-Bellerive / Hermance / Anières",
        "top_communes": ["Hermance", "Collonge-Bellerive", "Anières"],
        "discount_rate_est": 3.8,
        "agents": [
            {
                "name": "Daniela Dhotel",
                "role": "Associée Gérante",
                "specialty": "Villas Rive Gauche & Hermance",
                "deals_count": 9,
                "rating": 5.0,
                "reviews_count": 15,
                "top_communes": ["Hermance", "Collonge-Bellerive", "Anières"],
                "linkedin_profile_url": "https://www.linkedin.com/in/daniela-dhotel/",
                "phone": "+41 22 751 05 07",
                "email": "d.dhotel@105immo.ch"
            }
        ]
    },
    {
        "id": "john-taylor-geneva",
        "name": "John Taylor Luxury Real Estate Genève",
        "address": "Quai du Mont-Blanc 21, 1201 Genève",
        "headquarters_commune": "Genève",
        "lat": 46.2110,
        "lon": 6.1510,
        "radius_meters": 6500,
        "website": "https://john-taylor.com/geneva",
        "linkedin_url": "https://www.linkedin.com/company/john-taylor/",
        "instagram_url": "https://www.instagram.com/johntaylorswitzerland/",
        "phone": "+41 22 809 98 00",
        "email": "geneva@john-taylor.com",
        "specialties": ["Propriétés Rive Droite Lac", "Quai du Mont-Blanc", "Domaines Privés"],
        "sold_24m_count": 20,
        "sold_volume_chf_m": 88.0,
        "median_price_chf": 4200000,
        "median_house_chf": 7100000,
        "median_apartment_chf": 2500000,
        "rating": 4.85,
        "reviews_count": 28,
        "primary_territory": "Canton de Genève / Cologny / Pregny",
        "top_communes": ["Cologny", "Genève", "Genthod", "Pregny-Chambésy", "Bellevue"],
        "discount_rate_est": 4.8,
        "agents": [
            {
                "name": "Philippe Calame",
                "role": "Directeur Agence",
                "specialty": "Pieds-dans-l'eau & Hôtels Particuliers",
                "deals_count": 11,
                "rating": 4.90,
                "reviews_count": 17,
                "top_communes": ["Cologny", "Genève", "Genthod"],
                "linkedin_profile_url": "https://www.linkedin.com/in/philippe-calame/",
                "phone": "+41 22 809 98 02",
                "email": "p.calame@john-taylor.com"
            }
        ]
    }
]


def compute_agency_score(agency: Dict[str, Any]) -> int:
    """Compute 0-100 Cytria Agency Performance Score based on volume, rating, and closing rate."""
    vol_pts = min(30, (agency.get("sold_volume_chf_m", 0) / 200.0) * 30)
    deals_pts = min(25, (agency.get("sold_24m_count", 0) / 50.0) * 25)
    rating = agency.get("rating") or 4.0
    rating_pts = ((rating - 3.5) / 1.5) * 20  # 3.5 to 5.0 => 0 to 20 pts
    rating_pts = max(0, min(20, rating_pts))
    
    # Review confidence based on review volume
    rev_count = agency.get("reviews_count", 0)
    conf_pts = min(15, (rev_count / 50.0) * 15)
    
    # Discount efficiency (lower discount rate = higher accuracy)
    disc = agency.get("discount_rate_est", 5.0)
    disc_pts = max(0, min(10, (7.0 - disc) * 3.3))
    
    return int(round(vol_pts + deals_pts + rating_pts + conf_pts + disc_pts))


def compute_broker_score(broker: Dict[str, Any], agency_score: int) -> int:
    """Compute 0-100 Cytria Broker Performance Score for an individual agent."""
    deals_pts = min(40, (broker.get("deals_count", 0) / 20.0) * 40)
    rating = broker.get("rating") or 4.5
    rating_pts = max(0, min(30, ((rating - 4.0) / 1.0) * 30))
    rev_pts = min(15, (broker.get("reviews_count", 0) / 30.0) * 15)
    agency_bonus = (agency_score / 100.0) * 15
    return int(round(deals_pts + rating_pts + rev_pts + agency_bonus))


def get_ranked_league_table() -> Dict[str, Any]:
    """Generate the full ranked league table for Geneva agencies and individual brokers, merging curated agencies and the full 83-agency master dataset."""
    ranked_agencies = []
    all_brokers = []

    # Start with curated GENEVA_AGENCIES_DATA
    combined_agencies = list(GENEVA_AGENCIES_DATA)
    seen_ids = {a["id"] for a in combined_agencies}
    seen_names = {a["name"].lower().strip() for a in combined_agencies}

    # Merge external master dataset if available
    master_file = Path("data/exports/geneva_agencies_master.json")
    if not master_file.exists():
        master_file = Path("C:/Users/AI-Mini-PC/DEV/Real-state-agencies-intelligence/src/data/exports/geneva_agencies_master.json")

    if master_file.exists():
        try:
            with open(master_file, "r", encoding="utf-8") as f:
                ext_agencies = json.load(f)
            for ea in ext_agencies:
                eid = ea.get("id")
                ename = ea.get("name", "").lower().strip()
                if eid not in seen_ids and ename not in seen_names:
                    combined_agencies.append(ea)
                    seen_ids.add(eid)
                    seen_names.add(ename)
        except Exception as e:
            logger.warning("Could not merge master agencies JSON: %s", e)

    for ag in combined_agencies:
        score = compute_agency_score(ag)
        ag_copy = dict(ag)
        ag_copy["cytria_score"] = score
        ranked_agencies.append(ag_copy)

        for b in ag.get("agents", []):
            b_score = compute_broker_score(b, score)
            b_copy = dict(b)
            b_copy["cytria_score"] = b_score
            b_copy["agency_name"] = ag["name"]
            b_copy["agency_id"] = ag["id"]
            all_brokers.append(b_copy)

    # Sort agencies and brokers descending
    ranked_agencies.sort(key=lambda x: x.get("cytria_score", 0), reverse=True)
    all_brokers.sort(key=lambda x: x.get("cytria_score", 0), reverse=True)

    # Add ranks
    for i, a in enumerate(ranked_agencies, 1):
        a["rank"] = i
    for i, b in enumerate(all_brokers, 1):
        b["rank"] = i

    return {
        "agencies": ranked_agencies,
        "brokers": all_brokers
    }

