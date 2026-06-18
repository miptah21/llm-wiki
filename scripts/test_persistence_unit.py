import os
import sys
import unittest


project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_dir = os.path.join(project_root, "scripts")
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

from ingest.persistence import project_relative_path, validate_safe_path


class TestPersistencePathSafety(unittest.TestCase):
    def test_rejects_sibling_directory_with_shared_prefix(self) -> None:
        sibling_path = os.path.abspath(
            os.path.join(
                os.getcwd(),
                "..",
                f"{os.path.basename(os.getcwd())}-evil",
                "raw",
                "source.md",
            )
        )

        with self.assertRaises(ValueError):
            validate_safe_path(sibling_path)

    def test_project_relative_path_uses_forward_slashes(self) -> None:
        raw_path = os.path.abspath(os.path.join("raw", "articles", "example.md"))

        self.assertEqual(project_relative_path(raw_path), "raw/articles/example.md")

    def test_project_relative_path_rejects_external_path(self) -> None:
        external_path = os.path.abspath(os.path.join("..", "outside.md"))

        with self.assertRaises(ValueError):
            project_relative_path(external_path)

    def test_write_wiki_page_rejects_outside_vault(self) -> None:
        from ingest.persistence import write_wiki_page
        # Attempting to write a file inside scripts/ (which is outside wiki/) should raise ValueError
        with self.assertRaises(ValueError):
            write_wiki_page("scripts/test_persistence_unit.py", {}, "# Test Content")


if __name__ == "__main__":
    unittest.main()
