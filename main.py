from rca_agent.tools import fetch_bl_core, fetch_bl_core_expired
from rca_agent.skill_reader import read_skill
from rca_agent.llm_agent import run_rca_agent

# Agentic setup — no validators, no planner, no pre-classification.
# The LLM reads the skill, decides which tools to call, and reasons over
# the results itself.

bl_display_id = input("Enter BL Display ID: ")
user_issue = input("Issue to investigate? specs/title/aov/all: ").strip().lower() or "all"

bl_core_rows = fetch_bl_core(bl_display_id)

if not bl_core_rows:
    bl_core_rows = fetch_bl_core_expired(bl_display_id)

if not bl_core_rows:
    raise Exception("No BL found in live or expired tables.")

bl_core = bl_core_rows[0]
skill_text = read_skill()

final_rca = run_rca_agent(
    skill_text=skill_text,
    bl_core=bl_core,
    bl_display_id=bl_display_id,
    user_issue=user_issue,
)

print("\n========== FINAL RCA ==========\n")
print(final_rca)