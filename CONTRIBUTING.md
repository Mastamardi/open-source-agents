# Contributing to open-source-ai

Thank you for your interest in contributing! This repository is a community-driven collection of practical, documented, and open-source AI agents and developer tools.

Whether you are participating in an organized hackathon or contributing independently, this guide provides the exact steps needed to get your project prepared, documented, and submitted.

---

## Contribution Workflow

You do not need to open an issue before contributing. Follow these 12 steps to submit your project:

### Step 1: Fork the Repository
Fork the upstream repository to your personal GitHub account by clicking the **Fork** button on GitHub.

### Step 2: Clone Your Fork
Clone your fork locally:

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

Configure the upstream remote so you can stay in sync:

```bash
git remote add upstream https://github.com/<upstream-owner>/<repo-name>.git
git fetch upstream
```

### Step 3: Create a Descriptive Branch
Create a new feature branch starting from the upstream `main` branch:

```bash
git checkout -b feat/<your-project-slug> upstream/main
```

*Example branch names:* `feat/research-assistant`, `feat/mcp-doc-search`.

### Step 4: Choose the Appropriate Category & Directory
Select the directory that matches your project type:

- **`agents/<project-slug>/`**: For autonomous, semi-autonomous, or task-oriented AI agents, multi-agent systems, and interactive assistants.
- **`tools/<project-slug>/`**: For reusable developer tools, Model Context Protocol (MCP) servers, evaluation harnesses, prompt managers, and integration utilities.

Create your dedicated folder:

```bash
mkdir agents/<project-slug>   # or tools/<project-slug>
```

### Step 5: Copy the Documentation Template
Copy the shared template files into your project folder:

```bash
# On Linux/macOS:
cp template/README.md agents/<project-slug>/README.md
cp template/.gitignore agents/<project-slug>/.gitignore
cp template/.env.example agents/<project-slug>/.env.example

# On Windows (PowerShell):
Copy-Item template/README.md -Destination agents/<project-slug>/README.md
Copy-Item template/.gitignore -Destination agents/<project-slug>/.gitignore
Copy-Item template/.env.example -Destination agents/<project-slug>/.env.example
```

### Step 6: Implement Your Project
Build your agent or tool inside your dedicated directory. You are completely free to choose:
- **Frameworks**: Google Agent Development Kit (ADK), OpenAI Agents SDK, LangGraph, CrewAI, MCP, or vanilla custom code.
- **Languages**: Python, TypeScript, JavaScript, Go, Rust, etc.
- **Model Providers**: Gemini, OpenAI, Anthropic, open-weights models (via Ollama, vLLM, HuggingFace), or mock providers.

### Step 7: Document and Declare Dependencies
- Fill out all relevant sections of your `agents/<project-slug>/README.md` (or `tools/<project-slug>/README.md`). For simple tools, sections that do not apply may be noted as N/A with a short explanation.
- Declare all dependencies in a standard manifest file located inside your project folder (e.g., `requirements.txt`, `pyproject.toml`, or `package.json`).
- If your project requires environment variables or API keys, document them in your `README.md` and provide placeholder values in your project's `.env.example`.

### Step 8: Test the Setup and Functionality
Verify your project in a clean environment:
1. Ensure the installation instructions work on a fresh clone without unstated dependencies.
2. Run the tool or agent and confirm that core functionality works as described.
3. Validate that no real API keys, credentials, local databases, or virtual environments are tracked by Git.

### Step 9: Commit Your Changes
Stage only the files in your project directory:

```bash
git status
git add agents/<project-slug>/   # or tools/<project-slug>/
git commit -m "feat(agents): add <project-slug> with documentation and setup"
```

### Step 10: Push to Your Fork
Push your branch to your personal GitHub fork:

```bash
git push -u origin feat/<your-project-slug>
```

### Step 11: Open a Pull Request
1. Navigate to the upstream repository on GitHub.
2. Click **Compare & pull request**.
3. Ensure the base repository is set to the official repository and the base branch is **`main`**.
4. Complete the checklist and details in the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md).

### Step 12: Respond to Review Feedback
Maintainers will review your submission for code safety, reproducibility, documentation clarity, and project quality. If changes are requested:
1. Make edits locally in your branch.
2. Commit and push your changes to your fork. The PR will update automatically.

---

## Directory & Naming Rules

To keep the repository orderly:

1. **Dedicated Directory**: Every submission must reside in its own folder under `agents/` or `tools/`.
2. **Naming Convention**: Directory names must be **lowercase kebab-case** (e.g., `meeting-summarizer`, `prompt-evaluator`).
3. **Descriptive Names**: Choose a name that clearly identifies what your project does. Avoid generic names like `my-agent`, `final-project`, `test`, or `demo`.
4. **Uniqueness**: Directory names must be unique within their category. Check the directory before picking a name. If a naming conflict occurs, pick a more specific descriptive name (e.g., `research-assistant-arxiv`).
5. **Isolation**: Keep all project code, manifests, and documentation inside your own folder. Do not put multiple unrelated projects in one folder.
6. **No Cross-Project Modifications**: Do not modify another contributor's directory or code without prior coordination.

---

## Scoping Your Pull Request

To ensure quick review and avoid merge conflicts:
- **Keep changes isolated**: Your PR should modify only files within your `agents/<project-slug>/` or `tools/<project-slug>/` directory (and optionally add one row to the index table in `agents/README.md` or `tools/README.md`).
- **Do not modify root build files**: Do not add dependencies to the repository root.
- **Avoid formatting sweeps**: Do not reformat unrelated files across the repository.

---

## Quality & Security Standards

Before submitting, ensure your contribution adheres to these standards:

- **Reproducibility**: Setup steps must work on another developer's machine with clear prerequisites.
- **Dependency Tracking**: Always include a dependency manifest (`requirements.txt`, `package.json`, etc.). Do not assume global package installations.
- **Zero Secrets Policy**: Never commit `.env` files, API keys, access tokens, service account credentials, private SSH keys, or private datasets. Any PR containing secrets will be closed immediately.
- **Honest Documentation**: Example inputs and outputs must reflect genuine runs. State any model assumptions, token consumption, or third-party paid API requirements clearly.
- **Known Limitations**: Disclose known failure modes, rate-limit sensitivities, or platform restrictions (e.g., "Tested on Linux and macOS; Windows support untested").
- **Safety & Respect**: Do not contribute harmful, malicious, or deceptive code (e.g., unauthorized scraping, credential dumping, or uncontained execution loops).
- **Licensing & Attribution**: If you adapt open-source code from third parties, retain proper copyright notices and ensure license compatibility.

---

## Review and Acceptance Notice

Opening a Pull Request does not guarantee that it will be merged. Submissions are reviewed by project maintainers for:
- Quality and clarity of documentation
- Reproducibility of setup and execution
- General utility and relevance to the AI agent/developer tooling ecosystem
- Compliance with security and secret-handling guidelines

Thank you for contributing to open-source AI!
