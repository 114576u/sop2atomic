"""
Entry point for the sop2atomic command-line interface.

This module defines the CLI wrapper around the core SOP → Atomic
transformation pipeline. It wires together:
  - SOP parsing
  - Atomic catalogue loading
  - Prompt construction
  - LLM request
  - JSON output

Usage:
    python -m sop2atomic.cli.main <sop_file.docx> <atomic_catalogue.xlsx>
"""

import argparse
import json
from sop2atomic.parser.sop_parser import parse_sop_document
from sop2atomic.catalogue.atomic_catalogue_loader import load_atomic_catalogue
from sop2atomic.transformers.sop_to_atomic_transformer import SopToAtomicTransformer


def build_parser() -> argparse.ArgumentParser:
    """Create and return the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert SOP (.docx) into atomic workflow JSON."
    )
    parser.add_argument("sop_file", help="Path to the SOP .docx file")
    parser.add_argument(
        "catalogue_file", help="Path to the Atomic Components Catalogue (.xlsx)"
    )
    parser.add_argument(
        "--model",
        default="gpt-5.1",
        help="OpenAI model to use (default: gpt-5.1)",
    )
    parser.add_argument(
        "--output",
        help="Optional output file (default: print to stdout)",
    )
    return parser


def main() -> None:
    """Main CLI workflow."""
    parser = build_parser()
    args = parser.parse_args()

    sop_data = parse_sop_document(args.sop_file)
    catalogue = load_atomic_catalogue(args.catalogue_file)

    transformer = SopToAtomicTransformer(model=args.model)
    result_json = transformer.transform(sop_data, catalogue)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result_json, f, indent=2)
        print(f"Output written to {args.output}")
    else:
        print(json.dumps(result_json, indent=2))


if __name__ == "__main__":
    main()
