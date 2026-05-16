import os
import json
import requests
from dotenv import load_dotenv
from rca_agent.tools import (
    fetch_bl_specs,
    fetch_source_product_core,
    fetch_source_product_full,
    fetch_category_schema,
    fetch_aov_evidence,
)

load_dotenv()

BASE_URL = os.getenv("IMLLM_BASE_URL", "https://imllm.intermesh.net")
API_URL = f"{BASE_URL.rstrip('/')}/v1/chat/completions"
GPT_API_KEY = os.getenv("LLM_GATEWAY_API_KEY")
MODEL = os.getenv("LLM_MODEL", "google/gemini-2.5-pro")

# --- Tool definitions for the LLM ---

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_bl_specs",
            "description": (
                "Fetch all spec fields on the buylead including spec name, "
                "spec value, and eto_attribute source code. Call this when "
                "investigating specs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "bl_display_id": {
                        "type": "string",
                        "description": "The buylead display ID.",
                    }
                },
                "required": ["bl_display_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_source_product_core",
            "description": (
                "Fetch core data from the source product linked to this buylead: "
                "product title, price, category. Call this when investigating "
                "BL title or AOV, or when specs appear to be product-sourced."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_display_id": {
                        "type": "string",
                        "description": "The source product display ID from bl_core.",
                    }
                },
                "required": ["product_display_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_source_product_full",
            "description": (
                "Fetch the full spec list of the source product including spec "
                "names, values, and dates added. Call this when comparing "
                "product specs against BL specs in detail."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_display_id": {
                        "type": "string",
                        "description": "The source product display ID from bl_core.",
                    }
                },
                "required": ["product_display_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_category_schema",
            "description": (
                "Fetch the buyer-side category spec definitions for the BL's MCAT "
                "category: which spec fields are defined, their allowed values, "
                "and whether they are mandatory. Call this when you need to check "
                "if a spec is defined for the category. Do not call upfront — "
                "call only when spec investigation requires it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "mcat_id": {
                        "type": "integer",
                        "description": "The MCAT category ID from bl_core.",
                    }
                },
                "required": ["mcat_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_aov_evidence",
            "description": (
                "Fetch AOV model evidence for the buylead: category median price, "
                "product price, expected AOV range. Call this only when "
                "investigating AOV."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "bl_display_id": {
                        "type": "string",
                        "description": "The buylead display ID.",
                    }
                },
                "required": ["bl_display_id"],
            },
        },
    },
]

# --- Tool executor ---

TOOL_FUNCTIONS = {
    "fetch_bl_specs": lambda args: fetch_bl_specs(args["bl_display_id"]),
    "fetch_source_product_core": lambda args: fetch_source_product_core(args["product_display_id"]),
    "fetch_source_product_full": lambda args: fetch_source_product_full(args["product_display_id"]),
    "fetch_category_schema": lambda args: fetch_category_schema(args["mcat_id"]),
    "fetch_aov_evidence": lambda args: fetch_aov_evidence(args["bl_display_id"]),
}


def execute_tool(tool_name, tool_args):
    fn = TOOL_FUNCTIONS.get(tool_name)
    if not fn:
        return {"error": f"Unknown tool: {tool_name}"}
    try:
        result = fn(tool_args)
        return result if result else {"note": "No data returned for this query."}
    except Exception as e:
        return {"error": str(e)}


# --- LLM call ---

def call_llm(messages, tools=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GPT_API_KEY}",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 4000,
        "temperature": 0.1,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]


# --- Agentic loop ---

def run_rca_agent(skill_text, bl_core, bl_display_id, user_issue):
    system_prompt = f"""
You are a Buylead RCA Agent. Your job is to investigate a flagged buylead and
produce a precise, fact-based RCA summary.

Follow these instructions exactly:

{skill_text}

Additional rules:
- Do not pre-judge any attribute as wrong. Fetch evidence first, then reason.
- Specs like Business Type, Probable Requirement Type, Probable Order Value are
  system specs — never flag these as wrong or compare them against category specs.
- A spec not defined in the category schema does not mean it is wrong. Present
  it as a fact only.
- Call fetch_category_schema only when you need to check spec definitions.
  Do not call it upfront for every investigation.
- If a source product exists, use product_display_id from bl_core to fetch it.
- Separate facts from inferences in your output.
- If no issue is found from the evidence, say so clearly.
- If fetch_bl_specs returns empty or no rows, do not produce a spec table.
  Write exactly one line: "Spec data is not available for this buylead —
  specs are only retained for the last 30 days." Then move on to the next
  attribute if selected. Do not attempt any spec reasoning.
- Always include bl_date, call_recording, and referred_page from bl_core in the
  report header. Render call_recording and referred_page as markdown hyperlinks
  — [Listen to Recording](url) and [View Page](url). Skip the link if the value
  is null or empty.

"""

    initial_user_message = f"""
Investigate this buylead.

BL Display ID: {bl_display_id}
Issue to investigate: {user_issue}

BL Core Data:
{json.dumps(bl_core, indent=2, default=str)}

Use the available tools to fetch what you need. Start by deciding which tools
are relevant for the issue selected, then call them. Reason over the results
and produce the RCA report.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": initial_user_message},
    ]

    print("\n--- Agent starting ---")

    # Agentic loop — runs until LLM stops calling tools
    max_iterations = 8
    for i in range(max_iterations):
        response_message = call_llm(messages, tools=TOOL_DEFINITIONS)
        messages.append(response_message)

        tool_calls = response_message.get("tool_calls")

        if not tool_calls:
            # LLM has stopped calling tools — this is the final answer
            print(f"--- Agent completed in {i + 1} iteration(s) ---\n")
            return response_message.get("content", "No response generated.")

        # Execute each tool the LLM requested
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])

            print(f"  → Calling tool: {tool_name}({tool_args})")

            result = execute_tool(tool_name, tool_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": json.dumps(result, default=str),
            })

    return "Agent reached maximum iterations without producing a final answer."