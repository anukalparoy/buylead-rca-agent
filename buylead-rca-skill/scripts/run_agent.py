import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import json

from rca_agent.skill_reader import read_skill
from rca_agent.llm_agent import run_rca_agent


def main():
    parser = argparse.ArgumentParser(description="Run agentic RCA on a buylead.")
    parser.add_argument("--bl_core", required=True, help="Path to bl_core.json from fetch_data.py")
    parser.add_argument("--issue", default="all", help="Attribute to investigate: specs / title / aov / all")
    parser.add_argument("--out", default="rca_report.md", help="Output report file path")
    args = parser.parse_args()

    # Load BL core data
    raw = json.loads(Path(args.bl_core).read_text(encoding="utf-8"))
    bl_id = raw["bl_id"]
    bl_core = raw["bl_core"]

    print(f"\nStarting RCA Agent")
    print(f"  BL ID   : {bl_id}")
    print(f"  Issue   : {args.issue}")
    print(f"  Title   : {bl_core.get('bl_title', 'N/A')}")
    print(f"  Category: {bl_core.get('bl_mcat_name', 'N/A')}")
    print()

    # Load skill
    skill_text = read_skill()

    # Run agentic loop — agent decides which tools to call
    report = run_rca_agent(
        skill_text=skill_text,
        bl_core=bl_core,
        bl_display_id=bl_id,
        user_issue=args.issue,
    )

    # Write report
    Path(args.out).write_text(report, encoding="utf-8")

    print(f"\nReport written to {args.out}")
    print("\n========== FINAL RCA ==========\n")
    print(report)


if __name__ == "__main__":
    main()