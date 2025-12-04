"""
High-level transformer: SOP → Atomic Action JSON.

This class coordinates:
  - the user prompt
  - the LLM call
  - the returned JSON interpretation
"""

from typing import Dict, Any, List
from sop2atomic.llm.prompt_builder import build_user_prompt
from sop2atomic.llm.llm_client import LLMClient
from sop2atomic.llm.response_interpreter import parse_llm_json


class SopToAtomicTransformer:
    """Main workflow transformer class."""

    def __init__(self, model: str = "gpt-5.1"):
        self.llm = LLMClient(model=model)

    def transform(
        self,
        sop_data: Dict[str, Any],
        catalogue: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Execute full SOP → Atomic mapping.
        """
        user_prompt = build_user_prompt(sop_data, catalogue)
        raw_json = self.llm.call(user_prompt)
        result = parse_llm_json(raw_json)

        # Inject SOP ID if missing
        sop_id = sop_data.get("sop_card", {}).get("SCHRODERS_ID")
        if sop_id and not result.get("sop_id"):
            result["sop_id"] = sop_id

        return result
