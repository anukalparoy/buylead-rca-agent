# System Spec List

These specs appear on every BL regardless of category. They are auto-filled by the
platform (LEAP) and are never defined in mcat_spec_rules.

Do not compare these against category specs. Do not flag a mismatch for these fields.
Record fill source only, as you would for any other spec field.

## Exempt specs

| Spec Name                 | Fill mechanism         | Notes                                          |
|---------------------------|------------------------|------------------------------------------------|
| Business Type             | Auto-filled by LEAP    | Platform-level field; not category-specific    |
| Probable Requirement Type | Auto-filled by LEAP    | Platform-level field; not category-specific    |
| Probable Order Value      | Auto-filled by LEAP    | Reasonableness checked separately via AOV tool |

## How to handle these in the skill

1. When classifying specs in step 1 of the Core Workflow, check spec_name against
   this list first.
2. If the spec_name matches any entry above, mark spec_type as "System Spec".
3. Skip the category alignment check (step 4) entirely for these fields.
4. Still record the fill source (step 2) and eto_attribute for completeness.
5. For Probable Order Value specifically — note in the report that AOV reasonableness
   is evaluated separately via the AOV tool, not within this skill.