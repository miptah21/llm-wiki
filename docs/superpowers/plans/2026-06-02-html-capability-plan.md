# Kapabilitas Kompilasi Dashboard HTML Interaktif (/html) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Membangun kapabilitas `/html` dalam bentuk script `scripts/html_generator.py` yang mengompilasi dokumen raw Markdown beserta ringkasan Bahasa Indonesia terkompilasi, konsep, dan entitas terkait di wiki menjadi satu file Dashboard HTML Bahasa Indonesia tunggal mandiri (self-contained) berestetika premium dan berinteraktivitas tinggi.

**Architecture:** Script Python mandiri mendeteksi ringkasan sumber di folder `wiki/id/sources/` untuk suatu file raw, merayapi (*crawls*) semua wikilink konsep dan entitas Bahasa Indonesia yang tertaut, lalu mengompilasi data teks Markdown tersebut menjadi satu file HTML SPA. File HTML ini menggunakan CSS Glassmorphism premium (tema gelap default), Vanilla JS untuk kontrol tampilan dinamis (ukuran font, lebar halaman, parameter animasi tombol), pustaka MathJax CDN untuk render LaTeX rumus matematika, dan SVG interaktif untuk visualisasi peta hubungan.

**Tech Stack:** Python 3 (standard libraries: `os`, `sys`, `re`, `json`, `datetime`, `subprocess`), HTML5, CSS3, Vanilla JavaScript, MathJax CDN (untuk LaTeX).

---

### Task 1: Scaffolding scripts/html_generator.py & CLI Interface

**Files:**
- Create: `scripts/html_generator.py`

- [ ] **Step 1: Tulis struktur kode dasar generator HTML**
  Buat file `scripts/html_generator.py` dengan penanganan argumen CLI, safeguard pengodean Windows UTF-8, pemuatan fungsi utilitas parser YAML frontmatter dari `scripts/parser.py`, serta fungsi deteksi file sumber.

  ```python
  import os
  import sys
  import re
  from datetime import datetime

  # Windows Encoding Safeguard for non-ASCII characters / emojis
  if sys.platform.startswith("win"):
      import io
      sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
      sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

  # Tambahkan direktori scripts ke path
  sys.path.append(os.path.dirname(os.path.abspath(__file__)))
  from parser import parse_yaml_frontmatter

  WIKI_DIR = "wiki"
  EN_DIR = os.path.join(WIKI_DIR, "en")
  ID_DIR = os.path.join(WIKI_DIR, "id")
  HTML_DIR = os.path.join(WIKI_DIR, "html")

  def find_compiled_source_id(filename_base):
      """Mencari file ringkasan Bahasa Indonesia untuk file raw tertentu."""
      target_filename = f"source-{filename_base}-id.md"
      # Cari di wiki/id/sources/
      source_path = os.path.join(ID_DIR, "sources", target_filename)
      if os.path.exists(source_path):
          return source_path
      # Fallback pencarian case-insensitive
      sources_dir = os.path.join(ID_DIR, "sources")
      if os.path.exists(sources_dir):
          for file in os.listdir(sources_dir):
              if file.lower() == target_filename.lower():
                  return os.path.join(sources_dir, file)
      return None
  ```

- [ ] **Step 2: Tambahkan logika CLI entrypoint utama**
  Tambahkan fungsi `main()` untuk memproses argumen baris perintah, mencari file ringkasan, dan memicu integrasi ingest jika ringkasan belum ada.

  ```python
  def main():
      if len(sys.argv) < 2:
          print("Penggunaan: python scripts/html_generator.py <path-to-raw-file>")
          sys.exit(1)
          
      raw_path = sys.argv[1]
      if not os.path.exists(raw_path):
          print(f"Error: File mentah tidak ditemukan di '{raw_path}'")
          sys.exit(1)
          
      filename_base = os.path.splitext(os.path.basename(raw_path))[0]
      print(f"Memulai kompilasi HTML untuk aset mentah: {filename_base}")
      
      source_path_id = find_compiled_source_id(filename_base)
      if not source_path_id:
          print(f"Peringatan: Ringkasan Bahasa Indonesia tidak ditemukan untuk '{filename_base}'.")
          print("Memicu pipeline /ingest otomatis terlebih dahulu...")
          import subprocess
          try:
              subprocess.run([sys.executable, "scripts/ingest.py", raw_path], check=True)
              source_path_id = find_compiled_source_id(filename_base)
          except Exception as e:
              print(f"Error: Gagal memicu ingest otomatis: {e}")
              sys.exit(1)
              
      if not source_path_id or not os.path.exists(source_path_id):
          print("Error: Gagal menemukan file ringkasan hasil ingest.")
          sys.exit(1)
          
      print(f"Menemukan ringkasan terkompilasi: {source_path_id}")
      
  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 3: Uji jalankan struktur dasar script**
  Jalankan perintah pengujian untuk memastikan script dasar dapat diimpor tanpa kesalahan sintaks.
  Run: `python scripts/html_generator.py raw/articles/The\ Unreasonable\ Effectiveness\ Of\ HTML.md`
  Expected: Terbaca tulisan "Menemukan ringkasan terkompilasi: wiki\id\sources\source-The Unreasonable Effectiveness Of HTML-id.md" (atau sejenisnya).

- [ ] **Step 4: Commit**
  ```bash
  git add scripts/html_generator.py
  git commit -m "feat: tambahkan struktur dasar html_generator.py"
  ```

---

### Task 2: Markdown Parser & Wikilink Resolver

**Files:**
- Modify: `scripts/html_generator.py`

- [ ] **Step 1: Tulis fungsi parser Markdown ke HTML kustom**
  Tambahkan fungsi parser Markdown ke HTML berbasis RegEx di `scripts/html_generator.py`. Fungsi ini juga mendeteksi wikilink dan mengembalikannya ke pemanggilan JavaScript.

  ```python
  def parse_markdown_to_html(md_text, local_elements=None):
      """Parser Markdown-ke-HTML sederhana berbasis ekspresi reguler."""
      if not md_text:
          return ""
      
      html = md_text.strip()
      
      # Bersihkan frontmatter jika ada di awal teks
      if html.startswith("---"):
          parts = html.split("---", 2)
          if len(parts) >= 3:
              html = parts[2].strip()
              
      # 1. Lindungi blok kode multi-baris agar tidak dirusak format lain
      code_blocks = []
      def code_block_placeholder(match):
          lang = match.group(1) or "text"
          code = match.group(2)
          # Escape HTML karakter di dalam kode
          code_escaped = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
          idx = len(code_blocks)
          code_blocks.append(f'<pre><code class="language-{lang}">{code_escaped}</code></pre>')
          return f"__CODE_BLOCK_PLACEHOLDER_{idx}__"
          
      html = re.sub(r"```(\w*)\n(.*?)\n```", code_block_placeholder, html, flags=re.DOTALL)
      
      # 2. Lindungi kode inline
      inline_codes = []
      def inline_code_placeholder(match):
          code = match.group(1)
          code_escaped = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
          idx = len(inline_codes)
          inline_codes.append(f'<code>{code_escaped}</code>')
          return f"__INLINE_CODE_PLACEHOLDER_{idx}__"
          
      html = re.sub(r"`(.*?)`", inline_code_placeholder, html)

      # 3. Lindungi rumus LaTeX Math Block $$...$$ dan inline $...$
      math_blocks = []
      def math_block_placeholder(match):
          formula = match.group(1)
          idx = len(math_blocks)
          math_blocks.append(f'<div class="math-block">$${formula}$$</div>')
          return f"__MATH_BLOCK_PLACEHOLDER_{idx}__"
      html = re.sub(r"\$\$(.*?)\$\$", math_block_placeholder, html, flags=re.DOTALL)

      math_inlines = []
      def math_inline_placeholder(match):
          formula = match.group(1)
          idx = len(math_inlines)
          math_inlines.append(f'<span class="math-inline">${formula}$</span>')
          return f"__MATH_INLINE_PLACEHOLDER_{idx}__"
      html = re.sub(r"\$(.*?)\$", math_inline_placeholder, html)

      # 4. Heading formatting
      html = re.sub(r"^#### (.*?)$", r"<h4>\1</h4>", html, flags=re.MULTILINE)
      html = re.sub(r"^### (.*?)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
      html = re.sub(r"^## (.*?)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
      html = re.sub(r"^# (.*?)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

      # 5. Bold & Italic
      html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html)
      html = re.sub(r"\*(.*?)\*", r"<em>\1</em>", html)

      # 6. Blockquotes
      html = re.sub(r"^>\s?(.*?)$", r"<blockquote>\1</blockquote>", html, flags=re.MULTILINE)

      # 7. Unordered Lists (Grup berurutan)
      # Mengubah baris-baris list menjadi <li>
      html = re.sub(r"^[\-\*]\s+(.*?)$", r"<li>\1</li>", html, flags=re.MULTILINE)
      # Menyatukan deretan <li> yang berdekatan menjadi satu <ul>
      # Pendekatan sederhana: cari barisan <li> berurutan
      html = re.sub(r"(<li>.*?</li>\n?)+", lambda m: f"<ul>\n{m.group(0)}</ul>\n", html)

      # 8. Wikilinks Resolution (Interactive dynamic links)
      def wikilink_replacement(match):
          link_content = match.group(1).strip()
          parts = link_content.split("|")
          link_target = parts[0].strip()
          link_text = parts[1].strip() if len(parts) > 1 else link_target
          
          target_clean = link_target.lower().replace(" ", "-")
          
          # Cek apakah target ada di dalam list element lokal dashboard kita
          if local_elements and target_clean in local_elements:
              el_type = local_elements[target_clean]["type"] # 'concept' atau 'entity'
              return f'<a href="javascript:void(0)" class="wiki-link" onclick="focusElement(\'{el_type}\', \'{target_clean}\')">{link_text}</a>'
          else:
              # Jika target luar, buat tautan default non-aktif
              return f'<span class="wiki-link-external" title="Tautan luar: {link_target}">{link_text}</span>'
              
      html = re.sub(r"\[\[(.*?)\]\]", wikilink_replacement, html)

      # 9. Paragraf (baris baru ganda)
      paragraphs = []
      for block in html.split("\n\n"):
          block = block.strip()
          if not block:
              continue
          if block.startswith("<h") or block.startswith("<ul") or block.startswith("<pre") or block.startswith("<blockquote") or block.startswith("<div"):
              paragraphs.append(block)
          else:
              paragraphs.append(f"<p>{block}</p>")
      html = "\n\n".join(paragraphs)

      # 10. Kembalikan rumus LaTeX dan blok kode yang dilindungi
      for i, block in enumerate(math_blocks):
          html = html.replace(f"__MATH_BLOCK_PLACEHOLDER_{i}__", block)
      for i, inline in enumerate(math_inlines):
          html = html.replace(f"__MATH_INLINE_PLACEHOLDER_{i}__", inline)
      for i, block in enumerate(code_blocks):
          html = html.replace(f"__CODE_BLOCK_PLACEHOLDER_{i}__", block)
      for i, inline in enumerate(inline_codes):
          html = html.replace(f"__INLINE_CODE_PLACEHOLDER_{i}__", inline)

      return html
  ```

- [ ] **Step 2: Tambahkan fungsi parsing untuk merayapi konsep dan entitas**
  Tulis logika untuk membuka ringkasan Bahasa Indonesia, membaca daftar wikilink konsep dan entitas terasosiasi, memuat file MD-nya masing-masing, dan mengembalikan kumpulan data terstruktur.

  ```python
  def find_wiki_file(name, category_dir):
      """Mencari file markdown untuk konsep atau entitas tertentu."""
      name_clean = name.lower().replace(" ", "-")
      
      # Jelajahi subfolder domain di dalam category_dir
      if not os.path.exists(category_dir):
          return None
          
      for domain in os.listdir(category_dir):
          domain_path = os.path.join(category_dir, domain)
          if os.path.isdir(domain_path):
              # Cari file langsung
              filepath = os.path.join(domain_path, f"{name_clean}.md")
              if os.path.exists(filepath):
                  return filepath
              # Jika tidak ada akhiran -id, coba cari dengan akhiran -id
              if not name_clean.endswith("-id"):
                  filepath_id = os.path.join(domain_path, f"{name_clean}-id.md")
                  if os.path.exists(filepath_id):
                      return filepath_id
      return None

  def crawl_related_nodes(source_content):
      """Mengekstrak wikilink dan memuat data konsep & entitas Bahasa Indonesia terkait."""
      links = re.findall(r"\[\[(.*?)\]\]", source_content)
      
      local_elements = {}
      concepts = []
      entities = []
      
      for link in links:
          clean_name = link.split("|")[0].strip()
          key_name = clean_name.lower().replace(" ", "-")
          
          # Skip jika tautan luar
          if clean_name.startswith("http") or clean_name.startswith("www"):
              continue
              
          # 1. Coba cari di folder konsep Bahasa Indonesia
          concept_dir = os.path.join(ID_DIR, "concepts")
          concept_file = find_wiki_file(clean_name, concept_dir)
          
          if concept_file:
              try:
                  with open(concept_file, "r", encoding="utf-8") as f:
                      content = f.read()
                  metadata = parse_yaml_frontmatter(content)
                  concepts.append({
                      "key": key_name,
                      "name": clean_name.replace("-id", "").replace("-", " ").title(),
                      "metadata": metadata,
                      "content": content
                  })
                  local_elements[key_name] = {"type": "concept", "id": key_name}
                  if not key_name.endswith("-id"):
                      local_elements[f"{key_name}-id"] = {"type": "concept", "id": key_name}
                  continue
              except Exception as e:
                  print(f"Gagal membaca konsep {clean_name}: {e}")
                  
          # 2. Coba cari di folder entitas Bahasa Indonesia
          entity_dir = os.path.join(ID_DIR, "entities")
          entity_file = find_wiki_file(clean_name, entity_dir)
          
          if entity_file:
              try:
                  with open(entity_file, "r", encoding="utf-8") as f:
                      content = f.read()
                  metadata = parse_yaml_frontmatter(content)
                  entities.append({
                      "key": key_name,
                      "name": clean_name.replace("-id", "").replace("-", " ").title(),
                      "metadata": metadata,
                      "content": content
                  })
                  local_elements[key_name] = {"type": "entity", "id": key_name}
                  if not key_name.endswith("-id"):
                      local_elements[f"{key_name}-id"] = {"type": "entity", "id": key_name}
              except Exception as e:
                  print(f"Gagal membaca entitas {clean_name}: {e}")
                  
      return concepts, entities, local_elements
  ```

- [ ] **Step 3: Uji parser dengan contoh input**
  Tambahkan pemanggilan `crawl_related_nodes` di `main()` dan cetak konsep yang ditemukan untuk verifikasi sementara.
  Run: `python scripts/html_generator.py raw/articles/The\ Unreasonable\ Effectiveness\ Of\ HTML.md`
  Expected: Konsep tercetak seperti `html-maximalism-id` dan `agent-html-artifacts-id`.

- [ ] **Step 4: Commit**
  ```bash
  git add scripts/html_generator.py
  git commit -m "feat: tambahkan parser markdown & crawler relasi"
  ```

---

### Task 3: SVG Knowledge Graph Map Generator

**Files:**
- Modify: `scripts/html_generator.py`

- [ ] **Step 1: Tulis generator representasi graf SVG dinamis**
  Tambahkan fungsi Python di `scripts/html_generator.py` untuk menggambar peta hubungan dynamic berbasis koordinat lingkaran terdistribusi.

  ```python
  import math

  def generate_relations_svg(filename_base, concepts, entities):
      """Menggenerasikan diagram hubungan vektor SVG dinamis."""
      nodes = []
      # Taruh Source utama di tengah
      nodes.append({
          "id": "source-node",
          "name": filename_base.replace("-", " ").replace("_", " ").title(),
          "type": "source",
          "x": 400,
          "y": 300,
          "r": 50,
          "color": "var(--accent-cyan)",
          "glow": "rgba(0, 242, 254, 0.4)"
      })
      
      orbit_nodes = []
      for c in concepts:
          orbit_nodes.append({
              "id": c["key"],
              "name": c["name"],
              "type": "concept",
              "color": "var(--accent-purple)",
              "glow": "rgba(155, 81, 224, 0.4)",
              "r": 35
          })
      for e in entities:
          orbit_nodes.append({
              "id": e["key"],
              "name": e["name"],
              "type": "entity",
              "color": "#ff4757",
              "glow": "rgba(255, 71, 87, 0.4)",
              "r": 35
          })
          
      num_nodes = len(orbit_nodes)
      cx, cy = 400, 300
      r_orbit = 200
      
      for idx, node in enumerate(orbit_nodes):
          angle = (2 * math.pi * idx) / num_nodes if num_nodes > 0 else 0
          node["x"] = cx + r_orbit * math.cos(angle)
          node["y"] = cy + r_orbit * math.sin(angle)
          nodes.append(node)
          
      # Gambar elemen SVG
      svg_lines = []
      svg_circles = []
      
      # 1. Gambar Garis Penghubung
      for node in nodes:
          if node["id"] != "source-node":
              svg_lines.append(
                  f'<line x1="{cx}" y1="{cy}" x2="{node["x"]}" y2="{node["y"]}" '
                  f'class="relation-line relation-to-{node["id"]}" '
                  f'stroke="rgba(255, 255, 255, 0.15)" stroke-width="2" />'
              )
              
      # 2. Gambar Node Lingkaran
      for node in nodes:
          click_js = ""
          if node["type"] != "source":
              click_js = f'onclick="focusElement(\'{node["type"]}\', \'{node["id"]}\')"'
              
          svg_circles.append(
              f'<g class="node-group" id="g-{node["id"]}" {click_js} style="cursor: pointer;" '
              f'onmouseover="highlightNode(\'{node["id"]}\', \'{node["name"]}\', \'{node["type"]}\')" '
              f'onmouseout="resetHighlight(\'{node["id"]}\')">\n'
              f'  <circle cx="{node["x"]}" cy="{node["y"]}" r="{node["r"]}" '
              f'  fill="{node["color"]}" filter="url(#glow-{node["id"]})" />\n'
              f'  <text x="{node["x"]}" y="{node["y"] + 5}" text-anchor="middle" '
              f'  fill="#ffffff" font-size="10" font-weight="bold" font-family=\'Outfit\', sans-serif>'
              f'    {node["name"][:12] + "..." if len(node["name"]) > 12 else node["name"]}'
              f'  </text>\n'
              f'</g>'
          )
          
      # 3. Definisikan Filters Glow
      glow_defs = []
      for node in nodes:
          glow_defs.append(
              f'<filter id="glow-{node["id"]}" x="-30%" y="-30%" width="160%" height="160%">\n'
              f'  <feGaussianBlur stdDeviation="6" result="blur" />\n'
              f'  <feComposite in="SourceGraphic" in2="blur" operator="over" />\n'
              f'</filter>'
          )
          
      svg_content = (
          f'<svg width="100%" height="550" viewBox="0 0 800 600" class="interactive-graph-svg">\n'
          f'  <defs>\n'
          f'    {"".join(glow_defs)}\n'
          f'  </defs>\n'
          f'  {"".join(svg_lines)}\n'
          f'  {"".join(svg_circles)}\n'
          f'</svg>'
      )
      return svg_content
  ```

- [ ] **Step 2: Commit**
  ```bash
  git add scripts/html_generator.py
  git commit -m "feat: tambahkan generator graf relasi SVG interaktif"
  ```

---

### Task 4: Premium HTML/CSS/JS Template Rendering & Sandbox

**Files:**
- Modify: `scripts/html_generator.py`

- [ ] **Step 1: Buat template markup & styling HTML komprehensif**
  Tambahkan fungsi Python `build_html_template` untuk menyatukan desain CSS Glassmorphism premium, vanilla JavaScript tab logic, sandbox sliders, copy utilities, dan diagram hubungan SVG ke dalam satu string HTML utuh (Bahasa Indonesia).

  ```python
  def build_html_template(filename_base, raw_path, checksum, summary_html, raw_md_html, concepts_data, entities_data, svg_map):
      """Menggabungkan seluruh komponen menjadi halaman HTML SPA utuh."""
      current_date = datetime.now().strftime("%Y-%m-%d")
      
      # Bangun markup kartu Konsep
      concepts_html = []
      for c in concepts_data:
          desc_html = parse_markdown_to_html(c["metadata"].get("description", ""))
          body_html = parse_markdown_to_html(c["content"])
          concepts_html.append(
              f'<div class="info-card" id="card-concept-{c["key"]}">\n'
              f'  <div class="card-header concept-header">\n'
              f'    <h3>💡 {c["name"]}</h3>\n'
              f'    <span class="badge badge-purple">{c["metadata"].get("domain", "ai").upper()}</span>\n'
              f'  </div>\n'
              f'  <div class="card-body">\n'
              f'    <p class="card-desc"><em>{desc_html}</em></p>\n'
              f'    <div class="card-full-content">{body_html}</div>\n'
              f'  </div>\n'
              f'</div>'
          )
      if not concepts_html:
          concepts_html.append('<div class="empty-state"><p>Tidak ada konsep terkait yang dikompilasi.</p></div>')

      # Bangun markup kartu Entitas
      entities_html = []
      for e in entities_data:
          body_html = parse_markdown_to_html(e["content"])
          cat = e["metadata"].get("category", "tool").upper()
          entities_html.append(
              f'<div class="info-card" id="card-entity-{e["key"]}">\n'
              f'  <div class="card-header entity-header">\n'
              f'    <h3>👥 {e["name"]}</h3>\n'
              f'    <span class="badge badge-coral">{cat}</span>\n'
              f'  </div>\n'
              f'  <div class="card-body">\n'
              f'    <div class="card-full-content">{body_html}</div>\n'
              f'  </div>\n'
              f'</div>'
          )
      if not entities_html:
          entities_html.append('<div class="empty-state"><p>Tidak ada entitas terkait yang dikompilasi.</p></div>')
          
      html_output = f"""<!DOCTYPE html>
  <html lang="id">
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Kompilasi Dashboard: {filename_base.replace("-", " ").title()}</title>
      <!-- Google Fonts -->
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
      <!-- MathJax CDN -->
      <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
      <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
      
      <style>
          :root {{
              --bg-base: #080c14;
              --bg-surface: rgba(17, 24, 39, 0.7);
              --border-color: rgba(255, 255, 255, 0.08);
              --text-main: #e2e8f0;
              --text-muted: #94a3b8;
              --accent-cyan: #00f2fe;
              --accent-purple: #9b51e0;
              --accent-coral: #ff4757;
              --font-family-body: 'Inter', sans-serif;
              --font-family-heading: 'Outfit', sans-serif;
              --page-font-size: 16px;
              --page-max-width: 800px;
              --button-duration: 300ms;
              --button-radius: 8px;
          }}

          * {{
              box-sizing: border-box;
              margin: 0;
              padding: 0;
          }}

          body {{
              background-color: var(--bg-base);
              color: var(--text-main);
              font-family: var(--font-family-body);
              font-size: var(--page-font-size);
              line-height: 1.6;
              padding-bottom: 50px;
          }}

          .blur-bg {{
              position: fixed;
              top: 0;
              left: 0;
              width: 100%;
              height: 100%;
              z-index: -1;
              background: radial-gradient(circle at 10% 20%, rgba(155, 81, 224, 0.1) 0%, transparent 45%),
                          radial-gradient(circle at 90% 80%, rgba(0, 242, 254, 0.1) 0%, transparent 45%);
              pointer-events: none;
          }}

          /* Premium Header Navigation */
          header {{
              position: sticky;
              top: 0;
              z-index: 100;
              background: rgba(8, 12, 20, 0.75);
              backdrop-filter: blur(15px);
              border-bottom: 1px solid var(--border-color);
              padding: 15px 40px;
              display: flex;
              justify-content: space-between;
              align-items: center;
          }}

          header h1 {{
              font-family: var(--font-family-heading);
              font-size: 22px;
              font-weight: 700;
              background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
              -webkit-background-clip: text;
              -webkit-text-fill-color: transparent;
          }}

          .nav-tabs {{
              display: flex;
              gap: 10px;
          }}

          .tab-btn {{
              background: transparent;
              border: 1px solid transparent;
              color: var(--text-muted);
              font-family: var(--font-family-heading);
              font-size: 14px;
              font-weight: 500;
              padding: 8px 16px;
              border-radius: 8px;
              cursor: pointer;
              transition: all 0.3s ease;
          }}

          .tab-btn:hover {{
              color: #ffffff;
              background: rgba(255, 255, 255, 0.05);
          }}

          .tab-btn.active {{
              color: var(--accent-cyan);
              background: rgba(0, 242, 254, 0.1);
              border-color: rgba(0, 242, 254, 0.2);
          }}

          /* Main Container */
          .container {{
              max-width: 1200px;
              margin: 40px auto;
              padding: 0 20px;
          }}

          .tab-content {{
              display: none;
              animation: fadeIn 0.4s ease forwards;
          }}

          .tab-content.active {{
              display: block;
          }}

          @keyframes fadeIn {{
              from {{ opacity: 0; transform: translateY(10px); }}
              to {{ opacity: 1; transform: translateY(0); }}
          }}

          /* Elements & Styling */
          .info-grid {{
              display: grid;
              grid-template-columns: 2fr 1fr;
              gap: 30px;
          }}

          @media (max-width: 900px) {{
              .info-grid {{
                  grid-template-columns: 1fr;
              }}
          }}

          .card {{
              background: var(--bg-surface);
              backdrop-filter: blur(12px);
              border: 1px solid var(--border-color);
              border-radius: 12px;
              padding: 30px;
              margin-bottom: 30px;
          }}

          .card h2 {{
              font-family: var(--font-family-heading);
              font-size: 24px;
              margin-bottom: 20px;
              border-left: 4px solid var(--accent-cyan);
              padding-left: 12px;
          }}

          .badge {{
              display: inline-block;
              font-size: 11px;
              font-weight: 600;
              padding: 4px 10px;
              border-radius: 20px;
              text-transform: uppercase;
              letter-spacing: 0.5px;
          }}

          .badge-purple {{
              background: rgba(155, 81, 224, 0.15);
              color: #d1b3ff;
              border: 1px solid rgba(155, 81, 224, 0.3);
          }}

          .badge-coral {{
              background: rgba(255, 71, 87, 0.15);
              color: #ff9f9f;
              border: 1px solid rgba(255, 71, 87, 0.3);
          }}

          .wiki-link {{
              color: var(--accent-cyan);
              text-decoration: none;
              border-bottom: 1px dashed var(--accent-cyan);
              cursor: pointer;
              transition: all 0.2s ease;
          }}

          .wiki-link:hover {{
              color: #ffffff;
              background: rgba(0, 242, 254, 0.1);
              border-bottom-style: solid;
          }}

          .wiki-link-external {{
              color: var(--text-muted);
              border-bottom: 1px dotted var(--text-muted);
          }}

          blockquote {{
              border-left: 4px solid var(--accent-purple);
              background: rgba(155, 81, 224, 0.05);
              padding: 15px 20px;
              margin: 20px 0;
              border-radius: 0 8px 8px 0;
              font-style: italic;
          }}

          pre {{
              background: #0d1117;
              border: 1px solid var(--border-color);
              border-radius: 8px;
              padding: 15px;
              overflow-x: auto;
              margin: 20px 0;
          }}

          code {{
              font-family: 'Courier New', Courier, monospace;
              background: rgba(255, 255, 255, 0.08);
              padding: 2px 6px;
              border-radius: 4px;
              font-size: 90%;
          }}

          pre code {{
              background: transparent;
              padding: 0;
          }}

          /* Grid for Concepts/Entities cards */
          .cards-grid {{
              display: grid;
              grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
              gap: 20px;
          }}

          .info-card {{
              background: var(--bg-surface);
              backdrop-filter: blur(12px);
              border: 1px solid var(--border-color);
              border-radius: 12px;
              padding: 24px;
              transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
          }}

          .info-card:hover {{
              transform: translateY(-5px);
              border-color: rgba(255, 255, 255, 0.2);
              box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
          }}

          .card-header {{
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 15px;
              border-bottom: 1px solid var(--border-color);
              padding-bottom: 10px;
          }}

          .card-header h3 {{
              font-family: var(--font-family-heading);
              font-size: 18px;
          }}

          .card-desc {{
              color: var(--text-muted);
              font-size: 14px;
              margin-bottom: 15px;
          }}

          .card-full-content {{
              font-size: 14px;
              margin-top: 10px;
          }}

          /* Raw Content width controls */
          .raw-content-wrapper {{
              max-width: var(--page-max-width);
              margin: 0 auto;
              transition: max-width 0.3s ease;
          }}

          /* Highlight animation pulse */
          @keyframes pulseHighlight {{
              0% {{ box-shadow: 0 0 0 0 rgba(0, 242, 254, 0.7); border-color: var(--accent-cyan); }}
              70% {{ box-shadow: 0 0 0 12px rgba(0, 242, 254, 0); }}
              100% {{ box-shadow: 0 0 0 0 rgba(0, 242, 254, 0); }}
          }}

          .pulse-active {{
              animation: pulseHighlight 1.5s ease-in-out;
              border-color: var(--accent-cyan) !important;
          }}

          /* Tooltip for SVG SVG Map */
          .svg-tooltip {{
              position: absolute;
              background: rgba(8, 12, 20, 0.95);
              border: 1px solid var(--accent-cyan);
              padding: 10px 15px;
              border-radius: 8px;
              font-size: 12px;
              color: #ffffff;
              pointer-events: none;
              opacity: 0;
              transition: opacity 0.2s ease;
              z-index: 1000;
              max-width: 250px;
              box-shadow: 0 5px 15px rgba(0,0,0,0.5);
          }}

          /* SVG graph hover styles */
          .relation-line.highlight {{
              stroke: var(--accent-cyan) !important;
              stroke-width: 4px !important;
              opacity: 1 !important;
              filter: drop-shadow(0 0 8px var(--accent-cyan));
          }}

          .node-group:hover circle {{
              stroke: #ffffff;
              stroke-width: 2px;
              transform: scale(1.05);
              transform-origin: center;
              transition: all 0.2s ease;
          }}

          /* Sandbox components */
          .sandbox-container {{
              display: grid;
              grid-template-columns: 1fr 1fr;
              gap: 30px;
          }}

          @media (max-width: 800px) {{
              .sandbox-container {{
                  grid-template-columns: 1fr;
              }}
          }}

          .control-group {{
              margin-bottom: 20px;
          }}

          .control-group label {{
              display: block;
              margin-bottom: 8px;
              font-family: var(--font-family-heading);
              font-size: 14px;
              color: var(--text-muted);
          }}

          .control-slider {{
              width: 100%;
              height: 6px;
              background: rgba(255,255,255,0.1);
              border-radius: 3px;
              outline: none;
              -webkit-appearance: none;
          }}

          .control-slider::-webkit-slider-thumb {{
              -webkit-appearance: none;
              width: 18px;
              height: 18px;
              border-radius: 50%;
              background: var(--accent-cyan);
              cursor: pointer;
              box-shadow: 0 0 10px var(--accent-cyan);
              transition: transform 0.1s;
          }}

          .control-slider::-webkit-slider-thumb:hover {{
              transform: scale(1.2);
          }}

          /* Sandbox Demo Widget Button */
          .sandbox-widget-area {{
              display: flex;
              flex-direction: column;
              justify-content: center;
              align-items: center;
              background: rgba(255, 255, 255, 0.02);
              border: 1px dashed var(--border-color);
              border-radius: 12px;
              padding: 40px;
          }}

          .demo-action-btn {{
              background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
              color: #ffffff;
              font-family: var(--font-family-heading);
              font-weight: 600;
              font-size: 16px;
              padding: 12px 30px;
              border: none;
              border-radius: var(--button-radius);
              cursor: pointer;
              box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
              transition: transform var(--button-duration) ease, 
                          box-shadow var(--button-duration) ease,
                          border-radius var(--button-duration) ease;
          }}

          .demo-action-btn:hover {{
              transform: scale(1.05);
              box-shadow: 0 6px 20px rgba(155, 81, 224, 0.5);
          }}

          .demo-action-btn:active {{
              transform: scale(0.98);
          }}

          .sandbox-btn-export {{
              background: rgba(255,255,255,0.08);
              color: #ffffff;
              font-family: var(--font-family-heading);
              border: 1px solid var(--border-color);
              padding: 8px 16px;
              border-radius: 6px;
              cursor: pointer;
              margin-top: 20px;
              transition: all 0.2s;
          }}

          .sandbox-btn-export:hover {{
              background: rgba(0, 242, 254, 0.15);
              border-color: var(--accent-cyan);
          }}
      </style>
  </head>
  <body>
      <div class="blur-bg"></div>

      <header>
          <h1>📊 LLM Wiki Dashboard</h1>
          <div class="nav-tabs">
              <button class="tab-btn active" onclick="switchTab('summary')">📊 Ringkasan</button>
              <button class="tab-btn" onclick="switchTab('raw')">📄 Raw Markdown</button>
              <button class="tab-btn" onclick="switchTab('concepts')">💡 Konsep ({len(concepts_data)})</button>
              <button class="tab-btn" onclick="switchTab('entities')">👥 Entitas ({len(entities_data)})</button>
              <button class="tab-btn" onclick="switchTab('sandbox')">🎛️ Sandbox</button>
              <button class="tab-btn" onclick="switchTab('graph')">🕸️ Peta Hubungan</button>
          </div>
      </header>

      <div class="container">
          
          <!-- TAB 1: SUMMARY -->
          <div id="tab-summary" class="tab-content active">
              <div class="info-grid">
                  <div>
                      <div class="card">
                          <h2>Ringkasan Sumber: {filename_base.replace("-", " ").title()}</h2>
                          <div style="margin-top: 15px;">
                              {summary_html}
                          </div>
                      </div>
                  </div>
                  <div>
                      <div class="card" style="padding: 20px;">
                          <h3 style="font-family: var(--font-family-heading); margin-bottom: 15px; border-bottom: 1px solid var(--border-color); padding-bottom: 5px;">Metadata Aset</h3>
                          <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 10px;"><strong>Path Mentah:</strong><br><code style="word-break: break-all;">{raw_path}</code></p>
                          <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 10px;"><strong>SHA-256 Checksum:</strong><br><code style="font-size: 11px; word-break: break-all;">{checksum}</code></p>
                          <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 10px;"><strong>Kompilasi HTML:</strong> {current_date}</p>
                          <p style="font-size: 13px; color: var(--text-muted);"><strong>Status:</strong> <span class="badge badge-purple" style="font-size: 9px; vertical-align: middle;">Verified</span></p>
                      </div>
                  </div>
              </div>
          </div>

          <!-- TAB 2: RAW MARKDOWN -->
          <div id="tab-raw" class="tab-content">
              <div class="card">
                  <div class="raw-content-wrapper" id="raw-content-wrapper">
                      <h2>Dokumen Markdown Mentah</h2>
                      <div style="margin-top: 20px; white-space: pre-wrap;" class="raw-text-view">
                          {raw_md_html}
                      </div>
                  </div>
              </div>
          </div>

          <!-- TAB 3: CONCEPTS -->
          <div id="tab-concepts" class="tab-content">
              <div class="cards-grid">
                  {"".join(concepts_html)}
              </div>
          </div>

          <!-- TAB 4: ENTITIES -->
          <div id="tab-entities" class="tab-content">
              <div class="cards-grid">
                  {"".join(entities_html)}
              </div>
          </div>

          <!-- TAB 5: SANDBOX -->
          <div id="tab-sandbox" class="tab-content">
              <div class="card">
                  <h2>🎛️ Sandbox Parameter & Eksperimen UI</h2>
                  <p style="color: var(--text-muted); margin-bottom: 25px;">Sesuaikan variabel di bawah untuk mengontrol parameter tampilan visual secara real-time. Bagian ini mendemonstrasikan kekuatan interaktivitas HTML!</p>
                  
                  <div class="sandbox-container">
                      <div>
                          <h3 style="font-family: var(--font-family-heading); margin-bottom: 15px; border-bottom: 1px solid var(--border-color); padding-bottom: 5px;">Kontrol Tata Letak</h3>
                          
                          <div class="control-group">
                              <label for="slider-font-size">Ukuran Font Artikel: <span id="lbl-font-size">16</span>px</label>
                              <input type="range" id="slider-font-size" class="control-slider" min="14" max="24" value="16" oninput="updateFontSize(this.value)">
                          </div>

                          <div class="control-group">
                              <label for="slider-max-width">Lebar Konten Mentah: <span id="lbl-max-width">800</span>px</label>
                              <input type="range" id="slider-max-width" class="control-slider" min="600" max="1100" value="800" oninput="updateMaxWidth(this.value)">
                          </div>

                          <h3 style="font-family: var(--font-family-heading); margin-top: 25px; margin-bottom: 15px; border-bottom: 1px solid var(--border-color); padding-bottom: 5px;">Parameter Animasi Tombol</h3>
                          
                          <div class="control-group">
                              <label for="slider-duration">Durasi Transisi: <span id="lbl-duration">300</span>ms</label>
                              <input type="range" id="slider-duration" class="control-slider" min="100" max="1500" value="300" oninput="updateButtonDuration(this.value)">
                          </div>

                          <div class="control-group">
                              <label for="slider-radius">Border Radius Tombol: <span id="lbl-radius">8</span>px</label>
                              <input type="range" id="slider-radius" class="control-slider" min="0" max="25" value="8" oninput="updateButtonRadius(this.value)">
                          </div>
                      </div>

                      <div class="sandbox-widget-area">
                          <h4 style="font-family: var(--font-family-heading); margin-bottom: 20px;">Prototipe Animasi Tombol Aksi</h4>
                          <button class="demo-action-btn" onclick="triggerBtnInteraction()">Klik Saya!</button>
                          <p style="font-size: 12px; color: var(--text-muted); margin-top: 15px; text-align: center;">Tombol di atas dimodifikasi secara dinamis oleh variabel CSS menggunakan slider parameters di sebelah kiri.</p>
                          
                          <button class="sandbox-btn-export" onclick="exportSandboxConfig()">📥 Ekspor Konfigurasi JSON</button>
                      </div>
                  </div>
              </div>
          </div>

          <!-- TAB 6: INTERACTIVE GRAPH MAP -->
          <div id="tab-graph" class="tab-content">
              <div class="card" style="position: relative; overflow: hidden; padding: 10px;">
                  <h2 style="padding: 20px 0 0 20px;">🕸️ Peta Hubungan Vektor SVG</h2>
                  <p style="padding-left: 20px; color: var(--text-muted); font-size: 13px;">Arahkan kursor Anda ke node konsep atau entitas untuk menyoroti relasi neon. Klik pada salah satu node untuk berpindah tab dan menyorot detail halaman!</p>
                  {svg_map}
              </div>
          </div>

      </div>

      <div class="svg-tooltip" id="svg-tooltip"></div>

      <!-- Logic Script -->
      <script>
          function switchTab(tabId) {{
              // Hapus status aktif dari semua tab-btn dan tab-content
              document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
              document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
              
              // Temukan tombol saat ini berdasarkan tabId
              let btnIdx = 0;
              if (tabId === 'summary') btnIdx = 0;
              else if (tabId === 'raw') btnIdx = 1;
              else if (tabId === 'concepts') btnIdx = 2;
              else if (tabId === 'entities') btnIdx = 3;
              else if (tabId === 'sandbox') btnIdx = 4;
              else if (tabId === 'graph') btnIdx = 5;
              
              document.querySelectorAll('.tab-btn')[btnIdx].classList.add('active');
              document.getElementById('tab-' + tabId).classList.add('active');
              
              // Memicu re-render MathJax jika ada persamaan LaTeX di tab konsep
              if (tabId === 'concepts' && window.MathJax) {{
                  MathJax.typesetPromise();
              }}
          }}

          // In-page dynamic navigations
          function focusElement(type, cleanId) {{
              let tabTarget = type === 'concept' ? 'concepts' : 'entities';
              switchTab(tabTarget);
              
              let cardId = 'card-' + type + '-' + cleanId;
              let element = document.getElementById(cardId);
              
              if (element) {{
                  // Berikan sedikit waktu agar transisi tab selesai
                  setTimeout(() => {{
                      element.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                      element.classList.add('pulse-active');
                      
                      // Hapus class setelah animasi kedip selesai (1.5 detik)
                      setTimeout(() => {{
                          element.classList.remove('pulse-active');
                      }}, 1500);
                  }}, 200);
              }}
          }}

          // SVG Interactive map utilities
          const tooltip = document.getElementById('svg-tooltip');

          function highlightNode(nodeId, nodeName, nodeType) {{
              // Nyalakan neon line penghubung ke node pusat
              let lines = document.querySelectorAll('.relation-to-' + nodeId);
              lines.forEach(line => line.classList.add('highlight'));
              
              // Tampilkan tooltip
              let gGroup = document.getElementById('g-' + nodeId);
              if (gGroup) {{
                  let rect = gGroup.getBoundingClientRect();
                  tooltip.innerHTML = `<strong>${{nodeName}}</strong><br><span style="color:var(--text-muted); text-transform:uppercase; font-size:10px;">${{nodeType}}</span>`;
                  tooltip.style.opacity = 1;
                  tooltip.style.left = (window.scrollX + rect.left + (rect.width/2) - 100) + 'px';
                  tooltip.style.top = (window.scrollY + rect.top - 55) + 'px';
              }}
          }}

          function resetHighlight(nodeId) {{
              let lines = document.querySelectorAll('.relation-to-' + nodeId);
              lines.forEach(line => line.classList.remove('highlight'));
              tooltip.style.opacity = 0;
          }}

          // Sandbox UI controller
          function updateFontSize(val) {{
              document.getElementById('lbl-font-size').innerText = val;
              document.body.style.fontSize = val + 'px';
          }}

          function updateMaxWidth(val) {{
              document.getElementById('lbl-max-width').innerText = val;
              document.documentElement.style.setProperty('--page-max-width', val + 'px');
          }}

          function updateButtonDuration(val) {{
              document.getElementById('lbl-duration').innerText = val;
              document.documentElement.style.setProperty('--button-duration', val + 'ms');
          }}

          function updateButtonRadius(val) {{
              document.getElementById('lbl-radius').innerText = val;
              document.documentElement.style.setProperty('--button-radius', val + 'px');
          }}

          function triggerBtnInteraction() {{
              let btn = document.querySelector('.demo-action-btn');
              btn.style.transform = 'scale(0.9)';
              setTimeout(() => {{
                  btn.style.transform = '';
              }}, 150);
          }}

          function exportSandboxConfig() {{
              let config = {{
                  fontSize: document.getElementById('slider-font-size').value + 'px',
                  contentWidth: document.getElementById('slider-max-width').value + 'px',
                  transitionDuration: document.getElementById('slider-duration').value + 'ms',
                  borderRadius: document.getElementById('slider-radius').value + 'px',
                  compiledDate: "{current_date}"
              }};
              
              navigator.clipboard.writeText(JSON.stringify(config, null, 2)).then(() => {{
                  alert('Konfigurasi berhasil disalin ke clipboard!:\\n\\n' + JSON.stringify(config, null, 2));
              }}).catch(err => {{
                  alert('Gagal menyalin konfigurasi: ' + err);
              }});
          }}
      </script>
  </body>
  </html>
  """
      return html_output
  ```

- [ ] **Step 2: Gabungkan seluruh proses ke dalam write file utama**
  Tulis implementasi penuh logika kompilasi di `main()` dari `scripts/html_generator.py` untuk membaca file mentah, ringkasan, crawling relasi, menggabungkan SVG graf, merender template, dan menuliskan file HTML di direktori tujuan `wiki/html/`.

  ```python
  def main():
      if len(sys.argv) < 2:
          print("Penggunaan: python scripts/html_generator.py <path-to-raw-file>")
          sys.exit(1)
          
      raw_path = sys.argv[1]
      if not os.path.exists(raw_path):
          print(f"Error: File mentah tidak ditemukan di '{raw_path}'")
          sys.exit(1)
          
      filename_base = os.path.splitext(os.path.basename(raw_path))[0]
      print(f"Memulai kompilasi HTML untuk aset mentah: {filename_base}")
      
      source_path_id = find_compiled_source_id(filename_base)
      if not source_path_id:
          print(f"Peringatan: Ringkasan Bahasa Indonesia tidak ditemukan untuk '{filename_base}'.")
          print("Memicu pipeline /ingest otomatis terlebih dahulu...")
          import subprocess
          try:
              subprocess.run([sys.executable, "scripts/ingest.py", raw_path], check=True)
              source_path_id = find_compiled_source_id(filename_base)
          except Exception as e:
              print(f"Error: Gagal memicu ingest otomatis: {e}")
              sys.exit(1)
              
      if not source_path_id or not os.path.exists(source_path_id):
          print("Error: Gagal menemukan file ringkasan hasil ingest.")
          sys.exit(1)
          
      # 1. Baca isi file ringkasan terkompilasi
      with open(source_path_id, "r", encoding="utf-8") as f:
          summary_raw = f.read()
          
      # 2. Baca isi file mentah asli
      with open(raw_path, "r", encoding="utf-8") as f:
          raw_raw = f.read()
          
      # 3. Parse Metadata frontmatter ringkasan
      metadata = parse_yaml_frontmatter(summary_raw)
      checksum = metadata.get("sha256", "UNKNOWN-CHECKSUM")
      
      # 4. Rayapi node konsep & entitas Bahasa Indonesia yang tertaut
      concepts_data, entities_data, local_elements = crawl_related_nodes(summary_raw)
      print(f"Hasil rayapan relasi: Ditemukan {len(concepts_data)} konsep & {len(entities_data)} entitas.")
      
      # 5. Parse Markdown menjadi HTML (menyuplai local_elements untuk resolusi wikilink)
      summary_html = parse_markdown_to_html(summary_raw, local_elements)
      raw_md_html = parse_markdown_to_html(raw_raw, local_elements)
      
      # 6. Gambar Peta hubungan vektor SVG dinamis
      svg_map = generate_relations_svg(filename_base, concepts_data, entities_data)
      
      # 7. Kompilasikan template HTML lengkap
      full_html = build_html_template(
          filename_base, 
          raw_path, 
          checksum, 
          summary_html, 
          raw_md_html, 
          concepts_data, 
          entities_data, 
          svg_map
      )
      
      # 8. Tulis file output HTML
      os.makedirs(HTML_DIR, exist_ok=True)
      output_filename = f"source-{filename_base}-id.html"
      output_path = os.path.join(HTML_DIR, output_filename)
      
      with open(output_path, "w", encoding="utf-8") as f:
          f.write(full_html)
          
      print(f"Kompilasi sukses! Dashboard HTML disimpan di: {output_path}")
      
  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 3: Jalankan kompilasi untuk memverifikasi file HTML terbuat**
  Run: `python scripts/html_generator.py raw/articles/The\ Unreasonable\ Effectiveness\ Of\ HTML.md`
  Expected: Terbuat file baru `wiki/html/source-The Unreasonable Effectiveness Of HTML-id.html` berisi dashboard HTML Bahasa Indonesia yang sangat indah.

- [ ] **Step 4: Commit**
  ```bash
  git add scripts/html_generator.py
  git commit -m "feat: implementasikan template html komprehensif & sandbox"
  ```

---

### Task 5: Automated Testing in test_wiki.py

**Files:**
- Modify: `scripts/test_wiki.py` (Menambahkan unit test baru untuk `html_generator.py`)

- [ ] **Step 1: Modifikasi scripts/test_wiki.py**
  Tambahkan fungsi verifikasi pengujian `html_generator.py` di dalam `run_tests()` untuk membuktikan keberfungsian parsing Markdown kustom, crawler relasi, dan output visual HTML.

  Tambahkan target pembersihan baru di `cleanup()` dari `scripts/test_wiki.py` sekitar baris 155:
  ```python
  # Target file di cleanup()
  TEST_HTML_OUTPUT = os.path.join("wiki", "html", "source-mock_ingest_test-id.html")
  # Tambahkan TEST_HTML_OUTPUT ke list filepath yang dihapus oleh cleanup()
  ```

  Tambahkan langkah pengujian baru (Step 7) di `run_tests()` sebelum `cleanup()` di `scripts/test_wiki.py` (sekitar baris 290):
  ```python
  # --- Step 7: Test html_generator.py (HTML Dashboard Compiler) ---
  print("\n--- Testing html_generator.py ---")
  code, stdout, stderr = run_script("html_generator.py", [INGEST_RAW_FILE])
  print(stdout)
  if code != 0:
      print(f"❌ html_generator.py failed with exit code {code}! Error: {stderr}")
      return False
      
  test_html_path = os.path.join("wiki", "html", "source-mock_ingest_test-id.html")
  if os.path.exists(test_html_path):
      with open(test_html_path, "r", encoding="utf-8") as f:
          html_content = f.read()
      # Verifikasi keberadaan tag penting, bilingual elements, dan JS hooks
      if ("interactive-graph-svg" in html_content and 
          "focusElement" in html_content and 
          "tab-sandbox" in html_content and
          "lbl-font-size" in html_content):
          print("✅ html_generator.py compiled beautiful interactive dashboard successfully!")
      else:
          print("❌ html_content is missing key elements in test_html_path.")
          return False
  else:
      print("❌ html_generator.py failed to produce the test HTML file.")
      return False
  ```

- [ ] **Step 2: Jalankan test suite terintegrasi untuk membuktikan keberhasilan pengujian**
  Run: `python scripts/test_wiki.py`
  Expected: Seluruh test suite (termasuk parser, make_index, search, linter, ingest, dan generator HTML baru) lolos dengan tulisan `ALL BILINGUAL AUTOMATED TESTS COMPLETED SUCCESSFULLY!`.

- [ ] **Step 3: Commit**
  ```bash
  git add scripts/test_wiki.py
  git commit -m "test: tambahkan unit pengujian untuk html_generator.py ke test_wiki.py"
  ```

---

### Task 6: Hook Integration into scripts/ingest.py

**Files:**
- Modify: `scripts/ingest.py:470-480`

- [ ] **Step 1: Sisipkan pemanggilan html_generator.py di akhir ingest.py**
  Tambahkan pemanggilan script generator HTML pendamping secara otomatis setelah indeks catalog utama berhasil dibuat di bagian akhir fungsi `main()`.

  **Target Kode Asli:**
  ```python
      # 8. Re-Index the vault
      print("Auto-triggering wiki re-indexing pass...")
      try:
          subprocess.run([sys.executable, "scripts/make_index.py"], check=True)
          print("Re-indexing completed successfully!")
      except Exception as e:
          print(f"Warning: Failed to run make_index.py: {e}")
          
      print("\n🎉 Ingestion workflow finished successfully! 🎉")
  ```

  **Modifikasi Pengganti:**
  ```python
      # 8. Re-Index the vault
      print("Auto-triggering wiki re-indexing pass...")
      try:
          subprocess.run([sys.executable, "scripts/make_index.py"], check=True)
          print("Re-indexing completed successfully!")
      except Exception as e:
          print(f"Warning: Failed to run make_index.py: {e}")
          
      # 9. Auto-trigger Companion HTML Dashboard compilation
      print("Auto-triggering Companion HTML Dashboard compilation...")
      try:
          subprocess.run([sys.executable, "scripts/html_generator.py", raw_path], check=True)
          print("Companion HTML Dashboard successfully compiled!")
      except Exception as e:
          print(f"Warning: Failed to run html_generator.py: {e}")
          
      print("\n🎉 Ingestion workflow finished successfully! 🎉")
  ```

- [ ] **Step 2: Commit**
  ```bash
  git add scripts/ingest.py
  git commit -m "feat: integrasikan hook otomatis generator html ke scripts/ingest.py"
  ```

---

### Task 7: Index Catalog Upgrades in scripts/make_index.py

**Files:**
- Modify: `scripts/make_index.py` (Menambahkan referensi link HTML di bagian bawah index)

- [ ] **Step 1: Pelajari scripts/make_index.py**
  Baca kode `scripts/make_index.py` untuk mengidentifikasi bagaimana file indeks ditulis.
  Let's review the make_index.py file content first. We can add a function to read and list all HTML files in `wiki/html/` and append a dedicated section "## 🖥️ Interactive HTML Dashboards" di indeks Bahasa Indonesia `wiki/id/index.md` (dan opsional di indeks Bahasa Inggris).
