# NSE Intelligence Platform — System Design Document

**Version:** 2.0 — Production Grade AI Intelligence Architecture
**Status:** Client Deliverable
**Date:** 2026-06-01
**Prepared For:** Professional Trading Intelligence Platform Deployment

---

# Table of Contents

1. Executive Summary
2. System Overview
3. Architecture Overview
4. High-Level Data Flow
5. Infrastructure & Deployment
6. Core Trading Intelligence Engine
7. AI Research Terminal Architecture
8. Computer Vision & Chart Pattern Recognition Pipeline
9. Agentic RAG (Earnings + News Intelligence)
10. Real-Time Streaming & Async Orchestration
11. Backend Architecture
12. Frontend Architecture
13. Database Architecture
14. API Architecture
15. Security Design
16. Observability & Monitoring
17. CI/CD + Model Retraining + Rollback
18. Memory Budget & Scaling
19. Technical Safeguards
20. Disaster Recovery
21. Complete File Structure

---

# 1. Executive Summary

The **NSE Intelligence Platform** is a production-grade, AI-powered stock market intelligence platform designed for professional trading firms and quantitative research teams operating in Indian financial markets.

The platform continuously monitors **all Nifty 50 stocks**, processes live market data streams, computes technical indicators, performs machine learning–based forecasting, executes AI-assisted research, validates trading opportunities using retrieval-augmented reasoning, and presents actionable intelligence through a Bloomberg-style dashboard.

Unlike conventional trading dashboards, this platform combines:

* Quantitative trading intelligence
* Machine learning prediction systems
* Computer vision for chart pattern recognition
* Retrieval-Augmented Generation (RAG)
* Agentic AI reasoning systems
* Real-time streaming inference
* Explainable AI trading validation

The result is a multi-layer intelligence system capable of producing:

1. **Technical Predictions**
   Intraday and next-day directional forecasts using engineered features and LightGBM models.

2. **Visual Chart Intelligence**
   Detection of classical technical chart patterns using PyTorch CNNs and OpenCV preprocessing.

3. **Fundamental Context Intelligence**
   Earnings reports, financial disclosures, and transcript retrieval via vector search.

4. **Agentic Trading Validation**
   Autonomous reasoning agents that validate signals using multimodal evidence before surfacing recommendations.

---

## Business Objectives

The system is designed to provide:

| Objective                     | Description                                   |
| ----------------------------- | --------------------------------------------- |
| Real-time market intelligence | Continuous monitoring of 50 NSE stocks        |
| Predictive analytics          | ML-based direction and target prediction      |
| Reduced false positives       | Multi-stage signal validation                 |
| Explainability                | Human-readable AI reasoning                   |
| Research augmentation         | Earnings and management context retrieval     |
| Zero-cost cloud operation     | Operates entirely on free-tier infrastructure |
| Production reliability        | Safe rollback, monitoring, observability      |

---

## What This Platform Delivers

| Capability            | Description                                      |
| --------------------- | ------------------------------------------------ |
| Live Market Feed      | Real-time Nifty 50 monitoring                    |
| Technical Indicators  | RSI, MACD, ATR, VWAP, EMA, OBI, ROC, BB and more |
| AI Predictions        | Intraday and next-day forecasting                |
| Computer Vision       | CNN-based chart pattern recognition              |
| RAG Intelligence      | Earnings/news contextual validation              |
| Agentic AI            | Autonomous reasoning for signal verification     |
| Portfolio Tracking    | Holdings, exposure, P&L                          |
| Real-Time Dashboard   | Bloomberg-style streaming UI                     |
| Explainable Decisions | Confidence breakdown and reasoning chain         |

---

## Key Differentiation

Traditional trading platforms provide indicators.

This platform provides **intelligence**.

### Conventional Trading Platform

```text
Price Data
   ↓
Indicators
   ↓
Trader decides manually
```

### NSE Intelligence Platform

```text
Price Data
   ↓
Technical Feature Engine
   ↓
ML Forecasting Layer
   ↓
Computer Vision Pattern Detection
   ↓
RAG-Based Fundamental Validation
   ↓
Agentic Reasoning Engine
   ↓
Confidence Reconciliation
   ↓
Final Explainable Signal
```

---

# 2. System Overview

## Market Coverage

| Parameter            | Value                                  |
| -------------------- | -------------------------------------- |
| Exchange             | NSE (National Stock Exchange of India) |
| Universe             | Nifty 50                               |
| Trading Window       | 9:15 AM – 3:30 PM IST                  |
| Historical Retention | 365 days                               |
| Intraday Retention   | Rolling 7 days                         |
| Processing Cycle     | Every 30 seconds                       |

---

## Core System Philosophy

The platform is built around a **multi-layer intelligence pipeline**.

Each trading signal passes through multiple independent validation systems before being surfaced to users.

### Layer 1 — Technical Intelligence

Mathematical feature engineering:

* RSI
* MACD
* EMA
* ATR
* Bollinger Bands
* VWAP deviation
* Order Book Imbalance
* Buy/Sell ratio
* Spread statistics
* Volume ratios

Output:

```json
{
  "technical_signal": "Bullish",
  "confidence": 0.81,
  "target_price": 2874.21
}
```

---

### Layer 2 — Visual Intelligence

A generated candlestick image is analyzed using:

* OpenCV preprocessing
* CNN inference
* Transfer learning via ResNet18

Recognized setups:

* Head & Shoulders
* Double Bottom
* Double Top
* Breakout
* Support/Resistance breakout
* Neutral

Output:

```json
{
  "pattern": "Double Bottom",
  "vision_confidence": 0.87
}
```

---

### Layer 3 — Context Intelligence

Fundamental validation using:

* Earnings PDFs
* Financial transcripts
* Corporate announcements
* Management commentary
* News summaries

Documents are embedded into a vector database and queried using semantic retrieval.

Output:

```json
{
  "sentiment": "Positive",
  "reason": "Strong quarterly revenue growth"
}
```

---

### Layer 4 — Agentic Validation

An autonomous reasoning layer synthesizes:

* Technical prediction
* Vision signal
* Fundamental context

and generates:

```json
{
  "final_signal": "Bullish",
  "final_confidence": 0.91,
  "reasoning": [
    "Double Bottom detected",
    "Positive earnings guidance",
    "Momentum indicators aligned"
  ]
}
```

---

# 3. Architecture Overview

## High-Level System Architecture

```text
                         ┌──────────────────────────┐
                         │      VERCEL (FREE)       │
                         │  React Trading Dashboard │
                         │ Bloomberg-style Frontend │
                         └──────────────┬───────────┘
                                        │
                              HTTPS / WebSocket
                                        │
┌───────────────────────────────────────▼──────────────────────────────────────┐
│                               RENDER (FREE)                                  │
│                         FastAPI Intelligence Layer                            │
│                                                                               │
│ ┌──────────────────────────────────────────────────────────────────────────┐  │
│ │                     Core Trading Intelligence Engine                     │  │
│ │                                                                          │  │
│ │ Data Ingestion → Feature Engineering → ML Predictions                   │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│ ┌──────────────────────────────────────────────────────────────────────────┐  │
│ │                         AI Research Terminal                             │  │
│ │                                                                          │  │
│ │ Chart Renderer → OpenCV → CNN (PyTorch)                                 │  │
│ │ Earnings PDFs → pgvector → RAG Agent                                    │  │
│ │ LangChain Agent → Signal Validation                                     │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│ ┌──────────────────────────────────────────────────────────────────────────┐  │
│ │                   Streaming + WebSocket Broadcast                        │  │
│ └──────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬─────────────────────────────────────────────────┘
                              │
             ┌────────────────▼─────────────────┐
             │        SUPABASE (FREE)           │
             │ PostgreSQL + Storage + pgvector  │
             └────────────────┬──────────────────┘
                              │
                 ┌────────────▼─────────────┐
                 │  GitHub Actions (FREE)   │
                 │ Nightly Retraining Jobs  │
                 └────────────┬─────────────┘
                              │
                 ┌────────────▼─────────────┐
                 │ Angel One SmartAPI       │
                 │ Live NSE Market Feed     │
                 └──────────────────────────┘
```

---
# 4. High-Level Data Flow

The platform follows a **multi-stage intelligence pipeline** in which every trading signal is progressively enriched through independent analysis systems.

The system is intentionally modular to ensure:

* Fault isolation
* Asynchronous execution
* Independent subsystem upgrades
* Zero downtime model hot-swapping
* Explainable signal generation

---

## End-to-End Signal Flow

```text
Angel One SmartAPI / Mock Provider
                │
                ▼
     Real-Time Tick Ingestion
                │
                ▼
        Rolling Market State
      (OHLCV + Order Book)
                │
                ▼
      Technical Feature Engine
         (17+ indicators)
                │
                ▼
       LightGBM Prediction Layer
    (intraday + next-day forecasts)
                │
       ┌────────┼────────┐
       │        │        │
       ▼        ▼        ▼
 Vision AI   RAG Engine  Signal Detector
 (CNN)       (Earnings)  Threshold Logic
       │        │
       └────────┴─────────┐
                           ▼
                 LangChain Trading Agent
                           │
                           ▼
              Confidence Reconciliation
                           │
                           ▼
                 Final Trading Signal
                           │
                           ▼
            WebSocket Streaming Dashboard
```

---

## Real-Time Processing Timeline

The platform runs on a **30-second rolling inference cycle**.

Example:

```text
09:15:00 → Market tick ingestion starts

09:15:10 → Feature computation

09:15:12 → Technical prediction complete

09:15:13 → CNN pattern recognition starts

09:15:14 → RAG retrieval executes

09:15:15 → LangChain validation runs

09:15:16 → Final signal generated

09:15:17 → WebSocket broadcast
```

Target latency:

| Component              | Latency Budget |
| ---------------------- | -------------: |
| Market ingestion       |        < 2 sec |
| Feature generation     |        < 1 sec |
| LightGBM inference     |       < 500 ms |
| CNN inference          |        < 2 sec |
| Vector retrieval       |        < 1 sec |
| Agent reasoning        |        < 3 sec |
| Final dashboard update |       < 500 ms |

**Total target latency:** < 10 seconds

---

## Intelligence Layers

### Layer 1 — Quantitative Intelligence

Responsibilities:

* OHLCV feature engineering
* Technical indicators
* Market microstructure analysis
* Intraday + next-day prediction

Primary outputs:

```json
{
  "signal": "Bullish",
  "confidence": 0.84,
  "target_price": 2854.12
}
```

---

### Layer 2 — Vision Intelligence

Responsibilities:

* Candlestick rendering
* Chart normalization
* Pattern detection

Input:

```text
7-day OHLCV history
```

Output:

```json
{
  "pattern": "Double Bottom",
  "confidence": 0.88
}
```

---

### Layer 3 — Fundamental Intelligence (RAG)

Responsibilities:

* Retrieve earnings context
* Retrieve management guidance
* Validate market narratives

Output:

```json
{
  "sentiment": "positive",
  "reason":
  "Revenue guidance upgraded in Q4 earnings call"
}
```

---

### Layer 4 — Agentic Intelligence

Responsibilities:

* Merge multimodal evidence
* Validate signals
* Adjust confidence
* Generate explainability

Output:

```json
{
  "decision": "Bullish",
  "confidence": 0.91,
  "reasoning": [
    "Technical momentum aligned",
    "Double bottom pattern confirmed",
    "Positive earnings guidance"
  ]
}
```

---

# 5. Infrastructure & Deployment

The system is optimized for:

* Zero infrastructure cost
* Production-grade reliability
* Low operational complexity
* Modular AI upgrades

---

## Cloud Architecture

| Service       | Provider            | Purpose           | Tier |
| ------------- | ------------------- | ----------------- | ---- |
| Backend API   | Render              | FastAPI inference | Free |
| Frontend      | Vercel              | React SPA         | Free |
| Database      | Supabase            | PostgreSQL        | Free |
| Vector Search | pgvector (Supabase) | RAG retrieval     | Free |
| Storage       | Supabase Storage    | Models + archives | Free |
| Retraining    | GitHub Actions      | Nightly pipelines | Free |
| Market Feed   | Angel One           | Live NSE feed     | API  |

---

## Infrastructure Diagram

```text
┌────────────────────────────┐
│         VERCEL             │
│  React Trading Dashboard   │
└─────────────┬──────────────┘
              │ HTTPS/WSS
              ▼
┌───────────────────────────────────────┐
│              RENDER                   │
│      FastAPI Intelligence Layer       │
│                                       │
│  Trading Engine                       │
│  AI Research Terminal                 │
│  CNN Inference                        │
│  LangChain Agent                      │
│  WebSocket Broadcast                  │
└──────────────┬────────────────────────┘
               │
               ▼
┌───────────────────────────────────────┐
│             SUPABASE                  │
│ PostgreSQL + Storage + pgvector       │
└──────────────┬────────────────────────┘
               │
               ▼
┌───────────────────────────────────────┐
│          GITHUB ACTIONS               │
│ Retraining + Rollback + Keepalive     │
└───────────────────────────────────────┘
```

---

## Why pgvector Instead of Pinecone

The system intentionally uses PostgreSQL vector search.

Reasons:

1. Reduced architectural complexity
2. No additional vendor dependency
3. Lower operational cost
4. Easier security model
5. Native integration with Supabase

Comparison:

| Factor            | pgvector | Pinecone |
| ----------------- | -------: | -------: |
| Additional infra  |       No |      Yes |
| Cost              |     Free |     Paid |
| PostgreSQL native |      Yes |       No |
| Simplicity        |     High |   Medium |

---

## Deployment Strategy

### Frontend

Deployment target:

Vercel

Responsibilities:

* Dashboard UI
* AI Research Terminal
* WebSocket client
* Real-time updates

---

### Backend

Deployment target:

Render

Responsibilities:

* Inference engine
* CNN inference
* RAG retrieval
* Agent execution
* API routes
* WebSocket broadcasting

---

### Database

Deployment target:

Supabase

Responsibilities:

* Market storage
* Historical OHLCV
* Signal history
* Vector embeddings
* Earnings documents

---

## Cold Start Mitigation

Render free instances sleep after inactivity.

Mitigation strategy:

```text
GitHub Actions CRON
       │
       ▼
Ping /health endpoint
every 10 minutes
during market hours
```

Result:

```text
No cold starts during trading window
```

---

# 6. Core Trading Intelligence Engine

The Core Trading Engine is the deterministic quantitative layer responsible for generating trading predictions.

This layer is intentionally isolated from AI reasoning systems.

Principle:

```text
Trading engine works even if AI fails.
```

---

## Architecture

```text
Market Feed
     │
     ▼
Rolling State Manager
     │
     ▼
Feature Engineering
     │
     ▼
ML Prediction Layer
     │
     ▼
Signal Detector
```

---

## Feature Engineering

The system computes:

### Technical Indicators

* RSI(14)
* MACD
* ATR
* Bollinger Band Width
* EMA(9)
* EMA(21)
* ROC(5)
* ROC(15)
* VWAP deviation

---

### Market Microstructure Indicators

* Buy/Sell Ratio
* Order Book Imbalance
* Spread Mean
* Spread Std
* Volume Ratio
* High/Low Range
* Close Position

---

## Prediction Models

Four LightGBM models:

| Model        | Task               |
| ------------ | ------------------ |
| intraday_clf | Intraday direction |
| intraday_reg | Intraday return    |
| nextday_clf  | Next-day direction |
| nextday_reg  | Next-day return    |

---

## Prediction Output

Example:

```json
{
  "symbol": "RELIANCE",
  "intraday": {
    "direction": "Bullish",
    "confidence": 0.82,
    "target_price": 2870
  },
  "nextday": {
    "direction": "Bullish",
    "confidence": 0.79,
    "corridor": {
      "lower": 2860,
      "upper": 2915
    }
  }
}
```

---

## Signal Triggering

Signals are fired only when:

```text
confidence >= threshold
```

Default:

```text
0.75
```

This reduces noise and prevents over-alerting.

---

# 7. AI Research Terminal Architecture

The AI Research Terminal is a specialized intelligence layer added to the dashboard.

Purpose:

> Transform technical predictions into explainable AI trading intelligence.

The terminal does **not replace** the trading engine.

It augments it.

---

## Responsibilities

1. Chart pattern recognition
2. Earnings/news contextualization
3. AI reasoning generation
4. Confidence reconciliation
5. Explainable signal presentation

---

## AI Research Terminal Flow

```text
Technical Signal Triggered
           │
           ▼
   Chart Intelligence
 (PyTorch + OpenCV CNN)
           │
           ▼
 Fundamental Retrieval
     (RAG Engine)
           │
           ▼
 LangChain Trading Agent
           │
           ▼
 Final Confidence Verdict
           │
           ▼
 Dashboard Streaming
```

---

## Dashboard Tab Structure

```text
Dashboard
Portfolio
Signals
AI Research Terminal
```

---

## Research Terminal UI

```text
┌──────────────────────────────────┐
│ LIVE AGENT THOUGHTS              │
│ "Checking RELIANCE earnings..."  │
│ "Pattern detected..."            │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ CHART PATTERN RECOGNITION        │
│ Double Bottom (88%)              │
│ Rendered candlestick preview     │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ EARNINGS COPILOT                 │
│ Positive management guidance     │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ FINAL AI VERDICT                 │
│ BUY (91% Confidence)             │
└──────────────────────────────────┘
```

---

## Design Philosophy

The terminal acts as:

```text
AI copilot for traders
```

not

```text
Autonomous trade executor
```

The system assists decision making.

Human operators remain responsible for execution.

---
# 8. Computer Vision & Chart Pattern Recognition Pipeline

The Computer Vision subsystem provides **visual intelligence validation** for trading signals.

Instead of relying solely on mathematical indicators, the platform analyzes normalized candlestick chart images using a deep learning inference pipeline.

Purpose:

> Validate technical signals using learned visual chart structure.

This system detects classical technical formations commonly used by discretionary and institutional traders.

---

## Objectives

The Computer Vision layer provides:

* Chart pattern recognition
* Signal confirmation
* False-positive reduction
* Visual explainability
* Multimodal validation

---

## Supported Pattern Classes

The first production version supports:

| Pattern                  | Description             |
| ------------------------ | ----------------------- |
| Head & Shoulders         | Reversal pattern        |
| Double Bottom            | Bullish reversal        |
| Double Top               | Bearish reversal        |
| Breakout                 | Momentum continuation   |
| Support/Resistance Break | Level confirmation      |
| Neutral                  | No meaningful structure |

---

## Design Principle

The platform intentionally **does not use UI screenshots**.

Bad approach:

```text id="mh7q0q"
Browser Screenshot
      ↓
CNN
```

Problems:

* theme noise
* labels
* zoom inconsistency
* resolution variance
* browser rendering artifacts

---

### Production Approach

The system renders canonical candlestick images directly from OHLCV data.

```text id="3h3ewr"
OHLCV History
      ↓
Chart Renderer
      ↓
OpenCV Preprocessing
      ↓
PyTorch CNN
      ↓
Pattern Confidence
```

This ensures deterministic inference.

---

## Pipeline Overview

```text id="mkvf56"
7-Day OHLCV Data
        │
        ▼
Candlestick Renderer
(mplfinance)
        │
        ▼
Canonical Chart Image
        │
        ▼
OpenCV Preprocessing
        │
        ├── Grayscale
        ├── Denoise
        ├── Contrast normalize
        ├── Edge enhancement
        └── Resize(224x224)
        │
        ▼
PyTorch CNN
        │
        ▼
Pattern Classification
        │
        ▼
Confidence Score
```

---

## Image Rendering

Input:

```text id="5r2sw1"
7-day intraday OHLCV
```

Generated image:

```text id="0pp9ru"
clean candlestick chart
no axes
no labels
normalized dimensions
consistent theme
```

Example render:

```text id="fsrk7v"
black background
white candles
uniform spacing
224x224 output
```

This ensures model stability.

---

## OpenCV Processing Pipeline

The preprocessing stage standardizes inputs.

### Step 1 — Convert to Grayscale

Purpose:

Remove color dependence.

```text id="eskh2n"
RGB → grayscale
```

---

### Step 2 — Denoising

Purpose:

Remove chart rendering artifacts.

Method:

```text id="z1kwib"
Gaussian Blur
```

---

### Step 3 — Contrast Enhancement

Purpose:

Improve candle boundary visibility.

Method:

```text id="vjlwm9"
histogram normalization
```

---

### Step 4 — Edge Detection

Purpose:

Enhance candle structure.

Method:

```text id="i0f51v"
Canny edge filtering
```

---

### Step 5 — Resize

Target:

```text id="6j9jrw"
224 × 224
```

---

## CNN Architecture

The platform uses transfer learning.

Selected model:

PyTorch +
ResNet-18

Why:

| Factor            | Reason                         |
| ----------------- | ------------------------------ |
| Small footprint   | Free-tier friendly             |
| Fast inference    | Real-time capable              |
| Transfer learning | Minimal training data required |
| Stable            | Production-proven              |

---

## Transfer Learning Strategy

Architecture:

```text id="wfp5dr"
Pretrained ResNet18
         │
Remove final FC layer
         │
Replace classifier head
         │
Fine-tune on chart patterns
```

Output classes:

```text id="z0rnkz"
head_shoulders
double_bottom
double_top
breakout
support_break
neutral
```

---

## Training Dataset

Dataset composition:

```text id="0wgzgu"
Historical OHLCV
      ↓
Chart rendering
      ↓
Manual / semi-auto labeling
      ↓
Training images
```

Recommended minimum:

| Class            | Images |
| ---------------- | -----: |
| Double Bottom    |  2,000 |
| Double Top       |  2,000 |
| Breakout         |  2,000 |
| Head & Shoulders |  2,000 |
| Neutral          |  5,000 |

---

## Inference Output

Example:

```json id="4b88ur"
{
  "pattern": "Double Bottom",
  "confidence": 0.88,
  "vision_score": 0.72
}
```

---

## Performance Targets

| Metric                |  Target |
| --------------------- | ------: |
| CNN inference latency | < 2 sec |
| Memory footprint      | < 100MB |
| Model size            |  < 50MB |
| Pattern precision     |   > 80% |

---

# 9. Agentic RAG (Earnings + News Intelligence)

The RAG subsystem validates trading signals using **fundamental intelligence**.

Purpose:

> Prevent technically attractive but fundamentally weak trades.

The system autonomously retrieves:

* Earnings reports
* Corporate filings
* Management commentary
* Conference call transcripts
* Financial news

and injects context into decision making.

---

## Design Philosophy

The system uses:

**Retrieval-Augmented Generation (RAG)**

instead of:

```text id="kzkrjn"
LLM hallucination
```

The agent reasons over retrieved evidence.

---

## Architecture

```text id="63snjw"
PDF Filings / Earnings
          │
          ▼
Document Parsing
          │
          ▼
Chunking Pipeline
          │
          ▼
Embedding Generation
          │
          ▼
pgvector Database
          │
          ▼
Semantic Retrieval
          │
          ▼
LangChain Trading Agent
```

---

## Why pgvector

Chosen technology:

pgvector

Reason:

| Benefit         | Explanation             |
| --------------- | ----------------------- |
| No new infra    | Already using Supabase  |
| Native Postgres | Operational simplicity  |
| Free            | No vendor cost          |
| Secure          | Existing DB permissions |

The platform intentionally avoids:

Pinecone

for production simplicity.

---

## Document Sources

Supported sources:

| Source                      | Example               |
| --------------------------- | --------------------- |
| Earnings PDFs               | Quarterly filings     |
| Annual reports              | Company disclosures   |
| Conference call transcripts | Management commentary |
| Financial news              | Earnings summaries    |
| Internal research           | Analyst notes         |

---

## Chunking Strategy

Documents are split into chunks.

Example:

```text id="7e3mp4"
Chunk Size: 512–1024 tokens
Overlap: 100 tokens
```

Reason:

```text id="lh4j72"
Preserve semantic continuity
```

---

## Embedding Pipeline

Flow:

```text id="tvdll9"
Document
   │
   ▼
Text Chunking
   │
   ▼
Embedding Model
   │
   ▼
Vector Storage
```

Example embedding model:

```text id="skqj7x"
768-dimensional vectors
```

---

## Retrieval Flow

Example:

Signal:

```text id="4jlwmn"
RELIANCE → Bullish
```

Agent query:

```text id="fhjlwm"
Did RELIANCE recently report weak earnings,
guidance downgrade, or management concerns?
```

Retrieved context:

```json id="jlwmu5"
{
  "sentiment": "positive",
  "evidence":
  "Q4 earnings exceeded expectations"
}
```

---

## LangChain Trading Agent

Purpose:

> Reason over multimodal evidence.

Responsibilities:

1. Validate technical signal
2. Read retrieved evidence
3. Adjust confidence
4. Produce explainability

---

## Agent Workflow

```text id="7px6nd"
Technical Signal
       │
       ▼
CNN Pattern Result
       │
       ▼
RAG Retrieval
       │
       ▼
LangChain Agent
       │
       ▼
Confidence Reconciliation
```

---

## Example Decision

Input:

```text id="t23mm2"
Bullish signal
Double Bottom detected
Positive earnings guidance
```

Output:

```json id="sngs0t"
{
  "final_signal": "Bullish",
  "confidence": 0.91,
  "reasoning": [
    "Momentum indicators aligned",
    "Double Bottom pattern confirmed",
    "Positive quarterly guidance"
  ]
}
```

---

# 10. Real-Time Streaming & Async Orchestration

The system uses an asynchronous architecture.

Goal:

> Never block signal generation.

Even if AI inference fails, technical predictions continue.

---

## Async Execution Model

The 30-second loop spawns independent workers.

```text id="yrg37x"
Technical Prediction
       │
       ├── CNN Worker
       ├── RAG Worker
       └── Agent Worker
```

---

## Orchestration Flow

```text id="xjb21d"
30s Scheduler
      │
      ▼
Technical Prediction
      │
      ├── asyncio task → CNN inference
      ├── asyncio task → RAG retrieval
      └── asyncio task → Agent reasoning
```

---

## Failure Isolation

Example:

```text id="t2h3f7"
CNN failure
```

Expected behavior:

```text id="jlwm4r"
technical signal still works
dashboard still updates
warning logged
```

Design principle:

```text id="12u7cl"
AI layer augments,
never blocks.
```

---

## WebSocket Streaming

Update frequency:

```text id="j8zvqk"
every 30 seconds
```

Payload:

```json id="20x2gl"
{
  "symbol": "RELIANCE",
  "technical_prediction": {},
  "vision_analysis": {},
  "rag_context": {},
  "agent_reasoning": {},
  "final_signal": {}
}
```

---

## Streaming Guarantees

| Property                | Guarantee |
| ----------------------- | --------- |
| No duplicate processing | Yes       |
| Failure isolation       | Yes       |
| Async execution         | Yes       |
| Hot model reload        | Yes       |
| Zero downtime           | Yes       |

---

# 11. Backend Architecture

The backend follows a modular FastAPI architecture.

Principles:

* low coupling
* async everywhere
* fault isolation
* independent subsystems

---

## Updated Module Architecture

```text id="bh0mvz"
backend/
├── auth/
├── ingestion/
├── inference/
├── feature_core/
├── websocket/
├── notifications/
├── scheduler/
├── ai_research/
│   ├── chart_capture.py
│   ├── cv_preprocessing.py
│   ├── cnn_inference.py
│   ├── rag_pipeline.py
│   ├── embeddings.py
│   ├── agent.py
│   ├── reasoning_engine.py
│   └── schemas.py
├── db/
├── api/
└── scripts/
```

---

## AI Research Layer

Responsibilities:

| Module              | Responsibility            |
| ------------------- | ------------------------- |
| chart_capture.py    | chart generation          |
| cv_preprocessing.py | OpenCV transforms         |
| cnn_inference.py    | PyTorch model             |
| rag_pipeline.py     | retrieval                 |
| embeddings.py       | vector generation         |
| agent.py            | LangChain orchestration   |
| reasoning_engine.py | confidence reconciliation |

---

# 12. Frontend Architecture

The frontend exposes:

1. Dashboard
2. Portfolio
3. Signal History
4. AI Research Terminal

---

## UI Structure

```text id="gm22ur"
Dashboard
Portfolio
Signals
AI Research Terminal
```

---

## AI Research Terminal Components

```text id="jlwm8x"
components/
└── ai_terminal/
    ├── ResearchPanel.tsx
    ├── PatternCard.tsx
    ├── EarningsSummary.tsx
    ├── AgentThoughts.tsx
    └── ConfidenceBreakdown.tsx
```

---

## Research Panel Layout

```text id="jlwm0p"
┌────────────────────────────┐
│ AGENT THOUGHTS             │
├────────────────────────────┤
│ PATTERN DETECTION          │
├────────────────────────────┤
│ EARNINGS COPILOT           │
├────────────────────────────┤
│ CONFIDENCE BREAKDOWN       │
└────────────────────────────┘
```

---
# 13. Database Architecture

The platform uses a unified database architecture built on:

PostgreSQL +
pgvector

hosted through:

Supabase

The database is responsible for:

* Market data persistence
* Historical storage
* Portfolio management
* Authentication
* Signal tracking
* Vector search for RAG
* Model metadata
* Auditability

---

## Database Design Philosophy

The platform intentionally uses:

```text id="t9r0od"
single-source-of-truth database
```

instead of:

```text id="mjlwm0"
multiple disconnected stores
```

Benefits:

* simpler operations
* lower cloud cost
* easier backups
* transactional consistency
* reduced deployment complexity

---

## High-Level Database Architecture

```text id="mjlwm1"
Supabase PostgreSQL
│
├── Market Data Tables
├── Portfolio Tables
├── Auth Tables
├── Signal Tables
├── AI Research Tables
├── Embedding Tables
├── Model Metadata Tables
└── Audit Tables
```

---

## Market Data Schema

### intraday_ticks

Purpose:

Store rolling intraday market data.

Columns:

| Column                | Type      |
| --------------------- | --------- |
| id                    | UUID      |
| symbol                | TEXT      |
| timestamp             | TIMESTAMP |
| ltp                   | FLOAT     |
| bid_price             | FLOAT     |
| ask_price             | FLOAT     |
| bid_qty               | FLOAT     |
| ask_qty               | FLOAT     |
| volume                | FLOAT     |
| cold_storage_uploaded | BOOLEAN   |

Retention:

```text id="jlwm2"
7 days
```

---

### daily_ohlcv

Purpose:

Store historical bars.

Columns:

| Column     | Type   |
| ---------- | ------ |
| id         | UUID   |
| symbol     | TEXT   |
| trade_date | DATE   |
| open       | FLOAT  |
| high       | FLOAT  |
| low        | FLOAT  |
| close      | FLOAT  |
| volume     | BIGINT |

Retention:

```text id="jlwm3"
365 days
```

---

## Portfolio Schema

### portfolio_holdings

Columns:

| Column        | Type      |
| ------------- | --------- |
| symbol        | TEXT      |
| quantity      | FLOAT     |
| avg_buy_price | FLOAT     |
| buy_date      | DATE      |
| notes         | TEXT      |
| created_at    | TIMESTAMP |
| updated_at    | TIMESTAMP |

---

## Signal Tables

### trading_signals

Purpose:

Track generated signals.

Columns:

| Column            | Type      |
| ----------------- | --------- |
| id                | UUID      |
| symbol            | TEXT      |
| signal            | TEXT      |
| confidence        | FLOAT     |
| target_price      | FLOAT     |
| prediction_source | TEXT      |
| outcome           | TEXT      |
| created_at        | TIMESTAMP |

---

## AI Research Schema

### research_sessions

Purpose:

Persist AI reasoning history.

Columns:

| Column               | Type      |
| -------------------- | --------- |
| id                   | UUID      |
| symbol               | TEXT      |
| technical_confidence | FLOAT     |
| vision_confidence    | FLOAT     |
| rag_sentiment        | TEXT      |
| final_confidence     | FLOAT     |
| created_at           | TIMESTAMP |

---

### chart_patterns

Purpose:

Persist CNN detections.

Columns:

| Column           | Type      |
| ---------------- | --------- |
| id               | UUID      |
| symbol           | TEXT      |
| pattern_name     | TEXT      |
| confidence       | FLOAT     |
| generated_at     | TIMESTAMP |
| chart_image_path | TEXT      |

---

## RAG Schema

### earnings_documents

Purpose:

Store parsed documents.

| Column       | Type      |
| ------------ | --------- |
| id           | UUID      |
| symbol       | TEXT      |
| title        | TEXT      |
| source       | TEXT      |
| published_at | TIMESTAMP |
| raw_text     | TEXT      |

---

### earnings_chunks

Purpose:

Chunked semantic retrieval.

| Column      | Type        |
| ----------- | ----------- |
| id          | UUID        |
| document_id | UUID        |
| chunk_text  | TEXT        |
| embedding   | VECTOR(768) |
| created_at  | TIMESTAMP   |

---

## pgvector Similarity Search

Example query:

```sql id="jlwm4"
SELECT *
FROM earnings_chunks
ORDER BY embedding <=> :query_embedding
LIMIT 5;
```

Purpose:

```text id="jlwm5"
Top-k semantic retrieval
```

---

## Model Metadata Tables

### model_registry

Purpose:

Track production models.

| Column         | Type      |
| -------------- | --------- |
| model_name     | TEXT      |
| version        | TEXT      |
| trained_at     | TIMESTAMP |
| metrics_json   | JSONB     |
| schema_version | TEXT      |

---

## Audit Tables

### audit_logs

Purpose:

Security and observability.

Columns:

| Column     | Type      |
| ---------- | --------- |
| id         | UUID      |
| actor      | TEXT      |
| action     | TEXT      |
| metadata   | JSONB     |
| created_at | TIMESTAMP |

---

## Storage Architecture

Supabase Storage Buckets:

```text id="jlwm6"
market-csv-archives/
models/
chart-images/
earnings-pdfs/
```

---

## Database Retention Policy

| Data           | Retention  |
| -------------- | ---------- |
| intraday ticks | 7 days     |
| OHLCV          | 365 days   |
| signal history | indefinite |
| embeddings     | indefinite |
| model metadata | indefinite |

---

# 14. API Architecture

The backend exposes a versioned REST + WebSocket API.

API strategy:

```text id="jlwm7"
versioned contracts
```

Base path:

```text id="jlwm8"
/v1
```

---

## API Categories

```text id="jlwm9"
Auth
Predictions
Portfolio
Signals
Historical
AI Research
Internal Admin
WebSocket
```

---

## Authentication APIs

### Login

```http id="jlwm10"
POST /v1/auth/login
```

Response:

```json id="jlwm11"
{
  "access_token": "jwt",
  "expires_in": 86400
}
```

---

### Logout

```http id="jlwm12"
POST /v1/auth/logout
```

---

### Me

```http id="jlwm13"
GET /v1/auth/me
```

---

## Prediction APIs

### Live Predictions

```http id="jlwm14"
GET /v1/predictions/live
```

---

### Historical Predictions

```http id="jlwm15"
GET /v1/predictions/history
```

---

## Portfolio APIs

```http id="jlwm16"
GET /v1/portfolio/
POST /v1/portfolio/holdings
DELETE /v1/portfolio/holdings/{symbol}
```

---

## AI Research APIs

### Get Research Session

```http id="jlwm17"
GET /v1/research/{symbol}
```

Response:

```json id="jlwm18"
{
  "pattern": "Double Bottom",
  "earnings_context": "...",
  "agent_reasoning": [],
  "final_confidence": 0.91
}
```

---

### Trigger Research

```http id="jlwm19"
POST /v1/research/run/{symbol}
```

---

## Internal APIs

Protected via:

```text id="jlwm20"
X-Internal-Token
```

Routes:

```http id="jlwm21"
POST /v1/internal/reload-models
POST /v1/internal/rollback-models
GET /v1/internal/model-status
```

---

## WebSocket Streaming

Endpoint:

```text id="jlwm22"
/ws/stream
```

Payload:

```json id="jlwm23"
{
  "technical_prediction": {},
  "vision_analysis": {},
  "rag_context": {},
  "agent_reasoning": {},
  "final_signal": {}
}
```

---

# 15. Security Design

Security model:

```text id="jlwm24"
defense in depth
```

---

## Authentication

Method:

```text id="jlwm25"
JWT + RBAC
```

Capabilities:

* secure login
* role validation
* API authorization
* protected admin routes

Roles:

```text id="jlwm26"
admin
trader
viewer
```

---

## API Protection

Protected endpoints require:

```http id="jlwm27"
Authorization: Bearer <token>
```

---

## Internal Route Security

Protected by:

```text id="jlwm28"
X-Internal-Token
```

Prevents:

* unauthorized reloads
* rollback abuse
* model tampering

---

## Secrets Management

Secrets stored in:

* Render environment variables
* GitHub secrets
* Supabase secret storage

Never committed:

```text id="jlwm29"
.env excluded from git
```

---

## Rate Limiting

Angel One limit:

```text id="jlwm30"
3 req/sec
```

Mitigation:

```text id="jlwm31"
token bucket limiter
```

---

## AI Safety

The agent:

```text id="jlwm32"
does not execute trades
```

Purpose:

```text id="jlwm33"
decision support only
```

---

## Security Safeguards

Implemented protections:

* JWT auth
* RBAC
* internal tokens
* replay protection
* restricted internal routes
* audit logs
* secret isolation

---

# 16. Observability & Monitoring

Goal:

```text id="jlwm34"
production visibility
```

Monitoring stack:

* application logs
* metrics
* exceptions
* model lifecycle tracking

---

## Logging

Structured logging format:

```json id="jlwm35"
{
  "timestamp":"...",
  "service":"backend",
  "symbol":"RELIANCE",
  "event":"prediction_generated"
}
```

---

## Error Tracking

System:

Sentry

Tracks:

* crashes
* inference failures
* API failures
* scheduler failures

---

## Metrics

System:

Prometheus

Metrics:

```text id="jlwm36"
prediction_latency
cnn_latency
rag_latency
websocket_connections
market_ingestion_rate
```

---

## Health Endpoints

```http id="jlwm37"
GET /health
GET /metrics
```

---

## Alerting

Triggers:

* model reload failure
* websocket failure
* ingestion failure
* excessive latency
* failed retraining

---

# 17. CI/CD + Model Retraining + Rollback

The system supports continuous retraining.

Goal:

```text id="jlwm38"
zero downtime ML lifecycle
```

---

## Nightly Retraining Flow

```text id="jlwm39"
GitHub Actions
        │
        ▼
Download Training Data
        │
        ▼
Retrain LightGBM Models
        │
        ▼
Validate Metrics
        │
        ▼
Upload New Models
        │
        ▼
Hot Reload
```

---

## CNN Retraining

Vision model retraining:

```text id="jlwm40"
weekly schedule
```

Reason:

```text id="jlwm41"
patterns evolve slower than market signals
```

---

## Hot Reloading

Flow:

```text id="jlwm42"
new model
    │
    ▼
download
    │
    ▼
validation
    │
    ▼
atomic swap
```

No downtime.

---

## Rollback

Automatic rollback triggers:

```text id="jlwm43"
failed reload
bad metrics
failed health check
```

Flow:

```text id="jlwm44"
latest stable version
      │
      ▼
restore
      │
      ▼
hot swap
```

---

## CI Pipeline

Pipeline stages:

```text id="jlwm45"
lint
tests
build
deploy
health validation
```

---

## Production Guarantees

| Capability           | Supported |
| -------------------- | --------- |
| Hot reload           | Yes       |
| Rollback             | Yes       |
| Zero downtime        | Yes       |
| Model versioning     | Yes       |
| Scheduled retraining | Yes       |

---
# 18. Memory Budget & Scaling Strategy

The platform is designed to operate efficiently on free-tier cloud infrastructure while remaining horizontally extensible for future institutional deployment.

Primary goals:

* predictable resource usage
* bounded memory growth
* non-blocking inference
* fault isolation
* scalable AI subsystems

---

## Scaling Philosophy

The system follows:

```text id="jlwm46"
controlled vertical scaling first
horizontal scaling later
```

Reason:

```text id="jlwm47"
Nifty 50 universe size is fixed
```

The system only monitors:

```text id="jlwm48"
50 symbols
```

Therefore, massive distributed compute is unnecessary for Version 2.0.

---

## Memory Budget

Expected runtime memory usage:

| Component               | Estimated Usage |
| ----------------------- | --------------: |
| FastAPI runtime         |          ~120MB |
| Feature engine          |           ~50MB |
| LightGBM models         |          ~100MB |
| Rolling state cache     |           ~80MB |
| CNN inference           |          ~120MB |
| OpenCV preprocessing    |           ~50MB |
| RAG retrieval           |           ~80MB |
| LangChain orchestration |          ~100MB |
| WebSocket state         |           ~50MB |
| Total                   |          ~750MB |

Target:

```text id="jlwm49"
under 1GB memory
```

Compatible with:

```text id="jlwm50"
Render free-tier constraints
```

---

## CPU Budget

Expected CPU load:

| Operation           |   Cost |
| ------------------- | -----: |
| Market ingestion    |    Low |
| Feature engineering |    Low |
| LightGBM inference  |    Low |
| CNN inference       | Medium |
| Embedding retrieval |    Low |
| Agent reasoning     | Medium |

Average load:

```text id="jlwm51"
< 50%
```

during market hours.

---

## Batch Processing Strategy

To avoid market-open spikes:

```text id="jlwm52"
50 stocks processed in batches
```

Example:

```text id="jlwm53"
Batch A → 25 stocks
pause(500ms)
Batch B → 25 stocks
```

Benefits:

* memory smoothing
* predictable latency
* reduced CPU spikes

---

## WebSocket Scaling

Architecture:

```text id="jlwm54"
single producer
multiple subscribers
```

Flow:

```text id="jlwm55"
market update
      │
      ▼
state cache update
      │
      ▼
broadcast to all sockets
```

Advantages:

* no duplicated computation
* constant backend load

---

## AI Worker Parallelism

The system isolates expensive operations.

Example:

```text id="jlwm56"
technical prediction
      │
      ├── CNN worker
      ├── RAG worker
      └── Agent worker
```

Execution model:

```text id="jlwm57"
asyncio.create_task()
```

Purpose:

```text id="jlwm58"
non-blocking execution
```

---

## Future Scaling Path

When upgrading beyond free-tier:

```text id="jlwm59"
market ingestion service
feature service
ai research service
frontend service
```

can be independently containerized.

Potential production deployment:

```text id="jlwm60"
Docker + Kubernetes
```

---

## Horizontal Scaling Strategy

Future scaling model:

```text id="jlwm61"
API Gateway
      │
      ├── Trading Engine Pods
      ├── CNN Inference Pods
      ├── RAG Retrieval Pods
      └── Agent Workers
```

---

## Caching Strategy

Cache layers:

| Layer           | Purpose                   |
| --------------- | ------------------------- |
| Market cache    | avoid redundant API calls |
| Feature cache   | reduce recomputation      |
| Embedding cache | faster retrieval          |
| WebSocket cache | warm reconnect            |

---

## Resource Guarantees

| Property            | Guarantee |
| ------------------- | --------- |
| bounded memory      | yes       |
| bounded CPU         | yes       |
| async execution     | yes       |
| fault isolation     | yes       |
| predictable latency | yes       |

---

# 19. Technical Safeguards

The platform implements production safeguards to reduce operational failures, false positives, and infrastructure instability.

Goal:

```text id="jlwm62"
safe intelligent trading assistance
```

---

## Safeguard 1 — Rate Limiter

Constraint:

```text id="jlwm63"
Angel One SmartAPI = 3 req/sec
```

Implementation:

```text id="jlwm64"
token bucket algorithm
```

Behavior:

```text id="jlwm65"
request blocked until token available
```

Guarantee:

```text id="jlwm66"
API never exceeds vendor limits
```

---

## Safeguard 2 — Market Open Spike Protection

Problem:

```text id="jlwm67"
09:15 AM = simultaneous symbol updates
```

Mitigation:

```text id="jlwm68"
batched scheduling
```

Example:

```text id="jlwm69"
25 symbols
sleep(500ms)
25 symbols
```

---

## Safeguard 3 — AI Failure Isolation

Principle:

```text id="jlwm70"
AI augments, never blocks
```

Failure example:

```text id="jlwm71"
CNN unavailable
```

Expected behavior:

```text id="分快三"
technical prediction still executes
signal still streams
warning logged
```

---

## Safeguard 4 — RAG Timeout Protection

Risk:

```text id="jlwm72"
slow vector retrieval
```

Mitigation:

```text id="jlwm73"
hard timeout
```

Example:

```text id="jlwm74"
timeout = 2 sec
fallback = no RAG context
```

---

## Safeguard 5 — Agent Timeout Protection

Risk:

```text id="jlwm75"
slow reasoning generation
```

Mitigation:

```text id="jlwm76"
timeout = 3 sec
```

Fallback:

```text id="分快三2"
technical prediction only
```

---

## Safeguard 6 — Atomic Model Reload

Requirement:

```text id="分快三3"
never partially load models
```

Flow:

```text id="分快三4"
download
verify checksum
validate load
atomic replace
hot swap
```

Guarantee:

```text id="分快三5"
zero downtime
```

---

## Safeguard 7 — Automatic Rollback

Triggers:

* failed reload
* health check failure
* metric degradation

Recovery:

```text id="分快三6"
restore previous stable version
```

---

## Safeguard 8 — Vector Retrieval Safety

Risk:

```text id="分快三7"
hallucinated reasoning
```

Mitigation:

```text id="分快三8"
reason only over retrieved evidence
```

---

## Safeguard 9 — Data Purge Protection

Requirement:

```text id="分快三9"
never purge before backup
```

Policy:

```sql id="分快三10"
DELETE FROM intraday_ticks
WHERE cold_storage_uploaded = TRUE
```

---

## Safeguard 10 — Weekend/Holiday Mode

Behavior:

```text id="分快三11"
automatic mock provider
```

When:

* weekends
* NSE holidays
* outside trading hours

---

## Safeguard 11 — Circuit Breaker

If failures exceed threshold:

```text id="分快三12"
disable AI subsystem
```

Result:

```text id="分快三13"
technical engine survives
```

---

## Safeguard 12 — Security Audit Logging

All sensitive actions logged.

Examples:

* login attempts
* model reloads
* rollback operations
* internal API access

---

## Reliability Guarantees

| Property        | Status |
| --------------- | ------ |
| zero downtime   | yes    |
| rollback        | yes    |
| bounded latency | yes    |
| fault isolation | yes    |
| explainability  | yes    |

---

# 20. Disaster Recovery

The platform includes a formal disaster recovery plan.

Goals:

* recover quickly
* preserve signal integrity
* prevent corrupted deployment

---

## Recovery Objectives

| Metric                         |   Target |
| ------------------------------ | -------: |
| RTO (Recovery Time Objective)  | < 10 min |
| RPO (Recovery Point Objective) |  < 24 hr |

---

## Failure Categories

### Infrastructure Failure

Example:

```text id="分快三14"
Render outage
```

Mitigation:

```text id="分快三15"
redeploy from GitHub
restore env vars
```

---

### Model Corruption

Mitigation:

```text id="分快三16"
rollback latest stable model
```

---

### Database Failure

Mitigation:

```text id="分快三17"
Supabase backup restore
```

---

### CNN Failure

Fallback:

```text id="分快三18"
technical prediction only
```

---

### RAG Failure

Fallback:

```text id="分快三19"
signal without fundamentals
```

---

### WebSocket Failure

Fallback:

```text id="分快三20"
REST polling
```

---

## Recovery Workflow

```text id="分快三21"
detect failure
      │
      ▼
log incident
      │
      ▼
auto remediation
      │
      ▼
rollback if needed
      │
      ▼
health validation
```

---

## Backup Strategy

Backups:

| Asset         | Strategy           |
| ------------- | ------------------ |
| PostgreSQL    | Supabase snapshots |
| models        | storage versioning |
| embeddings    | DB backup          |
| earnings docs | storage archive    |

---

## Production Recovery Guarantees

| Capability     | Supported |
| -------------- | --------- |
| rollback       | yes       |
| failover       | partial   |
| hot reload     | yes       |
| backup restore | yes       |

---

# 21. Complete Updated File Structure

```text id="分快三22"
nse-intelligence-platform/
│
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── config_validator.py
│   ├── nse_holidays.json
│   │
│   ├── auth/
│   ├── api/
│   ├── db/
│   ├── websocket/
│   ├── scheduler/
│   ├── notifications/
│   ├── ingestion/
│   ├── feature_core/
│   ├── inference/
│   │
│   ├── ai_research/
│   │   ├── __init__.py
│   │   ├── chart_capture.py
│   │   ├── cv_preprocessing.py
│   │   ├── cnn_inference.py
│   │   ├── rag_pipeline.py
│   │   ├── embeddings.py
│   │   ├── agent.py
│   │   ├── reasoning_engine.py
│   │   ├── schemas.py
│   │   └── prompts.py
│   │
│   ├── models/
│   │   ├── intraday_clf.pkl
│   │   ├── intraday_reg.pkl
│   │   ├── nextday_clf.pkl
│   │   ├── nextday_reg.pkl
│   │   └── chart_pattern_cnn.pt
│   │
│   ├── scripts/
│   │   ├── retrain.py
│   │   ├── train_chart_model.py
│   │   ├── model_versioning.py
│   │   ├── download_training_data.py
│   │   ├── upload_models.py
│   │   └── download_models.py
│   │
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Portfolio.tsx
│   │   │   ├── SignalHistory.tsx
│   │   │   └── AIResearchTerminal.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── predictions/
│   │   │   ├── portfolio/
│   │   │   ├── common/
│   │   │   └── ai_terminal/
│   │   │       ├── ResearchPanel.tsx
│   │   │       ├── PatternCard.tsx
│   │   │       ├── EarningsSummary.tsx
│   │   │       ├── AgentThoughts.tsx
│   │   │       └── ConfidenceBreakdown.tsx
│   │   │
│   │   ├── hooks/
│   │   ├── store/
│   │   ├── services/
│   │   └── types/
│   │
│   └── package.json
│
├── docs/
│   ├── SYSTEM_DESIGN.md
│   └── DISASTER_RECOVERY.md
│
└── .github/
    └── workflows/
        ├── test.yml
        ├── retrain.yml
        ├── keepalive.yml
        ├── deploy-backend.yml
        └── deploy-frontend.yml
```

---

# Conclusion

The NSE Intelligence Platform v2.0 represents a production-grade, explainable, AI-powered market intelligence system.

Unlike traditional trading dashboards, the platform combines:

* quantitative forecasting
* computer vision
* retrieval-augmented intelligence
* agentic reasoning
* streaming inference
* explainable decision support

while preserving:

```text id="分快三23"
determinism
fault isolation
production safety
zero-cost deployment
```

The architecture is intentionally modular, scalable, and resilient, enabling future expansion into institutional-grade quantitative intelligence systems without redesigning the core platform.

---

**End of Document**
**Version 2.0 — Client Deliverable**
