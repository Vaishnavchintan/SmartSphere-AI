"""
CLI entry point for SmartSphere AI Code Review.
Usage:
    python -m src.main --file examples/sample_project/app.py --out report.md
    python -m src.main --repo examples/sample_project/ --out report.md
"""

import argparse
import sys
import os
from dotenv import load_dotenv

load_dotenv()

from src.agents.crew import SmartSphereCrew
from src.tools.static_analyzer import RadonTool, BanditTool, SecretScannerTool


def main():
    parser = argparse.ArgumentParser(description="SmartSphere AI — Multi-Agent Code Review & Doc Generation")
    parser.add_argument("--file", type=str, help="Target Python file to review")
    parser.add_argument("--repo", type=str, default=".", help="Repository path for RAG context")
    parser.add_argument("--out", type=str, default="report.md", help="Output Markdown report path")
    args = parser.parse_args()

    target_file = args.file or os.path.join(args.repo, "app.py")
    if not os.path.exists(target_file):
        print(f"[!] Target file '{target_file}' not found.")
        sys.exit(1)

    with open(target_file, "r", encoding="utf-8") as f:
        code_content = f.read()

    print(f"[*] Starting SmartSphere AI Multi-Agent Crew on '{target_file}'...")
    crew = SmartSphereCrew(repo_path=args.repo)
    report_markdown = crew.run(code_content=code_content, filename=os.path.basename(target_file))

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report_markdown)

    print(f"[✓] Multi-agent review completed successfully! Report written to '{args.out}'.")


if __name__ == "__main__":
    main()
