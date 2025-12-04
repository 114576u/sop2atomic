"""
Prompt builder for SOP → Atomic mapping.

This module constructs:
  - system instructions
  - user content
based on SOP data + atomic catalogue.
"""

from typing import List, Dict, Any


def build_system_prompt() -> str:
    """Return the system instructions for the LLM."""
    return (
        "You are an expert Business Analyst for investment reporting.\n"
        "You receive:\n"
        "1) A Standard Operating Procedure (SOP).\n"
        "2) A catalogue of 'atomic components'.\n\n"
        "Your task:\n"
        "- Break each SOP step into atomic actions.\n"
        "- Match each action with EXACTLY one component.\n"
        "- Fill parameter values when possible; use null when unknown.\n"
        "- If no component fits, output component_name='MISSING_COMPONENT'.\n\n"
        "Output STRICT JSON following the provided schema."
    )


def build_user_prompt(sop: Dict[str, Any], catalogue: List[Dict[str, Any]]) -> str:
    """Return the user message containing SOP steps + atomic catalogue."""
    sop_card = sop.get("sop_card", {})
    steps = sop.get("steps", [])

    lines = ["SOP CARD:"]
    for k, v in sop_card.items():
        lines.append(f"- {k}: {v}")

    lines.append("\nSOP STEPS:")
    for s in steps:
        lines.append(f"Step {s['step_number']}: {s['action']}")
        lines.append(f"Notes: {s['notes']}")

    lines.append("\nATOMIC COMPONENTS:")
    for c in catalogue:
        lines.append(
            f"- {c['id']} | {c['id_name']} | {c['category']} | params={c['parameters']}"
        )

    return "\n".join(lines)
