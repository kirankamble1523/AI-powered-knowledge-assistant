# Enterprise Knowledge Assistant

An AI-powered **Enterprise Knowledge Assistant** built using **Retrieval-Augmented Generation (RAG)**. The system enables employees to ask natural language questions and receive accurate, context-aware answers from enterprise documents with source citations.

---

## Features

* 📄 Document ingestion and preprocessing
* ✂️ Intelligent document chunking
* 🔍 Semantic search using vector embeddings
* 🤖 AI-powered answer generation
* 📚 Source citation with document references
* 💬 Interactive chat interface
* 🚫 Hallucination reduction through retrieval-based context
* ⚡ Fast vector similarity search

---

## Architecture

```
                Enterprise Documents
        (PDFs, HR Policies, FAQs, Guides)
                       │
                       ▼
             Document Processing Pipeline
        ┌─────────────────────────────────┐
        │ • Text Extraction               │
        │ • Chunking                      │
        │ • Metadata Creation             │
        │ • Embedding Generation          │
        └─────────────────────────────────┘
                       │
                       ▼
              Vector Database (FAISS/Chroma)
                       │
                       ▼
              Semantic Similarity Search
                       │
                       ▼
              Retrieved Relevant Context
                       │
                       ▼
                    Large Language Model
                       │
                       ▼
      Context-aware Answer + Source Citation
```

---

## Technology Stack

| Component       | Technology            |
| --------------- | --------------------- |
| Language        | Python                |
| Framework       | LangChain             |
| LLM             | OpenAI GPT-4 / GPT-4o |
| Embeddings      | OpenAI Embeddings     |
| Vector Database | FAISS / ChromaDB      |
| UI              | Streamlit             |
| Document Loader | PyPDFLoader           |
| Environment     | Python 3.10+          |

---

## Project Structure

```
enterprise-knowledge-assistant/

├── app.py
├── api.py
├── requirements.txt
├── .env.example
├── data/
│   ├── HR_Policy.pdf
│   ├── Product_Docs.pdf
│   └── Customer_FAQ.pdf
│
├── src/
│   ├── loader.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── rag_pipeline.py
│   └── prompt.py
│
├── vector_db/
├── screenshots/
└── README.md
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/yourusername/enterprise-knowledge-assistant.git

cd enterprise-knowledge-assistant
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file.

```
OPENAI_API_KEY=your_api_key
```

---

## Run the Application

```bash
streamlit run app.py
```

or

```bash
python app.py
```

---

## API (Optional)

Example request

```
POST /ask
```

Request

```json
{
    "question":"What is the employee leave policy?"
}
```

Response

```json
{
  "answer":"Employees receive 24 paid leaves annually.",
  "sources":[
      {
          "document":"HR_Policy.pdf",
          "page":12
      }
  ],
  "confidence":0.92
}
```

---

## How It Works

1. Load enterprise documents
2. Extract document text
3. Split into semantic chunks
4. Generate vector embeddings
5. Store embeddings in a vector database
6. Retrieve relevant chunks based on user queries
7. Generate answers using the LLM with retrieved context
8. Return the answer with source references

---

## Design Decisions

### Why Retrieval-Augmented Generation (RAG)?

* Reduces hallucinations
* Keeps responses grounded in enterprise documents
* Provides explainable answers with citations

### Chunking Strategy

* Recursive text splitting
* Overlapping chunks preserve context
* Optimized chunk size for retrieval accuracy

### Embeddings

Semantic embeddings capture contextual similarity rather than keyword matching, improving retrieval quality.

### Vector Database

FAISS (or ChromaDB) provides efficient similarity search for scalable document retrieval.

---

## Evaluation

The system is evaluated using:

* Retrieval relevance
* Answer accuracy
* Source citation correctness
* Hallucination rate
* Response latency

Example test questions:

* What is the leave policy?
* What is the refund policy?
* How can an employee apply for leave?
* What are the compliance guidelines?

---

## Future Improvements

* Hybrid Search (BM25 + Semantic Search)
* Conversation Memory
* Query Rewriting
* Re-ranking Models
* Multi-document Reasoning
* User Authentication
* Feedback Collection
* Cloud Deployment
* Docker Support
* Kubernetes Deployment

---

## Limitations

* Performance depends on document quality
* Large document collections require optimized indexing
* Requires an LLM API for answer generation
* OCR is needed for scanned PDFs

---

## Demo

Include:

* Application walkthrough
* Document ingestion
* Sample question answering
* Source citation demonstration

---

## License

This project is developed for an AI Engineering Assignment and is intended for educational and evaluation purposes.
