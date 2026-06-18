# Design Spec: Flat Ingestion and Paper-Specific Structure

This design document outlines the transition of the PDF ingestion pipeline from a multi-file, nested folder structure with media/table extraction to a clean, flat single-file structure with rich inline section summaries matching the paper's layout, inspired by [source-2509.20820v1.md](file:///C:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/wiki/en/sources/source-2509.20820v1.md).

## 1. Objectives

- Disable table and image extraction during ingestion to prevent extracting clutter.
- Stop generating separate subpages for `-experiments` and `-mathematics` and nested directories.
- Make all ingested sources flat files directly inside `wiki/en/sources/` and `wiki/id/sources/`.
- Ensure the ingested paper summaries follow a structured layout matching the paper sections (Abstract, Problem Statement, Core Method, Key Experimental Results, Limitations, etc.) and include metadata (Authors, Affiliations, Publication info, Code repositories).
- Update the local fallback and the test suite (`test_wiki.py`) to align with this new behavior.

## 2. Proposed Changes

### 2.1. Ingestion Pipeline (`scripts/ingest.py`)

- Disable calls to `extract_pdf_tables` and `extract_pdf_images`.
- Remove directory creation code under `wiki/en/sources/<filename_base>/` and always use the parent `wiki/en/sources/` (flat structure).
- Modify the formatting logic of `src_body_en` and `src_body_id` to include paper metadata (Authors, Affiliation, Published, Code) and sections dynamically.
- Remove the code that writes experiments and mathematics subpages.

### 2.2. LLM Ingestion Pipeline (`scripts/ingest/llm_pipeline.py`)

- Update the system prompts in `process_deepseek` to request paper metadata (`authors`, `affiliation`, `published`, `code`) in the JSON schema.
- Update the reduce prompt so the LLM outputs a structured summary organized under:
  - `## Abstract`
  - `## Problem Statement`
  - `## Core Method`
  - `## Key Experimental Results`
  - `## Limitations`
- Return these newly extracted metadata fields to the caller.

### 2.3. Offline Ingestion Pipeline (`scripts/ingest/local_fallback.py`)

- Update `process_offline` to output a clean flat structure.
- Align the output schema of `process_offline` with the updated JSON schema in `process_deepseek` (returning metadata like `authors`, `affiliation`, etc. if available, or empty/reasonable fallbacks).

### 2.4. Tests Suite (`scripts/test_wiki.py`)

- Update `test_wiki.py` to assert that:
  - Ingesting `mock_paper_test.pdf` creates flat source files `wiki/en/sources/source-mock_paper_test.md` and `wiki/id/sources/source-mock_paper_test-id.md`.
  - No subdirectories or subpages are created.
  - The generated source pages contain the proper frontmatter and structured headers.

## 3. Verification Plan

- Run the automated test suite locally: `python scripts/test_wiki.py` (or using `rtk python scripts/test_wiki.py` under the RTK guidelines).
- Run the project linter: `python scripts/linter.py`.
