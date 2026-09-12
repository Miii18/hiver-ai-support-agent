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