# System Design Document: Enterprise Knowledge Assistant

This document outlines the high-level architecture, data flow, component design, and scalability considerations for the **AnthraSync Enterprise Knowledge Assistant** RAG system.

---

## 1. High-Level Architecture

The system follows a standard microservices-like design inside a self-contained, lightweight Python architecture. It consists of three primary layers:
1. **Ingestion Pipeline (Offline/Startup)**: Collects files, extracts text page-by-page, breaks text into overlapping chunks, generates embedding vectors, and indexes them in a local store.
2. **FastAPI Web API Backend (Server)**: Exposes endpoints for client communication, manages configuration, and routes queries to the RAG services.
3. **Responsive Web UI (Frontend Client)**: A single-page application (SPA) providing visual interfaces for document listing, uploading, and conversation.

```
       +---------------------------------------------+
       |                  Frontend                   |
       |      Single Page App (HTML/CSS/Vanilla JS)  |
       +---------------------------------------------+
                              |
                     REST HTTP Requests
                              v
       +---------------------------------------------+
       |             FastAPI Web Server              |
       +---------------------------------------------+
             |                                 |
      Ingest Request                      Ask Request
             v                                 v
  +--------------------+             +-------------------+
  | Ingestion Pipeline |             |   Search & RAG    |
  |                    |             |                   |
  |  1. Text Extractor |             |  1. Query Embedder|
  |     (pypdf)        |             |  2. Vector Search |
  |  2. Recursive      |             |     (Local Cosine)|
  |     Chunker        |             |  3. Answer Gen    |
  |  3. OpenAI Embeds  |             |     (gpt-3.5)     |
  +--------------------+             +-------------------+
             |                                 |
        Write Chunks                      Read Chunks
             |                                 |
             v                                 v
       +---------------------------------------------+
       |           Custom Vector Database            |
       |             (NumPy + JSON Index)            |
       +---------------------------------------------+
```

---

## 2. Component Explanation

### 2.1. Text Extraction (`backend/text_extractor.py`)
Responsible for reading raw document streams (PDF, TXT, MD) and outputting page-indexed text blocks. It uses the `pypdf` library to navigate the PDF structure. Text is returned in a structured format: `{"text": str, "page": int, "source": str}`.

### 2.2. Chunker (`backend/chunker.py`)
Breaks down pages into smaller segments to fit within the context window of embedding models.
- **Strategy**: Recursive split on space boundaries, attempting to preserve paragraphs and sentences.
- **Overlap**: A sliding window overlap (default 100 characters) is used, allowing terms that occur on the boundary of split segments to still be captured as complete semantic concepts.
- **Metadata Tagging**: Tags every chunk with a unique `chunk_id`, the `source` file name, and the exact `page` number.

### 2.3. Embedding Generator (`backend/embeddings.py`)
Generates 1536-dimensional embedding vectors for text using OpenAI's API. If the API key is unauthorized or hits quota limits (429), it returns `None`, signaling the search engine to use keyword search instead of semantic search.

### 2.4. Custom Vector Store (`backend/custom_vector_store.py`)
An in-memory vector index that persists on disk in JSON format.
- **Semantic Indexing**: When query embeddings are available, it computes the cosine similarity between the query vector and all stored document vectors using NumPy matrix-vector multiplication.
- **Lexical Indexing**: When query embeddings are unavailable (API fail), it falls back to a lexical TF-IDF/word-overlap keyword matching algorithm that searches and scores terms across the document chunks.

### 2.5. LLM Client (`backend/llm_client.py`)
Forms prompts and handles completions.
- **Prompt Engineering**: Uses system instructions to align context. The LLM is instructed to answer *strictly* using the retrieved documents, format citations, assess confidence, and refuse to answer if facts are missing.
- **Fallback Answer Generation**: If the LLM client fails (due to API key quota), it automatically runs a local rule-based extractor that scans the top retrieved chunks for matching keywords, extracts the relevant sentences, and formats the response with precise citations.

---

## 3. Data Flow Diagram

The diagram below details the sequence of a question-answering query:

```
User UI                 FastAPI App            Vector Store              LLM Client             OpenAI API
  |                          |                      |                        |                       |
  |--- POST /ask (query) --->|                      |                        |                       |
  |                          |--- Get Embedding --->|                        |                       |
  |                          |    (or None if key)  |                        |                       |
  |                          |<-- Vector/None ------|                        |                       |
  |                          |                      |                        |                       |
  |                          |--- Search (Vector) ->|                        |                       |
  |                          |    (or Keyword query)|                        |                       |
  |                          |<-- Top-K Chunks -----|                        |                       |
  |                          |                                               |                       |
  |                          |------------- Generate Answer ---------------->|                       |
  |                          |              (context + query)                |                       |
  |                          |                                               |--- Chat request ----->|
  |                          |                                               |    (or local fallback)|
  |                          |                                               |<-- JSON result -------|
  |                          |<------------ JSON Response -------------------|                       |
  |<-- Response JSON --------|                                                                       |
  |   (answer, sources,      |                                                                       |
  |    confidence)           |                                                                       |
```

---

## 4. Scalability & Production Considerations

To scale this application to an enterprise level handling hundreds of thousands of documents, the following components would be upgraded:

### 4.1. Distributed Vector Database
The local JSON-based vector store loads all embeddings into memory. For large collections, this should be replaced with a distributed vector database like **Qdrant**, **Pinecone**, or **milvus**:
- Allows indexing millions of documents with disk-backed storage.
- Uses HNSW (Hierarchical Navigable Small World) indices for sub-millisecond approximate nearest neighbor (ANN) searches.

### 4.2. Document Ingestion Workers (Async Queue)
In the current implementation, file ingestion is run synchronously inside the request thread or standard background tasks.
- **Production Scaling**: Uploaded files should be placed in an object store (e.g. AWS S3).
- An asynchronous task queue (e.g. **Celery** with **Redis** or **RabbitMQ**) should dispatch files to distributed worker pools.
- Dedicated ingestion nodes extract, chunk, and embed documents in parallel, avoiding CPU blocks on the main API thread.

### 4.3. Hybrid Search (Lexical + Semantic)
For enterprise search, dense vector retrieval can sometimes miss specific serial numbers, product IDs, or codes. Combining dense semantic embeddings with sparse lexical indexing (e.g., Elasticsearch or OpenSearch running BM25) via Reciprocal Rank Fusion (RRF) delivers the highest search precision.

### 4.4. Security and Document Access Control (ACL)
In a corporate setting, employees should only see answers derived from documents they are authorized to access (e.g., executive docs versus general HR). Chunks stored in the vector database should include metadata fields for Access Control Lists (ACLs). During search, queries must be filtered based on the active user's permissions, ensuring secure retrieval boundaries.
