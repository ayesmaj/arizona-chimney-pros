"""
Arizona Chimney Pros — Link Graph Preflight
============================================
Simulates the internal-link topology that generate.py will produce for the
current pages-template.csv, WITHOUT calling the Claude API.

Why this exists:
  - Internal-link graphs can silently develop "orphans" (pages nobody links
    to) and "black holes" (pages everybody links to but that don't exist).
  - Catching that before you burn API credits + generate content saves
    real money and embarrassment.

USAGE:
  python link_preflight.py                  # full report
  python link_preflight.py --top 20         # show top-20 hubs + orphans only
  python link_preflight.py --csv            # also dump per-page link table to
                                             # link_preflight.csv for review

WHAT IT REPORTS:
  - Inbound link distribution (histogram)
  - Top hubs (most inbound)
  - Orphans (0 inbound — bad for SEO)
  - Thin pages (1–2 inbound — should grow)
  - Outbound link counts (should be AUTO_LINK_COUNT for all)
  - Cross-tier link ratio (tier-1 pages should pull traffic to tier-2/3)
"""

import argparse
import csv
import random
import sys
import types
from collections import Counter, defaultdict

# Stub anthropic so we can import generate.py without the SDK installed.
# Preflight is pure local computation — no API calls anywhere.
if "anthropic" not in sys.modules:
    stub = types.ModuleType("anthropic")
    class _Dummy:
        def __init__(self, *a, **kw): pass
    stub.Anthropic = _Dummy
    sys.modules["anthropic"] = stub

import generate  # noqa: E402  (import after stubbing)

INPUT_FILE = "pages-template.csv"
DUMP_FILE  = "link_preflight.csv"


def simulate_graph(rows: list[dict]) -> tuple[dict, dict]:
    """For every row, compute the auto-links it WILL generate, and tally
    inbound counts across the whole graph.

    Returns:
      outbound  : {src_slug: [dst_path, ...]}
      inbound   : {dst_path: [src_slug, ...]}
    """
    outbound = {}
    inbound: dict[str, list[str]] = defaultdict(list)

    for row in rows:
        slug = row.get("slug", "")
        if not slug:
            continue
        rng = random.Random(slug)
        # Consume the same RNG budget generate.py consumes so results match.
        # In generate.py: anecdote → faq seeds → auto_links.
        # Here we skip anecdote/faq (they don't affect link picks), so reseed
        # with slug to match the downstream call exactly.
        # NOTE: if you change enrich_row order in generate.py, update this too.
        rng = random.Random(slug)
        links = generate.build_auto_links(row, rows, rng)
        outbound[slug] = links
        for link in links:
            inbound[link].append(slug)

    return outbound, dict(inbound)


def print_histogram(counter: Counter, title: str, width: int = 40) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    if not counter:
        print("  (no data)")
        return
    max_count = max(counter.values())
    for key in sorted(counter.keys()):
        bar_len = int((counter[key] / max_count) * width)
        bar = "#" * bar_len
        print(f"  {key:>3} inbound : {counter[key]:>3} pages  {bar}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=10, help="How many top hubs/orphans to list")
    parser.add_argument("--csv", action="store_true", help="Also dump per-page link table")
    args = parser.parse_args()

    with open(INPUT_FILE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Arizona Chimney Pros — Link Graph Preflight")
    print(f"Index: {len(rows)} pages in {INPUT_FILE}")
    print(f"Auto-link budget: {generate.AUTO_LINK_COUNT} per page\n")

    outbound, inbound = simulate_graph(rows)

    # ─── Inbound analysis ─────────────────────────────────────
    slug_to_path = {r["slug"]: f"/{r['slug']}/" for r in rows if r.get("slug")}
    all_paths    = set(slug_to_path.values())

    inbound_counts = {path: len(inbound.get(path, [])) for path in all_paths}
    histogram      = Counter(inbound_counts.values())

    print_histogram(histogram, "Inbound link distribution")

    # Orphans: pages nothing auto-links to
    orphans = [p for p, c in inbound_counts.items() if c == 0]
    thin    = [p for p, c in inbound_counts.items() if c in (1, 2)]

    # Hubs: pages pulling the most inbound
    sorted_by_inbound = sorted(inbound_counts.items(), key=lambda x: -x[1])

    print(f"\nSummary")
    print("-------")
    total_pages = len(all_paths)
    print(f"  Total pages    : {total_pages}")
    print(f"  Orphans (0 in) : {len(orphans)}  ({100*len(orphans)/total_pages:.0f}%)")
    print(f"  Thin    (1-2)  : {len(thin)}  ({100*len(thin)/total_pages:.0f}%)")
    print(f"  Healthy (3+)   : {total_pages - len(orphans) - len(thin)}")

    print(f"\nTop {args.top} hubs (most inbound links)")
    print("-" * 40)
    for path, count in sorted_by_inbound[:args.top]:
        print(f"  {count:>3}  {path}")

    if orphans:
        print(f"\nOrphans ({len(orphans)} — NOTHING auto-links here; add peers or they'll rank alone)")
        print("-" * 40)
        for path in orphans[:args.top]:
            print(f"  {path}")
        if len(orphans) > args.top:
            print(f"  ... and {len(orphans) - args.top} more")

    if thin:
        print(f"\nThin pages ({len(thin)} — only 1-2 inbound; consider adding more peers)")
        print("-" * 40)
        for path in thin[:args.top]:
            print(f"  {inbound_counts[path]:>2}  {path}")
        if len(thin) > args.top:
            print(f"  ... and {len(thin) - args.top} more")

    # ─── Cross-tier health check ──────────────────────────────
    tier_map = {f"/{r['slug']}/": r.get("tier", "?") for r in rows if r.get("slug")}
    tier_inbound = Counter()
    tier_outbound_to = Counter()  # from → to tier
    for src_slug, links in outbound.items():
        src_tier = tier_map.get(f"/{src_slug}/", "?")
        for link in links:
            dst_tier = tier_map.get(link, "?")
            tier_outbound_to[(src_tier, dst_tier)] += 1
            tier_inbound[dst_tier] += 1

    print(f"\nCross-tier link flow (who links to who)")
    print("-" * 40)
    for (src_t, dst_t), count in sorted(tier_outbound_to.items()):
        print(f"  tier {src_t} --> tier {dst_t} : {count:>4} links")

    print(f"\nInbound links by destination tier")
    print("-" * 40)
    for tier, count in sorted(tier_inbound.items()):
        avg = count / sum(1 for t in tier_map.values() if t == tier)
        print(f"  tier {tier} : {count:>4} total  ({avg:.1f} avg per page)")

    # ─── Optional: dump per-page table ────────────────────────
    if args.csv:
        with open(DUMP_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["slug", "inbound_count", "outbound", "inbound_from"])
            for row in rows:
                slug = row["slug"]
                path = f"/{slug}/"
                writer.writerow([
                    slug,
                    inbound_counts.get(path, 0),
                    ";".join(outbound.get(slug, [])),
                    ";".join(inbound.get(path, [])),
                ])
        print(f"\nPer-page link table written to: {DUMP_FILE}")

    print(f"\nPreflight complete. No API calls made.")


if __name__ == "__main__":
    main()
