---
name: obsidian-vault
description: >
  Search, query, and chat with the bilingual LLM Wiki vault. Use when the user
  types "chat <question>", "query <question>", "/chat", "/query", asks a question
  about vault content, or wants to find, create, or organize notes. MUST run the
  search pipeline before answering — never answer from general knowledge alone.
---

# LLM Wiki — Obsidian Vault Operations

> **Master schema**: Read `WIKI_SCHEMA.md` at the project root for full page schemas,
> ingestion protocol, and cross-reference rules.

## Command Routing

When the user's message starts with `chat`, `/chat`, `query`, or `/query`:

| User Input | Agent Action |
|------------|--------------|
| `chat <question>` or `/chat <question>` | Run **Chat Protocol** below |
| `query <keywords>` or `/query <keywords>` | Run **Query Protocol** below |
| `/ingest <file>` | Follow WIKI_SCHEMA.md §3.1 Ingest Protocol |
| `/lint` | Run `rtk python scripts/linter.py` |

---

## Chat Protocol (`chat <question>`)

**CRITICAL**: Do NOT answer from general knowledge. Always search the wiki first.

### Step 1 — Run Search Script

```bash
rtk python scripts/search.py --chat "<question>"
```

### Step 2 — Interpret the Output

| Script Output | What to Do |
|---------------|------------|
| `=== COGNITIVE CHAT RESPONSE ===` followed by text | Display the LLM-generated response directly to the user |
| `AGENT_RAG_CONTEXT_START` ... `AGENT_RAG_CONTEXT_END` (exit code 2) | The script found wiki context but has no API key. **You** must synthesize the answer using the printed context (see Step 3) |
| `No matching context found` | Inform the user that no relevant pages exist in the wiki for this topic |

### Step 3 — Agent RAG Fallback (Exit Code 2)

When the script outputs structured context between `AGENT_RAG_CONTEXT_START` and `AGENT_RAG_CONTEXT_END`:

1. **Read the context** — it contains the top 5 wiki documents relevant to the question
2. **Synthesize an answer** grounded in the provided wiki context
3. **Follow these rules**:
   - Respond in the **same language** as the user's question
   - **Ground** your answer in the wiki context. Distinguish vault content from general knowledge
   - **Preserve** scientific terms and LaTeX notation natively (do not translate)
   - **Do NOT** include meta-summaries (e.g., "Work Summary" / "Ringkasan Pekerjaan")
   - **Always conclude** with a `## References` (or `## Referensi`) section containing a minimalist, clean bulleted list of standard Markdown links (no double brackets `[[` or `]]`) of the vault documents utilized:
     ```
     ## Referensi
     - Alec Radford et al. (2019) — [source-document-1](path)
     - Deskripsi singkat atau bidang/kategori — [concept-document-2](path)
     ```

---

## Query Protocol (`query <keywords>`)

```bash
rtk python scripts/search.py "<keywords>"
```

Display the ranked results (page names, scores, snippets) to the user.

---

## Vault Structure

```
wiki/
├── .search_index.db    # SQLite FTS5 search index (rebuilt via make_index.py)
├── en/                 # English sub-wiki
│   ├── concepts/       # Concept pages by domain
│   ├── entities/       # Entity pages by domain
│   └── sources/        # Source summary pages
└── id/                 # Indonesian sub-wiki (parallel structure)
```

- **Bilingual**: Every page has a parallel translation linked via `translation: "[[page-name]]"` in YAML frontmatter
- **Naming**: English pages use `kebab-case.md`, Indonesian pages append `-id` suffix (e.g., `concept-id.md`)
- **Linking**: Use Obsidian `[[wikilinks]]` syntax

## Creating / Updating Notes

1. Follow the YAML frontmatter schemas in `WIKI_SCHEMA.md` §2
2. Place files in the correct `wiki/<lang>/<type>/<domain>/` directory
3. Always create both EN and ID versions with reciprocal `translation:` links
4. After changes, run `rtk python scripts/make_index.py` to rebuild the index

## Rebuilding Search Index

If search returns stale or missing results:

```bash
rtk python scripts/make_index.py
```
