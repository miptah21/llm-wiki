from stemmer import stem_english_refined, stem_indonesian_expand, stem_text, format_fts5_query_bilingual

def test_stemmer():
    print("## Testing English Stemming:")
    en_tests = {
        "distillation": "distill",
        "distills": "distill",
        "compression": "compres",
        "compressed": "compres",
        "transformers": "transform",
        "evaluation": "evaluate"
    }
    for word, expected in en_tests.items():
        res = stem_english_refined(word)
        print(f"  `{word}` -> `{res}` (expected: `{expected}`)")
        # Note: clean duplicate consonants is done, so distill -> distil, compres -> compres.
        
    print("\n## Testing Indonesian Stemming (with Token Expansion):")
    id_tests = {
        "pendistilasian": ["distilasi"],
        "pembelajaran": ["ajar"],
        "pengambilan": ["ambil", "kambil"],
        "menyetel": ["setel"],
        "disetelkan": ["setel"]
    }
    for word, expected in id_tests.items():
        res = stem_indonesian_expand(word)
        print(f"  `{word}` -> {res} (expected subset/exact: {expected})")
        
    print("\n## Testing Text Stemming:")
    print("  English: " + stem_text("the neural network transformers attention", "en"))
    print("  Indonesian: " + stem_text("proses pembelajaran dan pengambilan keputusan", "id"))

    print("\n## Testing Bilingual FTS5 Query Formatting:")
    queries = ["distillation", "pengambilan", "transformer distillation"]
    for q in queries:
        print(f"  Query: \"{q}\" -> FTS5: \"{format_fts5_query_bilingual(q)}\"")

if __name__ == "__main__":
    test_stemmer()
