from typing import List, Dict, Any
from backend.config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

class Chunker:
    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """
        Splits a single string into chunks of maximum length self.chunk_size,
        with overlap self.chunk_overlap.
        This uses a simpler recursive-style character splitter.
        """
        if not text:
            return []
            
        separators = ["\n\n", "\n", ". ", " ", ""]
        chunks = []
        
        # Simple sliding window approach that respects word/sentence boundaries where possible
        # This is extremely robust and easy to read
        words = text.split(' ')
        current_chunk = []
        current_length = 0
        
        for word in words:
            # +1 is for the space we'll add
            word_len = len(word) + 1
            if current_length + word_len > self.chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                # Handle overlap: take words from the end of current_chunk that fit in overlap
                overlap_chunk = []
                overlap_len = 0
                for w in reversed(current_chunk):
                    if overlap_len + len(w) + 1 <= self.chunk_overlap:
                        overlap_chunk.insert(0, w)
                        overlap_len += len(w) + 1
                    else:
                        break
                current_chunk = overlap_chunk
                current_length = overlap_len
                
            current_chunk.append(word)
            current_length += word_len
            
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

    def chunk_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunks pages of text, preserving metadata.
        Each input page is a dict with: 'text', 'page', 'source'.
        Each returned chunk is a dict with keys:
          - 'text': str (chunk content)
          - 'page': int (page number)
          - 'source': str (document source name)
          - 'chunk_id': str (unique identifier source_page_idx)
        """
        all_chunks = []
        for page_data in pages:
            text = page_data["text"]
            page_num = page_data["page"]
            source = page_data["source"]
            
            page_chunks = self.split_text(text)
            for idx, chunk_text in enumerate(page_chunks):
                chunk_id = f"{source}_p{page_num}_c{idx}"
                all_chunks.append({
                    "text": chunk_text,
                    "page": page_num,
                    "source": source,
                    "chunk_id": chunk_id
                })
        return all_chunks

if __name__ == "__main__":
    chunker = Chunker(chunk_size=100, chunk_overlap=20)
    sample_text = "This is a very long text that will be split into smaller chunks so that we can index it and run vector search queries on it. The text needs to be split correctly."
    chunks = chunker.split_text(sample_text)
    print(f"Split sample text into {len(chunks)} chunks:")
    for idx, c in enumerate(chunks):
        print(f"  Chunk {idx}: {repr(c)}")
