"""Crawler and parser for Geneva real estate agencies and agents from RealAdvisor."""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


def parse_agencies_from_html(html_content: str) -> List[Dict[str, Any]]:
    """Parse agencies and agents from RealAdvisor canton/locality HTML page."""
    agencies: List[Dict[str, Any]] = []

    # 1. Look for agency-locality-schema
    match = re.search(r'<script[^>]*id=["\']agency-locality-schema["\'][^>]*>(.*?)</script>', html_content, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1).strip())
            # Usually a list containing ItemList or direct ItemList
            item_list = None
            if isinstance(data, list):
                for item in data:
                    if item.get("@type") == "ItemList":
                        item_list = item
                        break
            elif isinstance(data, dict) and data.get("@type") == "ItemList":
                item_list = data

            if item_list and "itemListElement" in item_list:
                for elem in item_list["itemListElement"]:
                    org = elem.get("item", {})
                    if org.get("@type") == "Organization":
                        employees = []
                        for emp in org.get("employee", []):
                            employees.append({
                                "name": emp.get("name"),
                                "address": emp.get("address"),
                                "image": emp.get("image"),
                                "url": emp.get("url")
                            })

                        rating_info = org.get("aggregateRating", {})
                        agency = {
                            "name": org.get("name"),
                            "url": org.get("url"),
                            "address": org.get("address"),
                            "image": org.get("image"),
                            "rating": rating_info.get("ratingValue"),
                            "reviews_count": rating_info.get("reviewCount", 0),
                            "employees": employees
                        }
                        agencies.append(agency)
        except Exception as e:
            logger.error(f"Error parsing agency-locality-schema: {e}")

    # 2. Extract recent verified reviews with agent & agency details
    review_cards_pattern = re.findall(
        r'<div class="font-bold text-base line-clamp-1">([^<]+?)\s*\(([^<]+?)\)</div>\s*<div class="text-sm font-medium text-gray-500">Noté par ([^<]+?)\s*\((Vendeur|Acheteur)\s+en\s+([^<]+?)\)</div>',
        html_content
    )
    
    recent_reviews = []
    for agent_name, agency_name, reviewer, role, location in review_cards_pattern:
        recent_reviews.append({
            "agent_name": agent_name.strip(),
            "agency_name": agency_name.strip(),
            "reviewer": reviewer.strip(),
            "role": role.strip(),
            "commune": location.strip()
        })

    return {
        "agencies": agencies,
        "recent_reviews": recent_reviews
    }


def parse_agency_detail_from_html(html_content: str) -> Dict[str, Any]:
    """Parse deep agency metrics (sold stats, median price, active listings) from agency detail HTML."""
    detail = {}

    # Extract JSON-LD Agency schema
    match = re.search(r'<script[^>]*id=["\']Agency-detail-page-schema["\'][^>]*>(.*?)</script>', html_content, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1).strip())
            if isinstance(data, list) and data:
                data = data[0]
            detail["name"] = data.get("name")
            detail["address"] = data.get("address")
            detail["url"] = data.get("url")
            detail["image"] = data.get("image")
            detail["employees"] = data.get("employee", [])
            detail["reviews"] = data.get("review", [])
            rating = data.get("aggregateRating", {})
            detail["rating"] = rating.get("ratingValue")
            detail["reviews_count"] = rating.get("reviewCount", 0)
        except Exception as e:
            logger.error(f"Error parsing Agency-detail-page-schema: {e}")

    # Extract Sales Statistics (last 24 months)
    # e.g.: In the last 24 months ... sold 16 properties with a median sale price of CHF 2.4M
    sales_stat_match = re.search(
        r'sold\s+([0-9]+)\s+properties\s+with\s+a\s+median\s+sale\s+price\s+of\s+CHF\s*([0-9\.]+[M|k]?)',
        html_content,
        re.IGNORECASE
    )
    if not sales_stat_match:
        # Check french version: Au cours des 24 derniers mois ... a vendu X biens avec un prix de vente médian de CHF ...
        sales_stat_match = re.search(
            r'vendu\s+([0-9]+)\s+biens\s+avec\s+un\s+prix\s+de\s+vente\s+m[eé]dian\s+de\s+CHF\s*([0-9\.]+[M|k]?)',
            html_content,
            re.IGNORECASE
        )

    if sales_stat_match:
        detail["sold_24m_count"] = int(sales_stat_match.group(1))
        detail["median_price_raw"] = sales_stat_match.group(2)
    else:
        detail["sold_24m_count"] = 0
        detail["median_price_raw"] = None

    # Breakdown houses vs apartments
    house_count_match = re.search(r'House.*?(\d+)</div>', html_content, re.DOTALL)
    if not house_count_match:
        house_count_match = re.search(r'Maison.*?(\d+)</div>', html_content, re.DOTALL)
    detail["sold_houses"] = int(house_count_match.group(1)) if house_count_match else 0

    apt_count_match = re.search(r'Apartment.*?(\d+)</div>', html_content, re.DOTALL)
    if not apt_count_match:
        apt_count_match = re.search(r'Appartement.*?(\d+)</div>', html_content, re.DOTALL)
    detail["sold_apartments"] = int(apt_count_match.group(1)) if apt_count_match else 0

    return detail
