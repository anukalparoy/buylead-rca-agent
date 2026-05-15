# Output Schema

Defines the exact fields and types for the BL RCA fact summary report.
One section per attribute investigated.


## Specs Section

One row per spec field in bl_spec_data.

| Field                    | Type    | Description                                                               |
|--------------------------|---------|---------------------------------------------------------------------------|
| spec_name                | string  | Name of the spec field                                                    |
| spec_value               | string  | Value as it appears on the BL                                             |
| spec_type                | enum    | "System Spec" or "Category Spec"                                          |
| fill_source              | string  | Plain label: Buyer Filled / Agent Filled / VANI / Auto-filled by LEAP / Predicted by Model / Aggregated from Delayed BL |
| eto_attribute            | integer | Raw eto_attribute code for traceability                                   |
| source_product_value     | string  | Spec value from source product; blank if not a LEAP product-sourced spec  |
| date_added_on_product    | date    | When this spec was added on the source product; blank if not applicable   |
| category_match_status    | enum    | "Matches category spec" / "Does not match category spec" / "Not defined in category spec" / "N/A (System Spec)" |
| tandem_sense_check       | string  | Observation on whether spec makes sense given BL title and category together; blank for system specs |
| vani_transcript_status   | enum    | "Confirmed in transcript" / "Not found in transcript" / "Transcript not checked" / "N/A" |
| notes                    | string  | Any additional observation: mismatches, unverifiable sources, anomalies   |

Specs summary (one paragraph):
- Distribution of fill sources across all specs
- Any tensions observed between specs, title, and category
- Count of specs confirmed vs not confirmed in transcript (if checked)


## BL Title Section

| Field                    | Type    | Description                                                               |
|--------------------------|---------|---------------------------------------------------------------------------|
| bl_title                 | string  | Title as it appears on the BL                                             |
| source_product_title     | string  | Title from the source product; blank if no product source                 |
| title_match_status       | enum    | "Exact match" / "Partial match" / "Mismatch" / "No product source"       |
| category_alignment       | enum    | "Aligned" / "Misaligned" / "Unable to determine"                         |
| spec_contradictions      | list    | Each contradiction as: {spec_name, title_says, spec_says}; empty if none |
| absurdity_flag           | boolean | true if title is unintelligible, placeholder, or entirely off             |
| absurdity_reason         | string  | Reason for absurdity flag; blank if false                                 |
| overall_observation      | string  | One sentence summarising the title situation                              |


## AOV Section

| Field                    | Type    | Description                                                               |
|--------------------------|---------|---------------------------------------------------------------------------|
| bl_aov                   | number  | AOV as it appears on the BL                                               |
| category_median_price    | number  | Median unit price for the BL's category                                   |
| product_price            | number  | Price of the source product; blank if unavailable                         |
| price_used_for_calc      | enum    | "Product price" / "Category median price (fallback)"                     |
| bl_quantity              | number  | Quantity filled by the buyer on the BL                                    |
| expected_aov             | number  | Calculated as product_price × bl_quantity (or fallback × bl_quantity)    |
| absolute_deviation       | number  | bl_aov − expected_aov                                                     |
| percentage_deviation     | number  | (absolute_deviation / expected_aov) × 100                                |
| category_sanity_check    | enum    | "Within expected range" / "Potentially off — higher than expected" / "Potentially off — lower than expected" |
| inference                | string  | Probable explanation for deviation; blank if AOV appears consistent      |


## Report Metadata

| Field                    | Type     | Description                               |
|--------------------------|----------|-------------------------------------------|
| buylead_id               | string   | BL under investigation                    |
| investigated_at          | datetime | Timestamp of report generation            |
| attributes_investigated  | list     | One or more of: specs, bl_title, aov      |
| investigated_by          | string   | Agent ID or system identifier             |
