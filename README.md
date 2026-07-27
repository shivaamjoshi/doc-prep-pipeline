# Document Ingestion & Preparation Pipeline (`doc-prep-pipeline`)

A lightweight, production-style document preprocessing pipeline that ingests raw PDF documents and transforms them into clean, structured, retrieval-ready text chunks. This repository represents Checkpoint 1 of a broader personal roadmap focused on AI-native data engineering and retrieval-augmented generation (RAG) infrastructure.

---

## Author Context & Engineering Rationale

Built by a data engineer with production experience designing data pipelines with Databricks, Delta Lake, and Delta Live Tables (DLT) data-quality patterns. 

Traditional ETL pipelines enforce quality standards on structured tabular data using expectations, validation checks, and quarantine routing. This project applies that exact production data-quality discipline to unstructured document processing before text reaches downstream embedding models or vector databases.

The evaluation corpus currently consists of technical documentation PDFs for Delta Lake and Unity Catalog—chosen specifically because prior familiarity with these subjects enables fast manual verification of extraction and chunking quality.

---

## Problem Statement: The Diluted Embedding Problem

In RAG systems, vector search quality depends directly on chunk quality:
* **Raw Document Noise:** Unstructured PDFs contain headers, footers, mangled tables of contents, page numbers, and empty image placeholders. Feeding raw extraction output directly to embedding models pollutes vector index space with low-signal noise.
* **Semantic Dilution & Boundary Splitting:** Large, unsegmented text blocks dilute dense embedding representations by packing multiple unrelated topics into one vector. Conversely, rigid chunk boundaries cut mid-sentence, splitting context across boundaries.

A dedicated document preparation pipeline acts as an upstream data-cleaning and transformation stage, ensuring high vector precision and context fidelity downstream.

---

## Project Roadmap & Current Status

* **Week 1 (Current State):** Raw PDF partitioning, table noise filtering heuristic, naive sliding-window chunking baseline, and JSON output generation.
* **Week 2 (Planned):** Structure-aware (heading-hierarchical) chunking and comparative analysis against fixed-size sliding-window chunking.
* **Week 3 (Planned):** Quality validation using Pandera schema checks and automated quarantine routing (`data/quarantine/`).

---

## Implementation Breakdown (Week 1)

1. **Extraction (`src/parse.py`):** Uses the `unstructured` library (`hi_res` partitioning strategy) to extract layout elements from PDFs into dictionary representations containing `text`, `category` (e.g., `Title`, `NarrativeText`, `Table`), `page`, and `source`. Extraction is kept pure (Bronze-layer raw ingestion).
2. **Noise Filtering (`src/pipeline.py`):** 
   * `is_low_signal_table()`: Applies a word-level heuristic measuring the ratio of purely numeric words in extracted tables. Mangled tables-of-contents (where OCR/extraction collates page numbers and headers into a single string) are filtered out, while real content tables (such as glossaries) are retained.
   * Filters out near-empty elements (`< 3` words) to remove stray OCR artifacts.
3. **Naive Fixed-Size Chunking (`src/chunk.py`):** `fixed_size_chunk()` implements a word-based sliding window with configurable chunk size and overlap (e.g., 200 words, 40 word overlap) to preserve context continuity across chunk boundaries.
4. **Pipeline Orchestration (`src/pipeline.py`):** `process_document()` and `run_pipeline()` connect parsing, filtering, chunking, and write output records to `data/processed/chunks.json`.

---

## Repository Structure

```
doc-prep-pipeline/
├── data/
│   ├── raw/          # Input raw PDF documents
│   ├── processed/    # Output clean chunk JSON datasets
│   └── quarantine/   # Isolated bad or failed elements (Week 3)
├── reports/          # Pipeline evaluation and benchmark reports
├── src/
│   ├── __init__.py
│   ├── parse.py      # PDF element partitioning via unstructured
│   ├── chunk.py      # Sliding-window chunking logic
│   ├── pipeline.py   # Filtering heuristics and pipeline runner
│   ├── dedupe.py     # (Plannned deduplication module)
│   ├── enrich.py     # (Planned metadata enrichment module)
│   ├── ingest.py     # (Planned source ingestion handlers)
│   └── quality.py    # (Planned quality & validation checks)
├── requirements.txt  # Python dependency specifications
└── README.md
```

---

## Known Limitations & Empirical Benchmark

### Limitations
* **Heuristic Table Filtering:** The numeric-word ratio filter is a basic heuristic, not a full structural table parser. Complex tabular layouts may occasionally bypass filtering or be false-positively dropped.
* **Naive Chunking Baseline:** The current implementation uses word-count sliding windows without awareness of document section boundaries or heading hierarchies.
* **Small Evaluation Dataset:** Tested on a small benchmark set of 3 technical documentation PDFs rather than a large enterprise corpus.

### Benchmark Results (Latest Run)
* **Documents Processed:** 3 PDFs
* **Total Chunks Generated:** 263 chunks
* **Chunk Word Count Range:** 3 to 200 words per chunk
* **Average Chunk Size:** ~29 words per chunk

---

## Setup & Running

### System Dependencies
PDF extraction via `unstructured` requires system libraries for rendering and OCR:

```bash
# Ubuntu / Debian
sudo apt-get update && sudo apt-get install -y \
  poppler-utils \
  tesseract-ocr \
  libmagic1
```

### Python Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Execution

Place raw PDF documents into `data/raw/` and execute the pipeline:

```bash
python3 -m src.pipeline
```

The processed chunks will be output to `data/processed/chunks.json`.
