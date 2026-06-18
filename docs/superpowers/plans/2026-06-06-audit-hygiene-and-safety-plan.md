# Repo Hygiene, Path Safety, and Test Collection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the 6 top audit findings regarding git hygiene, path safety, machine-specific paths, and pytest capture conflicts on Windows.

**Architecture:** 
1. Clean git tracking by untracking generated artifacts and bytecode while ensuring `.agents/`, `docs/`, `AGENTS.md`, and `requirements.txt` are tracked.
2. Secure path checks using `pathlib`'s resolution to prevent directory traversal.
3. Move module-level stdout stream configurations inside `if __name__ == "__main__":` blocks to resolve pytest collection and execution crashes.

**Tech Stack:** Python 3.12, Git, Pytest

---

### Task 1: Git Hygiene & Dependency Manifest Tracking

**Files:**
- Modify: `.gitignore`
- Modify: Root `requirements.txt`
- Untrack: `audit_report.md`, `scripts/__pycache__/*.pyc`

- [ ] **Step 1: Check `.gitignore` content**
  Verify that `.gitignore` contains the following lines:
  ```gitignore
  # Runtime/session artifacts
  .superpowers/
  scratch/
  .pytest_cache/
  __pycache__/
  *.py[cod]
  audit_report.md
  scripts/audit_report.md
  test_fig_1.png

  # Generated local cache
  /wiki/.search_index.db

  # Raw PDFs are local source assets; compiled wiki pages track source metadata.
  *.pdf
  ```
  Ensure `.agents/`, `docs/`, and `AGENTS.md` are NOT ignored.

- [ ] **Step 2: Untrack generated reports and bytecode**
  Run:
  ```powershell
  rtk git rm --cached audit_report.md
  rtk git rm --cached scripts/__pycache__/ingest.cpython-312.pyc scripts/__pycache__/parser.cpython-312.pyc scripts/__pycache__/stemmer.cpython-312.pyc
  ```
  Expected: Files are removed from index/tracking but remain on the local filesystem.

- [ ] **Step 3: Track root manifest, core files, and spec**
  Run:
  ```powershell
  rtk git add requirements.txt .agents/ docs/ AGENTS.md .gitignore
  ```
  Expected: Staged files ready for commit.

- [ ] **Step 4: Commit Git Hygiene changes**
  Run:
  ```powershell
  rtk git commit -m "chore: clean git tracking, untrack reports/bytecode, and track requirements.txt, docs, and agents"
  ```
  Expected: Commit succeeds.

---

### Task 2: Robust Path Validation

**Files:**
- Modify: `scripts/ingest/persistence.py`
- Test: `scripts/test_persistence_unit.py`

- [ ] **Step 1: Write path safety check in `persistence.py`**
  Modify `scripts/ingest/persistence.py` to import `Path` and implement `_is_within_path` using `Path.resolve()`.
  
  Replace lines 20-26:
  ```python
  def _is_within_path(child_path: str, parent_path: str) -> bool:
      child_norm = os.path.normcase(os.path.abspath(child_path))
      parent_norm = os.path.normcase(os.path.abspath(parent_path))
      try:
          return os.path.commonpath([child_norm, parent_norm]) == parent_norm
      except ValueError:
          return False
  ```
  
  With:
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

- [ ] **Step 2: Run persistence unit tests to verify**
  Run:
  ```powershell
  python -m unittest scripts.test_persistence_unit
  ```
  Expected: Tests pass.

- [ ] **Step 3: Commit Path Safety changes**
  Run:
  ```powershell
  rtk git add scripts/ingest/persistence.py
  rtk git commit -m "refactor(ingest): use robust pathlib-based path safety validation"
  ```
  Expected: Commit succeeds.

---

### Task 3: Pytest Stream Capture Compatibility

**Files:**
- Modify: `scripts/ingest.py`
- Modify: `scripts/linter.py`
- Modify: `scripts/make_index.py`
- Modify: `scripts/search.py`
- Modify: `scripts/test_wiki.py`

- [ ] **Step 1: Move stream reconfigure in `scripts/ingest.py`**
  Remove lines 7-14:
  ```python
  # Windows encoding safeguard for emoji output
  if sys.platform.startswith("win"):
      try:
          sys.stdout.reconfigure(encoding="utf-8")
          sys.stderr.reconfigure(encoding="utf-8")
      except AttributeError:
          import io
          sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
          sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
  ```
  
  And place it at the top of the `__main__` block (around line 545):
  ```python
  if __name__ == "__main__":
      if sys.platform.startswith("win"):
          try:
              sys.stdout.reconfigure(encoding="utf-8")
              sys.stderr.reconfigure(encoding="utf-8")
          except AttributeError:
              import io
              sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
              sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
      main()
  ```

- [ ] **Step 2: Move stream reconfigure in `scripts/linter.py`**
  Remove lines 5-9:
  ```python
  # Windows Encoding Safeguard for non-ASCII characters / emojis
  if sys.platform.startswith("win"):
      import io
      sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
      sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
  ```
  
  And place it at the top of the `__main__` block (around line 299):
  ```python
  if __name__ == "__main__":
      import sys
      if sys.platform.startswith("win"):
          import io
          sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
          sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
      sys.exit(lint_vault())
  ```

- [ ] **Step 3: Move stream reconfigure in `scripts/make_index.py`**
  Remove lines 6-10:
  ```python
  # Windows Encoding Safeguard for non-ASCII characters / emojis
  if sys.platform.startswith("win"):
      import io
      sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
      sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
  ```
  
  And place it at the top of the `__main__` block (around line 452):
  ```python
  if __name__ == "__main__":
      if sys.platform.startswith("win"):
          import io
          sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
          sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
      build_index()
  ```

- [ ] **Step 4: Move stream reconfigure in `scripts/search.py`**
  Remove lines 14-18:
  ```python
  # Windows Encoding Safeguard for non-ASCII characters / emojis
  if sys.platform.startswith("win"):
      import io
      sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
      sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
  ```
  
  And place it at the top of the `__main__` block (around line 281):
  ```python
  if __name__ == "__main__":
      if sys.platform.startswith("win"):
          import io
          sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
          sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
      main()
  ```

- [ ] **Step 5: Move stream reconfigure in `scripts/test_wiki.py`**
  Remove lines 6-10:
  ```python
  # Windows Encoding Safeguard for non-ASCII characters / emojis
  if sys.platform.startswith("win"):
      import io
      sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
      sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
  ```
  
  And place it at the top of the `__main__` block (around line 578):
  ```python
  if __name__ == "__main__":
      if sys.platform.startswith("win"):
          import io
          sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
          sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
      success = run_tests()
      sys.exit(0 if success else 1)
  ```

- [ ] **Step 6: Commit Stream Compatibility changes**
  Run:
  ```powershell
  rtk git add scripts/ingest.py scripts/linter.py scripts/make_index.py scripts/search.py scripts/test_wiki.py
  rtk git commit -m "fix(scripts): move Windows stream wrapping to main blocks to prevent pytest crashes"
  ```
  Expected: Commit succeeds.

---

### Task 4: Complete Validation

**Files:**
- Test: All workspace test files

- [ ] **Step 1: Run pytest suite**
  Run:
  ```powershell
  pytest
  ```
  Expected: Pytest successfully collects 17 tests and executes them without standard stream closed issues. All tests pass.

- [ ] **Step 2: Run individual unittest file**
  Run:
  ```powershell
  python -m unittest scripts.test_stemmer
  ```
  Expected: 4 tests run successfully and pass.

- [ ] **Step 3: Run integration test script**
  Run:
  ```powershell
  python scripts/test_wiki.py
  ```
  Expected: Test pipeline completes successfully and exits with code 0.

- [ ] **Step 4: Commit any remaining metadata path updates**
  Run:
  ```powershell
  rtk git add wiki/
  rtk git commit -m "fix(wiki): clean absolute paths in wiki pages, replacing them with relative paths"
  ```
  Expected: All remaining localized paths are committed.
