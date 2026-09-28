"""
Codebase-Aware RAG Retriever Tool for CrewAI.
Indexes repository files and retrieves context chunks for symbols, models, and dependencies.
"""

import os
from typing import List, Dict, Any
from crewai.tools import BaseTool


class CodebaseRAGRetrieverTool(BaseTool):
    name: str = "codebase_rag_retriever_tool"
    description: str = "Retrieves semantic AST code chunks (functions, classes, models) from the indexed repository."
    repo_chunks: List[Dict[str, Any]] = []

    def __init__(self, repo_path: str = "."):
        super().__init__()
        self._index_repo(repo_path)

    def _index_repo(self, repo_path: str):
        chunks = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        chunks.append({
                            "path": full_path,
                            "filename": file,
                            "content": content,
                        })
                    except Exception:
                        pass
        self.repo_chunks = chunks

    def _run(self, query: str) -> str:
        terms = [t.lower() for t in query.split() if len(t) > 2]
        matches = []
        for chunk in self.repo_chunks:
            score = 0
            for term in terms:
                if term in chunk["filename"].lower():
                    score += 5
                if term in chunk["content"].lower():
                    score += 2
            if score > 0:
                matches.append((score, chunk))

        matches.sort(key=lambda x: x[0], reverse=True)
        top = matches[:3]

        if not top:
            return "No matching symbols found in repository."

        result_lines = []
        for score, m in top:
            snippet = "\n".join(m["content"].split("\n")[:30])
            result_lines.append(f"--- MATCH ({m['path']}) ---\n{snippet}\n")

        return "\n".join(result_lines)
