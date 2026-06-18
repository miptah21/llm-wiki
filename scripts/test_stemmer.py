import os
import sys
import unittest


scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

from stemmer import (
    format_fts5_query_bilingual,
    stem_english_refined,
    stem_indonesian_expand,
    stem_text,
)


class TestStemmer(unittest.TestCase):
    def test_english_suffix_stemming(self) -> None:
        cases = {
            "distillation": "distill",
            "distills": "distill",
            "compression": "compres",
            "compressed": "compres",
            "transformers": "transform",
            "evaluation": "evalu",
        }

        for word, expected in cases.items():
            with self.subTest(word=word):
                self.assertEqual(stem_english_refined(word), expected)

    def test_indonesian_prefix_expansion(self) -> None:
        cases = {
            "pendistilasian": ["distilasi"],
            "pembelajaran": ["ajar"],
            "pengambilan": ["ambil", "kambil"],
            "menyetel": ["setel"],
            "disetelkan": ["setel"],
        }

        for word, expected in cases.items():
            with self.subTest(word=word):
                self.assertEqual(stem_indonesian_expand(word), expected)

    def test_text_stemming(self) -> None:
        self.assertEqual(
            stem_text("the neural network transformers attention", "en"),
            "atten network neur the transform",
        )
        self.assertEqual(
            stem_text("proses pembelajaran dan pengambilan keputusan", "id"),
            "ajar ambil dan kambil proses putus",
        )

    def test_bilingual_fts5_query_formatting(self) -> None:
        cases = {
            "distillation": "(distill* OR stillation*)",
            "pengambilan": "(ambil* OR kambil* OR pengambilan*)",
            "transformer distillation": "(transform* OR transformer*) AND (distill* OR stillation*)",
        }

        for query, expected in cases.items():
            with self.subTest(query=query):
                self.assertEqual(format_fts5_query_bilingual(query), expected)


if __name__ == "__main__":
    unittest.main()
