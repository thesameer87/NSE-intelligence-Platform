# V2_IMPLEMENTATION_PLAN.md

# V2 Overview

## Purpose

Version 2 (V2) upgrades the existing V1 production trading intelligence platform into an AI-powered market intelligence system.

V2 adds:

* Computer Vision for chart pattern recognition
* Retrieval-Augmented Generation (RAG) for earnings/news intelligence
* Agentic reasoning for explainable signal validation
* AI Research Terminal UI
* Streaming AI insights

V2 must satisfy the following rule:

```text
AI augments, never blocks
```

Meaning:

If V2 fails:

```text
technical prediction survives
```

The V1 prediction engine remains operational.

---

## Design Principles

V2 implementation must be:

* production-grade
* modular
* async-first
* fault isolated
* observable
* rollback-safe
* testable
* scalable

Forbidden:

```text
TODO placeholders
blocking architecture
tight coupling with V1
hardcoded secrets
monolithic files
```

---

## V2 High-Level Architecture

```text
Live Market Data
        │
        ▼
Technical Prediction Engine (V1)
        │
        ├──────────────┐
        │              │
        ▼              ▼
CNN Worker         RAG Worker
(OpenCV/PyTorch)   (earnings/news)
        │              │
        └──────┬───────┘
               ▼
         Agent Reasoning
               │
               ▼
        AI Research Result
               │
               ▼
        WebSocket Streaming
               │
               ▼
      AI Research Terminal
```

---

# Task 26 — AI Research Module Scaffold

## Objective

Create a production-safe AI subsystem integrated into V1.

This task creates:

```text
backend/ai_research/
```

Purpose:

Provide a safe foundation for future V2 components.

No AI inference occurs in this task.

---

## Architecture Context

Current V1 flow:

```text
Market Feed
      ↓
Feature Engineering
      ↓
Prediction Engine
      ↓
Signal Engine
```

V2 insertion point:

```text
Prediction Engine
      │
      ├── CNN Worker
      ├── RAG Worker
      └── Agent Worker
```

Important:

V1 must remain untouched.

---

## Scope

Task 26 only includes:

* folder structure
* schemas
* orchestrator scaffold
* config system
* feature flags
* health checks
* logging

Not included:

```text
OpenCV
PyTorch
LangChain
RAG
```

---

## Files To Create

```text
backend/
└── ai_research/
    ├── __init__.py
    ├── config.py
    ├── schemas.py
    ├── service.py
    ├── orchestrator.py
    ├── exceptions.py
    ├── feature_flags.py
    ├── logger.py
    └── health.py
```

---

## Responsibilities

### config.py

Purpose:

AI-specific configuration.

Example responsibilities:

```text
timeouts
thresholds
feature toggles
environment settings
```

Environment flags:

```text
AI_ENABLED
CNN_ENABLED
RAG_ENABLED
AGENT_ENABLED
```

---

### schemas.py

Purpose:

Pydantic contracts.

Models:

```text
ResearchRequest
PatternResult
RAGResult
AgentResult
AIResearchResult
```

---

### service.py

Purpose:

Public entrypoint.

Expose:

```python
run_ai_research(symbol)
```

Used by:

```text
scheduler
signal engine
websocket
```

---

### orchestrator.py

Purpose:

Coordinate async workers.

Later responsibilities:

```text
CNN worker
RAG worker
Agent worker
```

Task 26:

Scaffold only.

---

### feature_flags.py

Purpose:

Safe production rollout.

Example:

```python
if not settings.AI_ENABLED:
    return None
```

---

### exceptions.py

Purpose:

Custom exceptions.

Examples:

```text
AIResearchError
CNNTimeoutError
RAGFailureError
AgentFailureError
```

---

### logger.py

Purpose:

Structured logging.

Example:

```json
{
  "event":"ai_research_started",
  "symbol":"RELIANCE"
}
```

---

### health.py

Purpose:

AI subsystem health.

Expose:

```text
cnn_available
rag_available
agent_available
ai_enabled
```

---

## Database Changes

None.

---

## API Changes

None.

---

## Environment Variables

```env
AI_ENABLED=true

CNN_ENABLED=false
RAG_ENABLED=false
AGENT_ENABLED=false

CNN_TIMEOUT_SEC=2
RAG_TIMEOUT_SEC=2
AGENT_TIMEOUT_SEC=3
```

---

## Acceptance Criteria

Task complete if:

* backend boots successfully
* V1 unaffected
* ai_research imports cleanly
* feature flags work
* logging works
* health checks work

---

## Testing Steps

Run:

```bash
uvicorn app.main:app --reload
```

Test:

```python
run_ai_research("RELIANCE")
```

Expected:

```json
{
  "status":"disabled"
}
```

---

## Failure Handling

If AI crashes:

```text
technical prediction survives
warning logged
```

---

# Task 27 — Chart Rendering Pipeline

## Objective

Create deterministic candlestick image generation.

Purpose:

Convert OHLCV stock data into normalized chart images for CNN processing.

Flow:

```text
OHLCV
   ↓
Chart Renderer
   ↓
Canonical Candlestick Image
```

---

## Scope

Included:

* candlestick rendering
* image normalization
* fixed dimensions
* reproducible output

Excluded:

```text
CNN inference
OpenCV preprocessing
```

---

## Files To Create

```text
backend/
└── ai_research/
    ├── chart_renderer.py
    ├── renderer_config.py
    └── renderer_tests.py
```

---

## Responsibilities

### chart_renderer.py

Generate:

```text
PNG candlestick chart
```

Input:

```text
OHLCV dataframe
```

Output:

```text
224x224 image
```

Requirements:

* fixed scale
* no axis labels
* no watermark
* deterministic layout

---

## Rendering Constraints

Chart must always use:

```text
same zoom
same spacing
same dimensions
same normalization
```

Reason:

```text
CNN consistency
```

---

## Storage

Temporary storage:

```text
storage/chart-images/
```

Retention:

```text
24 hours
```

---

## Acceptance Criteria

Task complete if:

* image generation deterministic
* consistent rendering
* identical inputs → identical output
* image size fixed

---

## Testing

Input:

```text
sample OHLCV
```

Expected:

```text
canonical chart image
```

---

# Task 28 — OpenCV Preprocessing Pipeline

## Objective

Normalize chart images for CNN inference.

Flow:

```text
chart image
      ↓
OpenCV preprocessing
      ↓
normalized tensor input
```

---

## Scope

Included:

* resize
* grayscale
* denoise
* edge enhancement
* normalization

Excluded:

```text
CNN inference
training
```

---

## Files To Create

```text
backend/
└── ai_research/
    ├── cv_preprocessing.py
    ├── preprocessing_config.py
    └── preprocessing_tests.py
```

---

## Processing Steps

Pipeline:

```text
load image
     ↓
resize(224x224)
     ↓
grayscale
     ↓
gaussian blur
     ↓
edge enhancement
     ↓
normalize
```

---

## Libraries

Required:

```text
opencv-python
numpy
torchvision
```

---

## Output

Expected:

```text
CNN-ready tensor
```

---

## Acceptance Criteria

Complete if:

* deterministic preprocessing
* output tensor normalized
* identical input → identical output
* preprocessing < 200ms

---

## Failure Handling

If preprocessing fails:

```text
skip CNN pipeline
log warning
continue V1
```

---
# Task 29 — CNN Training Pipeline

## Objective

Create a production-grade Computer Vision training system for stock chart pattern recognition.

Purpose:

Train a PyTorch CNN capable of identifying chart formations from deterministic candlestick images.

The model will later validate technical trading signals.

Goal:

```text
chart image
      ↓
CNN
      ↓
pattern classification
```

Supported patterns:

```text
Head & Shoulders
Double Bottom
Double Top
Breakout
Support/Resistance Break
Neutral
```

---

## Architecture Context

Pipeline:

```text
OHLCV
   ↓
Chart Renderer
(Task 27)
   ↓
OpenCV Preprocessing
(Task 28)
   ↓
Training Dataset
   ↓
PyTorch CNN
   ↓
Saved Production Model
```

Output:

```text
chart_pattern_cnn.pt
```

---

## Scope

Included:

* dataset preparation
* train/validation split
* transfer learning
* model training
* checkpointing
* metrics tracking
* export pipeline

Excluded:

```text
live inference
API integration
scheduler integration
```

---

## Files To Create

```text
backend/
├── ai_research/
│   ├── training/
│   │   ├── dataset_builder.py
│   │   ├── dataset_loader.py
│   │   ├── trainer.py
│   │   ├── metrics.py
│   │   ├── augmentation.py
│   │   └── config.py
│
├── scripts/
│   ├── train_chart_model.py
│   └── evaluate_chart_model.py
│
├── models/
│   └── chart_pattern_cnn.pt
│
└── tests/
    └── test_chart_training.py
```

---

## Model Selection

Framework:

```text
PyTorch
```

Selected architecture:

```text
ResNet18
```

Reason:

* lightweight
* CPU friendly
* production stable
* transfer-learning capable

---

## Training Strategy

Approach:

```text
transfer learning
```

Flow:

```text
Pretrained ResNet18
         │
remove classifier head
         │
replace final layer
         │
fine-tune on chart dataset
```

Final classes:

```text
head_shoulders
double_bottom
double_top
breakout
support_break
neutral
```

---

## Dataset Structure

Directory format:

```text
dataset/
├── train/
│   ├── head_shoulders/
│   ├── double_bottom/
│   ├── double_top/
│   ├── breakout/
│   ├── support_break/
│   └── neutral/
│
├── val/
└── test/
```

---

## Data Generation Strategy

Training data source:

```text
historical OHLCV
      ↓
chart renderer
      ↓
label assignment
      ↓
image dataset
```

Minimum recommended:

| Class          | Images |
| -------------- | -----: |
| head_shoulders |   2000 |
| double_bottom  |   2000 |
| double_top     |   2000 |
| breakout       |   2000 |
| support_break  |   2000 |
| neutral        |   5000 |

---

## Data Augmentation

Allowed augmentations:

```text
small scaling
brightness normalization
minor translation
```

Forbidden:

```text
rotation
random perspective
heavy distortion
```

Reason:

```text
preserve chart geometry
```

---

## Training Config

Defaults:

```text
epochs = 20
batch_size = 16
learning_rate = 0.0001
image_size = 224
optimizer = AdamW
loss = CrossEntropyLoss
```

Hardware assumption:

```text
CPU compatible
```

GPU optional.

---

## Metrics

Track:

```text
accuracy
precision
recall
f1 score
confusion matrix
```

Target:

| Metric    | Goal |
| --------- | ---: |
| accuracy  | >80% |
| precision | >80% |
| recall    | >75% |

---

## Model Saving

Saved path:

```text
backend/models/chart_pattern_cnn.pt
```

Metadata:

```json
{
  "version":"v1",
  "trained_at":"timestamp",
  "accuracy":0.84,
  "classes":[]
}
```

---

## Acceptance Criteria

Task complete if:

* model trains successfully
* checkpoint generated
* validation metrics produced
* export works
* inference-compatible file saved

---

## Testing Steps

Run:

```bash
python scripts/train_chart_model.py
```

Expected:

```text
epoch logs
metrics
model export
```

Verify:

```text
chart_pattern_cnn.pt exists
```

---

## Failure Handling

If training fails:

```text
preserve previous checkpoint
log failure
abort deployment
```

---

# Task 30 — CNN Inference Service

## Objective

Serve chart-pattern predictions in real time.

Purpose:

Validate technical signals using visual pattern recognition.

Flow:

```text
OHLCV
   ↓
Chart Renderer
   ↓
OpenCV Pipeline
   ↓
CNN Inference
   ↓
Pattern Result
```

---

## Scope

Included:

* model loading
* prediction
* confidence scoring
* caching
* timeout handling

Excluded:

```text
RAG
LangChain
```

---

## Files To Create

```text
backend/
└── ai_research/
    ├── cnn_inference.py
    ├── model_loader.py
    ├── inference_cache.py
    └── inference_tests.py
```

---

## Responsibilities

### model_loader.py

Purpose:

Load model safely.

Requirements:

```text
lazy loading
checksum validation
hot reload support
```

---

### cnn_inference.py

Expose:

```python
predict_pattern(symbol)
```

Output:

```json
{
  "pattern":"double_bottom",
  "confidence":0.88,
  "vision_score":0.72
}
```

---

## Timeout Strategy

Hard timeout:

```text
2 seconds
```

If exceeded:

```text
skip CNN
log warning
continue system
```

---

## Caching

Cache window:

```text
30 seconds
```

Reason:

```text
avoid duplicate inference
```

---

## Acceptance Criteria

Task complete if:

* model loads successfully
* inference <2 sec
* prediction returned
* timeout safe
* V1 unaffected

---

## Testing

Run:

```python
predict_pattern("RELIANCE")
```

Expected:

```json
{
  "pattern":"double_bottom",
  "confidence":0.88
}
```

---

## Failure Handling

If model unavailable:

```text
technical signal survives
cnn skipped
warning logged
```

---

# Task 31 — Chart Pattern Database Schema

## Objective

Persist vision results.

Purpose:

Store CNN detections for:

* auditability
* explainability
* analytics
* research history

---

## Database Changes

Create:

```text
chart_patterns
```

Schema:

| Column           | Type      |
| ---------------- | --------- |
| id               | UUID      |
| symbol           | TEXT      |
| pattern_name     | TEXT      |
| confidence       | FLOAT     |
| vision_score     | FLOAT     |
| chart_image_path | TEXT      |
| model_version    | TEXT      |
| created_at       | TIMESTAMP |

---

## Files To Create

```text
backend/
└── db/
    ├── migrations/
    │   └── create_chart_patterns.sql
    └── repositories/
        └── chart_pattern_repository.py
```

---

## Storage Strategy

Images stored:

```text
storage/chart-images/
```

Retention:

```text
7 days
```

---

## API Exposure

Future route:

```http
GET /v1/research/chart-patterns/{symbol}
```

---

## Acceptance Criteria

Complete if:

* migration runs
* inserts succeed
* retrieval works
* indexes present

---

## Failure Handling

If DB insert fails:

```text
continue inference
log error
do not crash system
```

---
# Task 32 — Earnings Document Ingestion

## Objective

Create a production-grade document ingestion pipeline for fundamental intelligence.

Purpose:

Automatically ingest earnings reports, management commentary, conference call transcripts, and financial news into the V2 intelligence system.

Goal:

```text
PDF / Text Documents
         ↓
Document Parsing
         ↓
Chunking
         ↓
Metadata Storage
         ↓
Embedding Pipeline
```

This becomes the foundation for:

```text
RAG intelligence
fundamental validation
AI reasoning
```

---

## Architecture Context

Pipeline:

```text
earnings PDF
conference transcript
financial news
         │
         ▼
document ingestion
         │
         ▼
clean text extraction
         │
         ▼
document chunking
         │
         ▼
embedding pipeline
         │
         ▼
pgvector retrieval
```

Later integration:

```text
technical signal
      +
vision signal
      +
retrieved fundamentals
      ↓
agent reasoning
```

---

## Scope

Included:

* PDF ingestion
* text ingestion
* metadata extraction
* chunk generation
* ingestion scheduler
* document persistence

Excluded:

```text
embeddings
retrieval
LLM reasoning
```

---

## Supported Sources

V2 supports:

| Source             | Example                |
| ------------------ | ---------------------- |
| Earnings PDFs      | quarterly reports      |
| Annual reports     | disclosures            |
| Earnings summaries | news articles          |
| Conference calls   | management transcripts |
| Internal notes     | analyst comments       |

---

## Files To Create

```text
backend/
└── ai_research/
    ├── ingestion/
    │   ├── document_loader.py
    │   ├── pdf_parser.py
    │   ├── text_cleaner.py
    │   ├── chunker.py
    │   ├── metadata_extractor.py
    │   ├── ingestion_scheduler.py
    │   ├── ingestion_service.py
    │   └── ingestion_config.py
```

---

## Responsibilities

### document_loader.py

Purpose:

Load source documents.

Supports:

```text
pdf
txt
html
json
```

Responsibilities:

```text
file loading
validation
mime checks
error handling
```

---

### pdf_parser.py

Purpose:

Extract readable text.

Requirements:

```text
preserve semantic order
ignore visual noise
handle large PDFs
```

Output:

```text
clean plain text
```

---

### text_cleaner.py

Purpose:

Normalize extracted content.

Tasks:

```text
remove duplicate whitespace
remove page headers
remove repeated footers
normalize encoding
remove junk text
```

---

### chunker.py

Purpose:

Split documents into semantic chunks.

Defaults:

```text
chunk_size = 512–1024 tokens
overlap = 100 tokens
```

Reason:

```text
semantic continuity
```

---

### metadata_extractor.py

Extract:

```text
company symbol
document type
published_at
source
title
quarter
```

Example:

```json
{
  "symbol":"RELIANCE",
  "quarter":"Q4",
  "source":"earnings_pdf"
}
```

---

### ingestion_scheduler.py

Purpose:

Periodic ingestion.

Schedule:

```text
daily
market-close
manual trigger
```

---

### ingestion_service.py

Expose:

```python
ingest_document(filepath)
```

Returns:

```json
{
  "status":"success",
  "chunks_created":57
}
```

---

## Database Changes

Create:

```text
earnings_documents
```

Schema:

| Column       | Type      |
| ------------ | --------- |
| id           | UUID      |
| symbol       | TEXT      |
| title        | TEXT      |
| source       | TEXT      |
| quarter      | TEXT      |
| published_at | TIMESTAMP |
| raw_text     | TEXT      |
| created_at   | TIMESTAMP |

---

Create:

```text
document_chunks
```

Schema:

| Column      | Type      |
| ----------- | --------- |
| id          | UUID      |
| document_id | UUID      |
| chunk_text  | TEXT      |
| chunk_index | INT       |
| token_count | INT       |
| created_at  | TIMESTAMP |

---

## Storage

Raw files:

```text
storage/earnings-pdfs/
```

Retention:

```text
indefinite
```

Reason:

```text
auditability
retraining
re-indexing
```

---

## Acceptance Criteria

Task complete if:

* PDFs parsed
* metadata extracted
* chunking works
* DB inserts work
* ingestion scheduler functional

---

## Testing

Run:

```python
ingest_document("reliance_q4.pdf")
```

Expected:

```json
{
  "status":"success",
  "chunks_created":57
}
```

---

## Failure Handling

If parsing fails:

```text
mark ingestion failed
log error
continue system
```

Never crash V1.

---

# Task 33 — pgvector + Embedding Pipeline

## Objective

Convert chunked documents into vector embeddings for semantic retrieval.

Goal:

```text
text chunk
      ↓
embedding model
      ↓
vector
      ↓
pgvector storage
```

Purpose:

Enable:

```text
semantic search
context retrieval
earnings intelligence
```

---

## Scope

Included:

* embedding generation
* pgvector storage
* indexing
* similarity search
* batch embedding

Excluded:

```text
retrieval reasoning
agent decisions
```

---

## Files To Create

```text
backend/
└── ai_research/
    ├── embeddings/
    │   ├── embedder.py
    │   ├── vector_store.py
    │   ├── indexing_service.py
    │   ├── similarity_search.py
    │   └── config.py
```

---

## Embedding Strategy

Recommended:

```text
sentence-transformers
```

Optional:

```text
OpenAI embeddings
```

Preferred for student build:

```text
free local embeddings
```

Reason:

```text
zero recurring cost
```

---

## Embedding Flow

```text
chunk text
     ↓
embedding model
     ↓
768-d vector
     ↓
pgvector table
```

---

## Database Changes

Enable:

```sql
CREATE EXTENSION vector;
```

Create:

```text
earnings_chunks
```

Schema:

| Column      | Type        |
| ----------- | ----------- |
| id          | UUID        |
| document_id | UUID        |
| chunk_text  | TEXT        |
| embedding   | VECTOR(768) |
| metadata    | JSONB       |
| created_at  | TIMESTAMP   |

---

## Similarity Search

Example query:

```sql
SELECT *
FROM earnings_chunks
ORDER BY embedding <=> :query_embedding
LIMIT 5;
```

Purpose:

```text
top-k semantic retrieval
```

---

## Performance Targets

| Metric            |   Goal |
| ----------------- | -----: |
| embedding latency | <300ms |
| retrieval latency | <500ms |
| batch indexing    |  async |

---

## Acceptance Criteria

Complete if:

* embeddings generated
* pgvector populated
* similarity search works
* indexing async

---

## Testing

Input:

```text
Did RELIANCE report weak guidance?
```

Expected:

```text
top 5 relevant chunks
```

---

## Failure Handling

If embeddings fail:

```text
retry
log error
skip document
continue platform
```

---

# Task 34 — RAG Retrieval Service

## Objective

Create a production-grade Retrieval-Augmented Generation service.

Purpose:

Retrieve relevant earnings/news context to validate technical signals.

Goal:

```text
technical signal
      ↓
semantic retrieval
      ↓
context evidence
      ↓
agent reasoning
```

---

## Scope

Included:

* query generation
* vector retrieval
* ranking
* confidence scoring
* timeout handling

Excluded:

```text
LLM reasoning
agent orchestration
```

---

## Files To Create

```text
backend/
└── ai_research/
    ├── rag/
    │   ├── retrieval_service.py
    │   ├── query_builder.py
    │   ├── ranking.py
    │   ├── confidence.py
    │   └── rag_config.py
```

---

## Retrieval Flow

Example:

Signal:

```text
RELIANCE → bullish
```

Generated query:

```text
Did RELIANCE recently report weak earnings,
management changes,
guidance downgrade,
negative commentary?
```

Pipeline:

```text
query
   ↓
embedding
   ↓
pgvector search
   ↓
top-k retrieval
   ↓
ranked evidence
```

---

## Timeout Strategy

Hard timeout:

```text
2 seconds
```

If timeout occurs:

```text
skip RAG
continue V1
warning logged
```

---

## Output Contract

Expected:

```json
{
  "sentiment":"positive",
  "confidence":0.82,
  "evidence":[]
}
```

---

## Acceptance Criteria

Complete if:

* retrieval <2 sec
* evidence returned
* ranking works
* timeout safe

---

## Testing

Input:

```text
RELIANCE bullish signal
```

Expected:

```text
relevant earnings evidence
```

---

## Failure Handling

If retrieval fails:

```text
technical signal survives
warning logged
RAG skipped
```

---
# Task 35 — Agentic AI Reasoning Engine

## Objective

Create an explainable reasoning layer that combines:

* technical prediction (V1)
* computer vision (CNN)
* retrieved earnings/news evidence (RAG)

Purpose:

Generate:

```text
human-readable trading intelligence
```

instead of:

```text
black-box prediction
```

Goal:

```text
technical signal
      +
vision signal
      +
retrieved evidence
      ↓
agent reasoning
      ↓
final explainable verdict
```

---

## Architecture Context

Current V2 pipeline:

```text
Technical Prediction
        │
        ├── CNN Worker
        └── RAG Worker
```

Task 35 adds:

```text
Technical Prediction
        │
        ├── CNN Result
        ├── RAG Result
        │
        ▼
Agent Reasoning Engine
        │
        ▼
Explainable Trading Verdict
```

---

## Scope

Included:

* reasoning generation
* confidence reconciliation
* verdict generation
* evidence validation
* explainability

Excluded:

```text
trade execution
broker integration
autonomous trading
```

Important rule:

```text
decision support only
```

---

## LLM Provider Strategy

Preferred:

```text
Groq
OpenRouter
```

Reason:

```text
free / low cost
OpenAI-compatible
fast inference
```

Fallback:

```text
OpenAI
```

Optional:

```text
Ollama local model
```

---

## Files To Create

```text
backend/
└── ai_research/
    ├── agent/
    │   ├── reasoning_engine.py
    │   ├── prompt_builder.py
    │   ├── confidence_reconciliation.py
    │   ├── llm_client.py
    │   ├── output_parser.py
    │   ├── safety.py
    │   └── config.py
```

---

## Responsibilities

### reasoning_engine.py

Purpose:

Primary orchestration.

Expose:

```python
generate_reasoning(
    technical_signal,
    cnn_result,
    rag_result
)
```

Returns:

```json
{
  "final_signal":"bullish",
  "confidence":0.91,
  "reasoning":[]
}
```

---

### prompt_builder.py

Purpose:

Build structured reasoning prompts.

Example input:

```json
{
  "technical_signal":"bullish",
  "confidence":0.84,
  "pattern":"double_bottom",
  "earnings_sentiment":"positive"
}
```

Prompt goal:

```text
explain reasoning
validate signal
adjust confidence
```

---

### confidence_reconciliation.py

Purpose:

Combine confidence values.

Example:

| Source    | Confidence |
| --------- | ---------: |
| technical |       0.84 |
| CNN       |       0.88 |
| RAG       |       0.82 |

Output:

```text
final confidence
```

Requirements:

```text
deterministic
weighted
auditable
```

No hidden magic.

---

### llm_client.py

Purpose:

Provider abstraction.

Supported:

```text
Groq
OpenRouter
OpenAI
Ollama
```

Requirement:

```text
provider swappable
```

Meaning:

```text
minimal refactor required
```

---

### output_parser.py

Purpose:

Normalize LLM output.

Output contract:

```json
{
  "final_signal":"bullish",
  "confidence":0.91,
  "reasoning":[
    "Double bottom detected",
    "Positive earnings guidance"
  ],
  "risk_notes":[]
}
```

---

### safety.py

Purpose:

Guardrails.

Forbidden outputs:

```text
BUY NOW!!!
SELL EVERYTHING!!!
financial guarantees
```

Allowed:

```text
confidence-based decision support
```

---

## Agent Reasoning Rules

Agent must:

* explain reasoning
* cite retrieved evidence
* reconcile confidence
* mention uncertainty

Agent must NOT:

```text
guarantee profit
execute trades
hallucinate unsupported claims
```

---

## Timeout Strategy

Hard timeout:

```text
3 seconds
```

If timeout occurs:

Fallback:

```json
{
  "status":"agent_skipped",
  "reason":"timeout"
}
```

System continues.

---

## Output Example

Example:

```json
{
  "symbol":"RELIANCE",
  "final_signal":"bullish",
  "confidence":0.91,
  "reasoning":[
    "Momentum indicators aligned",
    "Double Bottom pattern detected",
    "Positive earnings guidance found"
  ]
}
```

---

## Acceptance Criteria

Complete if:

* reasoning generated
* confidence reconciled
* timeout safe
* provider swappable
* output deterministic

---

## Testing

Input:

```text
technical = bullish
cnn = double_bottom
rag = positive guidance
```

Expected:

```text
explainable verdict generated
```

---

## Failure Handling

If LLM fails:

```text
skip agent
continue system
log warning
```

Technical prediction survives.

---

# Task 36 — AI Research Session Persistence

## Objective

Persist AI reasoning history.

Purpose:

Store:

* reasoning history
* confidence changes
* retrieved evidence
* CNN detections
* audit trail

Goal:

```text
AI session
      ↓
database persistence
      ↓
historical explainability
```

---

## Scope

Included:

* session persistence
* auditability
* research history
* replay support

Excluded:

```text
analytics dashboards
```

---

## Database Changes

Create:

```text
research_sessions
```

Schema:

| Column               | Type      |
| -------------------- | --------- |
| id                   | UUID      |
| symbol               | TEXT      |
| technical_confidence | FLOAT     |
| cnn_confidence       | FLOAT     |
| rag_confidence       | FLOAT     |
| final_confidence     | FLOAT     |
| final_signal         | TEXT      |
| reasoning            | JSONB     |
| created_at           | TIMESTAMP |

---

Create:

```text
research_evidence
```

Schema:

| Column        | Type  |
| ------------- | ----- |
| id            | UUID  |
| session_id    | UUID  |
| evidence_text | TEXT  |
| source        | TEXT  |
| score         | FLOAT |

---

## Files To Create

```text
backend/
├── db/
│   ├── repositories/
│   │   ├── research_repository.py
│   │   └── evidence_repository.py
│
└── ai_research/
    └── persistence/
        ├── persistence_service.py
        └── session_serializer.py
```

---

## API Changes

Add:

```http
GET /v1/research/{symbol}
```

Response:

```json
{
  "final_signal":"bullish",
  "confidence":0.91,
  "reasoning":[]
}
```

---

## Acceptance Criteria

Complete if:

* session persisted
* retrieval works
* history query works
* inserts async

---

## Testing

Verify:

```text
research session saved
```

Query:

```http
GET /v1/research/RELIANCE
```

Expected:

```text
stored reasoning returned
```

---

## Failure Handling

If DB insert fails:

```text
log warning
continue system
```

No blocking.

---

# Task 37 — AI Research Terminal UI

## Objective

Create a dedicated frontend tab for AI-powered market intelligence.

Purpose:

Surface explainable trading insights.

New navigation:

```text
Dashboard
Portfolio
Signals
AI Research Terminal
```

---

## Scope

Included:

* research page
* live AI thoughts
* confidence breakdown
* reasoning panel
* evidence viewer

Excluded:

```text
trade execution
```

---

## Files To Create

```text
frontend/
└── src/
    ├── pages/
    │   └── AIResearchTerminal.tsx
    │
    └── components/
        └── ai_terminal/
            ├── ResearchPanel.tsx
            ├── PatternCard.tsx
            ├── EarningsSummary.tsx
            ├── AgentThoughts.tsx
            ├── ConfidenceBreakdown.tsx
            ├── EvidencePanel.tsx
            └── ResearchHistory.tsx
```

---

## UI Sections

### Pattern Card

Displays:

```text
pattern detected
confidence
chart preview
```

Example:

```text
Double Bottom
88%
```

---

### Earnings Summary

Displays:

```text
retrieved earnings context
sentiment
important notes
```

---

### Agent Thoughts

Displays:

```text
reasoning steps
confidence explanation
risk notes
```

---

### Confidence Breakdown

Visualize:

| Source    | Confidence |
| --------- | ---------: |
| technical |       0.84 |
| cnn       |       0.88 |
| rag       |       0.82 |
| final     |       0.91 |

---

### Research History

Displays:

```text
previous AI sessions
```

---

## Streaming

Use:

```text
WebSocket
```

Endpoint:

```text
/ws/stream
```

Payload:

```json
{
  "technical_prediction":{},
  "vision_analysis":{},
  "rag_context":{},
  "agent_reasoning":{}
}
```

---

## Acceptance Criteria

Complete if:

* page renders
* websocket updates live
* confidence visible
* reasoning visible
* responsive UI works

---

## Failure Handling

If websocket fails:

```text
fallback REST polling
```

---
# Task 38 — Real-Time AI Streaming Integration

## Objective

Integrate V2 AI outputs into the existing V1 streaming architecture.

Purpose:

Deliver:

```text
live explainable intelligence
```

to the dashboard in real time.

Goal:

```text
technical prediction
        +
cnn analysis
        +
rag evidence
        +
agent reasoning
        ↓
real-time websocket stream
        ↓
AI Research Terminal
```

Important rule:

```text
streaming must never block V1
```

---

## Architecture Context

Current V1 flow:

```text
prediction engine
       ↓
signal engine
       ↓
websocket stream
```

V2 upgraded flow:

```text
prediction engine
       │
       ├── CNN worker
       ├── RAG worker
       └── Agent worker
               │
               ▼
       AI research result
               │
               ▼
       websocket broadcaster
               │
               ▼
       frontend subscribers
```

---

## Scope

Included:

* websocket payload upgrade
* async worker integration
* live AI updates
* streaming orchestration
* retry handling
* timeout handling

Excluded:

```text
trade execution
broker automation
```

---

## Files To Create

```text
backend/
├── websocket/
│   ├── ai_stream.py
│   ├── stream_serializer.py
│   └── websocket_events.py
│
└── ai_research/
    └── streaming/
        ├── stream_service.py
        ├── broadcaster.py
        └── event_schema.py
```

---

## Streaming Strategy

Architecture:

```text
single producer
multiple subscribers
```

Meaning:

One backend calculation:

```text
RELIANCE prediction
```

is broadcast to:

```text
all connected clients
```

without duplicate compute.

---

## Async Worker Strategy

Execution model:

```text
technical prediction
      │
      ├── asyncio.create_task(cnn_worker)
      ├── asyncio.create_task(rag_worker)
      └── asyncio.create_task(agent_worker)
```

Requirements:

```text
fully async
non-blocking
timeout-safe
```

---

## WebSocket Payload Upgrade

Current V1:

```json
{
  "symbol":"RELIANCE",
  "signal":"bullish",
  "confidence":0.84
}
```

V2:

```json
{
  "symbol":"RELIANCE",
  "technical_prediction":{
    "signal":"bullish",
    "confidence":0.84
  },
  "vision_analysis":{
    "pattern":"double_bottom",
    "confidence":0.88
  },
  "rag_context":{
    "sentiment":"positive",
    "confidence":0.82
  },
  "agent_reasoning":{
    "final_signal":"bullish",
    "confidence":0.91,
    "reasoning":[
      "Double Bottom detected",
      "Positive earnings guidance"
    ]
  }
}
```

---

## Event Types

Supported:

```text
prediction_update
cnn_update
rag_update
research_update
health_update
```

Purpose:

Incremental streaming.

Meaning:

UI updates progressively.

Example:

```text
technical signal arrives
↓
cnn arrives
↓
rag arrives
↓
agent verdict arrives
```

No waiting.

---

## Timeout Strategy

Maximum timeout:

| Worker | Timeout |
| ------ | ------: |
| CNN    |   2 sec |
| RAG    |   2 sec |
| Agent  |   3 sec |

If exceeded:

```text
worker skipped
warning logged
stream continues
```

---

## Retry Strategy

Retries:

```text
max_retries = 2
```

Backoff:

```text
exponential
```

Reason:

```text
avoid websocket instability
```

---

## Acceptance Criteria

Complete if:

* websocket streams AI updates
* incremental updates work
* timeouts safe
* reconnect works
* V1 unaffected

---

## Testing

Connect client.

Expected sequence:

```text
technical prediction
cnn result
rag result
agent reasoning
```

Streaming must remain live.

---

## Failure Handling

If websocket crashes:

Fallback:

```text
REST polling
```

If AI fails:

```text
technical prediction survives
```

---

# Task 39 — AI Observability & Monitoring

## Objective

Create production-grade observability for V2 AI systems.

Purpose:

Track:

```text
latency
availability
errors
health
accuracy drift
```

Goal:

```text
production visibility
```

---

## Scope

Included:

* structured logging
* metrics
* health endpoints
* tracing
* error reporting
* alerting

Excluded:

```text
external SOC tooling
```

---

## Files To Create

```text
backend/
├── monitoring/
│   ├── ai_metrics.py
│   ├── ai_health.py
│   ├── ai_logging.py
│   ├── tracing.py
│   └── alerting.py
```

---

## Structured Logging

Format:

```json
{
  "timestamp":"...",
  "event":"cnn_prediction",
  "symbol":"RELIANCE",
  "latency_ms":134,
  "confidence":0.88
}
```

Required logs:

```text
cnn inference
rag retrieval
agent reasoning
timeouts
retries
stream failures
```

---

## Metrics

Expose:

```text
cnn_latency
rag_latency
agent_latency
research_failures
websocket_connections
stream_failures
retrieval_time
prediction_rate
```

---

## Monitoring Stack

Recommended:

Prometheus

Optional visualization:

Grafana

---

## Error Tracking

Recommended:

Sentry

Track:

```text
exceptions
timeout spikes
deployment failures
inference crashes
```

---

## Health Endpoints

Add:

```http
GET /health/ai
GET /metrics/ai
```

Response:

```json
{
  "cnn_available":true,
  "rag_available":true,
  "agent_available":true
}
```

---

## Alerting Rules

Triggers:

```text
cnn latency > 2 sec
rag timeout spike
agent timeout spike
websocket disconnect rate high
research failure > threshold
```

---

## Acceptance Criteria

Complete if:

* metrics exposed
* logs structured
* health route works
* sentry connected
* alerts configured

---

## Failure Handling

If monitoring fails:

```text
core platform continues
```

Monitoring never blocks system.

---

# Task 40 — Production Hardening & Rollback

## Objective

Make V2 production-safe.

Purpose:

Guarantee:

```text
AI failure never kills platform
```

Goal:

```text
zero downtime
rollback-safe
fault isolated
```

---

## Scope

Included:

* feature flags
* rollback
* circuit breakers
* retries
* graceful degradation
* hot reload
* timeout enforcement

Excluded:

```text
auto trade execution
```

---

## Files To Create

```text
backend/
├── ai_research/
│   ├── resilience/
│   │   ├── circuit_breaker.py
│   │   ├── retry_manager.py
│   │   ├── timeout_manager.py
│   │   ├── degradation.py
│   │   └── rollback_manager.py
```

---

## Feature Flags

Required:

```env
AI_ENABLED=true

CNN_ENABLED=true
RAG_ENABLED=true
AGENT_ENABLED=true
```

Emergency disable:

```env
AI_ENABLED=false
```

Behavior:

```text
V2 disabled instantly
V1 survives
```

---

## Circuit Breaker Strategy

If failures exceed threshold:

```text
disable subsystem
```

Example:

```text
CNN failing repeatedly
```

Result:

```text
cnn disabled
technical system continues
```

---

## Retry Strategy

Retries:

```text
2 attempts
```

Backoff:

```text
exponential
```

Never infinite retries.

---

## Graceful Degradation

If:

```text
CNN fails
```

System becomes:

```text
technical + RAG only
```

If:

```text
RAG fails
```

System becomes:

```text
technical + CNN only
```

If:

```text
Agent fails
```

System becomes:

```text
technical prediction only
```

---

## Model Rollback

Flow:

```text
new model deployed
      │
validation fails
      ▼
restore stable model
```

Requirements:

```text
atomic swap
checksum validation
health verification
```

---

## Hot Reloading

Flow:

```text
download model
validate checksum
load in memory
atomic swap
```

No downtime.

---

## Acceptance Criteria

Complete if:

* rollback works
* feature flags work
* circuit breaker works
* timeouts enforced
* graceful degradation works
* V1 survives failures

---

## Final V2 Deliverable

At completion:

Platform supports:

```text
technical prediction
computer vision
RAG intelligence
agentic reasoning
AI research terminal
real-time streaming
production observability
rollback-safe deployment
```

Result:

```text
production-grade AI-powered stock market intelligence platform
```

---

# End of V2_IMPLEMENTATION_PLAN.md

## Final Outcome

After Task 40:

```text
V1 = implementation-ready
V2 = implementation-ready
```

Combined system:

```text
production-grade
AI-powered
explainable
real-time
fault-isolated
NSE intelligence platform
```
