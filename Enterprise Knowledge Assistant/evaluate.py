import sys
import time
from pathlib import Path
from fastapi.testclient import TestClient

# Add root folder to Python path
sys.path.append(str(Path(__file__).resolve().parent))

from backend.app import app

def run_evaluation():
    # Test cases to evaluate the RAG system
    test_cases = [
        {
            "question": "What is the employee leave policy?",
            "expected_doc": "HR_Policy.pdf",
            "expected_page": 12,
            "keywords": ["24", "paid leaves"]
        },
        {
            "question": "What is the refund policy?",
            "expected_doc": "Customer_Policy.pdf",
            "expected_page": 5,
            "keywords": ["30 days", "refund"]
        },
        {
            "question": "What are the password requirements?",
            "expected_doc": "Compliance_Guidelines.pdf",
            "expected_page": 2,
            "keywords": ["12 characters", "MFA"]
        },
        {
            "question": "What database does AnthraSync Core v4.2 use?",
            "expected_doc": "Product_Docs.pdf",
            "expected_page": 2,
            "keywords": ["PostgreSQL", "Redis"]
        },
        {
            "question": "Do you have policies about inter-planetary space travel?",
            "expected_doc": None,
            "expected_page": None,
            "keywords": ["not find", "not available"]
        }
    ]
    
    print("\n=== Running RAG Pipeline Evaluation ===")
    results = []
    
    with TestClient(app) as client:
        for idx, tc in enumerate(test_cases):
            print(f"Running Test {idx+1}/{len(test_cases)}: '{tc['question']}'")
            
            start_time = time.time()
            response = client.post("/ask", json={"question": tc["question"]})
            elapsed = time.time() - start_time
        
            if response.status_code != 200:
                print(f"  FAILED: Status code {response.status_code}")
                results.append({
                    "question": tc["question"],
                    "success": False,
                    "error": f"Status code {response.status_code}",
                    "elapsed": elapsed
                })
                continue
                
            data = response.json()
            answer = data["answer"]
            sources = data["sources"]
            confidence = data["confidence"]
            
            # Check source validity
            source_correct = False
            if tc["expected_doc"] is None:
                source_correct = len(sources) == 0
            else:
                for s in sources:
                    if s["document"] == tc["expected_doc"] and s["page"] == tc["expected_page"]:
                        source_correct = True
                        break
                        
            # Check keyword presence in answer (lowercased comparison)
            keywords_matched = []
            for kw in tc["keywords"]:
                if kw.lower() in answer.lower():
                    keywords_matched.append(kw)
            
            keywords_ok = len(keywords_matched) > 0 or tc["expected_doc"] is None
            
            print(f"  Latency: {elapsed:.2f}s | Confidence: {confidence:.2f}")
            print(f"  Source Correct: {source_correct} | Keywords Matched: {keywords_matched}")
            
            results.append({
                "question": tc["question"],
                "success": True,
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "source_correct": source_correct,
                "keywords_matched": keywords_matched,
                "expected_doc": tc["expected_doc"],
                "expected_page": tc["expected_page"],
                "elapsed": elapsed
            })
        
    # Generate Markdown Report
    report_path = Path(__file__).resolve().parent / "evaluation_report.md"
    
    total_latency = sum(r["elapsed"] for r in results)
    avg_latency = total_latency / len(results)
    success_rate = sum(1 for r in results if r.get("success", False) and r.get("source_correct", False)) / len(results) * 100
    avg_confidence = sum(r.get("confidence", 0) for r in results if r.get("success", False)) / len(results)
    
    markdown_content = f"""# RAG Pipeline Evaluation Report

This report evaluates the performance, accuracy, and citation precision of the **AnthraSync Enterprise Knowledge Assistant** over a set of representative test cases.

## Summary Metrics

| Metric | Value | Description |
| :--- | :--- | :--- |
| **Total Test Cases** | {len(results)} | Number of queries tested |
| **Citation Accuracy** | {success_rate:.1f}% | % of queries returning exact expected source document and page number |
| **Avg. Query Latency** | {avg_latency:.2f} seconds | Average time elapsed per end-to-end question answering |
| **Avg. Model Confidence** | {avg_confidence:.2f} | Average confidence score outputted by the model |

---

## Detailed Test Results

"""
    
    for idx, r in enumerate(results):
        status_emoji = "✅ PASS" if r.get("success") and r.get("source_correct") else "❌ FAIL"
        
        sources_str = ", ".join([f"`{s['document']}` (Page {s['page']})" for s in r.get("sources", [])]) if r.get("sources") else "None"
        expected_str = f"`{r['expected_doc']}` (Page {r['expected_page']})" if r.get("expected_doc") else "None"
        
        markdown_content += f"""### Test {idx+1}: "{r['question']}"
- **Status**: {status_emoji}
- **Latency**: {r['elapsed']:.2f} seconds
- **Confidence Badge**: `{r.get('confidence', 0.0):.2f}`
- **Retrieved Source**: {sources_str}
- **Expected Source**: {expected_str}
- **Keywords Matched**: `{r.get('keywords_matched', [])}`
- **Generated Answer**:
  > {r.get('answer', 'N/A')}

---
"""
        
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    print(f"\n[Evaluation] Report generated successfully at {report_path.name}!")
    print(f"[Evaluation] Success Rate: {success_rate:.1f}% | Avg Latency: {avg_latency:.2f}s | Avg Confidence: {avg_confidence:.2f}")

if __name__ == "__main__":
    run_evaluation()
