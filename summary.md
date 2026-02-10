This document serves as the comprehensive technical documentation for your **Revenue Optimization Engine**. It is designed to be used as a standalone project report, a detailed GitHub `README.md`, or a technical case study for your portfolio.

---

# Project: Revenue Optimization Engine

**An End-to-End Data Engineering & Predictive Analytics Platform**

## 1. Executive Summary

The Revenue Optimization Engine is a full-stack data platform designed to address the inefficiencies of static pricing in e-commerce. By integrating historical sales data with real-time external signals (competitor pricing and weather patterns), the system predicts demand elasticity and recommends optimal price points to maximize revenue.

The project demonstrates a complete data lifecycle: from infrastructure provisioning (IaC) and batch ingestion to complex transformations, machine learning inference, and a user-facing analytical dashboard.

---

## 2. Problem Statement

In competitive retail markets, pricing strategies are often reactive or static.

* **The Gap:** Retailers miss revenue opportunities during high-demand periods (e.g., specific weather conditions) and lose market share during low-demand periods due to uncompetitive pricing.
* **The Challenge:** Connecting disparate data sources (legacy sales records, live competitor scrapes, meteorological API data) into a unified view to drive automated decision-making.

---

## 3. Solution Architecture

The system follows a modern Lakehouse architecture, decoupling storage, compute, and serving layers.

### **3.1 Infrastructure & Orchestration**

* **Terraform:** Manages the entire cloud footprint as code (IaC), provisioning AWS S3 buckets and Snowflake resources (Warehouses, Databases, Roles) to ensure a reproducible environment.
* **Docker:** Containerizes the application components (Backend API, Frontend Dashboard) for consistent deployment.
* **Apache Airflow:** Orchestrates the data pipelines, managing dependencies between ingestion jobs, dbt transformations, and ML training triggers.

### **3.2 Data Ingestion Layer**

* **Sources:**
* **Olist E-Commerce Data:** Historical transaction data (Orders, Items, Customers).
* **Weather API:** Historical and forecast weather data for key logistics regions.
* **ScraperDog:** Custom scraping agents that fetch real-time competitor pricing from major marketplaces.


* **Processing:**
* **Apache Spark:** Performs distributed data fetching and initial formatting.
* **AWS S3 (Data Lake):** Acts as the landing zone for raw data (Parquet/JSON/CSV formats), ensuring durability and creating a "Bronze" data layer.



### **3.3 Data Warehousing & Transformation**

* **Snowflake:** The central data warehouse.
* *Raw Schema:* Direct loading from S3 via Storage Integrations.
* *Analytics Schema:* Cleaned and enriched data.


* **dbt (Data Build Tool):** Handles the "T" in ELT.
* **The "Time Travel" Transformation:** A custom logic layer that shifts historical 2017 transaction timestamps forward by ~2,800 days. This aligns legacy training data with current 2026 competitor and weather data, simulating a "live" environment for the model.
* **One-Big-Table (OBT):** Joins Sales + Weather + Competitor Benchmarks into a single denormalized structure for high-performance ML training.



### **3.4 Machine Learning Core**

* **Model:** XGBoost Regressor.
* **Objective:** Predict `Quantity_Sold` based on `Price`, `Competitor_Price_Ratio`, `Weather_Condition`, and `Seasonality`.
* **Safety Mechanism (Monotonic Constraints):** The model is constrained to ensure economic validity. It strictly enforces that as Price increases, Demand must either decrease or stay flat. This prevents the model from hallucinating illogical pricing strategies (e.g., "Infinity price = Infinity demand").

### **3.5 Application Layer**

* **Backend (FastAPI):** Exposes the ML model and historical data via REST endpoints.
* `POST /predict`: Real-time demand inference.
* `GET /history`: Low-latency retrieval of cached analytics data (Parquet).


* **Frontend (Reflex):** A reactive Python-based Single Page Application (SPA).
* **Scenario Simulator:** Allows users to adjust price sliders and see instant revenue impact.
* **Visual Analytics:** interactive line charts comparing internal vs. competitor pricing over time.



---

## 4. Key Features & Innovations

### 🌦️ The "Storm Surge" Engine

Exploratory Data Analysis (EDA) revealed a strong correlation between precipitation and specific product categories (e.g., +20.5% lift in Electronics sales during rain). The engine detects "Rain" in the weather forecast and automatically adjusts the recommended margin to capture this high-intent demand.

### ⏳ Temporal Data Shifting

To bridge the gap between high-quality open-source datasets (often dated) and the need for modern context (current competitor prices), the pipeline implements a robust date-shifting algorithm. This allows the system to simulate realistic 2026 market scenarios using 2017 behavioral patterns.

### 🛡️ Economic Guardrails

Unlike generic ML models, this engine prioritizes business safety. By applying monotonic constraints to the XGBoost estimator, we guarantee that the model never recommends a price hike that would theoretically increase sales volume—a common artifact in unconstrained ML models that destroys trust with business stakeholders.

---

## 5. Technology Stack Summary

| Domain | Technology | Usage |
| --- | --- | --- |
| **Language** | Python 3.10+ | Core logic, ML, Scripting |
| **Cloud** | AWS (S3) | Object Storage / Data Lake |
| **Warehouse** | Snowflake | Storage, Compute, SQL Transformation |
| **Transformation** | dbt Core | Modeling, Testing, Lineage |
| **Orchestration** | Apache Airflow | Workflow Management |
| **Infrastructure** | Terraform | Infrastructure as Code |
| **Machine Learning** | XGBoost, Scikit-Learn | Predictive Modeling |
| **API Framework** | FastAPI | Model Serving & Data Access |
| **Frontend** | Reflex | Interactive Dashboard |

---

## 6. Setup & Installation

*(Prerequisites: Docker, Snowflake Account, AWS Credentials)*

1. **Provision Infrastructure:**
```bash
cd infrastructure
terraform init && terraform apply

```


2. **Run Data Pipeline:**
* Trigger Airflow DAGs to ingest S3 data to Snowflake.
* Run `dbt run` to build the OBT.


3. **Train Model:**
* Execute `notebooks/ml_training.ipynb` to generate `revenue_model.pkl`.


4. **Launch Application:**
```bash
# Backend
uvicorn backend.app.main:app --reload

# Frontend
reflex run

```



---

## 7. Future Roadmap

* **A/B Testing Module:** Implement a feedback loop to compare model recommendations against a control group (manual pricing).
* **Real-time Streaming:** Upgrade ingestion from batch (Airflow) to streaming (Kafka/Snowpipe) for instant competitor price reaction.
* **Kubernetes Deployment:** Migrate from local Docker to EKS for scalable model serving.