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
    # NOTE: Keep this stable – it defines the contract for the JSON output.
    return (
        "You are an expert Business Analyst for investment reporting.\n"
        "You receive:\n"
        "1) A Standard Operating Procedure (SOP) with steps.\n"
        "2) A catalogue of 'atomic components' with IDs, names, categories, descriptions "
        "and parameters.\n\n"
        "Your task is to map each SOP step into one or more atomic actions:\n"
        "- For each SOP step, preserve the original wording.\n"
        "- Break the step into the minimal sequence of atomic actions needed.\n"
        "- For each atomic action, choose EXACTLY ONE component from the catalogue.\n"
        "- Fill parameter values when they can be inferred from the SOP. If unknown, set the value to null.\n"
        "- If no component fits, use component_id = null and component_name = \"MISSING_COMPONENT\" and describe "
        "what is needed.\n\n"
        "You MUST output STRICT JSON with this schema, and nothing else:\n"
        "{\n"
        '  \"sop_id\": string | null,\n'
        '  \"steps\": [\n'
        "    {\n"
        '      \"step_number\": string,\n'
        '      \"original_action\": string,\n'
        '      \"notes\": string,\n'
        '      \"atomic_actions\": [\n'
        "        {\n"
        '          \"component_id\": string | null,\n'
        '          \"component_name\": string,\n'
        '          \"category\": string | null,\n'
        '          \"parameters\": { string: string | null }\n'
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Do not include any explanations, comments or text outside this JSON object."
    )


def _format_sop_section(sop: Dict[str, Any]) -> str:
    """Format SOP card + steps as text for the user prompt."""
    sop_card = sop.get("sop_card", {})
    steps = sop.get("steps", [])

    lines: List[str] = []

    lines.append("SOP CARD:")
    for k, v in sop_card.items():
        lines.append(f"- {k}: {v}")

    lines.append("\nSOP STEPS:")
    for s in steps:
        step_number = s.get("step_number", "")
        action = s.get("action", "")
        notes = s.get("notes", "")
        lines.append(f"Step {step_number}: {action}")
        lines.append(f"Notes: {notes}")

    return "\n".join(lines)


def _format_catalogue_section(catalogue: List[Dict[str, Any]]) -> str:
    """Format the atomic components catalogue as a compact list."""
    lines: List[str] = []
    lines.append("ATOMIC COMPONENT CATALOGUE:")
    lines.append(
        "For each component: id | id_name | category | description | parameters"
    )

    for c in catalogue:
        cid = c.get("id", "")
        id_name = c.get("id_name", "")
        category = c.get("category", "")
        description = c.get("description", "")
        parameters = c.get("parameters", [])
        lines.append(
            f"- {cid} | {id_name} | {category} | {description} | params={parameters}"
        )

    return "\n".join(lines)


def build_user_prompt(sop: Dict[str, Any], catalogue: List[Dict[str, Any]]) -> str:
    """
    Return the user message containing SOP steps + atomic catalogue.

    This is the content that will be sent as the 'user' role message.
    """
    sop_text = _format_sop_section(sop)
    catalogue_text = _format_catalogue_section(catalogue)

    return sop_text + "\n\n" + catalogue_text
