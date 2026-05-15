import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import json

from rca_agent.tools import fetch_bl_core, fetch_bl_core_expired


def main():
    parser = argparse.ArgumentParser(description="Fetch base BL context for RCA.")
    parser.add_argument("--bl_id", required=True, help="BL Display ID to investigate")
    parser.add_argument("--out", default="bl_core.json", help="Output file path")
    args = parser.parse_args()

    print(f"Fetching BL core for: {args.bl_id}")

    bl_core_rows = fetch_bl_core(args.bl_id)

    if not bl_core_rows:
        print("Not found in live table. Trying expired...")
        bl_core_rows = fetch_bl_core_expired(args.bl_id)

    if not bl_core_rows:
        raise Exception(f"No BL found for ID: {args.bl_id}")

    bl_core = bl_core_rows[0]

    output = {
        "bl_id": args.bl_id,
        "bl_core": bl_core,
    }

    Path(args.out).write_text(
        json.dumps(output, indent=2, default=str),
        encoding="utf-8",
    )

    print(f"BL core written to {args.out}")
    print(f"  Title    : {bl_core.get('bl_title', 'N/A')}")
    print(f"  Category : {bl_core.get('bl_mcat_name', 'N/A')}")
    print(f"  Source   : {bl_core.get('source_product_display_id', 'None')}")


if __name__ == "__main__":
    main()