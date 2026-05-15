from pathlib import Path


def read_skill():
    skill_dir = Path("buylead-rca-skill")

    files = [
        skill_dir / "SKILL.md",
        skill_dir / "references" / "eto-attribute-codes.md",
        skill_dir / "references" / "system-spec-list.md",
        skill_dir / "references" / "output-schema.md",
        skill_dir / "references" / "second-workflow-walkthrough.md",
        skill_dir / "assets" / "rca-report-template.md",
    ]

    combined = []

    for file_path in files:
        if file_path.exists():
            combined.append(f"\n\n# FILE: {file_path.as_posix()}\n")
            combined.append(file_path.read_text(encoding="utf-8"))

    if not combined:
        raise FileNotFoundError("No skill files found in buylead-rca-skill")

    return "\n".join(combined)