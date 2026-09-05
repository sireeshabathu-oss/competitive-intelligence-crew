"""
Generate a competitive intelligence report for any company.

Usage:
    python main.py "Figma"
    python main.py "Figma" --focus "AI features, enterprise pricing"
    python main.py                      # uses COMPANY_NAME / FOCUS_AREAS from .env, or defaults

Run with -h for all options.
"""

import argparse
import os
import sys

from dotenv import load_dotenv

load_dotenv()

def parse_args(argv=None):
    default_company = os.getenv("COMPANY_NAME", "Notion")
    default_focus = os.getenv(
        "FOCUS_AREAS", "pricing changes, AI features, recent product launches, main competitors"
    )

    parser = argparse.ArgumentParser(
        description="Generate a competitive intelligence report for a company using an AI agent crew."
    )
    parser.add_argument(
        "company",
        nargs="?",
        default=default_company,
        help=f"Company to research (default: '{default_company}', from COMPANY_NAME in .env)",
    )
    parser.add_argument(
        "--focus",
        default=default_focus,
        help="Comma-separated focus areas to research (default: from FOCUS_AREAS in .env)",
    )
    parser.add_argument(
        "--output",
        default="report.md",
        help="File to save the generated report to (default: report.md)",
    )
    return parser.parse_args(argv)


def validate_environment():
    """Returns a list of missing required environment variables, empty if all present."""
    missing = []
    if not (
        os.getenv("OPENAI_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY")
        or os.getenv("GEMINI_API_KEY")
    ):
        missing.append("OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY")
    if not os.getenv("SERPER_API_KEY"):
        missing.append("SERPER_API_KEY")
    return missing


def main():
    args = parse_args()

    missing = validate_environment()
    if missing:
        print("Missing required environment variable(s):")
        for m in missing:
            print(f"  - {m}")
        print("\nCopy .env.example to .env and fill these in before running.")
        sys.exit(1)

    # Imported after the environment check so a missing-key error surfaces
    # immediately, instead of failing deep inside the crewai library.
    from crew import build_crew

    print(f"Researching: {args.company}")
    print(f"Focus areas: {args.focus}\n")

    try:
        crew = build_crew(args.company, args.focus)
        result = crew.kickoff()
    except RuntimeError as e:
        # Raised by build_crew() for known setup problems (e.g. bad search key)
        print(f"\nSetup error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nSomething went wrong while running the crew: {e}")
        print("Common causes: invalid or expired API key, network issue, or rate limiting.")
        sys.exit(1)

    print("\n\n===== COMPETITIVE INTELLIGENCE REPORT =====\n")
    print(result)

    try:
        with open(args.output, "w") as f:
            f.write(str(result))
        print(f"\nSaved to {args.output}")
    except OSError as e:
        print(f"\nCould not save report to {args.output}: {e}")
        print("The report was still generated above — just couldn't be written to disk.")


if __name__ == "__main__":
    main()
