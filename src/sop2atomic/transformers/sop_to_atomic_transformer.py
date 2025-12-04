"""
High-level transformer: SOP → Atomic Action JSON.

This class coordinates the full workflow:
  - build the user prompt from parsed SOP + atomic catalogue
  - call the LLM (via LLMClient)
  - parse the JSON returned by the LLM
  - inject SOP metadata (e.g. SOP ID) if missing
  - perform light normalisation / validation of the structure
"""

from typing import Any, Dict, List, Optional

from sop2atomic.llm.prompt_builder import build_user_prompt
from sop2atomic.llm.llm_client import LLMClient
from sop2atomic.llm.response_interpreter import parse_llm_json


class SopToAtomicTransformer:
    """
    Main workflow transformer class.

    In production, this uses the real LLMClient. In tests, LLMClient is usually
    monkeypatched with a fake implementation (see tests/test_transformer.py),
    so that no external API calls are performed.
    """

    def __init__(self, model: str = "gpt-5.1", llm_client: Optional[LLMClient] = None):
        # Allow explicit injection for advanced use, but default to constructing
        # a client with the given model. In tests, LLMClient is monkeypatched
        # at the module level, so this will actually construct the fake client.
        self.llm: LLMClient = llm_client or LLMClient(model=model)
        self.model = model

    def transform(
        self,
        sop_data: Dict[str, Any],
        catalogue: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Execute the full SOP → Atomic mapping.

        Args:
            sop_data: Parsed SOP content from the parser.sop_parser module.
                      Expected keys:
                        - "sop_card": dict with fields like SCHRODERS_ID, CLIENT…
                        - "steps": list of {step_number, action, notes}
            catalogue: List of atomic components from the catalogue loader.

        Returns:
            A dict matching the JSON schema defined in build_system_prompt(),
            with additional guarantees:
              - result["sop_id"] is populated from SOP card if missing or null.
              - result["steps"] is always a list (may be empty).
              - Each step has keys: step_number, original_action, notes, atomic_actions.
              - Each atomic action has at least keys:
                    component_id, component_name, category, parameters.

        Raises:
            RuntimeError: if the LLM returns invalid or structurally inconsistent JSON.
        """
        # 1) Build the prompt from SOP + catalogue
        user_prompt = build_user_prompt(sop_data, catalogue)

        # 2) Call the LLM (real or fake, depending on environment)
        raw_json = self.llm.call(user_prompt)

        # 3) Parse JSON string into a Python object
        try:
            result = parse_llm_json(raw_json)
        except Exception as exc:  # ValueError most likely
            raise RuntimeError("LLM returned invalid JSON") from exc

        if not isinstance(result, dict):
            raise RuntimeError("LLM response is not a JSON object (expected dict)")

        # 4) Ensure sop_id is present: if missing/None, inject from SOP card
        sop_card = sop_data.get("sop_card", {}) or {}
        sop_id_from_card = sop_card.get("SCHRODERS_ID")

        if not result.get("sop_id") and sop_id_from_card:
            result["sop_id"] = sop_id_from_card

        # 5) Ensure steps is a list
        steps = result.get("steps")
        if steps is None:
            steps = []
            result["steps"] = steps

        if not isinstance(steps, list):
            raise RuntimeError("LLM response 'steps' field is not a list")

        # 6) Light normalisation of each step and atomic action
        for step in steps:
            if not isinstance(step, dict):
                raise RuntimeError("Each step must be a JSON object")

            # Normalise step fields
            step["step_number"] = str(step.get("step_number", ""))
            step["original_action"] = step.get(
                "original_action",
                step.get("action", ""),  # backward-compatibility, just in case
            )
            step["notes"] = step.get("notes", "")

            atomic_actions = step.get("atomic_actions", [])
            if atomic_actions is None:
                atomic_actions = []
            if not isinstance(atomic_actions, list):
                raise RuntimeError("Field 'atomic_actions' must be a list in each step")
            step["atomic_actions"] = atomic_actions

            for action in atomic_actions:
                if not isinstance(action, dict):
                    raise RuntimeError("Each atomic action must be a JSON object")

                # Ensure required keys exist with sensible defaults
                if "component_id" not in action:
                    action["component_id"] = None
                if "component_name" not in action:
                    action["component_name"] = "MISSING_COMPONENT"
                if "category" not in action:
                    action["category"] = None

                parameters = action.get("parameters")
                if parameters is None or not isinstance(parameters, dict):
                    action["parameters"] = {}

        return result
