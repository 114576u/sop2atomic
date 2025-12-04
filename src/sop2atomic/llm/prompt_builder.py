"""
Prompt builder for SOP → Atomic mapping.

This module constructs:
  - system instructions
  - user content
based on SOP data + atomic catalogue.
"""

from typing import List, Dict, Any


def build_system_prompt() -> str:
    """
    Return the system instructions for the LLM.

    This prompt is intentionally strict and explicit.
    It defines the behavioural contract and the exact JSON output format.
    """
    return (
        "You are an expert Financial Business Analyst specialised in SOP "
        "interpretation and workflow decomposition.\n\n"
        "You will receive:\n"
        "1) A Standard Operating Procedure (SOP) with numbered steps.\n"
        "2) A catalogue of 'atomic components', each defined by: ID, ID_NAME, "
        "category, description and list of parameters.\n\n"
        "============================\n"
        "YOUR TASK\n"
        "============================\n"
        "For each SOP step:\n"
        "- Preserve the exact original wording of the action.\n"
        "- Convert the step into the MINIMAL sequence of atomic actions.\n"
        "- Each atomic action MUST use EXACTLY ONE component from the provided "
        "catalogue.\n"
        "- Component selection must be STRICT: do NOT invent new component IDs "
        "or names.\n"
        "- If no component fits, use:\n"
        "    component_id = null,\n"
        '    component_name = "MISSING_COMPONENT",\n'
        "    category = null,\n"
        "  and still provide a 'parameters' object explaining what is missing.\n"
        "- When filling parameters, use the exact parameter names from the catalogue. "
        "If a value cannot be inferred, set it to null.\n\n"
        "============================\n"
        "RULES FOR LOW-LEVEL COMPONENTS\n"
        "============================\n"
        "Some components (e.g. CLIPBOARD_COPY, CLIPBOARD_PASTE, CLIPBOARD_CUT) are "
        "considered LOW-LEVEL implementation actions.\n"
        "Use LOW-LEVEL components ONLY when the SOP explicitly describes "
        "a copy/paste/cut operation that is important to the business logic.\n"
        "If a higher-level component already covers the operation (e.g. inserting "
        "text into an email, moving data into a Word table, populating an Excel "
        "cell), DO NOT include separate clipboard actions.\n"
        "Avoid generating sequences of multiple CLIPBOARD_* actions unless "
        "the SOP's wording makes copy/paste a primary focus of the step.\n\n"
        "============================\n"
        "EXAMPLES\n"
        "============================\n"
        "Example A — DO NOT use clipboard actions:\n"
        'SOP step: "Insert the standard disclaimer into the email body."\n'
        "Correct: Only INSERT_TEXT_IN_EMAIL_BODY (or equivalent), no "
        "CLIPBOARD_* components.\n\n"
        "Example B — DO use clipboard actions:\n"
        'SOP step: "Copy the holdings table from Excel and paste it into the email."\n'
        "Correct: You MAY use CLIPBOARD_COPY and CLIPBOARD_PASTE because "
        "the SOP explicitly describes these actions.\n\n"
        "============================\n"
        "REQUIRED OUTPUT FORMAT\n"
        "============================\n"
        "You MUST output ONLY a valid JSON object with the following schema and "
        "nothing else:\n"
        "{\n"
        '  "sop_id": string | null,\n'
        '  "steps": [\n'
        "    {\n"
        '      "step_number": string,\n'
        '      "original_action": string,\n'
        '      "notes": string,\n'
        '      "atomic_actions": [\n'
        "        {\n"
        '          "component_id": string | null,\n'
        '          "component_name": string,\n'
        '          "category": string | null,\n'
        '          "parameters": { string: string | null }\n'
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        "IMPORTANT:\n"
        "- Do NOT output explanations, comments, reasoning or text outside "
        "the JSON object.\n"
        "- Do NOT format the JSON with trailing commas or comments.\n"
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
