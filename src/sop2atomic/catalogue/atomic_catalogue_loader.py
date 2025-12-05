"""
Loader for the Atomic Components Catalogue (.xlsx).

Reads an Excel file and converts each atomic component into a dict:
{
    "id": "1_1",
    "id_name": "OPEN_FOLDER",
    "category": "Files & Folders",
    "description": "Open a local or network folder",
    "parameters": ["path"]
}

This catalogue is used to map SOP steps into atomic actions.
"""

from typing import List, Dict, Any
import pandas as pd


def load_atomic_catalogue(path: str) -> List[Dict[str, Any]]:
    """
    Load the Excel file containing atomic components.

    Args:
        path: file path

    Returns:
        list of component dicts
    """
    df = pd.read_excel(path)
    components = []

    for _, row in df.iterrows():
        raw_value = row.get("Parameters", "")

        # Handle NaN / missing values explicitly
        if pd.isna(raw_value):
            params_raw = ""
        else:
            params_raw = str(raw_value)

        params = [
            p.strip() for p in params_raw.replace(",", "\n").split("\n") if p.strip()
        ]

        components.append(
            {
                "id": str(row.get("ID", "")),
                "id_name": row.get("ID_NAME", ""),
                "category": row.get("Category", ""),
                "description": row.get("Description", ""),
                "parameters": params,
            }
        )

    return components
