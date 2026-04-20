"""
Arizona Chimney Pros — Schema.org JSON-LD Builder
==================================================
Turns a CSV row + Claude-generated content into a JSON-LD @graph that
WordPress can inject into the page <head>.

Why this matters:
  - LocalBusiness schema unlocks Google's Local Pack eligibility
  - FAQPage schema gets FAQ snippets in search results
  - Service schema with areaServed targets local intent
  - Offer schema with priceRange shows "$" signal in SERP

Output is a single JSON string that goes into the schema_json ACF field.
WordPress just dumps it inside <script type="application/ld+json"> tags.

USAGE (from generate.py):
  from schema_builder import build_page_schema
  content["schema_json"] = build_page_schema(row, content)
"""

import json
import re

# ─────────────────────────────────────────────
# BUSINESS INFO — EDIT THESE WITH REAL DATA
# ─────────────────────────────────────────────
# These values appear in every page's LocalBusiness schema. Getting them
# right matters more than 1000 pages of content — inaccurate NAP (Name,
# Address, Phone) data is a major local-SEO ranking penalty.

BUSINESS = {
    "name":        "Arizona Chimney Pros",
    "url":         "https://arizonachimneypros.com",
    "logo":        "https://arizonachimneypros.com/wp-content/uploads/logo.png",
    "telephone":   "+1-602-000-0000",           # TODO: replace with real
    "email":       "info@arizonachimneypros.com",  # TODO: replace with real
    "priceRange":  "$$",
    "image":       "https://arizonachimneypros.com/wp-content/uploads/truck.jpg",
    "address": {
        "streetAddress":   "TBD",               # TODO: real street
        "addressLocality": "Phoenix",
        "addressRegion":   "AZ",
        "postalCode":      "85001",             # TODO: real zip
        "addressCountry":  "US",
    },
    # Phoenix metro bounding box — adjust to actual service radius
    "geo": {
        "latitude":  33.4484,
        "longitude": -112.0740,
    },
    "serviceRadius_km": 80,  # ~50 miles covers Phoenix metro + suburbs
    "openingHours": [
        "Mo-Fr 07:00-18:00",
        "Sa 08:00-14:00",
    ],
    "sameAs": [
        # Social profiles — fill in as you get them
        # "https://www.facebook.com/arizonachimneypros",
        # "https://www.google.com/maps/place/?q=place_id:...",
    ],
    "founded": 2015,
    "licensed": True,
    "insured":  True,
}


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _business_id() -> str:
    """Stable @id for the LocalBusiness node (referenced across @graph)."""
    return f"{BUSINESS['url']}/#business"


def _parse_price_range(raw: str) -> dict | None:
    """Turn a CSV price_range like '$180-$450' into a LowPrice/HighPrice dict
    for Offer schema. Returns None if unparseable (e.g. '$$')."""
    if not raw:
        return None
    # Strip $ and commas, find two numbers
    numbers = re.findall(r"[\d,]+", raw)
    if len(numbers) < 2:
        return None
    try:
        low  = int(numbers[0].replace(",", ""))
        high = int(numbers[1].replace(",", ""))
        return {"lowPrice": low, "highPrice": high, "priceCurrency": "USD"}
    except ValueError:
        return None


def _strip_html(text: str) -> str:
    """Remove HTML tags for schema text (Google wants plain text)."""
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text).strip()


def _page_url(slug: str) -> str:
    return f"{BUSINESS['url']}/{slug}/"


# ─────────────────────────────────────────────
# Schema node builders
# ─────────────────────────────────────────────

def _collect_reviews(content: dict) -> list[dict]:
    """Extract review_1..3 fields from content into a structured list.

    Returns rows where BOTH author and text are present; missing fields
    are silently dropped (union-schema CSV behavior).
    """
    reviews = []
    for i in range(1, 4):
        author = content.get(f"review_{i}_author") or ""
        text   = content.get(f"review_{i}_text") or ""
        if not (author and text):
            continue
        try:
            rating = int(content.get(f"review_{i}_rating") or 5)
        except (TypeError, ValueError):
            rating = 5
        reviews.append({
            "author": author.strip(),
            "text":   _strip_html(text).strip(),
            "city":   (content.get(f"review_{i}_city") or "").strip(),
            "rating": max(1, min(5, rating)),
        })
    return reviews


def build_business_node(content: dict | None = None) -> dict:
    """Reusable LocalBusiness node — referenced by @id from other schemas.

    When content is provided and contains review_1..3 data, attaches
    AggregateRating so the business earns review stars in rich results.
    """
    node = {
        "@type":       "LocalBusiness",
        "@id":         _business_id(),
        "name":        BUSINESS["name"],
        "url":         BUSINESS["url"],
        "telephone":   BUSINESS["telephone"],
        "email":       BUSINESS["email"],
        "priceRange":  BUSINESS["priceRange"],
        "image":       BUSINESS["image"],
        "logo":        BUSINESS["logo"],
        "address": {
            "@type": "PostalAddress",
            **BUSINESS["address"],
        },
        "geo": {
            "@type":     "GeoCoordinates",
            "latitude":  BUSINESS["geo"]["latitude"],
            "longitude": BUSINESS["geo"]["longitude"],
        },
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "description": h}
            for h in BUSINESS["openingHours"]
        ],
        "areaServed": {
            "@type":       "GeoCircle",
            "geoMidpoint": {
                "@type":     "GeoCoordinates",
                "latitude":  BUSINESS["geo"]["latitude"],
                "longitude": BUSINESS["geo"]["longitude"],
            },
            "geoRadius": BUSINESS["serviceRadius_km"] * 1000,  # meters
        },
    }
    if BUSINESS["sameAs"]:
        node["sameAs"] = BUSINESS["sameAs"]

    if content is not None:
        reviews = _collect_reviews(content)
        if reviews:
            avg = sum(r["rating"] for r in reviews) / len(reviews)
            node["aggregateRating"] = {
                "@type":       "AggregateRating",
                "ratingValue": round(avg, 1),
                "bestRating":  5,
                "worstRating": 1,
                "reviewCount": len(reviews),
            }
    return node


def build_review_nodes(content: dict) -> list[dict]:
    """Build standalone Review nodes referencing the LocalBusiness.

    Separate from AggregateRating so both appear in @graph — Google uses
    AggregateRating for star display and individual Reviews for snippet
    context.
    """
    nodes = []
    for rv in _collect_reviews(content):
        node = {
            "@type":  "Review",
            "itemReviewed": {"@id": _business_id()},
            "reviewRating": {
                "@type":       "Rating",
                "ratingValue": rv["rating"],
                "bestRating":  5,
                "worstRating": 1,
            },
            "author": {"@type": "Person", "name": rv["author"]},
            "reviewBody": rv["text"],
        }
        if rv["city"]:
            node["publisher"] = {
                "@type": "Place",
                "name":  f"{rv['city']}, AZ",
            }
        nodes.append(node)
    return nodes


def build_service_node(row: dict, content: dict) -> dict:
    """Service schema — one per page, scoped to city + service combo."""
    city    = row.get("city") or "Arizona"
    state   = row.get("state") or "Arizona"
    service = row.get("service") or "Fireplace Services"
    slug    = row.get("slug", "")

    node = {
        "@type":       "Service",
        "@id":         _page_url(slug) + "#service",
        "name":        f"{service} in {city}, {state}",
        "serviceType": service,
        "provider":    {"@id": _business_id()},
        "areaServed": {
            "@type": "City" if city != state else "State",
            "name":  city,
            "containedInPlace": {
                "@type": "State",
                "name":  state,
            },
        },
        "description": _strip_html(content.get("intro", "")).split(".")[0][:250],
    }

    price = _parse_price_range(row.get("price_range", ""))
    if price:
        node["offers"] = {
            "@type":         "AggregateOffer",
            "priceCurrency": price["priceCurrency"],
            "lowPrice":      price["lowPrice"],
            "highPrice":     price["highPrice"],
            "availability":  "https://schema.org/InStock",
        }

    return node


def build_faq_node(content: dict) -> dict | None:
    """FAQPage schema from up to 6 Q&A pairs. Returns None if no FAQs."""
    questions = []
    for i in range(1, 7):
        q = _strip_html(content.get(f"faq_{i}_q", ""))
        a = _strip_html(content.get(f"faq_{i}_a", ""))
        if q and a:
            questions.append({
                "@type":          "Question",
                "name":           q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            })
    if not questions:
        return None
    return {
        "@type":      "FAQPage",
        "mainEntity": questions,
    }


def build_breadcrumb_node(row: dict) -> dict:
    """BreadcrumbList for navigational hierarchy — helps Google understand
    where this page fits in the site architecture."""
    service = row.get("service", "Services")
    city    = row.get("city", "")
    slug    = row.get("slug", "")

    items = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": BUSINESS["url"]},
        {"@type": "ListItem", "position": 2, "name": service, "item": f"{BUSINESS['url']}/services/"},
    ]
    if city:
        items.append({
            "@type": "ListItem", "position": 3,
            "name":  f"{service} in {city}",
            "item":  _page_url(slug),
        })
    return {
        "@type":           "BreadcrumbList",
        "itemListElement": items,
    }


def build_webpage_node(row: dict, content: dict) -> dict:
    """WebPage schema — ties everything together for this specific URL."""
    slug = row.get("slug", "")
    return {
        "@type":       "WebPage",
        "@id":         _page_url(slug),
        "url":         _page_url(slug),
        "name":        content.get("meta_title") or content.get("title", ""),
        "description": content.get("meta_description", ""),
        "isPartOf":    {"@id": f"{BUSINESS['url']}/#website"},
        "about":       {"@id": _business_id()},
    }


# ─────────────────────────────────────────────
# Top-level builder
# ─────────────────────────────────────────────

def build_page_schema(row: dict, content: dict) -> str:
    """Compose the full @graph for a page and return a JSON string.

    The @graph pattern is preferred by Google because it deduplicates
    shared entities (LocalBusiness) across multiple schema types.
    """
    graph = [
        build_webpage_node(row, content),
        build_business_node(content),   # attaches aggregateRating if reviews exist
        build_service_node(row, content),
        build_breadcrumb_node(row),
    ]

    faq = build_faq_node(content)
    if faq:
        graph.append(faq)

    graph.extend(build_review_nodes(content))

    schema = {
        "@context": "https://schema.org",
        "@graph":   graph,
    }

    # Compact JSON — WP page size matters for Core Web Vitals.
    # ensure_ascii=False keeps human-readable characters for non-ASCII
    # city names (though we have none in AZ) but still escapes </script>.
    return json.dumps(schema, ensure_ascii=False, separators=(",", ":"))


# ─────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────
if __name__ == "__main__":
    fake_row = {
        "slug":        "gas-fireplace-repair-phoenix",
        "city":        "Phoenix",
        "state":       "Arizona",
        "service":     "Gas Fireplace Repair",
        "price_range": "$180-$450",
    }
    fake_content = {
        "title":            "Gas Fireplace Repair in Phoenix, AZ",
        "meta_title":       "Gas Fireplace Repair Phoenix | Same Day",
        "meta_description": "Fast local gas fireplace repair in Phoenix.",
        "intro":            "When your gas fireplace won't light in Phoenix, it's usually a clogged pilot or a weak thermocouple. We diagnose and fix it same-day.",
        "faq_1_q":          "Is it safe to use my fireplace if the pilot won't stay on?",
        "faq_1_a":          "No. A pilot that keeps dropping out usually means the thermocouple or thermopile is failing. Shut off the gas and call a pro.",
        "faq_2_q":          "How much does gas fireplace repair cost in Phoenix?",
        "faq_2_a":          "Typical repairs run $180-$450 in Phoenix depending on the part.",
    }
    schema_str = build_page_schema(fake_row, fake_content)
    print(f"Schema size: {len(schema_str)} bytes")
    # Pretty-print for inspection
    schema = json.loads(schema_str)
    print(json.dumps(schema, indent=2, ensure_ascii=False))
