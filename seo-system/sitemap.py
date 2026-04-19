"""
Arizona Chimney Pros — XML Sitemap Generator
=============================================
Reads pages-generated.csv and emits a valid XML sitemap for Google / Bing.

Why a custom sitemap instead of relying on Yoast/RankMath:
  - Our programmatic pages are a CPT (service_area_page). Yoast sometimes
    mis-prioritizes CPT pages or drops new ones for 24-48 hours.
  - Priority + changefreq should be driven by CSV `tier`, not guessed.
  - We want the sitemap generated the MOMENT the CSV is ready, not on
    the next WP cron cycle.

USAGE:
  python sitemap.py
      # reads pages-generated.csv, writes sitemap-acp.xml
  python sitemap.py --input pages-template.csv --output sitemap-preview.xml
      # preview sitemap even before pages are generated (uses CSV slugs)

OUTPUT:
  sitemap-acp.xml — drop into WP root (wp-content/uploads/ or public_html/)
  or pipe into Yoast's sitemap index via:
    add_filter('wpseo_sitemap_index', fn($i) => $i . '<sitemap>...</sitemap>');

STRATEGY:
  tier 1 (primary cities)  → priority 0.9, changefreq weekly
  tier 2 (secondary)       → priority 0.7, changefreq weekly
  tier 3 (statewide hubs)  → priority 0.8, changefreq monthly
  (hubs outrank tier-2 city pages in priority because they funnel traffic)
"""

import argparse
import csv
import os
from datetime import datetime
from xml.sax.saxutils import escape

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────

BASE_URL = "https://arizonachimneypros.com"

# Tier → (priority, changefreq). Tuned for SEO freshness signaling.
TIER_WEIGHTS = {
    "1": (0.9, "weekly"),
    "2": (0.7, "weekly"),
    "3": (0.8, "monthly"),
    "":  (0.5, "monthly"),  # fallback for untiered rows
}

DEFAULT_INPUT  = "pages-generated.csv"
DEFAULT_OUTPUT = "sitemap-acp.xml"

# Static pages that should always be in the sitemap (homepage + key nav).
# Edit these to match your actual site structure.
STATIC_URLS = [
    {"loc": "/",                    "priority": 1.0, "changefreq": "daily"},
    {"loc": "/chimney-services/",   "priority": 0.9, "changefreq": "monthly"},
    {"loc": "/service-areas/",      "priority": 0.8, "changefreq": "monthly"},
    {"loc": "/installation/",       "priority": 0.8, "changefreq": "monthly"},
    {"loc": "/remodeling/",         "priority": 0.8, "changefreq": "monthly"},
    {"loc": "/gas-repair/",         "priority": 0.8, "changefreq": "monthly"},
    {"loc": "/contact/",            "priority": 0.7, "changefreq": "yearly"},
]


# ─────────────────────────────────────────────
# Core
# ─────────────────────────────────────────────

def read_rows(path: str) -> list[dict]:
    """Load CSV, silently skip rows without a slug."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"CSV not found: {path}\n"
            f"  Run generate.py first, or use --input pages-template.csv "
            f"to preview."
        )
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [r for r in rows if r.get("slug")]


def format_lastmod(iso_date: str | None = None) -> str:
    """YYYY-MM-DD — W3C date format Google accepts."""
    return (iso_date or datetime.utcnow().strftime("%Y-%m-%d"))


def build_url_entry(loc: str, priority: float, changefreq: str, lastmod: str) -> str:
    """One <url> block. Escapes the loc defensively — some slugs could
    contain characters that need XML escaping."""
    return (
        "  <url>\n"
        f"    <loc>{escape(loc)}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority:.1f}</priority>\n"
        "  </url>"
    )


def build_sitemap(rows: list[dict], lastmod: str) -> str:
    """Assemble the complete XML document."""
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    # Static pages first (homepage gets top priority)
    for s in STATIC_URLS:
        parts.append(build_url_entry(
            loc=BASE_URL + s["loc"],
            priority=s["priority"],
            changefreq=s["changefreq"],
            lastmod=lastmod,
        ))

    # Programmatic pages
    for row in rows:
        tier = str(row.get("tier", "")).strip()
        priority, changefreq = TIER_WEIGHTS.get(tier, TIER_WEIGHTS[""])
        slug = row["slug"].strip("/")
        parts.append(build_url_entry(
            loc=f"{BASE_URL}/{slug}/",
            priority=priority,
            changefreq=changefreq,
            lastmod=lastmod,
        ))

    parts.append("</urlset>\n")
    return "\n".join(parts)


def print_summary(rows: list[dict], output_path: str, size_bytes: int) -> None:
    from collections import Counter
    tier_counts = Counter(str(r.get("tier", "")).strip() for r in rows)
    total = len(rows) + len(STATIC_URLS)

    print(f"\n  Arizona Chimney Pros - Sitemap Generated")
    print(f"  {'-' * 50}")
    print(f"  Output:        {output_path}")
    print(f"  Size:          {size_bytes:,} bytes")
    print(f"  Total URLs:    {total}")
    print(f"    Static:      {len(STATIC_URLS)}")
    print(f"    Programmatic:{len(rows)}")
    print(f"  By tier:")
    for tier in sorted(tier_counts):
        label = f"tier {tier}" if tier else "no tier"
        print(f"    {label:>10} : {tier_counts[tier]}")
    print()
    print(f"  Next steps:")
    print(f"  1. Upload {output_path} to public_html/ or wp-content/uploads/")
    print(f"  2. Submit in Google Search Console:")
    print(f"     {BASE_URL}/{os.path.basename(output_path)}")
    print(f"  3. Add to robots.txt: Sitemap: {BASE_URL}/{os.path.basename(output_path)}")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate XML sitemap from pages CSV")
    parser.add_argument("--input",  default=DEFAULT_INPUT,
                        help=f"Input CSV (default: {DEFAULT_INPUT})")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help=f"Output XML (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--lastmod", default=None,
                        help="YYYY-MM-DD lastmod override (default: today)")
    args = parser.parse_args()

    rows    = read_rows(args.input)
    lastmod = format_lastmod(args.lastmod)
    xml     = build_sitemap(rows, lastmod)

    with open(args.output, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)

    print_summary(rows, args.output, len(xml.encode("utf-8")))


if __name__ == "__main__":
    main()
