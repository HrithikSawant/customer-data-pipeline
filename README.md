# Customer Data Pipeline

A containerised **ETL (Extract, Transform, Load)** pipeline that ingests customer records from a mock REST source, upserts them into PostgreSQL, and exposes them through a FastAPI service. The project demonstrates a modern microservices architecture using Docker Compose.

---

## Table of Contents

- [Architecture](#architecture)
- [Services](#services)
  - [Mock Server (Flask)](#mock-server-flask)
  - [Pipeline Service (FastAPI)](#pipeline-service-fastapi)
  - [PostgreSQL](#postgresql)
- [Data Model](#data-model)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
  - [Mock Server endpoints](#mock-server-endpoints)
  - [Pipeline Service endpoints](#pipeline-service-endpoints)
- [Configuration](#configuration)

---

## Architecture

```
┌──────────────────┐       HTTP (paginated)       ┌──────────────────────┐
│   Mock Server    │ ◄──────────────────────────── │  Pipeline Service    │
│  Flask :5000     │                               │  FastAPI :8000       │
│                  │                               │                      │
│  data/           │                               │  /api/ingest  (POST) │
│  customers.json  │                               │  /api/customers (GET)│
└──────────────────┘                               └──────────┬───────────┘
                                                              │ SQLAlchemy
                                                              ▼
                                                   ┌──────────────────────┐
                                                   │     PostgreSQL :5432  │
                                                   │     customer_db       │
                                                   └──────────────────────┘
```

**ETL flow:**
1. **Extract** – `pipeline-service` calls the mock server's paginated `/api/customers` endpoint and collects all records.
2. **Transform** – basic type coercion is handled by SQLAlchemy column definitions.
3. **Load** – each record is upserted (insert or update) into the `customers` table in PostgreSQL.

---

## Services

### Mock Server (Flask)

- **Image:** Python 3.12-slim, built from `mock-server/Dockerfile`
- **Purpose:** Simulates a legacy source system. Reads customer data from `mock-server/data/custermers.json` and serves it through a paginated REST API.

### Pipeline Service (FastAPI)

- **Image:** Python 3.12-slim, built from `pipeline-service/Dockerfile`
- **Purpose:** Orchestrates ingestion and acts as the read API. On demand (`POST /api/ingest`) it fetches all pages from the mock server and upserts them into PostgreSQL.

### PostgreSQL

- **Image:** `postgres:15`
- **Database:** `customer_db`

---

## Data Model

The `customers` table mirrors the JSON source records:

| Column           | Type            | Notes           |
|------------------|-----------------|-----------------|
| `customer_id`    | VARCHAR(50)     | Primary key     |
| `first_name`     | VARCHAR(100)    | Not null        |
| `last_name`      | VARCHAR(100)    | Not null        |
| `email`          | VARCHAR(255)    | Not null        |
| `phone`          | VARCHAR(20)     |                 |
| `address`        | TEXT            |                 |
| `date_of_birth`  | DATE            |                 |
| `account_balance`| NUMERIC(15,2)   |                 |
| `created_at`     | TIMESTAMP       |                 |

---

## Project Structure

```
customer-data-pipeline/
├── docker-compose.yml          # Orchestrates all three services
├── mock-server/
│   ├── Dockerfile
│   ├── app.py                  # Flask application
│   ├── requirements.txt
│   └── data/
│       └── custermers.json     # Seed customer records
└── pipeline-service/
    ├── Dockerfile
    ├── main.py                 # FastAPI application & route definitions
    ├── database.py             # SQLAlchemy engine & session factory
    ├── requirements.txt
    ├── models/
    │   └── customer.py         # Customer ORM model
    └── services/
        └── ingestion.py        # fetch_all_customers() + upsert_customer()
```

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) ≥ 20
- [Docker Compose](https://docs.docker.com/compose/) ≥ 2

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/HrithikSawant/customer-data-pipeline.git
cd customer-data-pipeline

# Build and start all services
docker compose up --build
```

Once all containers are healthy, trigger the ingestion:

```bash
curl -X POST "http://localhost:8000/api/ingest"
# {"status":"success","records_processed":N}
```

Stop all services:

```bash
docker compose down
```

---

## API Reference

### Mock Server endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check – returns `{"status":"ok"}` |
| `GET` | `/api/customers?page=1&limit=10` | Paginated list of customers |
| `GET` | `/api/customers/{customer_id}` | Single customer by ID |

**Example:**
```bash
curl "http://localhost:5000/api/customers?page=1&limit=5"
curl "http://localhost:5000/api/customers/1"
curl "http://localhost:5000/api/health"
```

### Pipeline Service endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/ingest` | Fetch all records from mock server and upsert into PostgreSQL |
| `GET`  | `/api/customers?page=1&limit=10` | Paginated customer list from PostgreSQL |
| `GET`  | `/api/customers/{customer_id}` | Single customer by ID from PostgreSQL |

**Example:**
```bash
curl -X POST "http://localhost:8000/api/ingest"
curl "http://localhost:8000/api/customers?page=1&limit=5"
curl "http://localhost:8000/api/customers/1"
```

Interactive API docs (provided by FastAPI) are available at:  
`http://localhost:8000/docs`

---

## Configuration

Environment variables consumed by `pipeline-service`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:changeme@postgres:5432/customer_db` | SQLAlchemy connection string |
| `FLASK_API` | `http://mock-server:5000/api/customers` | Base URL of the mock server |

These values are set automatically when running via Docker Compose. Override them in `docker-compose.yml` or a `.env` file for different environments.

---

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file included in the repository.

