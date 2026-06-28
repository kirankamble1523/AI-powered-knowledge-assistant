import os
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader

class TextExtractor:
    @staticmethod
    def extract_text_from_pdf(file_path: Path) -> List[Dict[str, Any]]:
        """
        Extracts text page-by-page from a PDF file.
        Returns a list of dictionaries with keys:
          - 'text': str (the text of the page)
          - 'page': int (1-based page number)
          - 'source': str (the filename of the document)
        """
        pages_content = []
        try:
            reader = PdfReader(str(file_path))
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages_content.append({
                    "text": text.strip(),
                    "page": i + 1,
                    "source": file_path.name
                })
        except Exception as e:
            print(f"[Extractor] Error reading PDF {file_path.name}: {e}")
        return pages_content

    @staticmethod
    def extract_text_from_txt(file_path: Path) -> List[Dict[str, Any]]:
        """
        Reads a TXT file and treats it as a single-page document.
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            return [{
                "text": text.strip(),
                "page": 1,
                "source": file_path.name
            }]
        except Exception as e:
            print(f"[Extractor] Error reading TXT {file_path.name}: {e}")
            return []

    @staticmethod
    def extract_text_from_md(file_path: Path) -> List[Dict[str, Any]]:
        """
        Reads an MD file and treats it as a single-page document.
        """
        # For simplicity, markdown reads exactly like TXT
        return TextExtractor.extract_text_from_txt(file_path)

    @classmethod
    def extract_file(cls, file_path: Path) -> List[Dict[str, Any]]:
        """
        Main interface to extract text from files based on their extension.
        """
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return cls.extract_text_from_pdf(file_path)
        elif ext == ".txt":
            return cls.extract_text_from_txt(file_path)
        elif ext == ".md":
            return cls.extract_text_from_md(file_path)
        else:
            print(f"[Extractor] Unsupported file extension {ext} for {file_path.name}")
            return []
            
if __name__ == "__main__":
    # Test extraction
    test_file = Path("../data/Compliance_Guidelines.pdf")
    if test_file.exists():
        pages = TextExtractor.extract_file(test_file)
        print(f"Extracted {len(pages)} pages from {test_file.name}")
        for page in pages:
            print(f"Page {page['page']} (first 50 chars): {repr(page['text'][:50])}")
