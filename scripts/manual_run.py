"""
Manual end-to-end runner for sop2atomic.

Usage (from project root, after `pip install -e .`):

    python scripts/manual_run.py \
        path/to/sop_file.docx \
        path/to/Atomic_Components_List_v1.xlsx \
        --output output.json

Requirements:
    - OPENAI_API_KEY must be set in the environment.
    - sop2atomic must be installed (e.g., `pip install -e .` from project root).
"""

import argparse
import json
from typing import Any, Dict, List

from sop2atomic.parser.sop_parser import parse_sop_document
from sop2atomic.catalogue.atomic_catalogue_loader import load_atomic_catalogue
from sop2atomic.transformers.sop_to_atomic_transformer import SopToAtomicTransformer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a manual end-to-end SOP → Atomic mapping using OpenAI."
    )
    parser.add_argument(
        "sop_file",
        help="Path to the SOP .docx file",
    )
    parser.add_argument(
        "catalogue_file",
        help="Path to the Atomic Components Catalogue .xlsx file",
    )
    parser.add_argument(
        "--model",
        default="gpt-5.1",
        help="OpenAI model to use (default: gpt-5.1)",
    )
    parser.add_argument(
        "--output",
        help="Optional output JSON file. If not provided, prints to stdout.",
    )
    return parser.parse_args()


def run_manual(
    sop_file: str,
    catalogue_file: str,
    model: str = "gpt-5.1",
) -> Dict[str, Any]:
    """
    Execute the full pipeline for a single SOP + catalogue.

    Returns:
        The JSON-compatible dict produced by the SopToAtomicTransformer.
    """
    # 1) Parse the SOP document
    sop_data: Dict[str, Any] = parse_sop_document(sop_file)

    # 2) Load the atomic components catalogue
    catalogue: List[Dict[str, Any]] = load_atomic_catalogue(catalogue_file)

    # 3) Run the transformer (this will call the LLM)
    transformer = SopToAtomicTransformer(model=model)
    result = transformer.transform(sop_data, catalogue)

    return result


def main() -> None:
    args = parse_args()

    result = run_manual(
        sop_file=args.sop_file,
        catalogue_file=args.catalogue_file,
        model=args.model,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"Result written to {args.output}")
    else:
        # Pretty-print to stdout
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
