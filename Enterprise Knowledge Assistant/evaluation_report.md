# RAG Pipeline Evaluation Report

This report evaluates the performance, accuracy, and citation precision of the **AnthraSync Enterprise Knowledge Assistant** over a set of representative test cases.

## Summary Metrics

| Metric | Value | Description |
| :--- | :--- | :--- |
| **Total Test Cases** | 5 | Number of queries tested |
| **Citation Accuracy** | 100.0% | % of queries returning exact expected source document and page number |
| **Avg. Query Latency** | 2.26 seconds | Average time elapsed per end-to-end question answering |
| **Avg. Model Confidence** | 0.76 | Average confidence score outputted by the model |

---

## Detailed Test Results

### Test 1: "What is the employee leave policy?"
- **Status**: ✅ PASS
- **Latency**: 8.52 seconds
- **Confidence Badge**: `0.95`
- **Retrieved Source**: `HR_Policy.pdf` (Page 12)
- **Expected Source**: `HR_Policy.pdf` (Page 12)
- **Keywords Matched**: `['24', 'paid leaves']`
- **Generated Answer**:
  > Employees are eligible for 24 paid leaves annually. Vacation requests must be submitted at least two weeks in advance. Unused leaves do not roll over to the next calendar year.

---
### Test 2: "What is the refund policy?"
- **Status**: ✅ PASS
- **Latency**: 0.72 seconds
- **Confidence Badge**: `0.95`
- **Retrieved Source**: `Customer_Policy.pdf` (Page 5)
- **Expected Source**: `Customer_Policy.pdf` (Page 5)
- **Keywords Matched**: `['30 days', 'refund']`
- **Generated Answer**:
  > Refunds are allowed within 30 days of purchase. The product must be returned in its original packaging and with all accessories. Allow 5-7 business days for processing.

---
### Test 3: "What are the password requirements?"
- **Status**: ✅ PASS
- **Latency**: 0.82 seconds
- **Confidence Badge**: `0.95`
- **Retrieved Source**: `Compliance_Guidelines.pdf` (Page 2)
- **Expected Source**: `Compliance_Guidelines.pdf` (Page 2)
- **Keywords Matched**: `['12 characters', 'MFA']`
- **Generated Answer**:
  > All corporate account passwords must be at least 12 characters long and contain a mix of uppercase letters, lowercase letters, numbers, and special characters. Multi-Factor Authentication (MFA) is mandatory.

---
### Test 4: "What database does AnthraSync Core v4.2 use?"
- **Status**: ✅ PASS
- **Latency**: 0.66 seconds
- **Confidence Badge**: `0.95`
- **Retrieved Source**: `Product_Docs.pdf` (Page 2)
- **Expected Source**: `Product_Docs.pdf` (Page 2)
- **Keywords Matched**: `['PostgreSQL', 'Redis']`
- **Generated Answer**:
  > AnthraSync Core v4.2 is built on a distributed microservices framework using PostgreSQL for relational storage and Redis for high-speed caching.

---
### Test 5: "Do you have policies about inter-planetary space travel?"
- **Status**: ✅ PASS
- **Latency**: 0.59 seconds
- **Confidence Badge**: `0.00`
- **Retrieved Source**: None
- **Expected Source**: None
- **Keywords Matched**: `[]`
- **Generated Answer**:
  > I'm sorry, but I couldn't find information about that in the provided documents.

---
