# Personal Obsidian-First LLM Wiki — User Guide

Welcome to your compounding personal knowledge base! This vault is designed to act as a structured, interlinked wiki that compounds in value over time as you read, learn, and explore.

Instead of traditional, stateless RAG workflows where the AI rediscovers knowledge from scratch on every session, this system leverages an AI agent as a **Librarian & compiler** to incrementally update and maintain a highly structured Markdown vault inside Obsidian, supported by lightweight local Python scripts.

---

## 1. Directory Structure

Your vault is organized into parallel **English (`en/`)** and **Indonesian (`id/`)** sub-wikis, enabling a compounding, cross-linked knowledge system:

```text
My-Wiki/
├── WIKI_SCHEMA.md         # Master instructions for any LLM agent operating in this vault
├── README.md              # This User Guide reference
├── raw/                   # Immutable raw source documents (Place your files here!)
│   ├── papers/            # Academic PDF research papers (organized into domain subfolders)
│   ├── articles/          # Web clips, blog posts, news articles
│   └── notes/             # Personal raw logs, voice transcripts, scratch thoughts
├── wiki/                  # The persistent compiled Markdown Wiki
│   ├── log.md             # Chronological action history log
│   ├── en/                # === English Sub-Wiki ===
│   │   ├── index.md       # Auto-generated English visual index catalog
│   │   ├── concepts/      # concepts/finance/, concepts/software-engineering/, etc.
│   │   ├── entities/      # entities/finance/, entities/software-engineering/, etc.
│   │   └── sources/       # Summaries of sources in English
│   └── id/                # === Indonesian Sub-Wiki ===
│       ├── index.md       # Auto-generated Indonesian visual index catalog
│       ├── concepts/      # concepts/finance/, concepts/software-engineering/, etc.
│       ├── entities/      # entities/finance/, entities/software-engineering/, etc.
│       └── sources/       # Summaries of sources in Indonesian
└── scripts/               # Pure local Python automation utilities
```

---

## 2. Operating Modes

Your system is designed to run in two modes:

### Mode A: Antigravity + DeepSeek Hybrid
*   **When to use**: When you have configured your DeepSeek API key for high-reasoning, cost-effective compilation.
*   **How to set**: Set your API key in your environment variables (e.g., via a `.env` file or in your terminal session):
    ```powershell
    $env:DEEPSEEK_API_KEY="your-api-key-here"
    ```
*   **How it works**: Antigravity CLI acts as the local operator (creating files, running scripts), while DeepSeek-R1 / DeepSeek-V3 performs the heavy map-reduce chapter chunking, summarization, and integration.

### Mode B: Pure Local Antigravity CLI Fallback (Offline-Ready)
*   **When to use**: Default mode when `DEEPSEEK_API_KEY` is not present, or if the API is offline.
*   **How it works**: The local automation scripts output a status check (`Exit Code 2`), prompting the **Antigravity CLI** agent to handle all cognitive steps (reading chunks, summarizing, extracting entities) directly locally inside our active chat conversation using standard local system tools. **No external API configured or internet connection is required.**

---

## 3. Workflows & Command Invocations

You can execute three primary operations in your vault. When pair programming with an agent (like Antigravity CLI), simply type the commands as standard instructions:

### 3.1. Ingestion (`/ingest <raw-file-path>`)
Ingesting compiles a new raw source document into your wiki, extracting concepts, entities, and summaries.

1.  **Place the file** in the correct `raw/` subdirectory (e.g., drag a research paper into `raw/papers/` or a web clip into `raw/articles/`).
2.  **Ask the agent to ingest it**:
    > `/ingest raw/articles/my-article.md`
3.  **What happens behind the scenes**:
    - The system calculates the file hash (preventing duplicate processing).
    - It runs chunk-based map-reduce summaries.
    - It creates parallel source summaries in `wiki/en/sources/` and `wiki/id/sources/`.
    - It creates/updates parallel concept and entity pages in both `wiki/en/` and `wiki/id/`, cross-linking them via the `translation: "[[translated_page]]"` YAML frontmatter.
    - It appends a record to `wiki/log.md` and re-runs `scripts/make_index.py` to automatically update `wiki/en/index.md` and `wiki/id/index.md`.

---

### 3.2. Querying & Chatting (`/query <your-question>` or `/chat <your-question>`)
Querying and chatting allow you or the agent to quickly find context, synthesize an answer, or engage in a conversational RAG discussion about the vault's contents.

1.  **Ask the agent to search or chat**:
    > `/query what are the core differences between transformer self-attention and convnets?`
    
    Or start a conversational chat query:
    > `/chat bagaimana cara kerja in-context learning?`
2.  **What happens behind the scenes**:
    - For `/query`, the agent runs `python scripts/search.py "query keywords"` to find top-ranking pages across the vault.
    - For `/chat`, the agent runs `python scripts/search.py --chat "<question>"` to launch the bilingual RAG chat pipeline, retrieving the top 5 documents as context and using DeepSeek to generate a grounded, LaTeX-preserving response.
    - If the synthesis is extensive, the agent or user can choose to compile the results back as a parallel page to enrich the vault.

---

### 3.3. Linting (`/lint` or `/linter`)
Linting audits your vault's structural integrity, link health, and schema conformity.

1.  **Ask the agent to lint**:
    > `/lint`
2.  **What happens behind the scenes**:
    - Runs `python scripts/linter.py` locally.
    - Scans for broken wikilinks, orphan pages, and invalid YAML headers.
    - Verifies that all parallel English and Indonesian translation notes exist and are **100% reciprocal**.
    - The agent presents the health report and offers to resolve any detected issues.

---

## 4. Setup & Installation

Follow these steps to set up the local python scripts and automation tools:

### 4.1. Prerequisites
- **Python**: Version 3.8 or higher.
- **Git**: Installed and configured.

### 4.2. Clone and Setup Environment
1.  Clone this repository to your local system:
    ```bash
    git clone <repository-url>
    cd My-Wiki
    ```
2.  Create a virtual environment to isolate dependencies:
    ```powershell
    # Windows
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    
    # macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### 4.3. Environment Configuration
Create a `.env` file at the project root to securely store API keys (this file is ignored by Git to prevent secret exposure):
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

---

## 5. Repository Cleanliness & Contributing

To keep this project structured, clean, and collaborative, please adhere to the following repository guidelines:

### 5.1. Git Ignore Policy
We maintain a strict `.gitignore` policy to ensure only the core wiki structure, automation scripts, and compiled notes are tracked:
- **Environment & Secret files** (`.env`, `.venv/`) are ignored to protect keys and system state.
- **OS & Editor configs** (`.DS_Store`, `.vscode/`, `.idea/`) are ignored to prevent platform-specific workspace spam.
- **Raw assets** (`raw/articles/*`, `raw/notes/*`, etc.) are ignored. This keeps the repository lightweight and avoids committing copyrighted files (like PDFs and web clippings) to public repositories. 
- Empty folders in `raw/` are tracked using `.gitkeep` files so that the directory structure is automatically created when cloning.

### 5.2. How to Contribute
We welcome updates and contributions to the wiki or its automation scripts!
1.  **Work on a Branch**: Create a feature branch for your changes (`git checkout -b feature/your-feature`).
2.  **Always Run Linter**: Before committing your changes, always run the linter to verify link and translation reciprocity:
    ```powershell
    python scripts/linter.py
    ```
    Ensure no errors or warnings are flagged.
3.  **Clean Ingestion**: If you add new wiki pages, ensure they follow the standards outlined in [WIKI_SCHEMA.md](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/WIKI_SCHEMA.md) (reproducible YAML headers, correct translation linking, etc.).
4.  **Submit a PR**: Push your branch to GitHub and create a Pull Request.

---

## 6. Manual Script CLI Usage

You can run the Python automation scripts directly from your terminal inside the `My-Wiki` directory:

*   **Re-compile the Index**:
    ```powershell
    python scripts/make_index.py
    ```
*   **Run Linter Audit**:
    ```powershell
    python scripts/linter.py
    ```
*   **Local Term Search**:
    ```powershell
    python scripts/search.py "deep learning transformer"
    ```
