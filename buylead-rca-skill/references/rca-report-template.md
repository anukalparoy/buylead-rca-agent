# BL RCA Report

**Buylead ID:** {{buylead_id}}
**Investigated at:** {{investigated_at}}
**Attributes investigated:** {{attributes_investigated}}
**Investigated by:** {{investigated_by}}

---

## Specs

{{#if specs_investigated}}

### Spec Summary

{{specs_summary_paragraph}}

### Spec Detail

| Spec Name | Spec Value | Type | Fill Source | ETO | Product Value | Date Added on Product | Category Match | Tandem Sense Check | VANI Transcript | Notes |
|-----------|------------|------|-------------|-----|---------------|----------------------|----------------|-------------------|-----------------|-------|
{{#each spec_rows}}
| {{spec_name}} | {{spec_value}} | {{spec_type}} | {{fill_source}} | {{eto_attribute}} | {{source_product_value}} | {{date_added_on_product}} | {{category_match_status}} | {{tandem_sense_check}} | {{vani_transcript_status}} | {{notes}} |
{{/each}}

{{else}}
Specs not investigated in this report.
{{/if}}

---

## BL Title

{{#if title_investigated}}

| Field                  | Value                        |
|------------------------|------------------------------|
| BL Title               | {{bl_title}}                 |
| Source Product Title   | {{source_product_title}}     |
| Title Match Status     | {{title_match_status}}       |
| Category Alignment     | {{category_alignment}}       |
| Absurdity Flag         | {{absurdity_flag}}           |
| Absurdity Reason       | {{absurdity_reason}}         |

**Spec Contradictions Found:**
{{#if spec_contradictions}}
{{#each spec_contradictions}}
- {{spec_name}}: title says "{{title_says}}" — spec says "{{spec_says}}"
{{/each}}
{{else}}
None found.
{{/if}}

**Overall Observation:** {{overall_observation}}

{{else}}
BL Title not investigated in this report.
{{/if}}

---

## AOV

{{#if aov_investigated}}

| Field                  | Value                        |
|------------------------|------------------------------|
| BL AOV (Actual)        | {{bl_aov}}                   |
| Category Median Price  | {{category_median_price}}    |
| Product Price          | {{product_price}}            |
| Price Used for Calc    | {{price_used_for_calc}}      |
| BL Quantity            | {{bl_quantity}}              |
| Expected AOV           | {{expected_aov}}             |
| Absolute Deviation     | {{absolute_deviation}}       |
| Percentage Deviation   | {{percentage_deviation}}%    |
| Category Sanity Check  | {{category_sanity_check}}    |

**Inference:** {{inference}}

{{else}}
AOV not investigated in this report.
{{/if}}

---

*This report presents facts and inferences only. No attribute is concluded as
definitively correct or incorrect. Analyst judgement is required.*
