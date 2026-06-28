import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from backend.config import VECTOR_STORE_DIR

class CustomVectorStore:
    def __init__(self, persist_dir: Path = VECTOR_STORE_DIR):
        self.persist_dir = persist_dir
        self.persist_path = persist_dir / "index.json"
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []
        self.load()

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: Optional[List[List[float]]]):
        """
        Adds a list of chunks and their embedding vectors to the vector store.
        If embeddings are None (API failed), pads with dummy zero vectors.
        """
        if embeddings is None:
            # Pad with dummy zero-vectors to maintain structure
            embeddings = [[0.0] * 1536 for _ in range(len(chunks))]
            
        if len(chunks) != len(embeddings):
            raise ValueError("The number of chunks and embeddings must match.")
            
        existing_ids = {c["chunk_id"] for c in self.chunks}
        for chunk, embedding in zip(chunks, embeddings):
            if chunk["chunk_id"] not in existing_ids:
                self.chunks.append(chunk)
                self.embeddings.append(embedding)
                existing_ids.add(chunk["chunk_id"])
                
        self.save()

    def delete_document(self, filename: str):
        """
        Deletes all chunks associated with a specific document name.
        """
        new_chunks = []
        new_embeddings = []
        for chunk, embedding in zip(self.chunks, self.embeddings):
            if chunk["source"] != filename:
                new_chunks.append(chunk)
                new_embeddings.append(embedding)
                
        self.chunks = new_chunks
        self.embeddings = new_embeddings
        self.save()

    def clear(self):
        """
        Clears the entire vector store.
        """
        self.chunks = []
        self.embeddings = []
        if self.persist_path.exists():
            try:
                self.persist_path.unlink()
            except Exception as e:
                print(f"[VectorStore] Error deleting file: {e}")
        self.save()

    def save(self):
        """
        Saves the index to index.json.
        """
        self.persist_dir.mkdir(exist_ok=True)
        data = {
            "chunks": self.chunks,
            "embeddings": self.embeddings
        }
        try:
            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[VectorStore] Error saving index: {e}")

    def load(self):
        """
        Loads the index from index.json.
        """
        if not self.persist_path.exists():
            self.chunks = []
            self.embeddings = []
            return
            
        try:
            with open(self.persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.chunks = data.get("chunks", [])
                self.embeddings = data.get("embeddings", [])
            print(f"[VectorStore] Loaded {len(self.chunks)} chunks from {self.persist_path.name}")
        except Exception as e:
            print(f"[VectorStore] Error loading index: {e}. Starting with an empty index.")
            self.chunks = []
            self.embeddings = []

    def search(self, query_embedding: Optional[List[float]], k: int = 3, query_text: Optional[str] = None) -> List[Tuple[Dict[str, Any], float]]:
        """
        Performs search. If query_embedding is None, performs keyword matching search.
        Otherwise performs cosine similarity search.
        """
        if not self.embeddings or not self.chunks:
            return []
            
        # Fallback to keyword search if query embedding is missing or contains all zeros (dummy embeddings)
        is_dummy = all(v == 0.0 for v in query_embedding) if query_embedding else True
        if query_embedding is None or is_dummy:
            if query_text:
                return self.keyword_search(query_text, k)
            return []
            
        # Convert to numpy arrays
        q_vec = np.array(query_embedding)
        emb_matrix = np.array(self.embeddings)
        
        # Calculate cosine similarities
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            if query_text:
                return self.keyword_search(query_text, k)
            return []
            
        matrix_norms = np.linalg.norm(emb_matrix, axis=1)
        matrix_norms[matrix_norms == 0] = 1e-10
        
        dot_products = np.dot(emb_matrix, q_vec)
        similarities = dot_products / (matrix_norms * q_norm)
        
        # Check if the top similarities are all zero (means dummy vectors were used)
        top_idx = np.argsort(similarities)[::-1][:k]
        if len(top_idx) > 0 and similarities[top_idx[0]] == 0.0 and query_text:
            return self.keyword_search(query_text, k)
            
        results = []
        for idx in top_idx:
            results.append((self.chunks[idx], float(similarities[idx])))
            
        return results

    def keyword_search(self, query: str, k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        """
        Performs local keyword-based search when embeddings are not available.
        Scores chunks based on term overlap (case-insensitive).
        """
        print(f"[VectorStore] API key unavailable or failed. Performing keyword search for '{query}'...")
        query_words = set(query.lower().split())
        
        # Remove common English stopwords to improve relevance
        stopwords = {"what", "is", "the", "are", "do", "you", "have", "policy", "for", "about", "a", "an", "and", "or", "in", "on", "of", "to", "does", "use", "corporate"}
        query_words = query_words - stopwords
        
        if not query_words:
            query_words = set(query.lower().split())
            
        scored_chunks = []
        for chunk in self.chunks:
            chunk_text_lower = chunk["text"].lower()
            score = 0.0
            for word in query_words:
                count = chunk_text_lower.count(word)
                if count > 0:
                    # Score based on word match + frequency incentive
                    score += (1.0 + 0.5 * count)
                    
            if score > 0:
                # Slight penalty for longer chunks to prefer more specific matches
                score = score / (1.0 + 0.005 * len(chunk["text"]))
                scored_chunks.append((chunk, score))
                
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        # Normalize scores to look like similarities [0, 1]
        results = []
        max_score = scored_chunks[0][1] if scored_chunks else 1.0
        for chunk, score in scored_chunks[:k]:
            normalized_score = min(0.95, 0.5 + (0.45 * (score / max_score)))
            results.append((chunk, normalized_score))
            
        return results

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Gets summary of all ingested documents.
        """
        docs_summary = {}
        for chunk in self.chunks:
            src = chunk["source"]
            pg = chunk["page"]
            if src not in docs_summary:
                docs_summary[src] = {
                    "filename": src,
                    "max_page": pg,
                    "chunk_count": 0
                }
            docs_summary[src]["chunk_count"] += 1
            if pg > docs_summary[src]["max_page"]:
                docs_summary[src]["max_page"] = pg
                
        return list(docs_summary.values())

if __name__ == "__main__":
    store = CustomVectorStore()
    print("All documents: ", store.get_all_documents())
