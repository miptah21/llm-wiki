import os
import re
import sys
import sqlite3

# Windows Encoding Safeguard for non-ASCII characters / emojis
if sys.platform.startswith("win"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Directory Paths
WIKI_DIR = "wiki"
EN_DIR = os.path.join(WIKI_DIR, "en")
ID_DIR = os.path.join(WIKI_DIR, "id")

from parser import parse_yaml_frontmatter, detect_page_attributes
from stemmer import stem_text

# Map domains to English formatted titles
DOMAINS_MAP_EN = {
    "finance": "📈 Finance",
    "software-engineering": "💻 Software Engineering",
    "ai": "🧠 Artificial Intelligence",
    "economics": "🏛️ Economics",
    "other": "📂 General / Uncategorized"
}

# Map domains to Indonesian formatted titles
DOMAINS_MAP_ID = {
    "finance": "📈 Keuangan",
    "software-engineering": "💻 Rekayasa Perangkat Lunak",
    "ai": "🧠 Kecerdasan Buatan",
    "economics": "🏛️ Ekonomi",
    "other": "📂 Umum / Tanpa Kategori"
}

def scan_lang_vault(lang_dir, lang_code):
    """
    Recursively scans all .md files in the specific language directory
    and extracts their metadata.
    """
    concepts = []
    entities = []
    sources = []
    
    if not os.path.exists(lang_dir):
        return concepts, entities, sources
        
    for root, _, files in os.walk(lang_dir):
        for filename in files:
            if not filename.endswith(".md") or filename == "index.md":
                continue
                
            filepath = os.path.join(root, filename)
            
            # Detect path attributes using the unified parser
            attrs = detect_page_attributes(filepath)
            dir_type = attrs["type"]
            detected_domain = attrs["domain"]
                
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                metadata = parse_yaml_frontmatter(content)
                if metadata:
                    metadata["_filename"] = filename
                    metadata["_name"] = os.path.splitext(filename)[0]
                    metadata["_path"] = filepath
                    metadata["lang"] = lang_code
                    
                    # Automap domain
                    if "domain" not in metadata and detected_domain != "other":
                        metadata["domain"] = detected_domain
                    elif "domain" in metadata:
                        # Handle potential list value (e.g. if domain was parsed as list)
                        dom_val = metadata["domain"]
                        if isinstance(dom_val, list):
                            dom_val = dom_val[0] if dom_val else "other"
                        metadata["domain"] = str(dom_val).lower()
                    else:
                        metadata["domain"] = "other"
                        
                    # Sort into lists
                    page_type = metadata.get("type", "concept")
                    if isinstance(page_type, list):
                        page_type = page_type[0] if page_type else "concept"
                    page_type = page_type.lower()
                    
                    if page_type == "source" or dir_type == "sources":
                        sources.append(metadata)
                    elif page_type == "entity" or dir_type == "entities":
                        entities.append(metadata)
                    else:
                        concepts.append(metadata)
            except Exception as e:
                print(f"Warning: Failed to read/parse {filepath}: {e}")
                
    return concepts, entities, sources

def build_localized_index(lang_code, lang_dir, DOMAINS_MAP, is_en=True):
    concepts, entities, sources = scan_lang_vault(lang_dir, lang_code)
    print(f"[{lang_code.upper()}] Found {len(concepts)} concepts, {len(entities)} entities, {len(sources)} sources.")
    
    index_path = os.path.join(lang_dir, "index.md")
    output = []
    
    # English vs Indonesian localization
    if is_en:
        output.append("# Wiki Index\n")
        output.append("Welcome to your compounding personal knowledge base. Below is an auto-generated visual and categorized catalog of all compiled knowledge in your vault, grouped by **Domain** first.\n")
        output.append("> [!NOTE]")
        output.append("> Do NOT edit this index file manually. It is automatically maintained and compiled by `scripts/make_index.py` during ingestion operations.\n")
        output.append("---")
        
        # Sources
        output.append("\n## 📚 Compiled Raw Sources\n")
        if not sources:
            output.append("*No sources compiled yet.*\n")
        else:
            output.append("| Title | Source File | Added/Updated | Tags |")
            output.append("| :--- | :--- | :--- | :--- |")
            sorted_sources = sorted(sources, key=lambda x: x.get("updated", x.get("created", "")), reverse=True)
            for s in sorted_sources:
                name = s["_name"].replace("source-", "").replace("-", " ").title()
                link = f"[[{s['_name']}]]"
                raw_file = s.get("source_file", "Unknown")
                date = s.get("updated", s.get("created", "Unknown"))
                tags = ", ".join([f"`{t}`" for t in s.get("tags", [])])
                output.append(f"| {link} | `{raw_file}` | {date} | {tags} |")
            output.append("")
            
        # Concepts
        output.append("\n## 💡 Core Concepts by Domain\n")
        
    else:  # Indonesian Translation
        output.append("# Indeks Wiki\n")
        output.append("Selamat datang di basis pengetahuan pribadi Anda. Di bawah ini adalah katalog visual dan terkategori otomatis dari semua pengetahuan yang terkompilasi, dikelompokkan berdasarkan **Ranah/Domain** terlebih dahulu.\n")
        output.append("> [!NOTE]")
        output.append("> Jangan mengedit file indeks ini secara manual. File ini diperbarui secara otomatis oleh `scripts/make_index.py` selama proses kompilasi.\n")
        output.append("---")
        
        # Sources
        output.append("\n## 📚 Sumber Mentah Terkompilasi\n")
        if not sources:
            output.append("*Belum ada sumber yang terkompilasi.*\n")
        else:
            output.append("| Judul | File Sumber | Tanggal Ditambahkan | Tag |")
            output.append("| :--- | :--- | :--- | :--- |")
            sorted_sources = sorted(sources, key=lambda x: x.get("updated", x.get("created", "")), reverse=True)
            for s in sorted_sources:
                name = s["_name"].replace("source-", "").replace("-", " ").title()
                link = f"[[{s['_name']}]]"
                raw_file = s.get("source_file", "Unknown")
                date = s.get("updated", s.get("created", "Unknown"))
                tags = ", ".join([f"`{t}`" for t in s.get("tags", [])])
                output.append(f"| {link} | `{raw_file}` | {date} | {tags} |")
            output.append("")
            
        # Concepts
        output.append("\n## 💡 Konsep Inti per Ranah\n")
        
    # Group Concepts by Domain
    if not concepts:
        no_concepts_msg = "*No concepts compiled yet. Ingest sources to begin.*\n" if is_en else "*Belum ada konsep yang terkompilasi. Masukkan dokumen untuk memulai.*\n"
        output.append(no_concepts_msg)
    else:
        domain_concepts = {d: [] for d in DOMAINS_MAP.keys()}
        for c in concepts:
            dom = c.get("domain", "other")
            if dom not in domain_concepts:
                dom = "other"
            domain_concepts[dom].append(c)
            
        for dom_key, dom_title in DOMAINS_MAP.items():
            comp_list = domain_concepts[dom_key]
            if comp_list:
                output.append(f"### {dom_title}\n")
                
                # Subgroup by tags
                tagged_concepts = {}
                untagged_concepts = []
                for c in comp_list:
                    tags = c.get("tags", [])
                    if not tags:
                        untagged_concepts.append(c)
                    for t in tags:
                        if t not in tagged_concepts:
                            tagged_concepts[t] = []
                        tagged_concepts[t].append(c)
                        
                for tag in sorted(tagged_concepts.keys()):
                    output.append(f"#### #{tag}")
                    for c in sorted(tagged_concepts[tag], key=lambda x: x["_name"]):
                        desc = c.get("description", "No description provided." if is_en else "Tidak ada deskripsi yang tersedia.")
                        # Check translation
                        trans = c.get("translation", "")
                        trans_note = f" (🌐 {trans})" if trans else ""
                        output.append(f"- [[{c['_name']}]] — {desc}{trans_note}")
                    output.append("")
                    
                if untagged_concepts:
                    uncat_header = "#### #uncategorized" if is_en else "#### #tanpa-kategori"
                    output.append(uncat_header)
                    for c in sorted(untagged_concepts, key=lambda x: x["_name"]):
                        desc = c.get("description", "No description provided." if is_en else "Tidak ada deskripsi yang tersedia.")
                        trans = c.get("translation", "")
                        trans_note = f" (🌐 {trans})" if trans else ""
                        output.append(f"- [[{c['_name']}]] — {desc}{trans_note}")
                    output.append("")
                output.append("---")

    # Group Entities by Domain & Category
    entities_section_header = "\n## 👥 Linked Entities by Domain\n" if is_en else "\n## 👥 Entitas Terkait per Ranah\n"
    output.append(entities_section_header)
    
    if not entities:
        no_entities_msg = "*No entities linked yet.*\n" if is_en else "*Belum ada entitas yang terkait.*\n"
        output.append(no_entities_msg)
    else:
        domain_entities = {d: [] for d in DOMAINS_MAP.keys()}
        for e in entities:
            dom = e.get("domain", "other")
            if dom not in domain_entities:
                dom = "other"
            domain_entities[dom].append(e)
            
        categories_en = {
            "person": "People",
            "organization": "Organizations",
            "model": "Models & AI Systems",
            "tool": "Tools & Software",
            "book": "Books & Publications",
            "other": "Other Entities"
        }
        
        categories_id = {
            "person": "Tokoh / Individu",
            "organization": "Organisasi / Perusahaan",
            "model": "Model & Sistem AI",
            "tool": "Alat & Perangkat Lunak",
            "book": "Buku & Publikasi",
            "other": "Entitas Lainnya"
        }
        
        categories = categories_en if is_en else categories_id
        
        for dom_key, dom_title in DOMAINS_MAP.items():
            ent_list = domain_entities[dom_key]
            if ent_list:
                output.append(f"### {dom_title} Entities\n" if is_en else f"### Entitas {dom_title}\n")
                
                grouped_entities = {k: [] for k in categories.keys()}
                for e in ent_list:
                    cat = e.get("category", "other").lower()
                    if cat not in grouped_entities:
                        cat = "other"
                    grouped_entities[cat].append(e)
                    
                for cat_key, cat_title in categories.items():
                    sub_list = grouped_entities[cat_key]
                    if sub_list:
                        output.append(f"#### {cat_title}")
                        for e in sorted(sub_list, key=lambda x: x["_name"]):
                            tags = " ".join([f"#{t}" for t in e.get("tags", [])])
                            trans = e.get("translation", "")
                            trans_note = f" (🌐 {trans})" if trans else ""
                            output.append(f"- [[{e['_name']}]] {tags}{trans_note}")
                        output.append("")
                output.append("---")

    # Write to file
    try:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        print(f"Success: Rebuilt {lang_code.upper()} index catalog at {index_path}")
    except Exception as e:
        print(f"Error: Failed to write to {index_path}: {e}")

DB_PATH = os.path.join(WIKI_DIR, ".search_index.db")

def build_sqlite_index(pages):
    # Remove existing database file if it exists to ensure a clean build
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception as e:
            print(f"Warning: Failed to remove old search index database: {e}")
            
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create FTS5 virtual table
        cursor.execute("""
            CREATE VIRTUAL TABLE search_index USING fts5(
                path,
                name,
                lang,
                type,
                domain,
                title,
                description,
                content,
                translation,
                stemmed_tokens,
                tokenize='unicode61'
            );
        """)
        
        insert_data = []
        for p in pages:
            filepath = p.get("_path", "")
            if not filepath or not os.path.exists(filepath):
                continue
                
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    full_content = f.read()
            except Exception as e:
                print(f"Warning: Failed to read {filepath} for SQLite indexing: {e}")
                continue
                
            # Extract body content (strip frontmatter)
            body = full_content
            if full_content.startswith("---"):
                parts = full_content.split("---", 2)
                if len(parts) >= 3:
                    body = parts[2].strip()
                    
            name = p.get("_name", "")
            lang = p.get("lang", "")
            page_type = p.get("_db_type", "concept")
            domain = p.get("domain", "other")
            title = p.get("title", name.replace("source-", "").replace("-", " ").title())
            description = p.get("description", "")
            translation = p.get("translation", "")
            if isinstance(translation, list):
                translation = translation[0] if translation else ""
            translation = str(translation).replace("[[", "").replace("]]", "").strip()
            
            # Combine text for stemming: title + description + body
            text_to_stem = f"{title} {description} {body}"
            stemmed_tokens = stem_text(text_to_stem, lang)
            
            insert_data.append((
                filepath,
                name,
                lang,
                page_type,
                domain,
                title,
                description,
                body,
                translation,
                stemmed_tokens
            ))
            
        cursor.executemany("""
            INSERT INTO search_index(path, name, lang, type, domain, title, description, content, translation, stemmed_tokens)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, insert_data)
        
        conn.commit()
        # Optimize FTS5 table
        cursor.execute("INSERT INTO search_index(search_index) VALUES('optimize');")
        conn.commit()
        conn.close()
        print(f"Success: Indexed {len(insert_data)} pages in SQLite FTS5 database.")
    except Exception as e:
        print(f"Error: Failed to build SQLite search index database: {e}")

def build_index():
    print("Running domain-aware bilingual indexing pass...")
    build_localized_index("en", EN_DIR, DOMAINS_MAP_EN, is_en=True)
    build_localized_index("id", ID_DIR, DOMAINS_MAP_ID, is_en=False)
    
    # Now scan all pages to build the SQLite FTS5 database
    print("Building SQLite FTS5 search index database...")
    en_concepts, en_entities, en_sources = scan_lang_vault(EN_DIR, "en")
    id_concepts, id_entities, id_sources = scan_lang_vault(ID_DIR, "id")
    
    all_pages = []
    # Collect all pages and ensure their metadata fits our schema
    for lang, concepts, entities, sources in [("en", en_concepts, en_entities, en_sources), 
                                              ("id", id_concepts, id_entities, id_sources)]:
        for p in concepts:
            p["_db_type"] = "concept"
            all_pages.append(p)
        for p in entities:
            p["_db_type"] = "entity"
            all_pages.append(p)
        for p in sources:
            p["_db_type"] = "source"
            all_pages.append(p)
            
    build_sqlite_index(all_pages)

if __name__ == "__main__":
    build_index()
