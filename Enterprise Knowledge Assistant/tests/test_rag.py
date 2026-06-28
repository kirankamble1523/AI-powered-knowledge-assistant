import unittest
import sys
from pathlib import Path

# Add root folder to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.chunker import Chunker
from backend.custom_vector_store import CustomVectorStore
from backend.text_extractor import TextExtractor

class TestRAGComponents(unittest.TestCase):
    
    def setUp(self):
        self.chunker = Chunker(chunk_size=100, chunk_overlap=20)
        self.temp_vector_dir = Path(__file__).resolve().parent / "temp_vector_store"
        self.temp_vector_dir.mkdir(exist_ok=True)
        self.vector_store = CustomVectorStore(persist_dir=self.temp_vector_dir)

    def tearDown(self):
        self.vector_store.clear()
        if self.vector_store.persist_path.exists():
            self.vector_store.persist_path.unlink()
        if self.temp_vector_dir.exists():
            self.temp_vector_dir.rmdir()

    def test_chunker_basic_split(self):
        text = "This is a simple phrase that should be split into smaller blocks because the chunk size is set very low."
        chunks = self.chunker.split_text(text)
        self.assertTrue(len(chunks) > 1)
        for chunk in chunks:
            self.assertTrue(len(chunk) <= self.chunker.chunk_size + 20)  # Tolerable margin for join

    def test_chunker_metadata_preservation(self):
        pages = [
            {"text": "Page 1 context here", "page": 1, "source": "test.pdf"},
            {"text": "Page 2 context is separate", "page": 2, "source": "test.pdf"}
        ]
        chunks = self.chunker.chunk_pages(pages)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0]["page"], 1)
        self.assertEqual(chunks[0]["source"], "test.pdf")
        self.assertEqual(chunks[1]["page"], 2)
        self.assertEqual(chunks[1]["source"], "test.pdf")
        self.assertIn("chunk_id", chunks[0])

    def test_vector_store_add_and_search(self):
        chunks = [
            {"text": "The quick brown fox jumps over the lazy dog", "page": 1, "source": "fox.txt", "chunk_id": "c1"},
            {"text": "Artificial Intelligence is shaping the future of work", "page": 2, "source": "ai.txt", "chunk_id": "c2"}
        ]
        
        # Simple embeddings (2 dimensions)
        embeddings = [
            [1.0, 0.0],
            [0.0, 1.0]
        ]
        
        self.vector_store.add_chunks(chunks, embeddings)
        
        # Verify saved chunks count
        self.assertEqual(len(self.vector_store.chunks), 2)
        
        # Search close to first chunk [1.0, 0.1]
        results = self.vector_store.search([1.0, 0.1], k=1)
        self.assertEqual(len(results), 1)
        best_chunk, score = results[0]
        self.assertEqual(best_chunk["chunk_id"], "c1")
        self.assertTrue(score > 0.9)

        # Search close to second chunk [0.1, 1.0]
        results = self.vector_store.search([0.1, 1.0], k=1)
        self.assertEqual(len(results), 1)
        best_chunk, score = results[0]
        self.assertEqual(best_chunk["chunk_id"], "c2")
        self.assertTrue(score > 0.9)

    def test_vector_store_delete_document(self):
        chunks = [
            {"text": "Doc 1 text", "page": 1, "source": "doc1.txt", "chunk_id": "c1"},
            {"text": "Doc 2 text", "page": 1, "source": "doc2.txt", "chunk_id": "c2"}
        ]
        embeddings = [[1.0, 0.0], [0.0, 1.0]]
        
        self.vector_store.add_chunks(chunks, embeddings)
        self.assertEqual(len(self.vector_store.chunks), 2)
        
        # Delete doc1
        self.vector_store.delete_document("doc1.txt")
        self.assertEqual(len(self.vector_store.chunks), 1)
        self.assertEqual(self.vector_store.chunks[0]["source"], "doc2.txt")

if __name__ == "__main__":
    unittest.main()
