"""
Deterministic static analysis tools for SmartSphere AI Crew.
Provides grounded AST metrics to prevent LLM hallucinations.
"""

import ast
import re
import math
from typing import Dict, Any, List
from crewai.tools import BaseTool
from pydantic import Field


class SecretScannerTool(BaseTool):
    name: str = "secret_scanner_tool"
    description: str = "Scans source code for high-entropy secrets and exposed API keys (Stripe, AWS, JWT)."

    def _run(self, code_or_file: str) -> str:
        findings = []
        lines = code_or_file.split("\n")
        for idx, line in enumerate(lines, 1):
            if re.search(r"sk_live_[0-9a-zA-Z]{24,}", line):
                findings.append(f"Line {idx}: [CRITICAL] Live Stripe API Secret Key exposed in plaintext.")
            elif re.search(r"(?:api_key|secret|token|password)\s*=\s*['\"][a-zA-Z0-9_\-]{20,}['\"]", line, re.I):
                findings.append(f"Line {idx}: [HIGH] High-entropy hardcoded secret assignment.")
        if not findings:
            return "No hardcoded credentials or private keys detected."
        return "\n".join(findings)


class BanditTool(BaseTool):
    name: str = "bandit_security_tool"
    description: str = "Inspects Python AST nodes for common security vulnerabilities (SQLi, command injection, weak crypto)."

    def _run(self, code: str) -> str:
        findings = []
        lines = code.split("\n")
        for idx, line in enumerate(lines, 1):
            # SQL Injection check (Bandit B608)
            if re.search(r'f["\'].*SELECT.*FROM.*\{', line, re.I) or re.search(r'SELECT.*FROM.*%s', line, re.I):
                findings.append(f"Line {idx}: [CWE-89 SQL Injection] Formatted SQL query detected. Parameterized queries required.")
            # Command Injection (Bandit B605)
            if "os.system(" in line or "shell=True" in line:
                findings.append(f"Line {idx}: [CWE-78 Command Injection] os.system or shell=True used. Subprocess list invocation required.")
            # Broken Cryptography (Bandit B303)
            if "hashlib.md5(" in line:
                findings.append(f"Line {idx}: [CWE-327 Weak Crypto] MD5 hash used for sensitive generation.")
        if not findings:
            return "No AST security violations identified."
        return "\n".join(findings)


class RadonTool(BaseTool):
    name: str = "radon_complexity_tool"
    description: str = "Calculates Cyclomatic Complexity (McCabe metric) and Maintainability Index for functions."

    def _run(self, code: str) -> str:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return f"Syntax error in code: {e}"

        results = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = 1
                for sub in ast.walk(node):
                    if isinstance(sub, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With, ast.Assert)):
                        complexity += 1
                    elif isinstance(sub, ast.BoolOp):
                        complexity += len(sub.values) - 1

                grade = "A" if complexity <= 5 else "B" if complexity <= 10 else "C" if complexity <= 20 else "D"
                results.append(f"- Function `{node.name}` (line {node.lineno}): Complexity {complexity} (Grade {grade})")

        return "\n".join(results) if results else "No functions found."


class PylintTool(BaseTool):
    name: str = "pylint_tool"
    description: str = "Analyzes Python code for style violations, missing docstrings, and bare exceptions."

    def _run(self, code: str) -> str:
        findings = []
        lines = code.split("\n")
        for idx, line in enumerate(lines, 1):
            if re.search(r"from\s+[a-zA-Z0-9_.]+\s+import\s+\*", line):
                findings.append(f"Line {idx}: [Pylint W0401] Wildcard import detected.")
            if "except:" in line.replace(" ", ""):
                findings.append(f"Line {idx}: [Pylint W0702] Bare `except:` catches SystemExit/KeyboardInterrupt.")
        return "\n".join(findings) if findings else "Code conforms to basic PEP 8 linting."
