import os
import sys
import re
import sqlite3
from parser import parse_yaml_frontmatter

try:
    from stemmer import format_fts5_query_bilingual, stem_english_refined, stem_indonesian_expand
except ImportError:
    format_fts5_query_bilingual = None
    stem_english_refined = lambda x: x
    stem_indonesian_expand = lambda x: [x]

# Windows Encoding Safeguard for non-ASCII characters / emojis
if sys.platform.startswith("win"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Directory Paths
WIKI_DIR = "wiki"

def clean_text(text):
    """Normalize text for consistent term matching."""
    text = text.lower()
    text = re.sub(r"[^\w\s\-]", " ", text)
    return text

def get_snippet(content, terms):
    """Extract a relevant text snippet from content containing search terms."""
    snippet = ""
    lines = content.splitlines()
    for line in lines:
        if line.strip().startswith("---") or line.strip().startswith("#"):
            continue
        line_clean = line.lower()
        if any(term in line_clean for term in terms):
            snippet = line.strip()
            # Shorten if very long
            if len(snippet) > 100:
                snippet = snippet[:100] + "..."
            return snippet
    return ""

def search_vault(query):
    if not query:
        print("Error: Empty search query.")
        return []
    
    terms = clean_text(query).split()
    if not terms:
        return []
        
    print(f"Searching vault for: {', '.join([f'\"{t}\"' for t in terms])}...")
    
    # SQLite FTS5 Search Attempt
    DB_PATH = os.path.join(WIKI_DIR, ".search_index.db")
    if os.path.exists(DB_PATH) and format_fts5_query_bilingual is not None:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            fts_query = format_fts5_query_bilingual(query)
            if fts_query:
                # Match query terms in title, description, content, stemmed_tokens
                match_expression = f"{{title description content stemmed_tokens}} : ({fts_query})"
                
                cursor.execute("""
                    SELECT path, name, lang, type, domain, title, description, content, translation,
                           bm25(search_index, 0.0, 0.0, 0.0, 0.0, 0.0, 15.0, 5.0, 1.0, 0.0, 5.0) AS rank
                    FROM search_index
                    WHERE search_index MATCH ?
                    ORDER BY rank ASC;
                """, (match_expression,))
                
                rows = cursor.fetchall()
                
                # Format FTS5 results
                results = []
                for row in rows:
                    path, name, lang, type_val, domain, title, description, content, translation, rank = row
                    score = max(1, int(-rank * 10))
                    
                    # Snippet extraction with stemming term expansion
                    snippet_terms = []
                    for t in terms:
                        snippet_terms.append(t)
                        snippet_terms.append(stem_english_refined(t))
                        snippet_terms.extend(stem_indonesian_expand(t))
                    snippet_terms = list(set([st.lower() for st in snippet_terms if st]))
                    
                    results.append({
                        "path": path,
                        "name": name,
                        "score": score,
                        "snippet": get_snippet(content, snippet_terms),
                        "is_translation": False,
                        "translation": translation
                    })
                
                # Cross-lingual search expansion using translation property
                matched = {r["name"].lower(): r for r in results}
                expanded_results = []
                for r in results:
                    expanded_results.append(r)
                    translation_val = r.get("translation", "")
                    if translation_val:
                        target_lower = translation_val.lower()
                        if target_lower not in matched:
                            cursor.execute("""
                                SELECT path, name, lang, type, domain, title, description, translation
                                FROM search_index
                                WHERE name = ?;
                            """, (translation_val,))
                            target_row = cursor.fetchone()
                            if target_row:
                                t_path, t_name, t_lang, t_type, t_domain, t_title, t_description, t_translation = target_row
                                trans_score = max(1, int(r["score"] * 0.8))
                                trans_result = {
                                    "path": t_path,
                                    "name": t_name,
                                    "score": trans_score,
                                    "snippet": f"(🌐 Translated version: [[{t_name}]])",
                                    "is_translation": True,
                                    "translation": t_translation
                                }
                                expanded_results.append(trans_result)
                                matched[target_lower] = trans_result
                                
                conn.close()
                return sorted(expanded_results, key=lambda x: x["score"], reverse=True)
        except Exception as e:
            print(f"Warning: SQLite FTS5 search failed, falling back to linear scan: {e}")
            # Fall through to linear scan
            
    # Fallback to slow linear scan if DB not present or error occurs

    
    # 1. First Pass: Scan the vault and index metadata and content
    vault_index = {}
    
    for root, _, files in os.walk(WIKI_DIR):
        for file in files:
            if not file.endswith(".md") or file == "index.md":
                continue
                
            filepath = os.path.join(root, file)
            filename_no_ext = os.path.splitext(file)[0]
            
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue
                
            metadata = parse_yaml_frontmatter(content)
            vault_index[filename_no_ext.lower()] = {
                "path": filepath,
                "name": filename_no_ext,
                "metadata": metadata,
                "content": content
            }
            
    # 2. Second Pass: Score each indexed page
    results = []
    
    for filename_lower, page in vault_index.items():
        score = 0
        content = page["content"]
        metadata = page["metadata"]
        filename_no_ext = page["name"]
        
        # Heuristic 1: Filename match (highest weight)
        filename_clean = clean_text(filename_no_ext)
        for term in terms:
            if term in filename_clean:
                score += 15
                
        # Heuristic 2: Frontmatter/YAML matches
        for term in terms:
            for key, val in metadata.items():
                if isinstance(val, list):
                    val_str = " ".join(val).lower()
                else:
                    val_str = str(val).lower()
                if term in val_str:
                    score += 5
                    
        # Heuristic 3: Content body matches
        content_clean = clean_text(content)
        for term in terms:
            count = content_clean.count(term)
            score += count * 1
            
        if score > 0:
            results.append({
                "path": page["path"],
                "name": filename_no_ext,
                "score": score,
                "snippet": get_snippet(content, terms),
                "is_translation": False
            })
            
    # 3. Third Pass: Cross-lingual search expansion using 'translation' property
    matched = {r["name"].lower(): r for r in results}
    expanded_results = []
    
    for r in results:
        expanded_results.append(r)
        
        # Check translation link
        page_lower = r["name"].lower()
        metadata = vault_index[page_lower]["metadata"]
        translation_val = metadata.get("translation", "")
        
        if translation_val:
            if isinstance(translation_val, list):
                translation_val = translation_val[0] if translation_val else ""
            # Clean brackets: "[[target]]" -> "target"
            target_name = str(translation_val).replace("[[", "").replace("]]", "").strip()
            target_lower = target_name.lower()
            
            if target_lower in vault_index:
                # If target is not already matched, or matched with a lower score
                if target_lower not in matched:
                    target_page = vault_index[target_lower]
                    
                    # Calculate translation relevance (e.g. 80% of parent's score)
                    trans_score = max(1, int(r["score"] * 0.8))
                    
                    trans_result = {
                        "path": target_page["path"],
                        "name": target_page["name"],
                        "score": trans_score,
                        "snippet": f"(🌐 Translated version: [[{target_page['name']}]])",
                        "is_translation": True
                    }
                    
                    expanded_results.append(trans_result)
                    matched[target_lower] = trans_result
                    
    # Sort results by score descending
    sorted_results = sorted(expanded_results, key=lambda x: x["score"], reverse=True)
    return sorted_results

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/search.py \"<search-query>\"")
        sys.exit(1)
        
    query = " ".join(sys.argv[1:])
    results = search_vault(query)
    
    if not results:
        print("No matches found in the vault.")
        return
        
    print(f"\nFound {len(results)} matching pages:\n")
    for idx, r in enumerate(results[:10], 1):
        suffix = f" (🌐 Translated version: [[{r['name']}]])" if r.get("is_translation") else ""
        print(f"{idx}. [[{r['name']}]]{suffix} (Score: {r['score']})")
        print(f"   Path: `{r['path']}`")
        if r['snippet']:
            print(f"   Snippet: \"{r['snippet']}\"")
        print("-" * 50)

if __name__ == "__main__":
    main()
