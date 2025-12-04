"""
Parser for SOP documents (.docx).

This module is responsible for:
  - loading the DOCX file
  - extracting SOP metadata (SOP Card)
  - extracting structured steps (Step, Action, Notes)

The output is a Python dictionary:
{
    "sop_card": {...},
    "steps": [
        {"step_number": "1", "action": "...", "notes": "..."},
        ...
    ]
}
"""

from typing import Dict, Any, List
from docx import Document


def _parse_sop_card(table) -> Dict[str, str]:
    """Extract SOP metadata from the first table in the document."""
    metadata = {}
    for row in table.rows:
        cells = [c.text.strip() for c in row.cells]
        if cells and cells[0]:
            # SOP tables sometimes put key/value in different positions
            if len(cells) >= 2:
                metadata[cells[0]] = cells[1]
            elif len(cells) >= 1:
                metadata[cells[0]] = ""
    return metadata


def _find_procedure_table(tables) -> Any:
    """Return the first table that appears to contain SOP steps."""
    for t in tables:
        header = [c.text.strip().lower() for c in t.rows[0].cells]
        if "step" in header and "action" in header:
            return t
    return None


def _parse_steps(table) -> List[Dict[str, str]]:
    """Extract structured SOP steps from the procedure table."""
    header = [c.text.strip().lower() for c in table.rows[0].cells]
    step_idx = header.index("step")
    action_idx = header.index("action")
    notes_idx = header.index("notes") if "notes" in header else None

    steps = []
    for row in table.rows[1:]:
        cells = [c.text.strip() for c in row.cells]
        if not cells or not cells[step_idx]:
            continue

        step_number = cells[step_idx]
        action_text = cells[action_idx]
        notes_text = cells[notes_idx] if notes_idx is not None else ""

        steps.append(
            {
                "step_number": step_number,
                "action": action_text,
                "notes": notes_text,
            }
        )
    return steps


def parse_sop_document(path: str) -> Dict[str, Any]:
    """
    Parse a full SOP DOCX document.

    Returns:
        dict with 'sop_card' and 'steps'
    """
    doc = Document(path)
    tables = doc.tables

    if not tables:
        raise ValueError("No tables detected in SOP. Expected SOP Card + Procedure.")

    sop_card = _parse_sop_card(tables[0])
    procedure = _find_procedure_table(tables[1:])

    if procedure is None:
        raise ValueError("Could not find Procedure table with Step/Action columns.")

    steps = _parse_steps(procedure)

    return {
        "sop_card": sop_card,
        "steps": steps,
    }
