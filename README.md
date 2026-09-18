# Hiver AI Support Agent — Phase 8 API

## Phase 8 — FastAPI backend

This repository includes a production-grade FastAPI backend for the Hiver AI Support Agent.

### API Architecture

```
Client -> FastAPI (src/api/app.py) -> Chatbot dependencies (singleton)
                |- /chat
                |- /intents
                |- /health
                |- /reset
```

### Endpoints

- `GET /` — API metadata
- `GET /health` — Health and readiness
- `GET /intents` — Canonical intents
- `POST /chat` — Query the chatbot
- `POST /reset` — Reset conversation memory

### Example curl

```bash
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d '{"query":"Where is my order?","top_k":3}'
```

### Example Python

```python
import requests
resp = requests.post('http://127.0.0.1:8000/chat', json={'query':'Where is my order?','top_k':3})
print(resp.json())
```

### Running locally

Start API:

```bash
python scripts/run_api.py
```

Run validation tests (Phase 8 automated):

```bash
python scripts/run_phase8.py
```
# Hiver AI Support Agent

This project contains the structure for an AI-powered support agent pipeline.

## Project Layout

- `data/` for raw/interim/processed datasets and embeddings
- `notebooks/` for exploratory and modeling notebooks
- `src/` for preprocessing, classification, RAG, escalation, evaluation, and app code
- `assets/` for architecture, screenshots, demo, and icons
- `report/` for generated reports
- `tests/` for test files
- `requirements.txt` for dependencies
- `decision_log.md` for major decisions and project notes




## Phase 3 Completed ✅

### Exploratory Data Analysis
- Reconstructed 82,556 Amazon customer support conversations.
- Generated conversation statistics and distributions.
- Added customer vs Amazon interaction visualizations.
- Generated language and keyword analysis assets.
- Created preprocessing pipeline for downstream intent discovery.

### Output Artifacts
- Conversation length distribution
- Customer vs Amazon scatter plot
- Customer message distribution
- Amazon message distribution
- Conversation word distribution
- Phase 3 EDA summary report

## Phase 4 Completed ✅

### Semantic Intent Discovery
- Rebuilt the embedding pipeline and generated 10,000 sentence embeddings using the SentenceTransformers all-MiniLM-L6-v2 model.
- Reduced the embedding space with UMAP for semantic clustering.
- Discovered intent groups using HDBSCAN and computed cluster quality metrics.
- Generated semantic summaries with TF-IDF keyword extraction and representative conversation examples.
- Exported cluster statistics, evaluation artifacts, reports, and visualization outputs in reproducible form.

### Generated Outputs
- `data/embeddings/sample_sentence_embeddings.npy`
- `data/embeddings/sample_metadata.csv`
- `data/embeddings/embedding_info.json`
- `data/clusters/umap_embeddings.npy`
- `data/clusters/umap_coordinates.csv`
- `data/clusters/hdbscan_labels.csv`
- `data/clusters/intent_summary.csv`
- `report/cluster_statistics.json`
- `report/cluster_evaluation.json`
- `report/cluster_quality_report.md`
- `report/semantic_intent_summary.md`
- `assets/clustering/*.png`
- `assets/clustering/interactive_umap.html`

### Run Command
- Use the project virtual environment and run:
  `D:\AI\venvs\hiver-agent\Scripts\python.exe scripts/run_phase4.py`
- To regenerate artifacts use:
  `D:\AI\venvs\hiver-agent\Scripts\python.exe scripts/run_phase4.py --force`

### Validation
- The Phase 4 runner prints the final completion banner and exits successfully when the pipeline passes all artifact and shape checks.

## Phase 5 — Golden Intent Labeling

### Overview
The Phase 5 pipeline converts the unsupervised HDBSCAN clusters from Phase 4 into a production-ready canonical intent taxonomy and a high-quality golden intent dataset for downstream RAG and support automation.

### Taxonomy generation
- Builds a canonical customer support taxonomy with intent categories and cluster-to-intent mappings.
- Preserves cluster IDs and assigns each discovered cluster to exactly one intent.
- Stores the taxonomy in `data/intents/intent_taxonomy.json`.

### Golden intent dataset
- Creates `data/intents/golden_intents.csv` with normalized columns for intent labeling.
- Preserves multilingual conversation text and Unicode content.
- Ensures no missing or duplicate conversation records and validates confidence in the range 0–1.

### Validation and reporting
- Validates label coverage, confidence ranges, empty intents, and duplicate IDs.
- Exports `report/intent_validation.json` and `report/intent_validation_report.md`.
- Creates summary-level analytics for representative examples and intent distributions.

### Visualizations
The Phase 5 pipeline writes high-resolution PNG artifacts to `assets/intents/`:
- `intent_distribution.png`
- `intent_category_distribution.png`
- `intent_confidence_histogram.png`
- `top_10_intents.png`
- `language_vs_intent_heatmap.png`

### Execution
Run the Phase 5 pipeline with:
- `D:\AI\venvs\hiver-agent\Scripts\python.exe scripts/run_phase5.py`
- `D:\AI\venvs\hiver-agent\Scripts\python.exe scripts/run_phase5.py --force`

This phase is idempotent and safe to rerun without modifying earlier phases.

## Phase 6 — Retrieval Layer for RAG

### Overview
Phase 6 builds the semantic retrieval layer that powers the support chatbot. It reuses the validated Phase 5 golden intent dataset, creates a retrieval-ready knowledge base, encodes the documents with a SentenceTransformers model, stores a FAISS cosine index, generates evaluation queries, computes retrieval metrics, and writes production-quality assets for downstream use.

### Pipeline components
- Builds knowledge documents from the golden intent corpus and conversation metadata.
- Generates 384-dimensional normalized embeddings using the all-MiniLM-L6-v2 encoder.
- Persists a document catalog and embedding matrix in `data/knowledge_base/`.
- Creates a FAISS similarity index in `models/faiss/amazon_support.index`.
- Generates deterministic evaluation queries in `data/evaluation/retrieval_eval_queries.csv`.
- Computes retrieval metrics including Recall@1, Recall@3, Recall@5, MRR, Hit Rate, and average similarity.
- Writes markdown and JSON reports to `report/`.
- Produces charts in `assets/retrieval/` for intent, language, recall, and embedding distributions.

### Key outputs
- `data/knowledge_base/knowledge_documents.parquet`
- `data/knowledge_base/knowledge_documents.csv`
- `data/knowledge_base/knowledge_embeddings.npy`
- `data/knowledge_base/document_metadata.csv`
- `models/faiss/amazon_support.index`
- `models/faiss/index_metadata.json`
- `data/evaluation/retrieval_eval_queries.csv`
- `report/retrieval_metrics.json`
- `report/retrieval_evaluation.md`
- `assets/retrieval/*.png`

### Execution
Run the full pipeline with:
- `D:\AI\venvs\hiver-agent\Scripts\python.exe scripts/run_phase6.py`
- `D:\AI\venvs\hiver-agent\Scripts\python.exe scripts/run_phase6.py --force`

### Validation
The Phase 6 runner validates all required outputs and the retrieval API, then prints the completion banner:
- `# ======================================================`
- `PHASE 6 COMPLETED SUCCESSFULLY`

The retrieval API is exposed via `src/retrieval/retriever.py` and can be queried in a CLI demo using:
- `D:\AI\venvs\hiver-agent\Scripts\python.exe scripts/query_retriever.py`

This phase is fully reusable, deterministic, and safe to rerun without altering earlier project phases.

## Phase 8 — Production FastAPI Backend

### Overview
Phase 8 packages the Phase 7 retrieval-augmented chatbot into a production-style FastAPI backend. The API reuses the existing FAISS index, embeddings, intent taxonomy, and chatbot modules and exposes REST endpoints for integration with frontends or other services.

### Features
- FastAPI application with OpenAPI and ReDoc docs
- CORS enabled for cross-origin clients
- Endpoints: `/`, `/health`, `/intents`, `/chat`, `/reset`
- Reuses `SupportChatbot` from `src/chatbot/chatbot.py` and the Phase 6 retriever
- Pydantic request/response schemas and validation
- Singleton dependency injection to reuse model and index across requests
- Logging for startup, requests, retrieval latency, response latency, and errors
- Automated validation tests under `tests/`

### Run the API locally
Start a local development server with Uvicorn:

```powershell
D:\AI\venvs\hiver-agent\Scripts\python.exe scripts/run_api.py
```

### Run the Phase 8 validation suite
Run the automated API validation (non-persistent server):

```powershell
D:\AI\venvs\hiver-agent\Scripts\python.exe scripts/run_phase8.py
```

If all checks pass the runner prints:

# ======================================================
PHASE 8 COMPLETED SUCCESSFULLY

### API examples
See `report/api_examples.json` for simple request examples and `report/api_validation_report.md` for the validation summary.
