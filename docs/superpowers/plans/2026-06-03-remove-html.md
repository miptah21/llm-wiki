# Remove HTML Conversion Capability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean up the codebase by removing the HTML dashboard generation module and all related triggers, indexes, and tests.

**Architecture:** Remove `scripts/html_generator.py` and `wiki/html/` from the repository, edit `scripts/ingest.py`, `scripts/make_index.py`, and `scripts/test_wiki.py` to strip out all HTML compilation and indexing references.

**Tech Stack:** Python, Git.

---

### Task 1: Delete HTML Generator and HTML Output Files

**Files:**
- [DELETE] `scripts/html_generator.py`
- [DELETE] `wiki/html/` (directory and compiled html files)

- [ ] **Step 1: Delete `scripts/html_generator.py`**
  Remove the Python script responsible for HTML generation.
  
- [ ] **Step 2: Delete `wiki/html/` directory**
  Remove the directory containing all compiled HTML files.
  
- [ ] **Step 3: Commit deletion**
  ```bash
  git rm scripts/html_generator.py
  # Delete the directory from git
  git rm -r wiki/html/
  git commit -m "refactor: delete html_generator and compiled html outputs"
  ```

---

### Task 2: Remove HTML Triggers from Ingest Pipeline

**Files:**
- Modify: `scripts/ingest.py:479-486`
- Test: Ingest test file and ensure no HTML generator subprocess is triggered.

- [ ] **Step 1: Modify `scripts/ingest.py`**
  Remove lines 479 to 486 which invoke `html_generator.py` inside `main()`.
  
  *Target Content to remove:*
  ```python
      # 9. Auto-trigger Companion HTML Dashboard compilation
      print("Auto-triggering Companion HTML Dashboard compilation...")
      try:
          subprocess.run([sys.executable, "scripts/html_generator.py", raw_path], check=True)
          print("Companion HTML Dashboard successfully compiled!")
      except Exception as e:
          print(f"Warning: Failed to run html_generator.py: {e}")
  ```

- [ ] **Step 2: Verify changes**
  Run `git diff scripts/ingest.py` to confirm the block is removed.

- [ ] **Step 3: Commit changes**
  ```bash
  git add scripts/ingest.py
  git commit -m "refactor: remove html dashboard compilation trigger from ingest"
  ```

---

### Task 3: Clean up Indexing and Test suite files

**Files:**
- Modify: `scripts/make_index.py:270-284`
- Modify: `scripts/test_wiki.py:39,156,292-314`
- Test: Run `scripts/test_wiki.py` to ensure all tests pass.

- [ ] **Step 1: Modify `scripts/make_index.py`**
  Remove the section appending Interactive HTML Dashboards to index pages (lines 270-284).
  
  *Target Content to remove:*
  ```python
      # Append Interactive HTML Dashboards
      output.append("\n## 🖥️ Dashboard HTML Interaktif\n" if not is_en else "\n## 🖥️ Interactive HTML Dashboards\n")
      html_dir = os.path.join(WIKI_DIR, "html")
      if os.path.exists(html_dir):
          html_files = [f for f in os.listdir(html_dir) if f.endswith(".html")]
          if not html_files:
              output.append("*Belum ada dashboard HTML terkompilasi.*\n" if not is_en else "*No interactive HTML dashboards compiled yet.*\n")
          else:
              for hf in sorted(html_files):
                  name = hf.replace("source-", "").replace("-id.html", "").replace("-id", "").replace(".html", "").replace("-", " ").title()
                  abs_path = os.path.abspath(os.path.join(html_dir, hf)).replace("\\", "/")
                  output.append(f"- [{name} (HTML)](file:///{abs_path}) — Dashboard interaktif Bahasa Indonesia." if not is_en else f"- [{name} (HTML)](file:///{abs_path}) — Interactive Indonesian dashboard.")
      else:
          output.append("*Belum ada dashboard HTML terkompilasi.*\n" if not is_en else "*No interactive HTML dashboards compiled yet.*\n")
  ```

- [ ] **Step 2: Modify `scripts/test_wiki.py`**
  - Remove line 39: `TEST_HTML_OUTPUT = os.path.join("wiki", "html", "source-mock_ingest_test-id.html")`
  - Remove `TEST_HTML_OUTPUT` from list on line 156 inside `cleanup()`.
  - Remove HTML dashboard tests block (lines 292-314).
  
- [ ] **Step 3: Run project tests**
  Ensure all automated tests pass successfully:
  ```powershell
  python scripts/test_wiki.py
  ```

- [ ] **Step 4: Commit and finalize**
  ```bash
  git add scripts/make_index.py scripts/test_wiki.py
  git commit -m "refactor: clean up index pages and test suite from HTML dashboard logic"
  ```
