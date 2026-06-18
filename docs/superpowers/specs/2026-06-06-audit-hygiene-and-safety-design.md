# Design Spec: Repository Hygiene, Path Safety, and Test Collection Fixes

## Status
- **Date**: 2026-06-06
- **Status**: Approved

## Problem Statement
The LLM Wiki repository was audited, revealing several hygiene, portability, and safety issues:
1. **Core project intelligence is ignored**: Upstream `.gitignore` ignores `.agents/`, `docs/`, and `AGENTS.md`.
2. **No root dependency manifest**: The root is missing a tracked `requirements.txt` to reproduce the environment.
3. **Path validation weakness**: Safe path checks are prone to misclassifying sibling directories with similar prefixes if done with `startswith`.
4. **Machine-specific path logic**: Absolute local paths were previously written into sources and indexes.
5. **Tracked generated artifacts / bytecode**: `audit_report.md` and `__pycache__` bytecode files are currently tracked in git.
6. **Inconsistent test entrypoints / pytest crashes**: Standard stream wrapping at module-level in CLI scripts causes pytest collection to crash on Windows.

## Proposed Changes

### 1. Git Hygiene and Portability
- Track `requirements.txt`, `.agents/`, `docs/`, and `AGENTS.md`.
- Remove `audit_report.md` and `scripts/__pycache__/*.pyc` from git tracking while keeping them ignored in `.gitignore`.
- Run:
  ```bash
  git rm --cached audit_report.md
  git rm -r --cached scripts/__pycache__
  ```

### 2. Robust Path Validation
- Replace the directory check in [persistence.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/ingest/persistence.py) with a `pathlib`-based check:
  ```python
  from pathlib import Path

  def _is_within_path(child_path: str, parent_path: str) -> bool:
      try:
          child = Path(child_path).resolve()
          parent = Path(parent_path).resolve()
          return parent == child or parent in child.parents
      except (ValueError, RuntimeError):
          return False
  ```

### 3. Portable Metadata Paths
- Ensure all ingested source files use relative paths. (Confirmed that the current local scripts already generate relative paths like `raw/papers/...`, we just need to stage/commit them).

### 4. Pytest & CLI Compatibility (Standard Output Reconfiguration)
- Move standard output and error stream wrapping blocks out of the module import scope and place them inside the `if __name__ == "__main__":` blocks of the following files:
  - [scripts/ingest.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/ingest.py)
  - [scripts/linter.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/linter.py)
  - [scripts/make_index.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/make_index.py)
  - [scripts/search.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/search.py)
  - [scripts/test_wiki.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/test_wiki.py)

This allows testing frameworks (like pytest) to import these modules safely without crashing due to stream capturing conflicts.

## Verification Plan

### Automated Tests
- Run `rtk pytest` to verify that all 17 tests are collected and run cleanly without stream crashes.
- Run `python -m unittest scripts.test_stemmer` and ensure it executes successfully.
- Run `python scripts/test_wiki.py` to check the end-to-end ingestion pipeline in mock mode.
