# Phase 10 Decision Log

## 1. SentenceTransformer for Embeddings
Use SentenceTransformer for semantic embeddings. Pre-trained, production-ready.

## 2. FAISS for Vector Search
Use FAISS for approximate nearest neighbor search. Scales to 10K+ vectors.

## 3. Keyword-based Intent Classifier
Implement keyword-based classifier before FAISS retrieval.

## 4. Conversation Memory
Store last 6 turns in memory for context-aware responses.

## 5. Confidence Thresholds
Implement tiered confidence scoring (100%, 90%+, <40%).

## 6. Escalation Engine
Rule-based escalation with critical/high/medium/low priorities.

## 7. Streamlit Frontend
Use Streamlit for rapid UI development.

## 8. FastAPI Backend
Use FastAPI for REST API.

## 9. Typo Normalization
Normalize common misspellings before classification.

## 10. Golden Dataset
Manually label 200+ examples for ground truth evaluation.

## 11. LLM-as-Judge Evaluation
Use Claude as judge for response quality evaluation.

## 12. Confusion Matrix Analysis
Track per-intent performance.

## 13. Failure Analysis
Categorize failures into types for systematic improvement.

## 14. Misleading Headline Prevention
Document why accuracy alone is misleading.

## 15. Reproducibility Scripts
Provide run_phase10.py to verify all artifacts.
