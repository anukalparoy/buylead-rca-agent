# Impact Analysis — BL RCA Skill

## Measurable Outcome

| Metric | Baseline | With Agent |
|--------|----------|------------|
| Time per RCA | ~15 minutes | ~2 minutes |
| Tools opened manually | 4–6 | 0 |
| Data sources cross-referenced | Manual, sequential | Automated, on demand |
| Consistency | Analyst-dependent | Skill-driven, reproducible |

---

## Trigger Prompt Tests

### Positive Test 1 — Spec Investigation

**Prompt entered:**
```
BL Display ID: 141841319146
Issue: specs
```

**Expected behaviour:** Skill fires. Agent fetches BL specs, source product data,
and category schema on demand. Returns per-spec fact table with fill source,
category match status, and tandem sense check.

**Observed behaviour:** ✅ Skill fired correctly.
- Agent called `fetch_bl_specs` → `fetch_source_product_full` → `fetch_category_schema`
  in 3 iterations
- Correctly identified Probable Order Value as a system spec — excluded from
  category comparison
- Correctly attributed Quantity, Quantity Unit, Variety to LEAP deleted source (eto 250)
- Correctly identified contradiction between Variety spec ("1121") and
  Buyer Filled Details ("buyer not aware of specific varieties")
- No false flags raised
- Completed in under 2 minutes

---

### Positive Test 2 — Full Investigation

**Prompt entered:**
```
BL Display ID: 141821371595
Issue: all
```

**Expected behaviour:** Skill fires. Agent investigates specs, BL title, and AOV.
Returns three-section report.

**Observed behaviour:** ✅ Skill fired correctly.
- Specs: All 5 category specs correctly attributed. System specs (Probable Order
  Value, Probable Requirement Type) correctly excluded. No false flags.
- Title: "India Basmati Rice" correctly aligned with category and specs. No
  contradictions found. Source product unavailable — handled gracefully.
- AOV: Evidence unavailable for this BL — agent stated this clearly rather than
  hallucinating a result.
- Completed in under 2 minutes

---

### Negative Test — Prompt That Should Not Trigger Skill

**Prompt entered:**
```
What is the median order value for the Basmati Rice category?
```

**Expected behaviour:** Skill should NOT fire. This is a general data query,
not a buylead quality investigation. No BL ID provided, no quality issue stated.

**Observed behaviour:** ✅ Skill correctly did not fire.
- No RCA report generated
- Agent responded with a general answer using available context
- Skill activation condition ("buylead flagged for review") was not met

---

## Edge Cases Verified

| Edge Case | Behaviour |
|-----------|-----------|
| BL older than 30 days — specs not retained | Agent returns one-line message; no empty table |
| BL not found in live table | Agent falls back to expired table automatically |
| Source product deleted (eto 250) | Flagged as unverifiable; no false verdict |
| AOV evidence unavailable | Stated clearly; no hallucinated calculation |
| System specs present | Correctly excluded from category comparison |
| Spec not defined in category schema | Presented as fact only; not flagged as wrong |

---

## Second Workflow — Catalog QA

The same skill (`bl-rca`) applies to Catalog QA spec validation with zero
modification. The Catalog QA team passes a product modid instead of a BL ID
and gets a spec completeness RCA against seller-side category definitions.

This demonstrates the skill is built around a transferable reasoning pattern,
not BL-specific logic.

See `references/second-workflow-walkthrough.md` for the full input mapping.