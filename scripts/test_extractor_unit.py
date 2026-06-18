import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from scripts.ingest.extractor import (
    extract_pdf_tables,
    extract_pdf_images,
    _ocr_page_worker,
    parallel_pdf_ingest
)


class TestExtractorUnit(unittest.TestCase):
    """Test cases for PDF extraction functions, verifying safety and logic via mocks."""

    def test_extract_pdf_tables_nonexistent(self) -> None:
        """Verify extract_pdf_tables handles nonexistent files and returns empty string."""
        res = extract_pdf_tables("nonexistent_file_xyz_123.pdf")
        self.assertEqual(res, "")

    def test_extract_pdf_images_nonexistent(self) -> None:
        """Verify extract_pdf_images handles nonexistent files and returns empty string."""
        res = extract_pdf_images("nonexistent_file_xyz_123.pdf", "nonexistent_source")
        self.assertEqual(res, "")

    @patch("pdfplumber.open")
    def test_extract_pdf_tables_success(self, mock_open) -> None:
        """Verify successful table extraction and conversion to markdown."""
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_table = MagicMock()
        mock_table.bbox = (10, 20, 100, 200)
        mock_table.extract.return_value = [
            ["Col1", "Col2"], ["Val1", "Val2"]
        ]
        mock_table.columns = [MagicMock(), MagicMock()]
        mock_page.find_tables.return_value = [mock_table]
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf

        res = extract_pdf_tables("dummy.pdf")
        self.assertIn("Col1", res)
        self.assertIn("Val1", res)
        self.assertIn("### Table 1 (Page 1)", res)

    @patch("pdfplumber.open")
    @patch("pandas.DataFrame.to_markdown", side_effect=Exception("Tabulate failed"))
    def test_extract_pdf_tables_fallback_formatter(self, mock_to_markdown, mock_open) -> None:
        """Verify custom markdown table formatter fallback when pandas to_markdown raises an exception."""
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_table = MagicMock()
        mock_table.bbox = (10, 20, 100, 200)
        mock_table.extract.return_value = [
            ["Col1", "Col2"], ["Val1", "Val2"]
        ]
        mock_table.columns = [MagicMock(), MagicMock()]
        mock_page.find_tables.return_value = [mock_table]
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf

        res = extract_pdf_tables("dummy.pdf")
        self.assertIn("Col1 | Col2", res)
        self.assertIn("--- | ---", res)
        self.assertIn("Val1 | Val2", res)

    @patch("fitz.open")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_extract_pdf_images_success(self, mock_makedirs, mock_file_open, mock_fitz_open) -> None:
        """Verify successful image extraction and creation of Obsidian figure links."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_images.return_value = [[123]]
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.extract_image.return_value = {
            "image": b"dummy_image_data",
            "ext": "png"
        }
        mock_fitz_open.return_value.__enter__.return_value = mock_doc

        res = extract_pdf_images("dummy.pdf", "test_source")
        self.assertIn("![[source-test_source-fig1-1.png]]", res)
        mock_file_open.assert_called_with(
            os.path.normpath("wiki/assets/images/source-test_source-fig1-1.png"), "wb"
        )

    @patch("fitz.open")
    def test_ocr_page_worker_normal_text(self, mock_fitz_open) -> None:
        """Verify ocr page worker returns extracted page text if it is sufficiently long."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "This is a long text that is definitely longer than fifty characters."
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value.__enter__.return_value = mock_doc

        p_num, text = _ocr_page_worker("dummy.pdf", 0, None, "eng")
        self.assertEqual(p_num, 0)
        self.assertIn("longer than fifty characters", text)

    @patch("fitz.open")
    @patch("os.path.exists", return_value=True)
    def test_ocr_page_worker_ocr_fallback(self, mock_exists, mock_fitz_open) -> None:
        """Verify ocr page worker falls back to OCR if text is short and tessdata exists."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        # First call gets short text, second get_text returns the OCR result
        mock_page.get_text.side_effect = ["short", "Extracted OCR text"]
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value.__enter__.return_value = mock_doc

        p_num, text = _ocr_page_worker("dummy.pdf", 0, "/path/to/tessdata", "eng")
        self.assertEqual(p_num, 0)
        self.assertEqual(text, "Extracted OCR text")

    @patch("fitz.open")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_extract_pdf_images_with_caption(self, mock_makedirs, mock_file_open, mock_fitz_open) -> None:
        """Verify image extraction matches with figure captions and uses fig<num> naming."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        
        # get_images returns one image
        mock_page.get_images.return_value = [[123]]
        # get_text returns blocks, one containing 'Figure 4 | My Caption'
        mock_page.get_text.return_value = [
            (10, 100, 100, 120, "Figure 4 | My Caption", 0, 0)
        ]
        
        # get_image_rects returns a rect close to the caption
        import fitz
        mock_page.get_image_rects.return_value = [fitz.Rect(10, 10, 100, 80)]
        
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.extract_image.return_value = {
            "image": b"dummy_image_data",
            "ext": "png"
        }
        mock_fitz_open.return_value.__enter__.return_value = mock_doc

        res = extract_pdf_images("dummy.pdf", "test_source")
        self.assertIn("![[source-test_source-fig4.png]]", res)
        mock_file_open.assert_called_with(
            os.path.normpath("wiki/assets/images/source-test_source-fig4.png"), "wb"
        )

    @patch("pdfplumber.open")
    def test_extract_pdf_tables_fallback(self, mock_open) -> None:
        """Verify table extraction falls back to vertical_strategy='text' if first run is single-column."""
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        
        mock_t1 = MagicMock()
        mock_t1.columns = [MagicMock()]
        mock_t2 = MagicMock()
        mock_t2.columns = [MagicMock(), MagicMock()]
        mock_t2.bbox = (10, 20, 100, 200)
        mock_t2.extract.return_value = [
            ["Col1", "Col2"], ["Val1", "Val2"]
        ]
        
        mock_page.find_tables.side_effect = [
            [mock_t1],
            [mock_t2]
        ]
        mock_pdf.pages = [mock_page]
        mock_open.return_value.__enter__.return_value = mock_pdf

        res = extract_pdf_tables("dummy.pdf")
        self.assertIn("Col1", res)
        self.assertIn("Col2", res)
        self.assertIn("### Table 1 (Page 1)", res)

    @patch("fitz.open")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_extract_pdf_images_vector_fallback(self, mock_makedirs, mock_file_open, mock_fitz_open) -> None:
        """Verify vector drawings are extracted when no raster images exist and captions are found."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        
        # get_images returns empty (no raster images)
        mock_page.get_images.return_value = []
        
        # get_text returns blocks containing a caption
        mock_page.get_text.return_value = [
            (10, 500, 100, 520, "Figure 2 | Benchmark Chart", 0, 0)
        ]
        
        # get_drawings returns a vector path above the caption
        mock_page.get_drawings.return_value = [
            {"rect": (20, 200, 200, 480)}
        ]
        
        # Mock the page width and height
        mock_page.rect.width = 600
        mock_page.rect.height = 800
        
        # Mock pixmap and its rendering
        mock_pix = MagicMock()
        mock_pix.tobytes.return_value = b"dummy_vector_png_bytes"
        mock_page.get_pixmap.return_value = mock_pix
        
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value.__enter__.return_value = mock_doc

        res = extract_pdf_images("dummy.pdf", "test_source")
        self.assertIn("![[source-test_source-fig2.png]]", res)
        mock_file_open.assert_called_with(
            os.path.normpath("wiki/assets/images/source-test_source-fig2.png"), "wb"
        )


if __name__ == "__main__":
    sys.exit(unittest.main())


