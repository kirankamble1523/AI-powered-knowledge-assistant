import os
import openai
from typing import List, Optional
from backend.config import EMBEDDING_MODEL, OPENAI_API_KEY

class EmbeddingGenerator:
    def __init__(self):
        # Configure client if key is set
        if OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        else:
            self.client = None
            print("[Embeddings] WARNING: No OpenAI API key set. Embedding generation will fail.")

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Gets embedding vector for a single string. Returns None if API fails.
        """
        if not self.client:
            return None
        
        model = EMBEDDING_MODEL
        if "ada-002" not in model:
            model = "text-embedding-ada-002"
            
        try:
            response = self.client.embeddings.create(
                input=text.replace("\n", " "),
                model=model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"[Embeddings] Error generating embedding: {e}. Falling back to local search.")
            return None

    def get_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Gets embedding vectors for a list of strings in batch. Returns None if API fails.
        """
        if not self.client or not texts:
            return None
            
        model = EMBEDDING_MODEL
        if "ada-002" not in model:
            model = "text-embedding-ada-002"
            
        cleaned_texts = [t.replace("\n", " ") for t in texts]
        
        try:
            response = self.client.embeddings.create(
                input=cleaned_texts,
                model=model
            )
            sorted_data = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in sorted_data]
        except Exception as e:
            print(f"[Embeddings] Error generating batch embeddings: {e}. Falling back to local search.")
            return None

if __name__ == "__main__":
    generator = EmbeddingGenerator()
    emb = generator.get_embedding("Hello world")
    print("Embedding generated:", emb is not None)
