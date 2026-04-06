# Customer Data Pipeline Project Overview

## Architecture Overview

The pipeline consists of two primary services:

### 1. Flask Mock Server
- Simulates a source system by exposing customer data stored in a JSON file (`data/customers.json`).
- Supports **paginated access** for efficient data retrieval.

### 2. FastAPI Pipeline Service
- Acts as the **ingestion and API layer**, performing the following tasks:
  - Fetches data from the Flask server.
  - Upserts the data into **PostgreSQL**.
  - Exposes **paginated** and **single-record endpoints** for consumption.

## Key Features
- Demonstrates a typical **ETL (Extract, Transform, Load)** workflow.
- Showcases a **modern microservices architecture** with containerized services.
- Provides **RESTful APIs** for downstream data consumers.

# Testing
## Flask
```bash
curl "http://localhost:5000/api/customers?page=1&limit=5"
curl "http://localhost:5000/api/customers/1"
curl "http://localhost:5000/api/health"
```

## FastAPI
```bash
curl -X POST "http://localhost:8000/api/ingest"
curl "http://localhost:8000/api/customers?page=1&limit=5"
curl "http://localhost:8000/api/customers/1"
```

