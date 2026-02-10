

# Dynamic Pricing & Revenue Optimization Engine

A specialized Data Engineering pipeline designed to ingest real-time competitor pricing data, analyze market trends, and suggest optimal pricing strategies using Apache Spark, Airflow, and Snowflake.

## Architecture
**Current Flow:**
`ScrapingDog API` → `Spark (Extraction)` → `AWS S3 (Data Lake)` → `Snowflake (Data Warehouse)`

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Orchestration** | Apache Airflow | Schedules and monitors pipeline tasks (Dockerized). |
| **Compute** | Apache Spark | Distributed data processing for ingestion and transformation. |
| **Storage** | AWS S3 | Raw data lake (Parquet format). |
| **Warehouse** | Snowflake | Structured storage for analytics and modeling. |
| **Containerization** | Docker | Fully containerized environment for reproducibility. |

## Setup & Usage

### 1. Prerequisites
* Docker Desktop (running with at least 4GB RAM)
* AWS Account (S3 access)
* ScrapingDog API Key

### 2. Environment Variables
Create a `.env` file in the root directory with the following secrets:
```
AWS_ACCESS_KEY_ID=your_id
AWS_SECRET_ACCESS_KEY=your_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=de-project-dynamic-pricing-raw-source
SCRAPINGDOG_API_KEY=your_scraping_key
```


### 3. Running the Pipeline

**Start the Infrastructure:**

```bash
docker-compose up -d

```

**Run the Competitor Pricing Ingestion Job (Manual Trigger):**

```bash
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --packages org.apache.hadoop:hadoop-aws:3.3.4 \
  --master spark://spark-master:7077 \
  /opt/spark/jobs/etl/ingest_competitor_prices.py

```

## Project Roadmap & Status

### Phase 1: Infrastructure & Ingestion (Complete)
- [x] Docker environment setup (Spark Cluster + Airflow).
- [x] Custom Docker image with AWS & Snowflake dependencies.
- [x] AWS S3 Bucket configuration for Data Lake.
- [x] **Spark Job:** Scaled ingestion for 25+ products.
- [x] **Backfill:** Generated 90 days of synthetic historical data.
- [x] **Storage:** Automated S3 Parquet landing.

### Phase 2: Warehousing & Transformation (In Progress)
- [x] Configure Snowflake Database & Warehouses.
- [x] Create **Storage Integration** (S3 ↔ Snowflake).
- [x] Automated Loading via Airflow (`COPY INTO`).
- [ ] Implement **dbt** (Data Build Tool) for transformations.

### Phase 3: Automation & Analytics

* [ ] Create Airflow DAGs to schedule Spark jobs daily.
* [ ] Build "Price Recommendation" logic (Python/Pandas).
* [ ] Connect visualization tool (Streamlit/Tableau) for final dashboard.

---

*Author: Avirukth*


