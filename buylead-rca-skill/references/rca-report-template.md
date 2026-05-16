# BL RCA Report

**Buylead ID:** {{buylead_id}}
**BL Date:** {{bl_date}}
**Investigated at:** {{investigated_at}}
**Attributes investigated:** {{attributes_investigated}}
{{#if call_recording}}**Call Recording:** [Listen to Recording]({{call_recording}}){{/if}}
{{#if referred_page}}**Referred Page:** [View Page]({{referred_page}}){{/if}}

---

## Specs

{{#if specs_investigated}}

### Spec Table

| Spec Name | Spec Value | Type | Fill Source | Category Match | Product Value | Date Added on Product | Tandem Sense Check |
|-----------|------------|------|-------------|----------------|---------------|-----------------------|--------------------|
{{#each spec_rows}}
| {{spec_name}} | {{spec_value}} | {{spec_type}} | {{fill_source}} | {{category_match_status}} | {{source_product_value}} | {{date_added_on_product}} | {{tandem_sense_check}} |
{{/each}}

### Summary
{{specs_summary_paragraph}}

{{#if show_category_spec_table}}
### Category Specs — {{mcat_category_name}}

All specs defined for this category:

| Spec Name | Allowed Values |
|-----------|----------------|
{{#each category_spec_rows}}
| {{spec_name}} | {{allowed_values}} |
{{/each}}
{{/if}}

{{#if show_product_spec_table}}
### Source Product Specs — {{source_product_id}}

All specs on the source product:

| Spec Name | Spec Values |
|-----------|-------------|
{{#each product_spec_rows}}
| {{spec_name}} | {{spec_values}} |
{{/each}}
{{/if}}

{{else}}
Spec data is not available for this buylead. BL specs are only retained for
buyleads created in the last 30 days. Spec investigation cannot be performed.
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