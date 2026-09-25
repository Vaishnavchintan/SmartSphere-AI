# SmartSphere AI — Multi-Agent Code Review & Documentation System

[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/Orchestrator-CrewAI%200.86+-orange)](https://github.com/crewAIInc/crewAI)
[![LangChain](https://img.shields.io/badge/RAG-LangChain%200.3.9-green)](https://github.com/langchain-ai/langchain)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

SmartSphere AI is an enterprise-grade multi-agent code analysis system. Unlike basic single-prompt LLM wrappers, SmartSphere AI orchestrates four domain-specialized agents grounded in **deterministic static analysis tools** (Radon, Bandit, Pylint, Secret Scanner) and **codebase-aware AST vector RAG**.

---

## 🏗️ Architecture

```
                       ┌────────────────────────┐
                       │   Target Codebase / PR │
                       └───────────┬────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              ▼                                         ▼
   ┌──────────────────────┐                  ┌──────────────────────┐
   │ Deterministic Static │                  │ LangChain Codebase   │
   │ Analysis (AST Tools) │                  │ FAISS Vector Store   │
   └──────────┬───────────┘                  └──────────┬───────────┘
              │                                         │
              └────────────────────┬────────────────────┘
                                   ▼
                   ┌───────────────────────────────┐
                   │  CrewAI Sequential Pipeline   │
                   └───────────────┬───────────────┘
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
 ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
 │  Code Quality   │      │ Security Audit  │      │   Doc Writer    │
 │ (Radon, Pylint) │      │(Bandit, Secrets)│      │  (PEP 257 RAG)  │
 └─────────────────┘      └─────────────────┘      └─────────────────┘
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   ▼
                        ┌─────────────────────┐
                        │    Test Engineer    │
                        │   (Pytest Mock DB)  │
                        └──────────┬──────────┘
                                   ▼
                        ┌─────────────────────┐
                        │   Lead Synthesizer  │
                        │ (Report & Diff Fix) │
                        └──────────┬──────────┘
                                   ▼
                    report.md & Clean Refactored Code
```

### The 4 Specialized Agents:
1. **Code Quality Agent**: Analyzes cyclomatic complexity (Radon), maintainability index, and PEP 8 structural anti-patterns.
2. **Security Auditor Agent**: Scans AST for OWASP Top 10 vulnerabilities (CWE-89 SQL injection, CWE-78 command execution) and entropy-based hardcoded credential leaks.
3. **Doc Writer Agent**: Retrieves symbol context via LangChain RAG and generates PEP 257 Sphinx/Google-format docstrings with parameter types.
4. **Test Engineer Agent**: Generates deterministic unit tests with `pytest` fixtures, database mocking, and boundary test cases.
5. **Lead Synthesizer**: Unifies agent outputs into an executive health scorecard (0-100), verdict, and 1-click refactoring diff.

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- Recommended: [Astral `uv`](https://github.com/astral-sh/uv) for fast, conflict-free installs.

### 2. Installation
```bash
git clone https://github.com/your-username/smartsphere-ai.git
cd smartsphere-ai

# Using uv (fastest):
uv pip install -r requirements.txt

# Or using standard pip:
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Provide your LLM API Key:
```ini
OPENAI_API_KEY=your_openai_api_key_here
# Or Gemini:
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Running a Code Review via CLI
```bash
# Review a single file:
python -m src.main --file examples/sample_project/app.py --out report.md

# Review entire directory with RAG context:
python -m src.main --repo examples/sample_project/ --out report.md
```

### 5. Launching the Webhook & REST API Server
```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```
API Docs available at: `http://localhost:8000/docs`

---

## 🧪 Running Automated Tests
```bash
pytest tests/ -v
```

---

## 🤖 GitHub Actions CI/CD Integration
An automated workflow is provided at `.github/workflows/ai-code-review.yml`. It runs on every Pull Request, analyzes changed Python files, and posts a consolidated Markdown report directly to the PR comments.
