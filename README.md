The Problem: Agent Framework Version Compatibility Issues

The agentic AI ecosystem is rapidly evolving, leading to frequent updates and breaking changes in popular agent frameworks (e.g., LangChain, LlamaIndex, Marvin). Developers often face `ImportError` or other runtime failures when upgrading framework versions, integrating components from different versions, or simply trying to maintain complex agent systems. This forces manual, time-consuming dependency management and hinders the adoption of new features, slowing down "agent ops."

Why This Project Shape/Stack?

This prototype is a Python CLI tool named `agent-dep-checker`. Python was chosen because it's the dominant language for agentic AI frameworks, making a Python-based tool the most accessible and natural fit for developers in this ecosystem. A CLI allows for easy integration into CI/CD pipelines, pre-commit hooks, or local development workflows. The tool leverages `pip-tools` for robust dependency management and `ast` (Abstract Syntax Trees) for static analysis, enabling it to "understand" Python code without execution.

`agent-dep-checker` provides:
1.  **Dependency Analysis:** Scans your agent project for imported modules from known agent frameworks.
2.  **Version Checking:** Compares detected framework imports against your project's `requirements.txt` (or `pyproject.toml`) and suggests potential mismatches or outdated versions.
3.  **Breaking Change Awareness (Basic):** While full semantic versioning and breaking change detection is complex, this tool offers a *blueprint* for how static analysis could flag common patterns of breaking changes (e.g., renamed modules, deprecated imports). For this prototype, it focuses on reporting *any* detected framework imports that might be a source of version conflict, rather than exhaustively listing every breaking change.

Setup and Usage (Zero API Keys)

1.  **Prerequisites:**
    *   Python 3.8+
    *   `pip`

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-org/agent-dep-checker.git
    cd agent-dep-checker
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the checker:**

    The tool needs two things:
    *   A path to your agent project's source code (e.g., `my_agent_project/src`).
    *   A path to your agent project's `requirements.txt` (or `pyproject.toml` in a real scenario, but `requirements.txt` for this prototype's simplicity).

    Example using the provided `fixtures/` project:
    ```bash
    python agent_dep_checker.py --project-path fixtures/agent_project --requirements-file fixtures/agent_project/requirements.txt
    ```

    You should see output similar to this:
    ```
    🔍 Analyzing agent project at fixtures/agent_project...
    📦 Reading dependencies from fixtures/agent_project/requirements.txt...

    Detected Framework Imports:
    - langchain (imported in fixtures/agent_project/my_agent.py)
    - llama_index (imported in fixtures/agent_project/my_agent.py)

    Project Dependencies (from requirements.txt):
    - langchain==0.0.300
    - llama-index==0.10.0

    Potential Version Inconsistencies or Warnings:
    - langchain: Found 'langchain==0.0.300' in requirements.txt. Consider checking for newer versions or known breaking changes if encountering issues with latest framework code.
    - llama-index: Found 'llama-index==0.10.0' in requirements.txt. Consider checking for newer versions or known breaking changes if encountering issues with latest framework code.

    Analysis Complete. Review the output for potential dependency issues.
    ```

Optional Real-LLM Adapter

This tool is purely for dependency management and static analysis; it does not involve processing or reasoning about LLM/agent behavior. Therefore, no LLM API or adapter is included or required. The tool operates entirely on code and dependency files.
