# Split-Screen Scrollytelling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modify the static horizontal-tabbed dashboard generator into a premium split-screen scrollytelling platform where the left column displays scroll-linked narratives, and the right column houses a persistent sticky visualizer (Three.js WebGL / SVG Map) with dynamic content overlays harvested from the source document.

**Architecture:** Implement a Python text harvester to clean and extract visual descriptions from section markdown, embed these as HTML `data-description` attributes, and update the JavaScript scroll observer to dynamically populate overlay card title and description.

**Tech Stack:** Python (BeautifulSoup, Regex, Frontmatter parser), Javascript (Vanilla ES6, Three.js WebGL, Intersection Observer, SVG DOM), CSS (Vanilla Custom Properties, Grid, Transitions).

---

### Task 1: Implement Dynamic Markdown Parser and Harvester in Python

**Files:**
- Modify: `scripts/html_generator.py`
- Test: Verify compiled html files contain parsed data-description attributes.

- [ ] **Step 1: Write markdown description cleaner helper**
  Add a helper function `extract_clean_description(md_text)` to strip wiki links, formatting, quotes, and extract the first 2 sentences for visual card overlays.
  
  ```python
  def extract_clean_description(md_text):
      """Mengekstrak deskripsi bersih (2 kalimat pertama) tanpa sintaks markdown untuk atribut HTML."""
      if not md_text:
          return ""
      
      # Hapus frontmatter jika ada
      text = md_text.strip()
      if text.startswith("---"):
          parts = text.split("---", 2)
          if len(parts) >= 3:
              text = parts[2].strip()
              
      # Bersihkan tag HTML
      text = re.sub(r"<[^>]*>", "", text)
      
      # Bersihkan wikilinks: [[Target|Teks]] -> Teks, [[Target]] -> Target
      def clean_wikilink(match):
          content = match.group(1).strip()
          parts = content.split("|")
          return parts[1].strip() if len(parts) > 1 else parts[0].strip()
      text = re.sub(r"\[\[(.*?)\]\]", clean_wikilink, text)
      
      # Bersihkan format bold/italic
      text = re.sub(r"\*\*([^\*]+)\*\*", r"\1", text)
      text = re.sub(r"\*([^\*]+)\*", r"\1", text)
      text = re.sub(r"`([^`]+)`", r"\1", text)
      
      # Ambil baris pertama atau paragraf pertama yang tidak kosong
      paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
      first_p = paragraphs[0] if paragraphs else text
      
      # Batasi hingga 2 kalimat pertama
      sentences = re.split(r"(?<=[.!?])\s+", first_p)
      summary = " ".join(sentences[:2])
      
      # Escape double quotes agar tidak merusak atribut HTML
      summary = summary.replace('"', '&quot;').replace("'", '&#39;')
      return summary[:280] + "..." if len(summary) > 280 else summary
  ```

- [ ] **Step 2: Update summary parsing to harvest descriptions**
  Update the summary compiler inside `main()` of `scripts/html_generator.py` to extract dynamic descriptions and compile them to `<section>` blocks.
  
  ```python
  sections_data = split_markdown_into_sections(summary_raw)
  sections_html = []
  for idx, sec in enumerate(sections_data):
      mode_attrs = get_visual_mode_for_section(sec["title"])
      clean_desc = extract_clean_description(sec["content"])
      body_html = parse_markdown_to_html(sec["content"], local_elements)
      sections_html.append(
          f'<section class="narrative-section" id="section-narrative-{idx}" {mode_attrs} data-description="{clean_desc}">\n'
          f'  <h2>{sec["title"]}</h2>\n'
          f'  <div class="section-body">{body_html}</div>\n'
          f'</section>'
      )
  summary_html = "\n\n".join(sections_html)
  ```

- [ ] **Step 3: Run compilation test**
  ```powershell
  python scripts/html_generator.py raw/articles/The_Unreasonable_Effectiveness_Of_HTML.md
  ```
  Expected: Success without syntax error.

- [ ] **Step 4: Commit changes**
  ```bash
  git add scripts/html_generator.py
  git commit -m "feat: implement dynamic markdown description harvester in Python"
  ```

---

### Task 2: Implement Dynamic HTML/CSS Layout

**Files:**
- Modify: `scripts/html_generator.py`
- Test: Verify grid structural styling.

- [ ] **Step 1: Implement split-screen container**
  Ensure CSS for `.scrollytelling-container` grid, active sections, and sticky visualizer panels are correctly defined inside `build_html_template`.
  
- [ ] **Step 2: Hook up DOM tab summary structure**
  Embed dynamic narrative text container and sticky visualizer controls.
  
- [ ] **Step 3: Verify output generation**
  Verify compilation.
  
- [ ] **Step 4: Commit changes**
  ```bash
  git add scripts/html_generator.py
  git commit -m "style: embed responsive split-column layout framework"
  ```

---

### Task 3: Update JavaScript Scroll Engine to use Dynamic Harvester

**Files:**
- Modify: `scripts/html_generator.py`
- Test: Test visual page scrolls.

- [ ] **Step 1: Replace JS static explanation maps with dynamic attributes**
  Remove the hardcoded string checks in JS and update `updateVisualExplanationText()` to pull description directly from DOM elements.
  
  ```javascript
  function updateVisualExplanationText(mode, ratio, highlightDebug, description) {
      const descCard = document.getElementById('visual-card-desc');
      if (description) {
          descCard.innerText = description;
      } else {
          descCard.innerText = "Gulir untuk meninjau bagian visualisasi.";
      }
  }
  ```

- [ ] **Step 2: Update active section activation handler**
  Update `activateSection` to read the descriptive attributes.
  
  ```javascript
  function activateSection(sectionEl) {
      if (activeSection === sectionEl) return;
      
      if (activeSection) {
          activeSection.classList.remove('active-section');
      }
      
      activeSection = sectionEl;
      activeSection.classList.add('active-section');
      
      const visualMode = sectionEl.getAttribute('data-visual-mode');
      const ratio = sectionEl.getAttribute('data-ratio');
      const highlightDebug = sectionEl.getAttribute('data-highlight-debug');
      const description = sectionEl.getAttribute('data-description');
      const sectionTitle = sectionEl.querySelector('h2').innerText;
      
      document.getElementById('visual-card-title').innerText = sectionTitle;
      updateVisualExplanationText(visualMode, ratio, highlightDebug, description);
      triggerVisualizerTransition(visualMode, ratio, highlightDebug);
  }
  ```

- [ ] **Step 3: Run compilation test**
  Verify generator compilation.
  
- [ ] **Step 4: Commit changes**
  ```bash
  git add scripts/html_generator.py
  git commit -m "feat: make scroll-linked JS observer engine fully dynamic"
  ```

---

### Task 4: Dual-document Verification & Project Audit

**Files:**
- Modify: `scripts/html_generator.py`
- Test: Compile paper PDF + HTML article, check layouts in browser.

- [ ] **Step 1: Compile paper dashboard**
  Run:
  ```powershell
  python scripts/html_generator.py raw/papers/2509.20820v1.pdf
  ```
  Expected: Dashboard compiles, contains paper-specific data-description values.

- [ ] **Step 2: Compile HTML article dashboard**
  Run:
  ```powershell
  python scripts/html_generator.py raw/articles/The_Unreasonable_Effectiveness_Of_HTML.md
  ```
  Expected: Dashboard compiles, contains HTML article-specific descriptions instead of paper data.

- [ ] **Step 3: Run test suite and linter**
  Verify everything builds.
  ```powershell
  python scripts/test_wiki.py
  python scripts/linter.py
  ```

- [ ] **Step 4: Git commit and cleanup**
  ```bash
  git status
  ```
