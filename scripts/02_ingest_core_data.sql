/* ===========================================================================
REVENUE OPTIMIZATION ENGINE - CORE DATA INGESTION
Author: [AvirukthGT]
Description: 
  This script loads the historical Olist e-commerce data and external weather data.
  Crucially, it includes the 'Time Travel' logic to shift 2017 sales data into 
  2025/2026, allowing me to simulate a "live" pricing environment.
===========================================================================
*/

USE SCHEMA DYNAMIC_PRICING.RAW;

-- ------------------------------------------------------------------------
-- STEP 1: DEFINE EXTERNAL STAGES
-- ------------------------------------------------------------------------
-- I create specific stages for each data source to keep things modular.
-- Re-using the 's3_int' integration I created in script 01.

-- Stage for Olist E-commerce Data (Parquet/CSV depending on source)
CREATE OR REPLACE STAGE olist_pricing_stage
  URL = 's3://de-project-dynamic-pricing-raw-source/olist/'
  STORAGE_INTEGRATION = s3_int
  FILE_FORMAT = (TYPE = CSV, FIELD_OPTIONALLY_ENCLOSED_BY = '"', SKIP_HEADER = 1); 
  -- Note: Adjusted file format to CSV based on the COPY command below.

-- Stage for Weather Data
CREATE OR REPLACE STAGE weather_stage
  URL = 's3://de-project-dynamic-pricing-raw-source/weather/'
  STORAGE_INTEGRATION = s3_int
  FILE_FORMAT = (TYPE = CSV, SKIP_HEADER = 1);


-- ------------------------------------------------------------------------
-- STEP 2: RAW TABLE DDL (SCHEMA DEFINITION)
-- ------------------------------------------------------------------------
-- 1. Orders: The central fact table (Who bought what and when).
CREATE OR REPLACE TABLE orders (
    order_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR,
    order_status VARCHAR,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

-- 2. Order Items: The details (Price, Quantity, Freight).
CREATE OR REPLACE TABLE order_items (
    order_id VARCHAR,
    order_item_id INT,
    product_id VARCHAR,
    seller_id VARCHAR,
    shipping_limit_date TIMESTAMP,
    price FLOAT,
    freight_value FLOAT
);

-- 3. Products: Dimension table (Dimensions, Category).
CREATE OR REPLACE TABLE products (
    product_id VARCHAR PRIMARY KEY,
    product_category_name VARCHAR,
    product_name_lenght INT,
    product_description_lenght INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT
);

-- 4. Weather: External signal table (Temperature, Rain).
CREATE OR REPLACE TABLE weather (
    date DATE,
    city VARCHAR,
    temperature_c FLOAT,
    precipitation_mm FLOAT,
    condition VARCHAR
);


-- ------------------------------------------------------------------------
-- STEP 3: DATA LOADING (COPY INTO)
-- ------------------------------------------------------------------------
-- I use pattern matching to ensure I only load the correct files from S3 folders.

-- Load Orders
COPY INTO DYNAMIC_PRICING.RAW.orders
FROM @olist_pricing_stage
PATTERN = '.*orders.*.csv' -- Adjusted pattern to be safer
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1, FIELD_OPTIONALLY_ENCLOSED_BY = '"');

-- Load Order Items
COPY INTO DYNAMIC_PRICING.RAW.order_items
FROM @olist_pricing_stage
PATTERN = '.*order_items.*.csv'
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1);

-- Load Products
COPY INTO DYNAMIC_PRICING.RAW.products
FROM @olist_pricing_stage
PATTERN = '.*products.*.csv'
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1, FIELD_OPTIONALLY_ENCLOSED_BY = '"');

-- Load Weather
COPY INTO DYNAMIC_PRICING.RAW.weather
FROM @weather_stage
PATTERN = '.*weather.*.csv'
FILE_FORMAT = (TYPE = 'CSV', SKIP_HEADER = 1);


-- ------------------------------------------------------------------------
-- STEP 4: MAPPING & BENCHMARKING
-- ------------------------------------------------------------------------
-- Quick check to see which categories have the most data.
SELECT 
    product_category_name, 
    COUNT(*) as total_sales
FROM DYNAMIC_PRICING.RAW.products p
JOIN DYNAMIC_PRICING.RAW.order_items oi ON p.product_id = oi.product_id
GROUP BY 1
ORDER BY 2 DESC;

-- I create a manual mapping table to link broad Olist categories (e.g., 'telefonia')
-- to specific real-world products I scraped (e.g., 'Samsung S22').
CREATE OR REPLACE TABLE DYNAMIC_PRICING.RAW.category_benchmarks (
    olist_category_name VARCHAR, -- The Portuguese name from Olist
    benchmark_asin VARCHAR,      -- The specific ASIN I scraped
    benchmark_name VARCHAR       -- Human readable reference
);

-- Seeding the mapping table with my chosen benchmark products.
INSERT INTO DYNAMIC_PRICING.RAW.category_benchmarks VALUES
('informatica_acessorios', 'B08N5M7S6K', 'MacBook Air M1'),
('telefonia', 'B09V3HMKS5', 'Samsung Galaxy S22'),
('relogios_presentes', 'B0D1XD1ZV3', 'Apple Watch Series 9'),
('audio', 'B08N5KWB9H', 'Sony WH-1000XM4'),
('eletronicos', 'B08J5F3G18', 'Sony Alpha a7 IV');

-- Validation: Check how many sales rows map to these benchmarks.
SELECT 
    b.benchmark_name,
    COUNT(oi.order_id) as total_sales_rows_linked
FROM DYNAMIC_PRICING.RAW.order_items oi
JOIN DYNAMIC_PRICING.RAW.products p ON oi.product_id = p.product_id
JOIN DYNAMIC_PRICING.RAW.category_benchmarks b 
    ON p.product_category_name = b.olist_category_name
GROUP BY 1
ORDER BY 2 DESC;


-- ------------------------------------------------------------------------
-- STEP 5: THE TIME MACHINE (DATA SHIFT)
-- ------------------------------------------------------------------------
-- Olist data is from 2017. To make the dashboard feel "Live", I shift the dates
-- forward by ~8 years (2800 days). This aligns the old sales patterns with
-- the current dates of my scraped competitor data.

CREATE OR REPLACE VIEW DYNAMIC_PRICING.RAW.orders_current AS
SELECT 
    order_id,
    customer_id,
    order_status,
    -- Time Shift Logic: 2017 -> 2025/2026
    DATEADD(day, 2800, order_purchase_timestamp) as order_purchase_timestamp
FROM DYNAMIC_PRICING.RAW.orders;

-- Final Verification: Joining the Time-Shifted Sales with Live Competitor Prices
SELECT 
    -- 1. The Sales Info (Now in 2026)
    DATE(o.order_purchase_timestamp) as sale_date,
    b.benchmark_name as category_benchmark,
    
    -- 2. The Volume (How many we sold)
    COUNT(oi.order_id) as total_items_sold,
    
    -- 3. The Competitor Price (From my Scraper)
    AVG(cp.price) as avg_competitor_price

FROM DYNAMIC_PRICING.RAW.order_items oi
-- Join to the TIME SHIFTED orders view
JOIN DYNAMIC_PRICING.RAW.orders_current o ON oi.order_id = o.order_id
JOIN DYNAMIC_PRICING.RAW.products p ON oi.product_id = p.product_id

-- Join to the Category Map
JOIN DYNAMIC_PRICING.RAW.category_benchmarks b 
    ON p.product_category_name = b.olist_category_name

-- Join to the Scraped Prices (Matching the new shifted date!)
JOIN DYNAMIC_PRICING.RAW.competitor_prices cp
    ON b.benchmark_asin = cp.asin 
    AND DATE(o.order_purchase_timestamp) = DATE(cp.scraped_at)

GROUP BY 1, 2
ORDER BY 1 DESC;