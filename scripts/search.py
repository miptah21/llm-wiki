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
        
    terms_str = ', '.join('"' + t + '"' for t in terms)
    print(f"Searching vault for: {terms_str}...")
    
    # SQLite FTS5 Search Attempt
    DB_PATH = os.path.join(WIKI_DIR, ".search_index.db")
    if not os.path.exists(DB_PATH):
        print("Warning: Search index database not found. Please run 'python scripts/make_index.py' to build it.")
        print("Falling back to slow linear file scan...\n")
        
    if os.path.exists(DB_PATH) and format_fts5_query_bilingual is not None:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Stage 1: Strict AND query (all terms must match)
            fts_query = format_fts5_query_bilingual(query, operator="AND")
            rows = []
            used_operator = "AND"
            if fts_query:
                match_expression = f"{{title description content stemmed_tokens}} : ({fts_query})"
                cursor.execute("""
                    SELECT path, name, lang, type, domain, title, description, content, translation,
                           bm25(search_index, 0.0, 0.0, 0.0, 0.0, 0.0, 15.0, 5.0, 1.0, 0.0, 5.0) AS rank
                    FROM search_index
                    WHERE search_index MATCH ?
                    ORDER BY rank ASC;
                """, (match_expression,))
                rows = cursor.fetchall()
            
            # Stage 2: If AND returned nothing, fallback to OR (any term can match)
            if not rows and fts_query:
                fts_query_or = format_fts5_query_bilingual(query, operator="OR")
                if fts_query_or:
                    match_expression = f"{{title description content stemmed_tokens}} : ({fts_query_or})"
                    cursor.execute("""
                        SELECT path, name, lang, type, domain, title, description, content, translation,
                               bm25(search_index, 0.0, 0.0, 0.0, 0.0, 0.0, 15.0, 5.0, 1.0, 0.0, 5.0) AS rank
                        FROM search_index
                        WHERE search_index MATCH ?
                        ORDER BY rank ASC;
                    """, (match_expression,))
                    rows = cursor.fetchall()
                    used_operator = "OR"
                    if rows:
                        print(f"  (Relaxed to OR search: {len(rows)} results)")
            
            if rows:
                # Format FTS5 results
                results = []
                for row in rows:
                    path, name, lang, type_val, domain, title, description, content, translation, rank = row
                    score = max(1, int(-rank * 10))
                    
                    # For OR-mode results, boost score by counting how many query terms actually match
                    if used_operator == "OR":
                        all_text = f"{title} {description} {content}".lower()
                        term_hits = sum(1 for t in terms if t in all_text)
                        score = max(1, int(score * (term_hits / max(len(terms), 1)) * 2))
                    
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
                                WHERE lower(name) = lower(?);
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
            
            conn.close()
        except Exception as e:
            print(f"Warning: SQLite FTS5 search failed, falling back to linear scan: {e}")
            # Fall through to linear scan
            
    # Fallback to slow linear scan if DB not present or error occurs

    
    # 1. First Pass: Scan the vault and index metadata and content
    vault_index = {}
    scanned_count = 0
    MAX_LINEAR_FILES = 200
    
    for root, _, files in os.walk(WIKI_DIR):
        if scanned_count >= MAX_LINEAR_FILES:
            print(f"\nWarning: Linear scan limit reached ({MAX_LINEAR_FILES} files). Search results may be incomplete.")
            print("Please run 'python scripts/make_index.py' to rebuild the SQLite database.\n")
            break
        for file in files:
            if not file.endswith(".md") or file in ("index.md", "log.md"):
                continue
            
            if scanned_count >= MAX_LINEAR_FILES:
                break
                
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
            scanned_count += 1
            
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
                "is_translation": False,
                "translation": metadata.get("translation", "")
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
                        "is_translation": True,
                        "translation": r["name"]
                    }
                    
                    expanded_results.append(trans_result)
                    matched[target_lower] = trans_result
                    
    # Sort results by score descending
    sorted_results = sorted(expanded_results, key=lambda x: x["score"], reverse=True)
    return sorted_results

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/search.py \"<search-query>\" OR --chat \"<question>\"")
        sys.exit(1)
        
    if len(sys.argv) >= 2 and sys.argv[1] == '--chat':
        if len(sys.argv) == 2:
            # Interactive chat loop
            print("Entering Wiki Chat mode. Type 'exit' or 'quit' to end.")
            chat_history = []
            while True:
                try:
                    question = input("\nWiki Chat> ").strip()
                    if not question:
                        continue
                    if question.lower() in ("exit", "quit"):
                        break
                    answer = run_chat(question, history=chat_history)
                    if answer:
                        chat_history.append({"role": "user", "content": question})
                        chat_history.append({"role": "assistant", "content": answer})
                        # Keep history to last 5 turns (10 messages total)
                        if len(chat_history) > 10:
                            chat_history = chat_history[-10:]
                except (KeyboardInterrupt, EOFError):
                    print("\nGoodbye!")
                    break
        else:
            question = " ".join(sys.argv[2:])
            run_chat(question)
        return

    query = " ".join(sys.argv[1:])
    results = search_vault(query)
    
    if not results:
        print("No matches found in the vault.")
        return
        
    print(f"\nFound {len(results)} matching pages:\n")
    for idx, r in enumerate(results[:10], 1):
        suffix = f" (🌐 Translated version of: [[{r.get('translation')}]])" if r.get("is_translation") else ""
        print(f"{idx}. [[{r['name']}]]{suffix} (Score: {r['score']})")
        print(f"   Path: `{r['path']}`")
        if r['snippet']:
            print(f"   Snippet: \"{r['snippet']}\"")
        print("-" * 50)


COMMON_QUESTION_STOPWORDS = {
    # English question words & common words
    "what", "is", "are", "was", "were", "the", "a", "an", "how", "to", "do", "does", "did",
    "you", "know", "about", "tell", "me", "explain", "define", "concept", "of", "in", "on", 
    "at", "for", "with", "by", "from", "that", "this", "these", "those", "which", "who", 
    "whom", "whose", "why", "where", "when", "can", "could", "would", "should", "definition",
    "chat", "query", "search", "my", "i", "we", "our", "they", "it", "if", "after", "before",
    # Indonesian question words & common words
    "apa", "itu", "siapa", "bagaimana", "dimana", "kapan", "mengapa", "kenapa", "adalah", 
    "yaitu", "merupakan", "dari", "di", "ke", "yang", "dan", "atau", "dengan", "untuk", 
    "pada", "tentang", "mengenai", "jelaskan", "terangkan", "apakah", "ini", "tersebut",
    "seperti", "maksud", "arti", "pengertian", "definisi", "bisa", "dapat", "buat",
    "tanya", "cari", "obrolan",
    # Indonesian pronouns & temporal words (low semantic value in questions)
    "saya", "kamu", "aku", "kita", "kami", "mereka", "dia", "ia",
    "sudah", "belum", "akan", "sedang", "masih", "pernah", "baru",
    "setelah", "sebelum", "ketika", "saat", "jika", "kalau", "maka",
    "juga", "pun", "lagi", "dulu", "nanti", "tadi", "kemarin", "besok"
}

def extract_search_terms(question):
    # Strip leading slash commands like /chat, /query
    question = re.sub(r"^/(?:chat|query)\s+", "", question, flags=re.IGNORECASE)
    # Normalize and split into words
    words = clean_text(question).split()
    # Remove common question stopwords
    keywords = [w for w in words if w not in COMMON_QUESTION_STOPWORDS]
    # If we filtered out everything, fall back to all words
    if not keywords:
        return words
    return keywords

def run_chat(question, history=None):
    # Extract search terms
    keywords = extract_search_terms(question)
    search_query = " ".join(keywords)
    
    print(f"Asking Wiki Chat: \"{question}\"")
    results = search_vault(search_query)
    
    # Context generation
    if not results:
        print("\nWarning: No matching context found in the vault for these keywords.")
        print("Will attempt to answer based on general knowledge.")
        context_str = "(No context found in vault. Answer based on general knowledge.)"
    else:
        # Deduplicate results: if a page and its translation are both in results, only keep the higher-scoring one
        deduped_results = []
        seen_names = set()
        for r in results:
            name_lower = r["name"].lower()
            if name_lower in seen_names:
                continue
            seen_names.add(name_lower)
            trans_val = r.get("translation", "")
            if trans_val:
                if isinstance(trans_val, list):
                    trans_val = trans_val[0] if trans_val else ""
                trans_clean = str(trans_val).replace("[[", "").replace("]]", "").strip().lower()
                if trans_clean:
                    seen_names.add(trans_clean)
            deduped_results.append(r)

        print(f"\nFound {len(deduped_results)} relevant page(s) for context:")
        for idx, r in enumerate(deduped_results[:5], 1):
            suffix = f" (🌐 Translated version of: [[{r.get('translation')}]])" if r.get("is_translation") else ""
            print(f"  {idx}. [[{r['name']}]]{suffix}")
        
        # Build context from top 5 pages
        context_blocks = []
        MAX_DOC_CHARS = 8000
        for idx, r in enumerate(deduped_results[:5], 1):
            try:
                with open(r["path"], "r", encoding="utf-8") as f:
                    content = f.read()
                # Strip frontmatter for cleaner context
                content_clean = re.sub(r"^---.*?---", "", content, flags=re.DOTALL).strip()
                if len(content_clean) > MAX_DOC_CHARS:
                    content_clean = content_clean[:MAX_DOC_CHARS] + "\n... [Context truncated due to size] ..."
                context_blocks.append(f"Document {idx}: [[{r['name']}]]\n{content_clean}")
            except Exception:
                pass
        context_str = "\n\n".join(context_blocks)
        
    # Construct Prompt
    history_str = ""
    if history:
        history_str = "\nConversation History:\n" + "\n".join([f"{h['role'].title()}: {h['content']}" for h in history]) + "\n"

    prompt = f"""Search Context:
{context_str}
{history_str}
User Question: {question}

Please answer the question based on the search context and conversation history above.
"""

    SYSTEM_PROMPT = (
        "You are a helpful assistant for a bilingual (English/Indonesian) personal wiki/vault.\n"
        "Your goal is to answer the user's question accurately using the provided search context from the vault.\n"
        "Guidelines:\n"
        "1. Ground your answer in the provided context as much as possible.\n"
        "2. If the context does not contain enough information, explain what is missing, but you may also provide a general explanation. Clearly distinguish between what is in the vault and what is general knowledge.\n"
        "3. Respond in the same language as the user's question (e.g., if the question is in Indonesian, reply in Indonesian; if in English, reply in English).\n"
        "4. Preserve all scientific terms, definitions, and LaTeX mathematical notations natively. Do not translate core mathematical/scientific terms unless there is a standard equivalent.\n"
        "5. Use clear, structured formatting (Markdown) with lists, bold text, and code blocks where appropriate.\n"
        "6. If the user asks about relationships between documents or concepts (e.g. supports, contradicts, extends), scan the frontmatter 'relations' and 'Cross-References' / 'Koneksi Penelitian Terkait' / 'Referensi Silang' sections in the context to explain how they are linked.\n"
        "7. Do not include any meta-summaries of your work or actions (e.g., 'Work Summary' or 'Ringkasan Pekerjaan') at the beginning or end of your answer. Instead, always conclude your response with a 'References' (or 'Referensi' if replying in Indonesian) section containing a minimalist, clean bulleted list of the documents utilized. Each item must use a standard Markdown link (no double brackets [[ or ]]). For source documents (papers/articles), you MUST format each item as: - Author Name (Year) — [source-document-name](path). For concepts or entities, format each item as: - Category/Domain — [document-name](path) (or simply list the link if no category exists)."
    )
    
    # Mocking check for testing offline
    if os.environ.get("MOCK_DEEPSEEK") == "1" or os.environ.get("DEEPSEEK_API_KEY") == "mock-key" or os.environ.get("GEMINI_API_KEY") == "mock-key":
        answer = f"[Mock Answer] Grounded answer in the queried language about: {question}.\nContext has {len(results)} pages."
        print("\n=== COGNITIVE CHAT RESPONSE ===")
        print(answer)
        return answer

    # Call DeepSeek API
    try:
        from deepseek_helper import call_deepseek, MissingAPIKeyError, DeepSeekAPIError
    except ImportError:
        print("\nError: Could not import deepseek_helper. Make sure scripts/deepseek_helper.py is present.")
        return
        
    try:
        answer = call_deepseek(prompt, system_prompt=SYSTEM_PROMPT)
        print("\n=== COGNITIVE CHAT RESPONSE ===")
        print(answer)
        return answer
    except MissingAPIKeyError as e:
        # Output structured context so the AI agent can perform RAG directly
        print("\n" + "=" * 60)
        print("AGENT_RAG_CONTEXT_START")
        print(f"Question: {question}")
        print(f"Language: {'id' if any(w in question.lower() for w in ['apa','bagaimana','mengapa','dari','untuk','dengan']) else 'en'}")
        if results:
            print(f"Documents Found: {len(deduped_results if 'deduped_results' in dir() else results)}")
            print("\n--- WIKI CONTEXT ---")
            print(context_str)
            print("--- END WIKI CONTEXT ---")
            print("\nReferences:")
            ref_list = deduped_results[:5] if 'deduped_results' in dir() else results[:5]
            for r in ref_list:
                print(f"  - [[{r['name']}]] ({r['path']})")
        else:
            print("Documents Found: 0")
        print("AGENT_RAG_CONTEXT_END")
        print("=" * 60)
        print("\n⚠️  No LLM API key configured. The above context is provided for your AI agent to answer directly.")
        sys.exit(2)
    except DeepSeekAPIError as e:
        print(f"\nAPI Error: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    return None


if __name__ == "__main__":
    # Windows Encoding Safeguard for non-ASCII characters / emojis
    if sys.platform.startswith("win"):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    main()
