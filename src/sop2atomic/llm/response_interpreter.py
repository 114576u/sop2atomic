"""
Utilities for interpreting or validating the JSON returned by the LLM.
"""

from typing import Dict, Any
import json


def parse_llm_json(raw_text: str) -> Dict[str, Any]:
    """
    Convert raw string returned by LLM into a Python dict.
    """
    return json.loads(raw_text)
