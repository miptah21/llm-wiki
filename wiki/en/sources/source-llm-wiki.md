---
type: source
source_file: "raw/articles/llm-wiki.md"
sha256: "dc3efe98ae62f23dd08acad13aba2e95287beb20b6bec2f4af0423557fe37401"
translation: "[[source-llm-wiki-id]]"
created: 2026-06-03
updated: 2026-06-03
tags: [llm-wiki, knowledge-base, system-design, obsidian]
---

# LLM Wiki

**Author:** Andrej Karpathy
**Format:** Concept Proposal
**Reading Time:** 4 minutes

---

## Abstract / Summary

This document describes the **LLM Wiki Pattern**, a software architecture and workflow for constructing compounding, persistent personal knowledge bases using LLMs. Unlike standard RAG systems where an LLM rediscovers knowledge from raw documents on each query without accumulation, the LLM Wiki pattern introduces a persistent intermediate layer of LLM-maintained Markdown files (the *wiki*). As new sources are ingested, the LLM incrementally updates relevant concept and entity summaries, files cross-references, and logs conflicts, creating a self-improving knowledge base that gets richer over time.

---

## Key Architectural Layers

1. **Raw Sources**: The curation layer containing immutable source documents (papers, articles, transcripts). The LLM reads from here but never writes to it.
2. **The Wiki**: The persistent, structured directory of compiled, LLM-generated markdown files (summaries, concepts, entities, indices).
3. **The Schema**: The configuration and protocol layer (e.g., `AGENTS.md` or `WIKI_SCHEMA.md`) that guides the LLM agent on how to manage, lint, and update the wiki.

---

## Core Operations

1. **Ingest**: Triggered upon adding a new source. The LLM summarizes the file, extracts key concepts and entities, updates existing wiki pages to integrate the new knowledge, and appends a chronological audit log.
2. **Query**: Answering user questions by searching and reading compiled wiki pages, synthesizing cited responses, and optionally filing high-value queries back into the wiki as new pages.
3. **Lint**: Periodic automated audits checking for factual contradictions, broken cross-references, orphaned pages, or gaps that require web searches or deeper research.

---

## Key System Components

* **index.md**: Content-oriented visual catalog listing all compiled knowledge pages, categories, and sources.
* **log.md**: Chronological, append-only record of system operations.
* **CLI/MCP Tools**: Optional scripting tools (e.g., [qmd](https://github.com/tobi/qmd) for hybrid BM25/vector search) to automate indexing or query-routing tasks.

---

## Linked Concepts

- [[llm-wiki-pattern]]
- [[in-context-learning]]

## Linked Entities

- [[obsidian]]
- [[vannevar-bush]]
- [[memex]]
