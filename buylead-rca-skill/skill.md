---
name: bl-rca
description: >
  Use this skill when a buylead attribute has been flagged for review and you need
  to understand what is captured, how it got there, and whether it appears off.
  Trigger phrases: "RCA for buylead", "spec is wrong on BL", "wrong spec on buylead",
  "BL title seems wrong", "AOV seems off", "incorrect spec", "buylead quality issue".
  Supports three attributes: Specs, BL Title, AOV. Returns a structured fact summary
  with reasoning and inferences per attribute.
---

1. Run scripts/fetch_data.py with the BL ID to fetch base BL context (bl_core).
2. Run scripts/run_agent.py with the bl_core output and the issue to investigate.
3. The agent reads this skill, decides which tools to call, and fetches data on demand.
4. Where on-demand tool calls are indicated, wait for user confirmation before calling.
5. Compile the report using assets/rca-report-template.md.


## Inputs

Base inputs (always pre-fetched before skill runs):

- buylead_id
- bl_date — date the buylead was created
- call_recording — link to the call recording associated with this BL; null if none
- referred_page — link to the page from which this BL was referred; null if none
- selected_attributes — one or more of: specs, bl_title, aov
- bl_spec_data — list of spec fields; each entry contains:
    - spec_name, spec_value, eto_attribute
- bl_title — the title as it appears on the BL
- bl_category — the MCAT category assigned to the BL
- bl_aov — the AOV value on the BL
- bl_quantity — quantity value filled by the buyer on the BL
- source_product_data — data from the source product (if BL originated from a product):
    - product_title
    - product_modid
    - product_price
    - product_specs (list of spec_name, spec_value, date_added)
- mcat_spec_rules — buyer-side category specs (spec_name, allowed_values, value_type, is_mandatory)
- category_median_price — median price for the BL's category

On-demand inputs (fetched only when user confirms):

- seller_category_specs — seller-side category spec definitions; fetch only when
  investigating product-sourced specs and user wants this comparison
- vani_call_transcript — transcript or summary of the VANI call linked to this BL;
  fetch only when "Buyer Filled Details" spec is present and user wants to verify
- call_recording — audio or full transcript of the call; fetch only when user
  explicitly requests recording review after transcript check


## Outputs

A structured report containing:
- Header: buylead_id, bl_date, call_recording link (if available), referred_page link (if available)
- One section per investigated attribute:
  - Specs section: per-spec fact table, summary paragraph, conditional category and product spec tables
  - BL Title section: source comparison, tandem check result, absurdity flag if applicable
  - AOV section: expected AOV calculation, actual vs expected comparison, inference

Use the template in assets/rca-report-template.md.


## Environment Variables

REDASH_API_KEY               — API key for Redash query execution
REDASH_BASE_URL              — Base URL of the Redash instance
BL_SPEC_QUERY_ID             — Returns BL spec fields with eto_attribute
MCAT_SPEC_QUERY_ID           — Returns buyer-side MCAT spec rules for the category
SOURCE_PRODUCT_QUERY_ID      — Returns source product title, price, specs with dates
CATEGORY_MEDIAN_PRICE_QUERY_ID — Returns median price for the BL category
SELLER_CATEGORY_SPEC_QUERY_ID — Returns seller-side category spec definitions (on-demand)
VANI_TRANSCRIPT_QUERY_ID     — Returns VANI call transcript or summary (on-demand)
CALL_RECORDING_QUERY_ID      — Returns call recording or full transcript (on-demand)


## Core Workflow

---

### ATTRIBUTE 1 — Specs

#### Step S1. Check if specs are available

If fetch_bl_specs returns empty or no rows, do not produce a spec table.
Instead write exactly this and move on:

  "Spec data is not available for this buylead. BL specs are only retained for
  buyleads created in the last 30 days. Spec investigation cannot be performed."

Do not attempt steps S2–S6. Proceed to the next selected attribute if any.

If specs are returned, split bl_spec_data into two groups using
references/system-spec-list.md:

- System specs (Business Type, Probable Requirement Type, Probable Order Value):
  record fill source only; skip all further steps for these fields.
- Category specs: proceed with steps S2–S5.

Also identify any spec named "Buyer Filled Details" — handle separately in step S5.


#### Step S2. Classify fill source

For each category spec, read eto_attribute and map to a source class using
references/eto-attribute-codes.md. Record source class and plain label.


#### Step S3. For buyer-filled specs — tandem sense check

For specs with source class BUYER (1–199, 202–205, 999):

1. Check spec_value against mcat_spec_rules for this spec_name.
   Record whether value: matches category spec / does not match / not defined in category.

2. Additionally, check whether the spec value makes sense in the context of both
   bl_title and bl_category together:
   - Does the spec value contradict anything implied by the BL title?
     Example: title mentions "heavy duty industrial pump" but spec says capacity 0.5 litres.
   - Does the spec combination as a whole appear coherent for the category?
   Record observations as facts. Do not conclude the spec is wrong — note the tension
   if one exists.


#### Step S4. For product-sourced specs — source trace

For specs with source class LEAP and eto_attribute 230, 240, or 260:

1. Find spec_name in source_product_data.product_specs.
   - Found, same value → spec was copied correctly from the product.
     Note the date_added of that spec on the product.
   - Found, different value → value changed during extraction or mapping.
     Note both values and the date_added of the product spec.
   - Not found → LEAP mapped a field not present on the source product.
     Note this.

2. Ask user: "Do you want to compare product specs against seller-side category
   specs to check if the product spec itself is correctly defined?"
   If yes → call SELLER_CATEGORY_SPEC_QUERY_ID (on-demand).
   Once fetched, check whether the product spec value aligns with the seller-side
   category spec definition. Record match / mismatch / not defined as a fact.
   Do not conclude the BL spec is wrong based on this alone.


#### Step S5. For "Buyer Filled Details" spec — VANI verification

If a spec named "Buyer Filled Details" is present:

1. Check the eto_attribute. If it falls in the VANI range (212–215), note that
   this spec is expected to have originated from a VANI call.
2. Present to user: "This spec was filled by VANI. Do you want to check the call
   transcript to verify this detail was discussed in the call?"
   If yes → call VANI_TRANSCRIPT_QUERY_ID (on-demand).
   Check whether the spec value appears in the transcript summary.
   Record: confirmed in transcript / not found in transcript / transcript unavailable.
3. Present to user: "Do you want to listen to the call recording to confirm?"
   If yes → call CALL_RECORDING_QUERY_ID (on-demand).
   This is a separate step — do not call this automatically after the transcript.


#### Step S6. Compile specs section of report

For each spec field produce one row in this exact column order:
spec_name | spec_value | spec_type | fill_source | category_match_status |
source_product_value | date_added_on_product | tandem_sense_check

Do not include eto_attribute, vani_transcript_status, or notes columns.

Then write a summary paragraph: how many specs were buyer-filled, how many were
product-sourced, any tensions observed across specs, title, and category.

After the spec table and summary, add the following conditional tables:

**Conditional Table 1 — Category Specs**
Show this table if any spec in the BL has category_match_status of "Matches category spec"
or "Does not match category spec" (i.e. the category schema was fetched and has data).
Show ALL specs defined for this MCAT category, not just the ones on the BL.

Format:
| Spec Name | Allowed Values |
where Allowed Values lists all valid values for that spec in comma-separated form.

**Conditional Table 2 — Source Product Specs**
Show this table if all category specs on the BL are product-sourced (LEAP eto_attribute
230, 240, or 260). Show ALL specs present on the source product, not just the ones
copied to the BL.

Format:
| Spec Name | Spec Values |
where Spec Values lists all values for that spec in comma-separated form.

---

### ATTRIBUTE 2 — BL Title

#### Step T1. Compare BL title against source product title

If source_product_data is available:
- Compare bl_title against source_product_data.product_title.
- Record: exact match / partial match / mismatch.
- A mismatch alone is not a finding. Proceed to step T2.

If no source product is linked, note this and proceed to T2 with bl_title only.


#### Step T2. Tandem check — title vs specs vs category

Check the BL title in the context of bl_category and bl_spec_data together:

1. Does the title align with the assigned category?
   Example: title says "Ladies Kurti" but category is "Industrial Machinery" →
   flag as likely category-title mismatch.

2. Does the title contradict any specific spec value?
   Go through bl_spec_data and look for direct contradictions:
   - Numeric contradictions: title mentions a quantity or capacity that differs from
     the corresponding spec value. Example: title says "20kg" but spec says "10kg capacity".
   - Product type contradictions: title names a product variant that is inconsistent
     with what the specs describe.
   Record each contradiction found as a specific fact: which spec, what the title says,
   what the spec says.

3. Is the title absurd on its own?
   Flag only if the title is clearly unintelligible, a placeholder, or entirely
   unrelated to any recognisable product or category.
   Do not flag a title as wrong just because it is short or informal.


#### Step T3. Compile title section of report

Record:
- bl_title
- source_product_title (if available) and match status
- category alignment: aligned / misaligned / unable to determine
- spec contradictions found: list each one specifically, or "none found"
- absurdity flag: yes / no, with reason if yes
- overall observation: one sentence summarising the title situation

---

### ATTRIBUTE 3 — AOV

#### Step A1. Sanity check against category

Compare bl_aov against category_median_price:
- If bl_aov is within a reasonable band of category_median_price
  (accounting for quantity), record as: within expected range.
- If bl_aov is significantly higher or lower, flag as: potentially off, and
  note the direction and magnitude of deviation.
This step uses category_median_price only — no calculation yet.


#### Step A2. Calculate expected AOV

Expected AOV is derived from three inputs:
- category_median_price — the median unit price for this category
- source_product_data.product_price — the price of the specific product enquired
- bl_quantity — the quantity the buyer filled on the BL

Calculation:
  expected_aov = product_price × bl_quantity

If product_price is unavailable, fall back to:
  expected_aov = category_median_price × bl_quantity

Record:
- product_price used (or category_median_price if fallback)
- bl_quantity
- expected_aov calculated
- bl_aov (actual)
- difference: bl_aov − expected_aov, and percentage deviation


#### Step A3. Inference

Based on steps A1 and A2, produce an inference:
- If bl_aov ≈ expected_aov → AOV appears consistent with product price and quantity.
- If bl_aov >> expected_aov → possible causes: quantity entered is too high, product
  price is an outlier, or buyer specified a bulk order not reflected in standard pricing.
- If bl_aov << expected_aov → possible causes: quantity entered is too low, product
  price used is lower than actual market rate, or AOV was auto-filled from a
  different source.

State the inference clearly as a probable explanation, not a verdict.


#### Step A4. Compile AOV section of report

Record:
- bl_aov (actual)
- category_median_price
- product_price (or fallback used)
- bl_quantity
- expected_aov
- deviation (absolute and percentage)
- category sanity check result
- inference paragraph


## Features

| Feature                        | Description                                                          |
|--------------------------------|----------------------------------------------------------------------|
| System spec exemption          | Pre-filled specs excluded from category comparison                   |
| Buyer spec tandem check        | Checks spec values against title and category together, not in isolation |
| Product spec trace             | Shows product spec value, date added, and LEAP copy accuracy         |
| Seller spec comparison         | On-demand comparison of product specs vs seller-side category specs  |
| VANI spec verification         | Confirms Buyer Filled Details against call transcript (on-demand)    |
| Call recording review          | Separate on-demand tool to review call recording                     |
| Title tandem check             | Checks title against specs and category for contradictions           |
| AOV calculation                | Derives expected AOV from product price and quantity; compares to actual |
| Fact-only output               | No verdicts — observations and inferences only                       |


## Best Practices

- Never conclude a spec, title, or AOV is definitively wrong. Present facts and
  inferences; let the analyst decide.
- For buyer-filled specs, always do the tandem check with both title and category —
  checking against category rules alone misses spec-title contradictions.
- Do not call SELLER_CATEGORY_SPEC_QUERY_ID at the start. Call it only when the
  user is investigating product-sourced specs and explicitly wants this comparison.
- Do not call VANI_TRANSCRIPT_QUERY_ID or CALL_RECORDING_QUERY_ID automatically.
  Always present the option to the user and wait for confirmation.
- For AOV, always attempt the product_price-based calculation first. Use
  category_median_price as a fallback only if product_price is unavailable, and
  note the fallback in the report.
- A title mismatch with the source product is not a finding by itself. Only flag
  the title if a tandem check reveals an absurdity or a spec contradiction.
- For LEAP deleted BL source (250), note that the origin is unverifiable. Do not
  speculate on what the original value was.
- If eto_attribute is null or missing, record fill source as Unknown and set a
  note for manual investigation.
- If fetch_bl_specs returns empty, do not render a spec table or attempt any
  spec reasoning. Write the unavailability message and stop the specs section.
  This is expected behaviour for BLs older than 30 days — do not treat it as
  an error.


## Reference Files

| File                                      | Purpose                                                          |
|-------------------------------------------|------------------------------------------------------------------|
| references/eto-attribute-codes.md         | Full mapping of eto_attribute integers to source labels          |
| references/system-spec-list.md            | Pre-filled system specs exempt from category comparison          |
| references/output-schema.md               | Field definitions for the full RCA report                        |
| references/second-workflow-walkthrough.md | How this skill applies to Catalog QA spec validation             |
| assets/rca-report-template.md             | Report scaffold this skill fills in                              |
| scripts/fetch_data.py                     | Fetches bl_core for a given BL ID; outputs bl_core.json          |
| scripts/run_agent.py                      | Runs the agentic RCA loop; reads bl_core.json, writes rca_report.md |