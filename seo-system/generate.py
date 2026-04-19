"""
Arizona Chimney Pros — Programmatic SEO Content Generator
==========================================================
Reads pages-template.csv → calls Claude API → writes pages-enriched.csv

SETUP:
  pip install anthropic

USAGE:
  python generate.py                         # process all rows
  python generate.py --limit 10             # process first 10 rows (test)
  python generate.py --start 50             # resume from row 50
  python generate.py --limit 5 --dry-run    # print prompts only, no API calls

RESULT:
  pages-enriched.csv  — import this into WordPress via WP All Import
"""

import anthropic
import csv
import json
import time
import argparse
import os
import random
import sys
from datetime import datetime

from schema_builder import build_page_schema

# ─────────────────────────────────────────────
# CONFIG — set your API key here or in env var
# ─────────────────────────────────────────────
API_KEY       = os.environ.get("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
MODEL         = "claude-opus-4-5"        # claude-sonnet-4-5 for faster/cheaper
MAX_TOKENS    = 2000
DELAY_SECONDS = 1.5                     # pause between API calls (rate limiting)
INPUT_FILE    = "pages-template.csv"
OUTPUT_FILE   = "pages-enriched.csv"
ANECDOTE_FILE = "content-banks/anecdotes.json"
FAQ_FILE      = "content-banks/faq-bank.json"
FAQ_SEED_COUNT = 8    # How many candidate questions to show Claude (picks 4)
AUTO_LINK_COUNT = 5   # Auto-injected internal links added to Claude's 3 manual picks

# Generated fields that Claude fills in (+ locally-computed extras).
# schema_json is computed locally after Claude returns content — it's in this
# list so the CSV writer includes it in the output header.
GENERATED_FIELDS = [
    "slug", "title",
    "meta_title", "meta_description",
    "intro", "local_section", "signs_section", "pricing_section",
    "process_section", "trust_section",
    "faq_1_q", "faq_1_a",
    "faq_2_q", "faq_2_a",
    "faq_3_q", "faq_3_a",
    "faq_4_q", "faq_4_a",
    "cta_headline", "cta_text",
    "internal_links",
    "schema_json",    # locally-computed JSON-LD
]

# Fields that come back from Claude as arrays but must be flattened
# to a semicolon-joined string before writing to CSV.
ARRAY_FIELDS = {"internal_links"}
ARRAY_JOIN   = ";"


def flatten_arrays(content: dict) -> dict:
    """Convert list-valued fields into semicolon-joined strings for CSV."""
    flat = {}
    for key, value in content.items():
        if key in ARRAY_FIELDS and isinstance(value, list):
            flat[key] = ARRAY_JOIN.join(str(v).strip() for v in value if v)
        else:
            flat[key] = value
    return flat


# ─────────────────────────────────────────────
# Content banks: inject unique flavor per page
# ─────────────────────────────────────────────

PAGE_TYPE_TO_INTENT = {
    "service_city": "service",
    "problem_city": "problem",
    "cost_page":    "cost",
    "comparison":   "comparison",
    "emergency":    "emergency",
    "maintenance":  "maintenance",
    "location_hub": "service",
}


def load_banks() -> tuple[list, list]:
    """Load anecdote + FAQ banks from disk. Called once per run."""
    try:
        with open(ANECDOTE_FILE, "r", encoding="utf-8") as f:
            anecdotes = json.load(f)
        with open(FAQ_FILE, "r", encoding="utf-8") as f:
            faqs = json.load(f)
        return anecdotes, faqs
    except FileNotFoundError as e:
        print(f"  ! Content bank missing ({e}). Continuing without injected banks.")
        return [], []


def _city_slug(city: str) -> str:
    return city.strip().lower().replace(" ", "-")


def pick_anecdote(anecdotes: list, row: dict, rng: random.Random) -> str:
    """Score anecdotes against the row, pick from top matches.

    Scoring: city tag > service/appliance tag > fuel match. We return a
    random pick from the top 5 to keep variety across a city run."""
    if not anecdotes:
        return ""

    city = _city_slug(row.get("city", ""))
    fuel = (row.get("fuel_type") or "any").lower()
    service = (row.get("service") or "").lower()
    appliance = (row.get("appliance_type") or "").lower()

    scored = []
    for a in anecdotes:
        tags = [t.lower() for t in a.get("tags", [])]
        fuels = [f.lower() for f in a.get("fuel", [])]
        score = 0
        if city and city in tags:
            score += 10
        if appliance and appliance in tags:
            score += 3
        # Service keywords overlap with tags (e.g. "chimney-repair", "remodel")
        for word in service.split():
            if word and word in tags:
                score += 2
        if fuel in fuels or "any" in fuels:
            score += 1
        scored.append((score, a))

    scored.sort(reverse=True, key=lambda x: x[0])
    # Keep variety: pick randomly from top 5 (or all if fewer)
    top_n = min(5, len(scored))
    pick = rng.choice(scored[:top_n])[1]
    return pick.get("note", "")


def pick_faq_seeds(faqs: list, row: dict, rng: random.Random, n: int = FAQ_SEED_COUNT) -> list[dict]:
    """Pick N candidate FAQ seeds, prioritizing intent + fuel match."""
    if not faqs:
        return []

    intent = PAGE_TYPE_TO_INTENT.get(row.get("page_type", "service_city"), "service")
    fuel = (row.get("fuel_type") or "any").lower()
    appliance = (row.get("appliance_type") or "").lower()

    def score(faq: dict) -> int:
        s = 0
        if faq.get("intent") == intent:
            s += 5
        fuels = [f.lower() for f in faq.get("fuel", [])]
        if fuel in fuels or "any" in fuels:
            s += 2
        appls = [a.lower() for a in faq.get("appliance", [])]
        if appliance in appls:
            s += 1
        return s

    ranked = sorted(faqs, key=score, reverse=True)
    # Take top 2*n then sample n — adds variety without drifting off-topic
    pool = ranked[: max(n * 2, n)]
    rng.shuffle(pool)
    return pool[:n]


def format_faq_seeds(seeds: list[dict]) -> str:
    """Format FAQ candidates as a numbered list Claude can pick from."""
    if not seeds:
        return "(no seed bank available — generate 4 original FAQs)"
    lines = []
    for i, f in enumerate(seeds, 1):
        lines.append(f'{i}. Q: "{f["q"]}"')
        lines.append(f'   Suggested angle: {f["a_seed"]}')
    return "\n".join(lines)


def enrich_row(row: dict, anecdotes: list, faqs: list, rng: random.Random) -> dict:
    """Attach sampled anecdote + FAQ seeds to the row as prompt variables."""
    enriched = dict(row)
    enriched["technician_anecdote"] = pick_anecdote(anecdotes, row, rng)
    enriched["faq_seeds"] = format_faq_seeds(pick_faq_seeds(faqs, row, rng))
    # Ensure seed_angle has a default if missing (legacy rows)
    if not enriched.get("seed_angle"):
        enriched["seed_angle"] = "reassuring"
    return enriched


# ─────────────────────────────────────────────
# Auto internal-link injector
# ─────────────────────────────────────────────
#
# Claude generates 3 editorial links per page from the prompt. We add up to
# AUTO_LINK_COUNT more by mining the full CSV for relevant peers. Result: a
# dense internal graph (~8 links/page) that amplifies ranking signal and
# keeps visitors inside the funnel.
#
# All links use the flat /{slug}/ format — must match actual WP permalinks.

def _as_path(slug: str) -> str:
    slug = (slug or "").strip().strip("/")
    return f"/{slug}/" if slug else ""


def _split_list(value: str) -> list[str]:
    """Parse semicolon-separated CSV field (e.g. nearby_cities)."""
    if not value:
        return []
    return [p.strip() for p in value.split(";") if p.strip()]


def build_auto_links(row: dict, all_rows: list[dict], rng: random.Random,
                     count: int = AUTO_LINK_COUNT) -> list[str]:
    """Return up to `count` related /{slug}/ paths from the full page index.

    The algorithm is page-type-aware because different page types need
    different link patterns:

      - service_city  pages pull users down into specific problems + nearby cities
      - problem_city  pages MUST link up to their parent service_city page
                      (highest conversion signal) + sibling problems
      - comparison/cost_page hubs spread link equity across tier-1 city pages

    Each pool is shuffled within tier so a batch of Phoenix pages doesn't
    all link to the same 5 neighbors in the same order.
    """
    self_slug = (row.get("slug") or "").strip()
    city      = (row.get("city") or "").strip().lower()
    service   = (row.get("service") or "").strip().lower()
    page_type = (row.get("page_type") or "").strip().lower()
    nearby    = {c.strip().lower() for c in _split_list(row.get("nearby_cities", ""))}

    # Categorize every other row into typed pools
    pools: dict[str, list[str]] = {
        "parent_service":         [],  # same city + same service, service_city
        "same_city_diff_svc":     [],  # same city, different service, service_city
        "same_city_problems":     [],  # same city, problem_city (excluding self)
        "nearby_same_svc":        [],  # nearby city, same service, service_city
        "nearby_problems":        [],  # nearby city, problem_city
        "hub_pages":              [],  # comparison / cost_page
        "same_service_anywhere":  [],  # any service_city with same service
                                        # (non-local — redistributes link equity
                                        #  to tier-2/3 cities + lets hubs link
                                        #  to city-level service pages)
    }

    for r in all_rows:
        if not r:
            continue
        r_slug    = (r.get("slug") or "").strip()
        if not r_slug or r_slug == self_slug:
            continue
        r_city    = (r.get("city") or "").strip().lower()
        r_service = (r.get("service") or "").strip().lower()
        r_type    = (r.get("page_type") or "").strip().lower()

        if r_type in ("comparison", "cost_page", "location_hub"):
            pools["hub_pages"].append(r_slug)
        elif r_city == city:
            if r_type == "problem_city":
                pools["same_city_problems"].append(r_slug)
            elif r_type == "service_city":
                if r_service == service:
                    pools["parent_service"].append(r_slug)
                else:
                    pools["same_city_diff_svc"].append(r_slug)
        elif r_city in nearby:
            if r_type == "problem_city":
                pools["nearby_problems"].append(r_slug)
            elif r_type == "service_city" and r_service == service:
                pools["nearby_same_svc"].append(r_slug)

        # Separately (not exclusive with above): any non-self service_city with
        # same service feeds the cross-city fallback pool.
        if (r_type == "service_city" and r_service == service and r_city != city):
            pools["same_service_anywhere"].append(r_slug)

    for pool in pools.values():
        rng.shuffle(pool)

    # Page-type-aware quotas. Each tuple is (pool_name, max_from_this_pool).
    if page_type == "problem_city":
        # Problem pages need: parent service hub + sibling problems + nearby
        quotas = [
            ("parent_service",        1),  # "we fix gas fireplaces in Phoenix" — critical
            ("same_city_problems",    1),  # "another issue we see in Phoenix"
            ("same_city_diff_svc",    1),  # "we also do chimney work"
            ("nearby_problems",       1),  # "same problem next city over"
            ("hub_pages",             1),  # funnel depth
            ("same_service_anywhere", 1),  # "we service gas fireplaces across AZ"
        ]
    elif page_type in ("comparison", "cost_page", "location_hub"):
        # Hub pages push link equity DOWN into city-level service pages
        quotas = [
            ("same_service_anywhere", 3),  # link to 3 city-level service pages
            ("hub_pages",             1),  # other hubs
            ("same_city_diff_svc",    1),
        ]
    else:  # service_city (default)
        # Total quota sums to 6 but AUTO_LINK_COUNT caps at 5 — the last pool
        # (same_service_anywhere) drops FIRST when a large city fills the
        # problem/diff-service pools. Tier-2 small cities with empty problem
        # pools still get the same_service_anywhere cross-city boost via
        # the backfill loop below.
        quotas = [
            ("same_city_diff_svc",    1),  # "also in this city"
            ("same_city_problems",    2),  # bumped: big-city problem pools
                                           # (10+) otherwise starve 1-pick selection
            ("nearby_same_svc",       1),  # "same service nearby"
            ("hub_pages",             1),  # funnel
            ("same_service_anywhere", 1),  # cross-city reach (tier-2 booster)
        ]

    picked: list[str] = []
    for pool_name, quota in quotas:
        for slug in pools[pool_name][:quota]:
            path = _as_path(slug)
            if path and path not in picked:
                picked.append(path)

    # Backfill if a pool came up short (small-pool cities, edge cases)
    if len(picked) < count:
        # Backfill in the same priority order as the quotas for this type
        for pool_name, _ in quotas:
            for slug in pools[pool_name]:
                path = _as_path(slug)
                if path and path not in picked:
                    picked.append(path)
                    if len(picked) >= count:
                        break
            if len(picked) >= count:
                break

    return picked[:count]


def merge_internal_links(content: dict, row: dict, all_rows: list[dict],
                         rng: random.Random) -> dict:
    """Append auto-links to Claude's manual internal_links, deduped + validated.

    Claude occasionally hallucinates links to pages we haven't built. We drop
    those silently so the auto-injector can backfill with real pages — better
    than letting a 404 ship to production.
    """
    manual = content.get("internal_links", [])
    if isinstance(manual, str):
        manual = _split_list(manual)
    manual = [_as_path(link.strip("/")) if not link.startswith("/") else link.strip()
              for link in manual if link]

    # Build the known-good slug set and the self-slug (both to reject)
    known = {_as_path(r.get("slug", "")) for r in all_rows if r.get("slug")}
    self_path = _as_path(row.get("slug", ""))

    validated_manual = [
        link for link in manual
        if link in known and link != self_path
    ]

    auto = build_auto_links(row, all_rows, rng)

    merged: list[str] = []
    for link in [*validated_manual, *auto]:
        if link and link not in merged:
            merged.append(link)

    content["internal_links"] = merged
    return content


# Load prompt templates
def load_prompt(page_type: str) -> str:
    """Pick the prompt template for a given page_type.

    Uses PAGE_TYPE_TO_INTENT if a dedicated template exists for that
    intent (e.g. prompts/cost-city.txt for cost_page). Falls back to
    service-city.txt when the intent-specific file isn't present —
    so the pipeline never breaks on a missing prompt.
    """
    intent = PAGE_TYPE_TO_INTENT.get(page_type, "service")
    preferred = f"prompts/{intent}-city.txt"
    fallback  = "prompts/service-city.txt"

    path = preferred if os.path.exists(preferred) else fallback

    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# Fill prompt template with row data
def build_prompt(template: str, row: dict) -> str:
    result = template
    for key, value in row.items():
        result = result.replace(f"{{{{{key}}}}}", value or "")
    return result

# Call Claude API and parse JSON response
def generate_content(client: anthropic.Anthropic, prompt: str, row_id: str) -> dict:
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw = message.content[0].text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        return json.loads(raw)

    except json.JSONDecodeError as e:
        print(f"  ✗ JSON parse error on row {row_id}: {e}")
        print(f"    Raw response: {raw[:200]}...")
        return {}
    except anthropic.RateLimitError:
        print(f"  ⏳ Rate limited on row {row_id} — waiting 30s...")
        time.sleep(30)
        return generate_content(client, prompt, row_id)  # retry once
    except Exception as e:
        print(f"  ✗ API error on row {row_id}: {e}")
        return {}

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate SEO content with Claude")
    parser.add_argument("--limit",   type=int, default=None, help="Max rows to process")
    parser.add_argument("--start",   type=int, default=0,    help="Start from row index (0-based)")
    parser.add_argument("--dry-run", action="store_true",    help="Print prompts without calling API")
    args = parser.parse_args()

    # Validate API key
    if not args.dry_run and API_KEY == "YOUR_API_KEY_HERE":
        print("❌ Set ANTHROPIC_API_KEY environment variable or update API_KEY in generate.py")
        sys.exit(1)

    # Read input CSV
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
        sys.exit(1)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Load content banks once (reused across all rows)
    anecdotes, faqs = load_banks()
    if anecdotes or faqs:
        print(f"Loaded banks: {len(anecdotes)} anecdotes, {len(faqs)} FAQs")

    total = len(rows)
    start = args.start
    end   = min(start + args.limit, total) if args.limit else total
    batch = rows[start:end]

    print(f"Arizona Chimney Pros — SEO Content Generator")
    print(f"Model:  {MODEL}")
    print(f"Rows:   {start} → {end-1} of {total} total")
    print(f"Output: {OUTPUT_FILE}")
    if args.dry_run:
        print(f"Mode:   DRY RUN (no API calls)\n")
    else:
        print(f"Mode:   LIVE\n")

    client = anthropic.Anthropic(api_key=API_KEY) if not args.dry_run else None

    # Prepare output fieldnames (original + generated)
    original_fields = list(rows[0].keys()) if rows else []
    all_fields = original_fields + [f for f in GENERATED_FIELDS if f not in original_fields]

    # Open output CSV (append mode so we can resume)
    write_header = not os.path.exists(OUTPUT_FILE) or args.start == 0
    out_file = open(OUTPUT_FILE, "a" if not write_header else "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(out_file, fieldnames=all_fields)
    if write_header:
        writer.writeheader()

    # Track results
    success = 0
    failed  = 0

    for i, row in enumerate(batch):
        global_idx  = start + i
        slug        = row.get("slug", f"row-{global_idx}")
        page_type   = row.get("page_type", "service_city")

        print(f"[{global_idx+1}/{total}] {slug}")

        # Load correct prompt template
        try:
            template = load_prompt(page_type)
        except FileNotFoundError as e:
            print(f"  ✗ Prompt file missing: {e}")
            failed += 1
            continue

        # Inject sampled anecdote + FAQ seeds per row.
        # Seed RNG deterministically by slug so reruns produce the same sampling
        # (easier debugging; swap in random.Random() for variety on reruns).
        rng = random.Random(slug)
        enriched_row = enrich_row(row, anecdotes, faqs, rng)
        prompt = build_prompt(template, enriched_row)

        if args.dry_run:
            print(f"  → Prompt preview ({len(prompt)} chars):")
            print(f"    {prompt[:300]}...\n")
            continue

        # Call API
        content = generate_content(client, prompt, slug)

        if not content:
            failed += 1
            # Write row with empty generated fields so we know it failed
            writer.writerow({**row, **{f: "ERROR" for f in GENERATED_FIELDS}})
            out_file.flush()
            continue

        # Auto-inject 5 related internal links on top of Claude's 3 manual picks.
        # Uses the same deterministic RNG so reruns are reproducible.
        content = merge_internal_links(content, row, rows, rng)

        # Compute JSON-LD schema BEFORE flattening (needs raw content fields,
        # and internal_links stays as a list for schema_builder).
        content["schema_json"] = build_page_schema(row, content)

        # Flatten any array fields (e.g. internal_links) into delimited strings
        content = flatten_arrays(content)

        # Merge original row with generated content
        enriched = {**row, **content}
        writer.writerow(enriched)
        out_file.flush()  # checkpoint: write immediately so progress is saved

        success += 1
        print(f"  ✓ Done — {content.get('meta_title', '(no title)')}")

        # Rate limiting delay
        if i < len(batch) - 1:
            time.sleep(DELAY_SECONDS)

    out_file.close()

    print(f"\n{'='*50}")
    print(f"Complete: {success} success, {failed} failed")
    print(f"Output saved to: {OUTPUT_FILE}")
    if failed > 0:
        print(f"Tip: Re-run with --start to retry failed rows")

if __name__ == "__main__":
    main()
