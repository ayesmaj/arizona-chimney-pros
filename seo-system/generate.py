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

# Generated fields that Claude fills in
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


# Load prompt templates
def load_prompt(page_type: str) -> str:
    if page_type in ("problem_city",):
        path = "prompts/problem-city.txt"
    else:
        path = "prompts/service-city.txt"

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
