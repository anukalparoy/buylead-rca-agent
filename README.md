# Buylead RCA Agent

An agentic AI system that performs root cause analysis on poor quality buyleads
in under 2 minutes — replacing a manual process that takes 15 minutes per buylead.

---

## The Problem

When a buylead is flagged for poor quality, a Quality Analyst manually investigates:
- Where did the specs come from?
- Does the BL title make sense against the specs and category?
- Is the AOV reasonable?

This involves opening multiple internal tools, cross-referencing data sources, and
applying judgment. On average it takes **15 minutes per buylead** across hundreds
of flagged BLs per day.

---

## The Solution

The BL RCA Agent takes a Buylead ID, decides which data to fetch, reasons over
the evidence using a structured skill, and returns a precise fact summary in
**under 2 minutes**.

It investigates three attributes:
- **Specs** — where each spec came from (buyer, LEAP, VANI, agent, model), whether
  it aligns with the category, and whether it makes sense against the BL title
- **BL Title** — source product comparison, category alignment, spec contradictions
- **AOV** — expected vs actual calculation with inference on deviation

---

## Results

| Metric | Before | After |
|--------|--------|-------|
| Time per RCA | ~15 minutes | ~2 minutes |
| Data sources checked | Manual, one by one | Automated, in parallel |
| Consistency | Analyst-dependent | Skill-driven, reproducible |

---

## How It Works

```
User enters BL ID + attribute to investigate
        ↓
fetch_data.py fetches BL core (title, category, source product ID)
        ↓
Agent reads SKILL.md and decides which tools to call
        ↓
Agent calls tools on demand (specs, product data, category schema)
        ↓
Agent reasons over evidence and produces structured RCA report
```

The agent is built on an agentic loop — it is not a fixed workflow. It decides
what to fetch based on what it finds, in the same way an analyst would.

---

## Skill

The core reasoning lives in `buylead-rca-skill/SKILL.md`. It follows Anthropic's
canonical skill format and covers:

- Source classification using eto_attribute codes
- System spec exemption (Business Type, Probable Order Value, Probable Requirement Type)
- Buyer spec tandem check against title and category together
- LEAP product spec trace with date comparison
- VANI spec verification against call transcript (on-demand)
- Title absurdity and contradiction detection
- AOV calculation and inference

The same skill applies to Catalog QA spec validation without modification —
see `buylead-rca-skill/references/second-workflow-walkthrough.md`.

---

## Project Structure

```
buylead_rca_agent/
├── app.py                          — Streamlit web app
├── main.py                         — CLI entry point
├── requirements.txt
├── buylead-rca-skill/
│   ├── SKILL.md                    — Core reasoning skill
│   ├── scripts/
│   │   ├── fetch_data.py           — Fetches BL core data
│   │   └── run_agent.py            — Runs agentic RCA loop
│   ├── references/
│   │   ├── eto-attribute-codes.md  — Spec source classification
│   │   ├── system-spec-list.md     — System specs exempt from checks
│   │   ├── output-schema.md        — Report field definitions
│   │   └── second-workflow-walkthrough.md
│   └── assets/
│       └── rca-report-template.md
└── rca_agent/
    ├── llm_agent.py                — Agentic loop with tool calling
    ├── tools.py                    — Redash query wrappers
    ├── skill_reader.py             — Loads SKILL.md
    └── redash_client.py            — Redash API client
```

---

## Running Locally

**Prerequisites:** Python 3.9+, access to IndiaMart Redash and LLM Gateway

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Fill in your API keys in .env

# Option 1 — CLI
python main.py

# Option 2 — Two-step scripts
python buylead-rca-skill/scripts/fetch_data.py --bl_id 141841319146 --out bl_core.json
python buylead-rca-skill/scripts/run_agent.py --bl_core bl_core.json --issue specs --out rca_report.md

# Option 3 — Web app
streamlit run app.py
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `REDASH_BASE_URL` | Base URL of the Redash instance |
| `REDASH_API_KEY` | Redash API key |
| `IMLLM_BASE_URL` | IndiaMart LLM Gateway base URL |
| `LLM_GATEWAY_API_KEY` | LLM Gateway API key |
| `LLM_MODEL` | Model to use (default: google/gemini-2.5-pro) |
| `QUERY_BL_CORE` | Redash query ID for BL core data |
| `QUERY_BL_CORE_EXPIRED` | Redash query ID for expired BL core data |
| `QUERY_BL_SPECS` | Redash query ID for BL specs |
| `QUERY_SOURCE_PRODUCT_CORE` | Redash query ID for source product core |
| `QUERY_SOURCE_PRODUCT_FULL` | Redash query ID for source product specs |
| `QUERY_CATEGORY_SCHEMA` | Redash query ID for category spec rules |
| `QUERY_AOV_EVIDENCE` | Redash query ID for AOV evidence |

---

## Second Workflow — Catalog QA

The same skill applies to Catalog QA spec validation with zero modification.
Instead of a BL ID, the Catalog QA team passes a product modid and gets a
spec completeness RCA against seller-side category definitions.

See `buylead-rca-skill/references/second-workflow-walkthrough.md` for details.

---

*Built for IndiaMart Hackathon 2026 — Solo submission*