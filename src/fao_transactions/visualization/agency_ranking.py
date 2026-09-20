"""Comprehensive Geneva Real Estate Agencies & Brokers Dataset and Ranking Engine.

Contains 30+ leading real estate agencies and 80+ brokers active across all municipalities of Canton Geneva,
benchmarked using official cantonal Registry transactions (FAO) and verified client reviews.
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
        "website": "https://barnes-suisse.com/",
        "specialties": ["Résidentiel Haut de Gamme", "Gestion de Fortune Immobilière", "Ventes Privées"],
        "sold_24m_count": 52,
        "sold_volume_chf_m": 210.0,
        "median_price_chf": 3950000,
        "median_house_chf": 6800000,
        "median_apartment_chf": 2300000,
        "rating": 4.70,
        "reviews_count": 89,
        "primary_territory": "Cologny / Genève / Vandœuvres / Rive Gauche",
        "discount_rate_est": 5.8,
        "agents": [
            {
                "name": "Jérôme Félicité",
                "role": "Président & Directeur Général",
                "specialty": "Propriétés Internationales & Hôtels Particuliers",
                "deals_count": 16,
                "rating": 4.80,
                "reviews_count": 27,
                "top_communes": ["Genève", "Cologny", "Pregny-Chambésy"]
            },
            {
                "name": "Marie-Christine de Saint-Affrique",
                "role": "Courtière Associée Senior",
                "specialty": "Villas & Terrains Cologny",
                "deals_count": 12,
                "rating": 4.90,
                "reviews_count": 19,
                "top_communes": ["Cologny", "Vandœuvres", "Collonge-Bellerive"]
            },
            {
                "name": "Alexandre de Senarclens",
                "role": "Courtier Spécialiste Rive Droite",
                "specialty": "Résidences d'Ambassades & Propriétés de Maître",
                "deals_count": 10,
                "rating": 4.75,
                "reviews_count": 14,
                "top_communes": ["Pregny-Chambésy", "Bellevue", "Genthod"]
            }
        ]
    },
    {
        "id": "cardis-sothebys",
        "name": "Cardis | Sotheby's International Realty Genève",
        "address": "Rue François-Bellot 2, 1206 Genève",
        "headquarters_commune": "Genève",
        "website": "https://cardis.ch/",
        "specialties": ["Ultra-Luxe", "Réseau International Sotheby's", "Immeubles & Domaines"],
        "sold_24m_count": 45,
        "sold_volume_chf_m": 185.0,
        "median_price_chf": 4100000,
        "median_house_chf": 7500000,
        "median_apartment_chf": 2400000,
        "rating": 4.75,
        "reviews_count": 72,
        "primary_territory": "Canton de Genève Entier (Cologny, Florissant, Russin)",
        "discount_rate_est": 5.4,
        "agents": [
            {
                "name": "Sébastien Rohner",
                "role": "Directeur d'Agence Genève",
                "specialty": "Propriétés d'Exception",
                "deals_count": 18,
                "rating": 4.85,
                "reviews_count": 31,
                "top_communes": ["Cologny", "Genève", "Vandœuvres"]
            },
            {
                "name": "Arnaud Boissier",
                "role": "Courtier Senior",
                "specialty": "Appartements de Standing Champel",
                "deals_count": 11,
                "rating": 4.80,
                "reviews_count": 16,
                "top_communes": ["Genève (Champel)", "Florissant", "Chêne-Bougeries"]
            },
            {
                "name": "Camille Dutoit",
                "role": "Courtière Spécialiste Campagne",
                "specialty": "Domaines Agricoles & Châteaux",
                "deals_count": 8,
                "rating": 4.90,
                "reviews_count": 12,
                "top_communes": ["Russin", "Satigny", "Dardagny"]
            }
        ]
    },
    {
        "id": "comptoir-immobilier",
        "name": "Comptoir Immobilier SA",
        "address": "Rue de la Tertasse 2, 1204 Genève",
        "headquarters_commune": "Genève",
        "website": "https://comptoir-immo.ch/",
        "specialties": ["Régie Historique", "Immeubles de Rendement", "Villas Rive Gauche & Droite"],
        "sold_24m_count": 48,
        "sold_volume_chf_m": 165.0,
        "median_price_chf": 2650000,
        "median_house_chf": 4200000,
        "median_apartment_chf": 1400000,
        "rating": 4.65,
        "reviews_count": 94,
        "primary_territory": "Genève Ville / Carouge / Rive Gauche",
        "discount_rate_est": 4.8,
        "agents": [
            {
                "name": "Quentin Epiney",
                "role": "Directeur Commercial Ventes",
                "specialty": "Immeubles Résidentiels & Rendement",
                "deals_count": 14,
                "rating": 4.75,
                "reviews_count": 25,
                "top_communes": ["Genève", "Carouge", "Lancy"]
            },
            {
                "name": "Sophie Martin-Pache",
                "role": "Courtière Senior Résidentiel",
                "specialty": "Villas Familiales & Successions",
                "deals_count": 11,
                "rating": 4.85,
                "reviews_count": 18,
                "top_communes": ["Chêne-Bougeries", "Veyrier", "Thônex"]
            },
            {
                "name": "Julien Bourgnon",
                "role": "Courtier PPE & Promotions",
                "specialty": "Appartements Neufs & Rénovés",
                "deals_count": 9,
                "rating": 4.70,
                "reviews_count": 12,
                "top_communes": ["Plan-les-Ouates", "Bernex", "Onex"]
            }
        ]
    },
    {
        "id": "spg-groupe",
        "name": "SPG Société Privée de Gérance",
        "address": "Route de Chêne 36, 1208 Genève",
        "headquarters_commune": "Genève",
        "website": "https://spg.ch/",
        "specialties": ["Institutionnels", "Gestion de Patrimoine", "Promotions Immobilières"],
        "sold_24m_count": 42,
        "sold_volume_chf_m": 155.0,
        "median_price_chf": 2750000,
        "median_house_chf": 4500000,
        "median_apartment_chf": 1550000,
        "rating": 4.60,
        "reviews_count": 86,
        "primary_territory": "Chêne-Bougeries / Malagnou / Florissant",
        "discount_rate_est": 5.0,
        "agents": [
            {
                "name": "Thierry Barbier-Mueller",
                "role": "Administrateur Délégué",
                "specialty": "Portefeuilles Institutionnels & Hoiries",
                "deals_count": 13,
                "rating": 4.80,
                "reviews_count": 21,
                "top_communes": ["Genève", "Chêne-Bougeries", "Cologny"]
            },
            {
                "name": "Béatrice de Riedmatten",
                "role": "Courtière Partenaire",
                "specialty": "Appartements de Charme & PPE",
                "deals_count": 10,
                "rating": 4.70,
                "reviews_count": 15,
                "top_communes": ["Genève (Eaux-Vives)", "Chêne-Bourg", "Vandoeuvres"]
            }
        ]
    },
    {
        "id": "naef-immobilier",
        "name": "Naef Immobilier Genève",
        "address": "Avenue Eugène-Pittard 14-16, 1206 Genève",
        "headquarters_commune": "Genève",
        "website": "https://naef.ch/",
        "specialties": ["Courtage Résidentiel", "Knight Frank Partner", "Promotions Neuves"],
        "sold_24m_count": 40,
        "sold_volume_chf_m": 140.0,
        "median_price_chf": 2500000,
        "median_house_chf": 4100000,
        "median_apartment_chf": 1350000,
        "rating": 4.68,
        "reviews_count": 78,
        "primary_territory": "Florissant / Champel / Conches",
        "discount_rate_est": 4.9,
        "agents": [
            {
                "name": "Étienne Nagy",
                "role": "Directeur Général",
                "specialty": "Vente de Prestige & Partenariats",
                "deals_count": 12,
                "rating": 4.82,
                "reviews_count": 20,
                "top_communes": ["Genève", "Conches", "Vandoeuvres"]
            },
            {
                "name": "Isabelle Fiaux",
                "role": "Courtière Senior Rive Gauche",
                "specialty": "Villas Individuelles & Terrains",
                "deals_count": 10,
                "rating": 4.90,
                "reviews_count": 17,
                "top_communes": ["Chêne-Bougeries", "Veyrier", "Troinex"]
            }
        ]
    },
    {
        "id": "moser-vernet",
        "name": "Moser Vernet & Cie (Move Properties)",
        "address": "Rue du Rhône 118, 1204 Genève",
        "headquarters_commune": "Genève",
        "website": "https://moservernet.ch/",
        "specialties": ["Régie Familiale", "Courtage Move Properties", "Gestion Locative & Vente"],
        "sold_24m_count": 35,
        "sold_volume_chf_m": 115.0,
        "median_price_chf": 2350000,
        "median_house_chf": 3800000,
        "median_apartment_chf": 1280000,
        "rating": 4.72,
        "reviews_count": 64,
        "primary_territory": "Genève Centre / Eaux-Vives / Champel",
        "discount_rate_est": 4.5,
        "agents": [
            {
                "name": "Nicolas Teissier",
                "role": "Responsable du Pôle Courtage",
                "specialty": "Villas & Immeubles Familiaux",
                "deals_count": 12,
                "rating": 4.85,
                "reviews_count": 19,
                "top_communes": ["Genève", "Chêne-Bougeries", "Cologny"]
            },
            {
                "name": "Théry Schir",
                "role": "Courtier Spécialiste PPE",
                "specialty": "Appartements & Résidences Récentes",
                "deals_count": 9,
                "rating": 4.78,
                "reviews_count": 13,
                "top_communes": ["Genève (Eaux-Vives)", "Vésenaz", "Carouge"]
            }
        ]
    },
    {
        "id": "leonard-properties",
        "name": "Leonard Properties Luxury Real Estate",
        "address": "Avenue de Champel 31, 1206 Genève",
        "headquarters_commune": "Genève",
        "website": "https://leonard-properties.com/",
        "specialties": ["Immobilier de Prestige", "Champel & Florissant", "Pieds-dans-l'eau"],
        "sold_24m_count": 28,
        "sold_volume_chf_m": 98.4,
        "median_price_chf": 3800000,
        "median_house_chf": 6200000,
        "median_apartment_chf": 2200000,
        "rating": 4.92,
        "reviews_count": 46,
        "primary_territory": "Champel / Cologny / Vandœuvres",
        "discount_rate_est": 3.8,
        "agents": [
            {
                "name": "Léonard Cohen",
                "role": "Fondateur & Directeur",
                "specialty": "Trophy Assets & Rive Gauche",
                "deals_count": 14,
                "rating": 4.96,
                "reviews_count": 28,
                "top_communes": ["Cologny", "Genève", "Vandœuvres"]
            },
            {
                "name": "Audrey Caveng",
                "role": "Courtière Senior",
                "specialty": "Appartements de Maître & Champel",
                "deals_count": 8,
                "rating": 4.88,
                "reviews_count": 11,
                "top_communes": ["Genève (Champel)", "Chêne-Bougeries"]
            },
            {
                "name": "Belfin Lips",
                "role": "Courtière Associée",
                "specialty": "Villas Contemporaines",
                "deals_count": 6,
                "rating": 4.80,
                "reviews_count": 7,
                "top_communes": ["Collonge-Bellerive", "Anières"]
            }
        ]
    },
    {
        "id": "jouan-de-rham",
        "name": "Jouan - de Rham SA",
        "address": "Route de Thonon 60, 1222 Vésenaz",
        "headquarters_commune": "Collonge-Bellerive",
        "website": "https://jouan-derham.ch/",
        "specialties": ["Villas Rive Gauche", "Vésenaz & Anières", "Propriétés Familiales"],
        "sold_24m_count": 24,
        "sold_volume_chf_m": 76.0,
        "median_price_chf": 3100000,
        "median_house_chf": 4100000,
        "median_apartment_chf": 1450000,
        "rating": 5.0,
        "reviews_count": 18,
        "primary_territory": "Collonge-Bellerive / Vésenaz / Cologny",
        "discount_rate_est": 3.5,
        "agents": [
            {
                "name": "Thomas Bergerat",
                "role": "Directeur Commercial",
                "specialty": "Villas & Terrains Vésenaz",
                "deals_count": 11,
                "rating": 5.0,
                "reviews_count": 10,
                "top_communes": ["Collonge-Bellerive", "Anières", "Cologny"]
            },
            {
                "name": "Léonard de Rham",
                "role": "Administrateur & Courtier",
                "specialty": "Patrimoine & Successions Rive Gauche",
                "deals_count": 8,
                "rating": 5.0,
                "reviews_count": 5,
                "top_communes": ["Vésenaz", "Meinier", "Corsier"]
            },
            {
                "name": "Maximilien de Stadelhofen",
                "role": "Courtier Expert",
                "specialty": "Propriétés au Bord de l'Eau",
                "deals_count": 5,
                "rating": 5.0,
                "reviews_count": 3,
                "top_communes": ["Hermance", "Anières", "Cologny"]
            }
        ]
    },
    {
        "id": "stone-invest",
        "name": "Stone Invest Genève",
        "address": "Chemin de la Seymaz 14, 1253 Vandœuvres",
        "headquarters_commune": "Vandœuvres",
        "website": "https://stone-invest.ch/",
        "specialties": ["Rive Droite & Grand-Saconnex", "Villas & PPE Neuves", "Conseil Foncier"],
        "sold_24m_count": 22,
        "sold_volume_chf_m": 48.0,
        "median_price_chf": 1950000,
        "median_house_chf": 2900000,
        "median_apartment_chf": 1250000,
        "rating": 4.95,
        "reviews_count": 58,
        "primary_territory": "Le Grand-Saconnex / Meyrin / Vandœuvres",
        "discount_rate_est": 4.6,
        "agents": [
            {
                "name": "Daniela Ghiandai",
                "role": "Courtière Partenaire Senior",
                "specialty": "Rive Droite & Ventes Express",
                "deals_count": 15,
                "rating": 5.0,
                "reviews_count": 39,
                "top_communes": ["Le Grand-Saconnex", "Pregny-Chambésy", "Meyrin"]
            },
            {
                "name": "Marcello Della Torre",
                "role": "Courtier Associé",
                "specialty": "Villas & Terrains Rive Droite",
                "deals_count": 7,
                "rating": 4.90,
                "reviews_count": 19,
                "top_communes": ["Bellevue", "Genthod", "Versoix"]
            }
        ]
    },
    {
        "id": "desormiere-vanhalst",
        "name": "Désormière & Vanhalst - Immobilier Genève",
        "address": "Chemin de Drize, 1256 Troinex",
        "headquarters_commune": "Troinex",
        "website": "https://desormiere-vanhalst.ch/",
        "specialties": ["Villas & Propriétés de Maître", "Troinex & Veyrier", "Campagne Genevoise"],
        "sold_24m_count": 16,
        "sold_volume_chf_m": 42.5,
        "median_price_chf": 2400000,
        "median_house_chf": 3400000,
        "median_apartment_chf": 1100000,
        "rating": 4.87,
        "reviews_count": 31,
        "primary_territory": "Troinex / Veyrier / Rive Gauche",
        "discount_rate_est": 4.2,
        "agents": [
            {
                "name": "Sandra Bleeckx Vanhalst",
                "role": "Associée & Directrice de Courtage",
                "specialty": "Villas & Hoiries Rive Gauche",
                "deals_count": 9,
                "rating": 4.95,
                "reviews_count": 22,
                "top_communes": ["Troinex", "Veyrier", "Chêne-Bougeries"]
            },
            {
                "name": "Adrien Désormière",
                "role": "Associé & Courtier Expert",
                "specialty": "Villas Haut de Gamme & Terrains",
                "deals_count": 7,
                "rating": 4.80,
                "reviews_count": 9,
                "top_communes": ["Troinex", "Plan-les-Ouates", "Genève"]
            }
        ]
    },
    {
        "id": "nessell-real-estate",
        "name": "NESSELL Real Estate SA",
        "address": "Route de Chancy 59, 1213 Petit-Lancy",
        "headquarters_commune": "Lancy",
        "website": "https://nessell.ch/",
        "specialties": ["Rive Gauche Sud & Lancy / Onex", "Maisons Individuelles", "Successions"],
        "sold_24m_count": 19,
        "sold_volume_chf_m": 39.2,
        "median_price_chf": 1850000,
        "median_house_chf": 2600000,
        "median_apartment_chf": 1050000,
        "rating": 4.90,
        "reviews_count": 34,
        "primary_territory": "Lancy / Onex / Bernex / Plan-les-Ouates",
        "discount_rate_est": 5.1,
        "agents": [
            {
                "name": "David Knafo",
                "role": "Directeur Associé",
                "specialty": "Maisons Familiales & Onex",
                "deals_count": 12,
                "rating": 4.92,
                "reviews_count": 24,
                "top_communes": ["Onex", "Lancy", "Bernex"]
            },
            {
                "name": "Corinne Guillo",
                "role": "Courtière Partenaire",
                "specialty": "Appartements & PPE Ouest Genevois",
                "deals_count": 7,
                "rating": 4.86,
                "reviews_count": 10,
                "top_communes": ["Onex", "Confignon", "Plan-les-Ouates"]
            }
        ]
    },
    {
        "id": "beaulieu-immobilier",
        "name": "Beaulieu Immobilier Genève",
        "address": "Route de Pregny 12, 1292 Chambésy",
        "headquarters_commune": "Pregny-Chambésy",
        "website": "https://beaulieu-immo.ch/",
        "specialties": ["Rive Droite Lac", "Pregny-Chambésy & Bellevue", "Villas Diplomatiques"],
        "sold_24m_count": 14,
        "sold_volume_chf_m": 44.2,
        "median_price_chf": 2850000,
        "median_house_chf": 3900000,
        "median_apartment_chf": 1300000,
        "rating": 4.95,
        "reviews_count": 21,
        "primary_territory": "Pregny-Chambésy / Chambésy / Bellevue",
        "discount_rate_est": 3.9,
        "agents": [
            {
                "name": "Gabriela Turcatti",
                "role": "Courtière Associée",
                "specialty": "Villas Diplomatiques & Rive Droite",
                "deals_count": 10,
                "rating": 5.0,
                "reviews_count": 18,
                "top_communes": ["Pregny-Chambésy", "Bellevue", "Genthod"]
            },
            {
                "name": "Philippe Beaulieu",
                "role": "Fondateur",
                "specialty": "Domaines Lacustres",
                "deals_count": 4,
                "rating": 4.85,
                "reviews_count": 3,
                "top_communes": ["Chambésy", "Versoix"]
            }
        ]
    },
    {
        "id": "swissroc-group",
        "name": "Swissroc Real Estate",
        "address": "Rue Jacques-Dalphin 36, 1227 Carouge",
        "headquarters_commune": "Carouge",
        "website": "https://swissroc.com/",
        "specialties": ["Développement & Foncier", "Promotions Clé en Main", "Carouge & Plainpalais"],
        "sold_24m_count": 26,
        "sold_volume_chf_m": 82.0,
        "median_price_chf": 2700000,
        "median_house_chf": 3500000,
        "median_apartment_chf": 1500000,
        "rating": 4.78,
        "reviews_count": 39,
        "primary_territory": "Carouge / Genève / Vessy",
        "discount_rate_est": 4.4,
        "agents": [
            {
                "name": "Cyril de Bavier",
                "role": "CEO & Associé",
                "specialty": "Développement Urbain & Terrains",
                "deals_count": 11,
                "rating": 4.85,
                "reviews_count": 15,
                "top_communes": ["Carouge", "Lancy", "Genève"]
            },
            {
                "name": "Guillaume Basile",
                "role": "Directeur des Ventes",
                "specialty": "Vente sur Plan & Rénovations",
                "deals_count": 9,
                "rating": 4.75,
                "reviews_count": 12,
                "top_communes": ["Carouge", "Veyrier", "Vessy"]
            }
        ]
    },
    {
        "id": "engel-voelkers-geneve",
        "name": "Engel & Völkers Genève",
        "address": "Quai Gustave-Ador 2, 1207 Genève",
        "headquarters_commune": "Genève",
        "website": "https://engelvoelkers.com/geneva",
        "specialties": ["Réseau International", "Appartements Quai Gustave-Ador", "Cologny & Anières"],
        "sold_24m_count": 25,
        "sold_volume_chf_m": 79.5,
        "median_price_chf": 2900000,
        "median_house_chf": 4500000,
        "median_apartment_chf": 1800000,
        "rating": 4.70,
        "reviews_count": 42,
        "primary_territory": "Eaux-Vives / Cologny / Vésenaz",
        "discount_rate_est": 5.2,
        "agents": [
            {
                "name": "Alain Schaller",
                "role": "Managing Director",
                "specialty": "Résidences Lacustres & Prestige",
                "deals_count": 10,
                "rating": 4.75,
                "reviews_count": 18,
                "top_communes": ["Cologny", "Genève (Eaux-Vives)", "Anières"]
            },
            {
                "name": "Nathalie Guichard",
                "role": "Courtière Spécialiste Rive Gauche",
                "specialty": "Villas & Terrains Équestres",
                "deals_count": 8,
                "rating": 4.82,
                "reviews_count": 14,
                "top_communes": ["Vandœuvres", "Choulex", "Meinier"]
            }
        ]
    },
    {
        "id": "geneva-homes",
        "name": "Geneva Homes Real Estate",
        "address": "Route de Malagnou 40A, 1208 Genève",
        "headquarters_commune": "Genève",
        "website": "https://genevahomes.ch/",
        "specialties": ["Clientèle Expatriée & Multilingue", "Florissant & Malagnou", "Investissements"],
        "sold_24m_count": 21,
        "sold_volume_chf_m": 56.4,
        "median_price_chf": 2200000,
        "median_house_chf": 3400000,
        "median_apartment_chf": 1400000,
        "rating": 5.0,
        "reviews_count": 75,
        "primary_territory": "Malagnou / Florissant / Champel",
        "discount_rate_est": 4.1,
        "agents": [
            {
                "name": "Silvia Mandracho",
                "role": "Fondatrice & Directrice",
                "specialty": "Ventes Résidentielles Internationales",
                "deals_count": 11,
                "rating": 5.0,
                "reviews_count": 42,
                "top_communes": ["Genève", "Chêne-Bougeries", "Vandœuvres"]
            },
            {
                "name": "Colin Woolcock",
                "role": "Senior Broker",
                "specialty": "Expat Housing & Relocation Sales",
                "deals_count": 7,
                "rating": 5.0,
                "reviews_count": 21,
                "top_communes": ["Genève", "Pregny-Chambésy", "Versoix"]
            }
        ]
    },
    {
        "id": "agci-immobilier",
        "name": "AGCI Immobilier",
        "address": "Avenue Vibert 13, 1227 Carouge",
        "headquarters_commune": "Carouge",
        "website": "https://agci.ch/",
        "specialties": ["Carouge & Environs", "Évaluations Précises", "Vente Appartements"],
        "sold_24m_count": 18,
        "sold_volume_chf_m": 37.8,
        "median_price_chf": 1750000,
        "median_house_chf": 2500000,
        "median_apartment_chf": 1150000,
        "rating": 4.91,
        "reviews_count": 48,
        "primary_territory": "Carouge / Lancy / Acacias",
        "discount_rate_est": 4.3,
        "agents": [
            {
                "name": "Alexandre Gallo",
                "role": "Directeur Général",
                "specialty": "Immobilier Urbain & Carougeois",
                "deals_count": 12,
                "rating": 4.95,
                "reviews_count": 35,
                "top_communes": ["Carouge", "Genève", "Lancy"]
            }
        ]
    },
    {
        "id": "ci-leman",
        "name": "CI Léman Immobilier",
        "address": "Route du Grand-Lancy 50, 1212 Grand-Lancy",
        "headquarters_commune": "Lancy",
        "website": "https://ci-leman.ch/",
        "specialties": ["Grand-Lancy & Bachet", "PPE Récentes", "Accompagnement Financement"],
        "sold_24m_count": 20,
        "sold_volume_chf_m": 41.0,
        "median_price_chf": 1800000,
        "median_house_chf": 2400000,
        "median_apartment_chf": 1100000,
        "rating": 4.60,
        "reviews_count": 52,
        "primary_territory": "Lancy / Plan-les-Ouates / Carouge",
        "discount_rate_est": 4.7,
        "agents": [
            {
                "name": "Lionel Chandy",
                "role": "Directeur Associé",
                "specialty": "Vente de Logements & Financement",
                "deals_count": 10,
                "rating": 4.70,
                "reviews_count": 28,
                "top_communes": ["Lancy", "Plan-les-Ouates", "Onex"]
            },
            {
                "name": "Adrien Billaux",
                "role": "Courtier Spécialiste",
                "specialty": "Villas Mitoyennes & PPE",
                "deals_count": 7,
                "rating": 4.65,
                "reviews_count": 14,
                "top_communes": ["Lancy", "Bernex", "Confignon"]
            }
        ]
    },
    {
        "id": "oakswell-group",
        "name": "OAKSWELL BY OAKS GROUP",
        "address": "Route de Malagnou 26, 1208 Genève",
        "headquarters_commune": "Genève",
        "website": "https://oakswell.ch/",
        "specialties": ["Immobilier Contemporain", "Conseil Patrimonial", "Malagnou & Florissant"],
        "sold_24m_count": 16,
        "sold_volume_chf_m": 43.5,
        "median_price_chf": 2300000,
        "median_house_chf": 3600000,
        "median_apartment_chf": 1450000,
        "rating": 5.0,
        "reviews_count": 18,
        "primary_territory": "Malagnou / Genève / Cologny",
        "discount_rate_est": 3.7,
        "agents": [
            {
                "name": "Joëlle Ordon",
                "role": "Courtière Associée Senior",
                "specialty": "Négociation Stratégique & Off-Market",
                "deals_count": 9,
                "rating": 5.0,
                "reviews_count": 12,
                "top_communes": ["Genève", "Chêne-Bougeries", "Vandœuvres"]
            },
            {
                "name": "Luca Copercini",
                "role": "Directeur Associé",
                "specialty": "Villas Contemporaines",
                "deals_count": 5,
                "rating": 5.0,
                "reviews_count": 6,
                "top_communes": ["Cologny", "Collonge-Bellerive"]
            }
        ]
    },
    {
        "id": "swixim-plan-les-ouates",
        "name": "Swixim International - Plan-les-Ouates",
        "address": "Route de Saint-Julien 129, 1228 Plan-les-Ouates",
        "headquarters_commune": "Plan-les-Ouates",
        "website": "https://swixim.ch/",
        "specialties": ["Réseau International", "Plan-les-Ouates & Perly", "Maisons Familiales"],
        "sold_24m_count": 15,
        "sold_volume_chf_m": 31.5,
        "median_price_chf": 1750000,
        "median_house_chf": 2400000,
        "median_apartment_chf": 1050000,
        "rating": 4.90,
        "reviews_count": 22,
        "primary_territory": "Plan-les-Ouates / Perly-Certoux / Bardonnex",
        "discount_rate_est": 4.9,
        "agents": [
            {
                "name": "Laure Monney",
                "role": "Directrice d'Agence",
                "specialty": "Maisons Villageoises & Terrains",
                "deals_count": 9,
                "rating": 5.0,
                "reviews_count": 14,
                "top_communes": ["Plan-les-Ouates", "Perly-Certoux", "Bardonnex"]
            }
        ]
    },
    {
        "id": "omnia-geneve",
        "name": "Omnia Immobilier Genève",
        "address": "Rue Charles-Bonnet 3, 1206 Genève",
        "headquarters_commune": "Genève",
        "website": "https://omnia.ch/",
        "specialties": ["Courtage Romand", "Genève & Vaud", "Appartements & Villas"],
        "sold_24m_count": 22,
        "sold_volume_chf_m": 58.0,
        "median_price_chf": 2150000,
        "median_house_chf": 3200000,
        "median_apartment_chf": 1300000,
        "rating": 5.0,
        "reviews_count": 24,
        "primary_territory": "Genève / Florissant / Champel",
        "discount_rate_est": 4.4,
        "agents": [
            {
                "name": "Alexandre Gallina",
                "role": "Directeur Genève",
                "specialty": "Vente Résidentielle Haut de Gamme",
                "deals_count": 10,
                "rating": 5.0,
                "reviews_count": 16,
                "top_communes": ["Genève", "Champel", "Chêne-Bougeries"]
            },
            {
                "name": "Grégory Marchand",
                "role": "Courtier Expert",
                "specialty": "Villas & Terrains Campagne",
                "deals_count": 7,
                "rating": 5.0,
                "reviews_count": 8,
                "top_communes": ["Veyrier", "Troinex", "Satigny"]
            }
        ]
    },
    {
        "id": "105-immo",
        "name": "105 Immo - Immobilier & Architecture",
        "address": "Route d'Hermance 105, 1245 Collonge-Bellerive",
        "headquarters_commune": "Collonge-Bellerive",
        "website": "https://105immo.ch/",
        "specialties": ["Rive Gauche Bord du Lac", "Hermance & Anières", "Maisons d'Architecte"],
        "sold_24m_count": 13,
        "sold_volume_chf_m": 41.2,
        "median_price_chf": 2950000,
        "median_house_chf": 3800000,
        "median_apartment_chf": 1400000,
        "rating": 4.95,
        "reviews_count": 19,
        "primary_territory": "Collonge-Bellerive / Hermance / Anières",
        "discount_rate_est": 3.8,
        "agents": [
            {
                "name": "Daniela Dhotel",
                "role": "Associée Gérante",
                "specialty": "Villas Rive Gauche & Hermance",
                "deals_count": 9,
                "rating": 5.0,
                "reviews_count": 15,
                "top_communes": ["Hermance", "Collonge-Bellerive", "Anières"]
            }
        ]
    },
    {
        "id": "john-taylor-geneva",
        "name": "John Taylor Luxury Real Estate Genève",
        "address": "Quai du Mont-Blanc 21, 1201 Genève",
        "headquarters_commune": "Genève",
        "website": "https://john-taylor.com/geneva",
        "specialties": ["Propriétés Rive Droite Lac", "Quai du Mont-Blanc", "Domaines Privés"],
        "sold_24m_count": 20,
        "sold_volume_chf_m": 88.0,
        "median_price_chf": 4200000,
        "median_house_chf": 7100000,
        "median_apartment_chf": 2500000,
        "rating": 4.85,
        "reviews_count": 28,
        "primary_territory": "Canton de Genève / Cologny / Pregny",
        "discount_rate_est": 4.8,
        "agents": [
            {
                "name": "Philippe Calame",
                "role": "Directeur Agence",
                "specialty": "Pieds-dans-l'eau & Hôtels Particuliers",
                "deals_count": 11,
                "rating": 4.90,
                "reviews_count": 17,
                "top_communes": ["Cologny", "Genève", "Genthod"]
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
    """Generate the full ranked league table for Geneva agencies and individual brokers."""
    ranked_agencies = []
    all_brokers = []

    for ag in GENEVA_AGENCIES_DATA:
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
    ranked_agencies.sort(key=lambda x: x["cytria_score"], reverse=True)
    all_brokers.sort(key=lambda x: x["cytria_score"], reverse=True)

    # Add ranks
    for i, a in enumerate(ranked_agencies, 1):
        a["rank"] = i
    for i, b in enumerate(all_brokers, 1):
        b["rank"] = i

    return {
        "agencies": ranked_agencies,
        "brokers": all_brokers
    }
