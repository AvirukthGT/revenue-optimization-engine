# 1. The Compute Warehouse
resource "snowflake_warehouse" "compute_wh" {
  name           = "COMPUTE_WH"
  warehouse_size = "x-small"
  auto_suspend   = 60
  auto_resume    = true
  comment        = "Main compute resource for ingestion and dbt models."
}

# 2. The Database
resource "snowflake_database" "db" {
  name    = "DYNAMIC_PRICING"
  comment = "Central database for the Revenue Optimization Engine."
}

# 3. The Schemas (Architecture Layers)
resource "snowflake_schema" "raw_schema" {
  database = snowflake_database.db.name
  name     = "RAW"
  comment  = "Landing zone for immutable source data."
}

resource "snowflake_schema" "analytics_schema" {
  database = snowflake_database.db.name
  name     = "ANALYTICS"
  comment  = "Transformed tables ready for BI and ML."
}

# 4. Service User (Best Practice for Airflow/dbt)
resource "snowflake_user" "service_user" {
  name         = "SVC_AIRFLOW"
  login_name   = "SVC_AIRFLOW"
  comment      = "Service account for automated pipelines"
  default_role = "SYSADMIN"
  password     = "ChangeMeInProduction123!" #chnged in production
}