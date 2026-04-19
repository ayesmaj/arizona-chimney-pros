"""
Arizona Chimney Pros — Pre-Commit Verification Runner
=====================================================
Single-command sanity check for the whole programmatic SEO pipeline.

Runs offline (no API calls) and validates:
  1. CSV structure (required columns, unique slugs)
  2. Content bank tag coverage (every CSV city has tagged anecdotes)
  3. Prompt files exist for each page_type in the CSV
  4. ACF field definitions cover every GENERATED_FIELD
  5. Schema builder can render a row without error
  6. Link graph has no orphans and healthy cross-tier flow

Exit codes:
  0 — all checks pass
  1 — at least one check failed (CI-friendly)

USAGE:
  python verify.py           # full run, colorized output
  python verify.py --quiet   # only print failures

Run this before every commit + before every API-powered generate run
to catch config drift and prevent wasted API credits.
"""

import argparse
import csv
import json
import os
import sys
import types
from collections import Counter
from pathlib import Path


# ─────────────────────────────────────────────
# Setup — stub anthropic so we can import generate.py offline
# ─────────────────────────────────────────────
if "anthropic" not in sys.modules:
    stub = types.ModuleType("anthropic")
    class _Dummy:
        def __init__(self, *a, **kw): pass
    stub.Anthropic = _Dummy
    sys.modules["anthropic"] = stub


REQUIRED_CSV_COLUMNS = {
    "slug", "title", "city", "state", "service",
    "appliance_type", "fuel_type", "page_type",
    "primary_keyword", "seed_angle", "tier",
}


# ─────────────────────────────────────────────
# Check result primitive
# ─────────────────────────────────────────────
class Check:
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"

    def __init__(self, name: str, status: str, detail: str = ""):
        self.name   = name
        self.status = status
        self.detail = detail

    def icon(self) -> str:
        return {"PASS": "[OK]  ", "WARN": "[WARN]", "FAIL": "[FAIL]"}[self.status]


# ─────────────────────────────────────────────
# Individual checks
# ─────────────────────────────────────────────

def check_csv_structure(csv_path: str) -> list[Check]:
    checks = []
    if not os.path.exists(csv_path):
        return [Check("CSV exists", Check.FAIL, f"not found: {csv_path}")]

    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        return [Check("CSV has rows", Check.FAIL, "file has header but no rows")]

    checks.append(Check("CSV exists + has rows", Check.PASS,
                        f"{len(rows)} rows loaded"))

    # Columns
    columns = set(rows[0].keys())
    missing = REQUIRED_CSV_COLUMNS - columns
    if missing:
        checks.append(Check("Required columns", Check.FAIL,
                            f"missing: {sorted(missing)}"))
    else:
        checks.append(Check("Required columns", Check.PASS,
                            f"{len(columns)} columns"))

    # Slug uniqueness
    slugs = [r["slug"] for r in rows if r.get("slug")]
    dups = [s for s, n in Counter(slugs).items() if n > 1]
    if dups:
        checks.append(Check("Slug uniqueness", Check.FAIL,
                            f"{len(dups)} duplicates: {dups[:5]}"))
    else:
        checks.append(Check("Slug uniqueness", Check.PASS,
                            f"all {len(slugs)} unique"))

    # Required field values per row
    missing_required = 0
    for r in rows:
        for col in ("slug", "title", "city", "service", "primary_keyword"):
            if not r.get(col):
                missing_required += 1
                break
    if missing_required:
        checks.append(Check("Required values filled", Check.FAIL,
                            f"{missing_required} rows have empty required fields"))
    else:
        checks.append(Check("Required values filled", Check.PASS,
                            "all rows complete"))

    return checks


def check_content_banks(csv_path: str) -> list[Check]:
    checks = []
    anecdote_path = "content-banks/anecdotes.json"
    faq_path      = "content-banks/faq-bank.json"

    for path, label in [(anecdote_path, "Anecdote"), (faq_path, "FAQ")]:
        if not os.path.exists(path):
            checks.append(Check(f"{label} bank exists", Check.FAIL,
                                f"missing: {path}"))
            continue
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            checks.append(Check(f"{label} bank valid JSON", Check.PASS,
                                f"{len(data)} entries"))
        except json.JSONDecodeError as e:
            checks.append(Check(f"{label} bank valid JSON", Check.FAIL,
                                f"parse error: {e}"))

    # Tag coverage — every unique city in CSV should have >= 1 anecdote
    if not os.path.exists(anecdote_path):
        return checks
    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    cities = set()
    for r in rows:
        c = (r.get("city") or "").strip().lower().replace(" ", "-")
        if c and c != "arizona":
            cities.add(c)

    with open(anecdote_path, encoding="utf-8") as f:
        anecdotes = json.load(f)
    tag_counts = Counter()
    for a in anecdotes:
        for t in a.get("tags", []):
            tag_counts[t] += 1

    uncovered = [c for c in cities if tag_counts.get(c, 0) == 0]
    weak      = [c for c in cities if 0 < tag_counts.get(c, 0) < 2]

    if uncovered:
        checks.append(Check("Anecdote city coverage", Check.WARN,
                            f"{len(uncovered)} cities with 0 anecdotes: "
                            f"{sorted(uncovered)[:5]}"))
    elif weak:
        checks.append(Check("Anecdote city coverage", Check.WARN,
                            f"{len(weak)} cities with only 1 anecdote: "
                            f"{sorted(weak)[:5]}"))
    else:
        checks.append(Check("Anecdote city coverage", Check.PASS,
                            f"all {len(cities)} cities have >= 2 anecdotes"))

    return checks


def check_prompts(csv_path: str) -> list[Check]:
    """Verify a usable prompt exists for every page_type in the CSV.

    generate.load_prompt() falls back to service-city.txt when an
    intent-specific prompt isn't present. So:
      - service-city.txt missing -> FAIL (breaks everything)
      - intent-specific prompt missing -> WARN (falls back, works
        but generic copy for cost/comparison intents)
    """
    checks = []
    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    page_types = sorted(set(r.get("page_type", "") for r in rows
                            if r.get("page_type")))

    # Fallback prompt is mandatory.
    fallback = "prompts/service-city.txt"
    if not os.path.exists(fallback):
        checks.append(Check("Base prompt (fallback)", Check.FAIL,
                            f"missing: {fallback} — required as fallback"))
        return checks
    checks.append(Check("Base prompt (fallback)", Check.PASS, fallback))

    import generate
    for pt in page_types:
        intent = generate.PAGE_TYPE_TO_INTENT.get(pt, "service")
        preferred = f"prompts/{intent}-city.txt"
        if os.path.exists(preferred):
            checks.append(Check(f"Prompt for page_type={pt}", Check.PASS,
                                preferred))
        else:
            checks.append(Check(f"Prompt for page_type={pt}", Check.WARN,
                                f"no dedicated {preferred}, falls back to "
                                f"{fallback} (sub-optimal for {pt} intent)"))
    return checks


def check_acf_coverage() -> list[Check]:
    checks = []
    acf_path = "acf-fields.json"
    if not os.path.exists(acf_path):
        return [Check("ACF field group exists", Check.FAIL, "acf-fields.json missing")]

    with open(acf_path, encoding="utf-8") as f:
        acf_data = json.load(f)
    if not acf_data or not acf_data[0].get("fields"):
        return [Check("ACF field group structure", Check.FAIL,
                      "no fields in group")]

    field_names = {f["name"] for f in acf_data[0]["fields"]}
    checks.append(Check("ACF field group valid", Check.PASS,
                        f"{len(field_names)} fields registered"))

    import generate
    generated = set(generate.GENERATED_FIELDS)
    missing_acf = generated - field_names
    extra_acf   = field_names - generated - {
        # Input-only CSV columns that don't need to be in GENERATED_FIELDS
        "slug", "title", "city", "state", "service", "appliance_type",
        "fuel_type", "page_type", "price_range", "primary_keyword",
        "secondary_keywords", "nearby_cities", "local_notes",
    }

    if missing_acf:
        checks.append(Check("GENERATED_FIELDS -> ACF mapping", Check.FAIL,
                            f"missing ACF entries for: {sorted(missing_acf)}"))
    else:
        checks.append(Check("GENERATED_FIELDS -> ACF mapping", Check.PASS,
                            "every generated field has an ACF definition"))

    return checks


def check_schema_builder() -> list[Check]:
    try:
        import schema_builder
    except ImportError as e:
        return [Check("schema_builder importable", Check.FAIL, str(e))]

    try:
        fake_row = {
            "slug": "test-slug-phoenix",
            "city": "Phoenix",
            "state": "Arizona",
            "service": "Gas Fireplace Repair",
            "price_range": "$180-$450",
        }
        fake_content = {
            "title": "Test Page",
            "meta_title": "Test",
            "meta_description": "Test description",
            "intro": "Test intro content.",
            "faq_1_q": "Q1?",
            "faq_1_a": "A1.",
        }
        schema_json = schema_builder.build_page_schema(fake_row, fake_content)
        parsed = json.loads(schema_json)
        graph = parsed.get("@graph", [])
        types = {node.get("@type") for node in graph}
        expected = {"LocalBusiness", "Service", "WebPage", "BreadcrumbList"}
        missing = expected - types
        if missing:
            return [Check("Schema builder output", Check.FAIL,
                          f"missing node types: {sorted(missing)}")]
        return [Check("Schema builder output", Check.PASS,
                      f"{len(graph)} nodes, {len(schema_json)} bytes")]
    except Exception as e:
        return [Check("Schema builder execution", Check.FAIL, str(e))]


def check_link_graph(csv_path: str) -> list[Check]:
    import generate
    import random

    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    inbound = Counter()
    outbound_counts = []
    for row in rows:
        slug = row.get("slug", "")
        if not slug:
            continue
        rng = random.Random(slug)
        links = generate.build_auto_links(row, rows, rng)
        outbound_counts.append(len(links))
        for link in links:
            inbound[link] += 1

    total_pages = len(rows)
    all_paths = {f"/{r['slug']}/" for r in rows if r.get("slug")}
    orphan_count = sum(1 for p in all_paths if inbound.get(p, 0) == 0)
    thin_count   = sum(1 for p in all_paths if 0 < inbound.get(p, 0) <= 2)

    out_underfilled = sum(1 for c in outbound_counts
                          if c < generate.AUTO_LINK_COUNT)

    checks = []
    if orphan_count > 0:
        checks.append(Check("Link graph: orphans", Check.FAIL,
                            f"{orphan_count} orphans (should be 0)"))
    else:
        checks.append(Check("Link graph: orphans", Check.PASS,
                            "0 orphans across graph"))

    thin_pct = (100 * thin_count / total_pages) if total_pages else 0
    if thin_pct > 25:
        checks.append(Check("Link graph: thin pages", Check.WARN,
                            f"{thin_count} ({thin_pct:.0f}%) pages have <= 2 inbound"))
    else:
        checks.append(Check("Link graph: thin pages", Check.PASS,
                            f"{thin_count} ({thin_pct:.0f}%) thin — acceptable"))

    if out_underfilled > total_pages * 0.1:
        checks.append(Check("Link graph: outbound density", Check.WARN,
                            f"{out_underfilled} pages have < {generate.AUTO_LINK_COUNT} auto-links"))
    else:
        checks.append(Check("Link graph: outbound density", Check.PASS,
                            f"avg outbound: "
                            f"{sum(outbound_counts)/max(len(outbound_counts),1):.1f}"))

    return checks


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true",
                        help="Only print failures")
    parser.add_argument("--csv", default="pages-template.csv",
                        help="CSV file to validate (default: pages-template.csv)")
    args = parser.parse_args()

    # Ensure we run from the seo-system directory so relative paths resolve.
    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)

    sections = [
        ("CSV Structure",        lambda: check_csv_structure(args.csv)),
        ("Content Banks",        lambda: check_content_banks(args.csv)),
        ("Prompt Templates",     lambda: check_prompts(args.csv)),
        ("ACF Field Coverage",   lambda: check_acf_coverage),  # lazy below
        ("Schema Builder",       lambda: check_schema_builder()),
        ("Link Graph Topology",  lambda: check_link_graph(args.csv)),
    ]

    total_pass = total_warn = total_fail = 0

    print("\nArizona Chimney Pros - Pipeline Verification")
    print("=" * 55)

    for section_name, runner in sections:
        try:
            # Handle the lazy ACF one
            result = runner() if callable(runner) else runner
            if callable(result):
                result = result()
            checks = result
        except Exception as e:
            checks = [Check(section_name, Check.FAIL, f"exception: {e}")]

        failed_in_section = [c for c in checks if c.status == Check.FAIL]
        warned_in_section = [c for c in checks if c.status == Check.WARN]

        should_show_section = (not args.quiet or failed_in_section
                               or warned_in_section)

        if should_show_section:
            print(f"\n-- {section_name}")
            print("-" * 55)

        for c in checks:
            if c.status == Check.PASS:
                total_pass += 1
                if args.quiet: continue
            elif c.status == Check.WARN:
                total_warn += 1
            else:
                total_fail += 1
            detail = f"  ({c.detail})" if c.detail else ""
            print(f"  {c.icon()} {c.name}{detail}")

    print("\n" + "=" * 55)
    print(f"RESULTS: {total_pass} pass, {total_warn} warn, {total_fail} fail")
    print("=" * 55 + "\n")

    return 1 if total_fail else 0


if __name__ == "__main__":
    sys.exit(main())
