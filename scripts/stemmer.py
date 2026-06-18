import re

def stem_english_refined(word):
    """Refined English stemmer with rules for plurals, -ing, -ed, -y, and common suffixes."""
    word = word.lower().strip()
    if len(word) <= 3:
        return word
        
    # Step 1: Plurals and basic suffixes
    if word.endswith("sses"):
        word = word[:-2]
    elif word.endswith("ies"):
        word = word[:-3] + "i"
    elif word.endswith("ss"):
        pass
    elif word.endswith("s") and not word.endswith(("is", "as", "us", "os")):
        word = word[:-1]
        
    if len(word) <= 3:
        return word
        
    # Step 2: -eed, -ing, -ed
    if word.endswith("eed"):
        word = word[:-1]
    elif word.endswith("ing"):
        word = word[:-3]
        if word.endswith(("at", "bl", "iz")):
            word += "e"
        elif word.endswith(("bb", "dd", "ff", "gg", "mm", "nn", "pp", "rr", "tt")):
            word = word[:-1]
    elif word.endswith("ed"):
        word = word[:-2]
        if word.endswith(("at", "bl", "iz")):
            word += "e"
        elif word.endswith(("bb", "dd", "ff", "gg", "mm", "nn", "pp", "rr", "tt")):
            word = word[:-1]
            
    if len(word) <= 3:
        return word
        
    # Step 3: -y
    if word.endswith("y") and word[-2] not in ("a", "e", "i", "o", "u"):
        word = word[:-1] + "i"
        
    # Step 4: Refined derivational suffixes
    suffixes = {
        "ational": "ate",
        "tional": "tion",
        "ation": "",      # distillation -> distill
        "izer": "ize",
        "alli": "al",
        "entli": "ent",
        "eli": "e",
        "ousli": "ous",
        "alism": "al",
        "aliti": "al",
        "iviti": "ive",
        "biliti": "ble",
        "icate": "ic",
        "alise": "al",
        "iciti": "ic",
        "ical": "ic",
        "ness": "",
        "ful": "",
        "ment": "",
        "sion": "",       # compression -> compres
        "tion": "",       # connection -> connec
        "al": "",         # retrieval -> retriev
        "ate": "",        # evaluate -> evalu
        "er": ""          # transformer -> transform
    }
    
    for suff, repl in suffixes.items():
        if word.endswith(suff):
            if len(word) - len(suff) + len(repl) >= 3:
                word = word[:-len(suff)] + repl
                break
            
    # Clean duplicate double consonants at the end (e.g. distill -> distil)
    if len(word) > 3 and word[-1] == word[-2] and word[-1] in "bdfgmnprst":
        word = word[:-1]
        
    return word

def stem_indonesian_expand(word):
    """
    Refined Indonesian stemmer that returns a list of candidate stems
    to handle morphological ambiguity (token expansion) without a dictionary.
    """
    word = word.lower().strip()
    if len(word) <= 3:
        return [word]
        
    # Step 1: Remove inflectional particle suffixes (-kah, -lah, -tah, -pun)
    if word.endswith(("kah", "lah", "tah", "pun")):
        word = word[:-3]
        
    # Step 2: Remove possessive pronoun suffixes (-ku, -mu, -nya)
    if word.endswith(("ku", "mu")):
        word = word[:-2]
    elif word.endswith("nya"):
        word = word[:-3]
        
    if len(word) <= 3:
        return [word]

    # Step 3: Remove derivational suffixes (-kan, -an, -i)
    if word.endswith("kan"):
        word = word[:-3]
    elif word.endswith("an"):
        word = word[:-2]
    elif word.endswith("i"):
        if not word.endswith(("ci", "di", "gi", "hi", "li", "mi", "ni", "pi", "ri", "si", "ti", "vi", "zi")):
            word = word[:-1]
            
    if len(word) <= 3:
        return [word]

    # Step 4: Remove derivational prefixes (di-, ke-, se-, me-, pe-, be-, te-)
    vowels = ("a", "i", "u", "e", "o")
    
    # Track candidate roots
    candidates = []
    
    if word.startswith("di"):
        candidates.append(word[2:])
    elif word.startswith("ke") and len(word) > 4:
        candidates.append(word[2:])
    elif word.startswith("se") and len(word) > 4:
        candidates.append(word[2:])
    elif word.startswith("ber"):
        candidates.append(word[3:])
    elif word.startswith("be"):
        candidates.append(word[2:])
    elif word.startswith("ter"):
        candidates.append(word[3:])
    elif word.startswith("te"):
        candidates.append(word[2:])
    elif word.startswith("me"):
        if word.startswith("meny") and len(word) > 4 and word[4] in vowels:
            candidates.append("s" + word[4:])
        elif word.startswith("meng") and len(word) > 4 and word[4] in vowels:
            # Ambiguity: meng-ambil -> ambil, meng-irim -> kirim
            candidates.append(word[4:])
            candidates.append("k" + word[4:])
        elif word.startswith("mem") and len(word) > 3:
            if word[3] in vowels:
                candidates.append("p" + word[3:])
                candidates.append(word[3:])
            else:
                candidates.append(word[3:])
        elif word.startswith("men") and len(word) > 3:
            if word[3] in vowels:
                candidates.append("t" + word[3:])
                candidates.append(word[3:])
            else:
                candidates.append(word[3:])
        else:
            candidates.append(word[2:])
    elif word.startswith("pe"):
        if word.startswith("peny") and len(word) > 4 and word[4] in vowels:
            candidates.append("s" + word[4:])
        elif word.startswith("peng") and len(word) > 4 and word[4] in vowels:
            candidates.append(word[4:])
            candidates.append("k" + word[4:])
        elif word.startswith("pem") and len(word) > 3:
            if word[3] in vowels:
                candidates.append("p" + word[3:])
                candidates.append(word[3:])
            else:
                candidates.append(word[3:])
        elif word.startswith("pen") and len(word) > 3:
            if word[3] in vowels:
                candidates.append("t" + word[3:])
                candidates.append(word[3:])
            else:
                candidates.append(word[3:])
        else:
            candidates.append(word[2:])
            
    if not candidates:
        candidates.append(word)
        
    # Post-process candidates to normalize special roots like "belajar" -> "ajar"
    final_candidates = []
    for c in candidates:
        if c.startswith("belajar") or c.startswith("ajar"):
            final_candidates.append("ajar")
        elif len(c) > 0:
            final_candidates.append(c)
            
    if not final_candidates:
        final_candidates.append(word)
        
    # Standardize output (unique, sorted)
    unique_candidates = sorted(list(set(final_candidates)))
    return unique_candidates

def stem_text(text, lang_code):
    """Tokenize and stem text to produce space-separated tokens."""
    words = re.findall(r"\b\w+\b", text.lower())
    stemmed_words = []
    for w in words:
        if lang_code == "id":
            # Indonesian expands to multiple candidates; add all of them
            stemmed_words.extend(stem_indonesian_expand(w))
        else:
            stemmed_words.append(stem_english_refined(w))
    return " ".join(sorted(list(set(stemmed_words))))

def format_fts5_query_bilingual(query_text, operator="AND"):
    """Format search query for SQLite FTS5 matching, combining EN and ID stemming with prefix wildcards.
    
    Args:
        query_text: The raw search query string.
        operator: Join logic between term groups. "AND" (strict, all terms must match)
                  or "OR" (relaxed, any term can match). Default is "AND".
    """
    words = re.findall(r"\b\w+\b", query_text.lower())
    query_parts = []
    for w in words:
        # Stem using English
        en_stem = stem_english_refined(w)
        # Stem using Indonesian
        id_stems = stem_indonesian_expand(w)
        
        # Combine all candidates, remove duplicates, sort
        all_candidates = set([en_stem] + id_stems)
        
        # Generate prefix wildcard terms for FTS5
        parts = [f"{c}*" for c in sorted(all_candidates) if len(c) > 0]
        if parts:
            query_parts.append(f"({' OR '.join(parts)})")
        
    if not query_parts:
        return ""
    joiner = f" {operator.upper()} "
    return joiner.join(query_parts)
