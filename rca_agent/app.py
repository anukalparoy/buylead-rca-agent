import sys
import os
import json
from pathlib import Path

import streamlit as st

# --- Secrets: works locally via .env and on Streamlit Cloud via st.secrets ---
def load_secrets():
    try:
        # Streamlit Cloud
        for key, val in st.secrets.items():
            os.environ.setdefault(key, val)
    except Exception:
        # Local — dotenv handles it
        from dotenv import load_dotenv
        load_dotenv()

load_secrets()

from rca_agent.tools import fetch_bl_core, fetch_bl_core_expired
from rca_agent.skill_reader import read_skill
from rca_agent.llm_agent import (
    call_llm,
    execute_tool,
    TOOL_DEFINITIONS,
)

# --- Page config ---
st.set_page_config(
    page_title="BL RCA Agent",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Buylead RCA Agent")
st.caption("Investigates poor quality buyleads and surfaces root causes in under 2 minutes.")

# --- Input form ---
with st.form("rca_form"):
    bl_id = st.text_input("BL Display ID", placeholder="e.g. 141841319146")
    issue = st.selectbox(
        "Attribute to investigate",
        options=["all", "specs", "title", "aov"],
        format_func=lambda x: {
            "all": "All — Specs, Title and AOV",
            "specs": "Specs only",
            "title": "BL Title only",
            "aov": "AOV only",
        }[x],
    )
    submitted = st.form_submit_button("Run RCA", type="primary")

# --- Agent runner with live tool call updates ---
def run_agent_with_updates(skill_text, bl_core, bl_display_id, user_issue, tool_log):
    import json as _json
    import requests

    BASE_URL = os.getenv("IMLLM_BASE_URL", "https://imllm.intermesh.net")
    API_URL = f"{BASE_URL.rstrip('/')}/v1/chat/completions"
    GPT_API_KEY = os.getenv("LLM_GATEWAY_API_KEY")
    MODEL = os.getenv("LLM_MODEL", "google/gemini-2.5-pro")

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
"""

    initial_user_message = f"""
Investigate this buylead.

BL Display ID: {bl_display_id}
Issue to investigate: {user_issue}

BL Core Data:
{_json.dumps(bl_core, indent=2, default=str)}

Use the available tools to fetch what you need. Start by deciding which tools
are relevant for the issue selected, then call them. Reason over the results
and produce the RCA report.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": initial_user_message},
    ]

    max_iterations = 8
    for i in range(max_iterations):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GPT_API_KEY}",
        }
        payload = {
            "model": MODEL,
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.1,
            "tools": TOOL_DEFINITIONS,
            "tool_choice": "auto",
        }
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        response_message = response.json()["choices"][0]["message"]
        messages.append(response_message)

        tool_calls = response_message.get("tool_calls")

        if not tool_calls:
            return response_message.get("content", "No response generated.")

        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = _json.loads(tool_call["function"]["arguments"])

            tool_log.write(f"→ `{tool_name}` called with `{tool_args}`\n\n")

            result = execute_tool(tool_name, tool_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": _json.dumps(result, default=str),
            })

    return "Agent reached maximum iterations without producing a final answer."


# --- Main execution ---
if submitted:
    if not bl_id.strip():
        st.error("Please enter a BL Display ID.")
    else:
        # Fetch BL core
        with st.spinner("Fetching BL data..."):
            bl_core_rows = fetch_bl_core(bl_id.strip())
            if not bl_core_rows:
                bl_core_rows = fetch_bl_core_expired(bl_id.strip())

        if not bl_core_rows:
            st.error(f"No BL found for ID: {bl_id}. Please check the ID and try again.")
        else:
            bl_core = bl_core_rows[0]

            # Show BL summary
            st.divider()
            col1, col2, col3 = st.columns(3)
            col1.metric("BL Title", bl_core.get("bl_title", "N/A"))
            col2.metric("Category", bl_core.get("bl_mcat_name", "N/A"))
            col3.metric("Source Product", bl_core.get("source_product_display_id", "None"))

            st.divider()

            # Run agent
            skill_text = read_skill()

            with st.status("Agent is running...", expanded=True) as status:
                st.write(f"**BL ID:** {bl_id} | **Issue:** {issue}")
                st.write("---")
                tool_log = st.empty()
                tool_messages = []

                class ToolLogger:
                    def write(self, text):
                        tool_messages.append(text)
                        tool_log.markdown("".join(tool_messages))

                    def flush(self):
                        pass

                logger = ToolLogger()

                report = run_agent_with_updates(
                    skill_text=skill_text,
                    bl_core=bl_core,
                    bl_display_id=bl_id.strip(),
                    user_issue=issue,
                    tool_log=logger,
                )
                status.update(label="RCA complete", state="complete")

            # Show report
            st.divider()
            st.subheader("RCA Report")
            st.markdown(report)

            # Download button
            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"rca_{bl_id}.md",
                mime="text/markdown",
            )