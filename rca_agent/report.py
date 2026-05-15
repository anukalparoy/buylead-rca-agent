def render_report(bl_core, findings, root_cause):
    invalid_specs = [
        f for f in findings
        if f.get("status") == "SPEC_NOT_DEFINED_FOR_CATEGORY"
    ]

    category_findings = [
        f for f in findings
        if f.get("check") == "source_product_category_comparison"
    ]

    report = f"""
# Buylead RCA Report

## BL Details
- BL ID: {bl_core.get("bl_display_id")}
- BL Title: {bl_core.get("bl_title")}
- BL Category: {bl_core.get("bl_mcat_name")} ({bl_core.get("bl_mcat_id")})
- Source Product ID: {bl_core.get("source_product_display_id")}

## RCA
- Primary Issue: {root_cause.get("primary_issue")}
- Root Cause: {root_cause.get("root_cause")}
- Confidence: {root_cause.get("confidence")}

## Category Evidence
"""

    if category_findings:
        f = category_findings[0]
        report += f"- BL MCAT ID: {f.get('bl_mcat_id')}\n"
        report += f"- Source Product MCAT IDs: {f.get('source_product_mcat_ids')}\n"
        report += f"- Status: {f.get('status')}\n"
    else:
        report += "- No source product category comparison available.\n"

    report += "\n## Spec Evidence\n"

    if invalid_specs:
        for f in invalid_specs:
            report += f"- Spec `{f.get('spec_name')}` with value `{f.get('spec_value')}` is not defined for this BL category.\n"
    else:
        report += "- No invalid category-spec mismatch found.\n"

    return report