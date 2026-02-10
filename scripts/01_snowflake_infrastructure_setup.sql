/* ===========================================================================
REVENUE OPTIMIZATION ENGINE - SNOWFLAKE INFRASTRUCTURE SETUP
Author: [AvirukthGT]
Description: 
  This script bootstraps the Snowflake environment for my Dynamic Pricing project.
  It handles the secure connection to AWS S3, sets up the compute warehouse,
  and defines the raw data layer for ingestion.
===========================================================================
*/

-- ------------------------------------------------------------------------
-- STEP 1: COMPUTE & STORAGE CONTAINER SETUP
-- ------------------------------------------------------------------------
-- I need to switch to ACCOUNTADMIN to create top-level integrations and databases.
USE ROLE ACCOUNTADMIN;

-- I create a dedicated X-Small warehouse to keep costs low while handling
-- the initial data ingestion workloads.
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;

-- I establish the main database for the project.
CREATE DATABASE IF NOT EXISTS DYNAMIC_PRICING;

-- I create the Schema Architecture:
-- 1. RAW: To hold the immutable data exactly as it arrives from S3.
CREATE SCHEMA IF NOT EXISTS DYNAMIC_PRICING.RAW;
-- 2. ANALYTICS: To hold the transformed data ready for the dashboard (populated later by dbt).
CREATE SCHEMA IF NOT EXISTS DYNAMIC_PRICING.ANALYTICS;

-- Set the active context for the following commands.
USE DATABASE DYNAMIC_PRICING;
USE SCHEMA RAW;


-- ------------------------------------------------------------------------
-- STEP 2: SECURE INTEGRATION (AWS S3 HANDSHAKE)
-- ------------------------------------------------------------------------
-- I create a Storage Integration object to generate an IAM User for Snowflake.
-- This allows me to access my S3 bucket without hardcoding AWS keys in the script.
CREATE OR REPLACE STORAGE INTEGRATION s3_int
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  -- Placeholder ARN initially; I will update this after getting the external_id
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::000000000000:role/placeholder_role' 
  STORAGE_ALLOWED_LOCATIONS = ('s3://de-project-dynamic-pricing-raw-source/');

-- I run this command to retrieve the 'STORAGE_AWS_IAM_USER_ARN' and 'STORAGE_AWS_EXTERNAL_ID'
-- needed to configure the Trust Relationship in AWS IAM.
DESC INTEGRATION s3_int;

-- Once I have updated the AWS IAM Role trust policy, I update the integration 
-- with the correct Role ARN.
ALTER STORAGE INTEGRATION s3_int 
SET STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::982081062053:role/Snowflake_S3_Connection_Role';


-- ------------------------------------------------------------------------
-- STEP 3: STAGE CREATION & VALIDATION
-- ------------------------------------------------------------------------
-- I create an external stage pointing specifically to the competitor pricing data.
-- This acts as a window into the S3 bucket.
CREATE OR REPLACE STAGE competitors_pricing_stage
  URL = 's3://de-project-dynamic-pricing-raw-source/competitors/pricing/'
  STORAGE_INTEGRATION = s3_int
  FILE_FORMAT = (TYPE = PARQUET);

-- Verification step: I list the files to ensure the connection to S3 is successful.
LIST @competitors_pricing_stage;


-- ------------------------------------------------------------------------
-- STEP 4: RAW TABLE DDL & INGESTION
-- ------------------------------------------------------------------------
-- I define the raw table structure to capture the scraping data.
-- I added 'load_timestamp' to track data freshness and lineage.
CREATE OR REPLACE TABLE competitor_prices (
    asin STRING,
    price FLOAT,
    currency STRING,
    scraped_at TIMESTAMP,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- I load the Parquet data into the structured Snowflake table.
-- Using 'ON_ERROR = CONTINUE' ensures the pipe doesn't break on a single bad record.
COPY INTO competitor_prices (asin, price, currency, scraped_at)
FROM (
    SELECT 
        $1:asin::STRING,
        $1:price::FLOAT,
        $1:currency::STRING,
        $1:scraped_at::TIMESTAMP
    FROM @competitors_pricing_stage
)
FILE_FORMAT = (TYPE = 'PARQUET')
ON_ERROR = 'CONTINUE';

-- Final check to validate that data has been loaded correctly.
SELECT * FROM competitor_prices;