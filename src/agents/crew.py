"""
CrewAI Multi-Agent Architecture for Code Review.
Orchestrates 4 specialized domain agents and a lead synthesizer.
"""

from crewai import Agent, Crew, Process, Task
from src.tools.static_analyzer import RadonTool, BanditTool, PylintTool, SecretScannerTool
from src.tools.rag_retriever import CodebaseRAGRetrieverTool


class SmartSphereCrew:
    def __init__(self, repo_path: str = "."):
        self.radon_tool = RadonTool()
        self.bandit_tool = BanditTool()
        self.pylint_tool = PylintTool()
        self.secret_tool = SecretScannerTool()
        self.rag_tool = CodebaseRAGRetrieverTool(repo_path=repo_path)

    def create_agents(self):
        # 1. Code Quality Agent
        code_quality_agent = Agent(
            role="Code Quality & Complexity Specialist",
            goal="Analyze code maintainability, Cyclomatic Complexity via Radon, and identify PEP 8 code smells.",
            backstory=(
                "You are a Staff Software Architect dedicated to clean code, decomposition, "
                "and maintainability. You never guess; you rely strictly on static tools."
            ),
            tools=[self.radon_tool, self.pylint_tool],
            verbose=True,
        )

        # 2. Security Auditor Agent
        security_agent = Agent(
            role="Application Security (AppSec) Specialist",
            goal="Identify OWASP Top 10 vulnerabilities (SQLi, command injection) and exposed credentials.",
            backstory=(
                "You are a battle-hardened Security Engineer. You inspect AST nodes for "
                "dangerous sinks and identify leaked production secrets and credentials."
            ),
            tools=[self.bandit_tool, self.secret_tool],
            verbose=True,
        )

        # 3. Doc Writer Agent
        doc_agent = Agent(
            role="Technical Documentation Specialist",
            goal="Produce comprehensive PEP 257 docstrings and type annotations grounded in repository context.",
            backstory=(
                "You are an API Documentation Lead. You use the RAG tool to understand related data models "
                "and produce Sphinx/Google-formatted docstrings."
            ),
            tools=[self.rag_tool],
            verbose=True,
        )

        # 4. Test Engineer Agent
        test_agent = Agent(
            role="QA Automation Engineer",
            goal="Synthesize deterministic pytest unit tests with mock database fixtures and edge cases.",
            backstory=(
                "You are an experienced Test Automation Engineer. You write tests for both happy paths "
                "and vulnerability regressions (e.g. verifying parameterized SQL behavior)."
            ),
            tools=[self.rag_tool],
            verbose=True,
        )

        # 5. Lead Synthesizer Agent
        synthesizer_agent = Agent(
            role="Lead Synthesizer & Code Review Orchestrator",
            goal="Consolidate all findings into a unified health scorecard, executive summary, and clean refactored diff.",
            backstory=(
                "You are the Engineering Manager consolidating all agent outputs into an actionable PR review."
            ),
            tools=[],
            verbose=True,
        )

        return [code_quality_agent, security_agent, doc_agent, test_agent, synthesizer_agent]

    def create_tasks(self, agents, code_content: str, filename: str):
        quality_agent, security_agent, doc_agent, test_agent, synthesizer_agent = agents

        task1 = Task(
            description=f"Analyze code complexity and linting in {filename}:\n\n```python\n{code_content}\n```",
            expected_output="Detailed breakdown of cyclomatic complexity, Radon grades, and style violations.",
            agent=quality_agent,
        )

        task2 = Task(
            description=f"Audit {filename} for security flaws, SQLi, command injection, and leaked secrets:\n\n```python\n{code_content}\n```",
            expected_output="Security audit report with CWE classifications and remediation steps.",
            agent=security_agent,
        )

        task3 = Task(
            description=f"Query RAG context and generate PEP 257 docstrings with typed arguments for {filename}.",
            expected_output="Complete Google/Sphinx style docstrings and type annotations.",
            agent=doc_agent,
        )

        task4 = Task(
            description=f"Generate a deterministic pytest test suite with mock fixtures for {filename}.",
            expected_output="Executable pytest test suite covering normal and boundary edge cases.",
            agent=test_agent,
        )

        task5 = Task(
            description="Consolidate all agent findings into a unified Markdown report and produce refactored clean code.",
            expected_output="Full Markdown review report and refactored Python code.",
            agent=synthesizer_agent,
        )

        return [task1, task2, task3, task4, task5]

    def run(self, code_content: str, filename: str = "app.py") -> str:
        agents = self.create_agents()
        tasks = self.create_tasks(agents, code_content, filename)

        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()
        return str(result)
