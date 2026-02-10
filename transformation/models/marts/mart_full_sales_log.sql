{{ config(
    materialized='table',
    schema='marts'
) }}

WITH sales_items AS (
    SELECT 
        oi.order_id,
        oi.product_id,
        oi.unit_price,
        o.order_purchase_timestamp,
        DATE(o.order_purchase_timestamp) as sales_date,
        p.category_name
    FROM {{ ref('stg_order_items') }} oi
    JOIN {{ ref('stg_orders') }} o ON oi.order_id = o.order_id
    JOIN {{ ref('stg_products') }} p ON oi.product_id = p.product_id
),

benchmarks AS (
    SELECT * FROM {{ ref('category_benchmarks') }}
),

final_enrichment AS (
    SELECT
        -- IDs & Core Sales Data
        s.order_id,
        s.product_id,
        s.sales_date,
        s.order_purchase_timestamp,
        s.category_name,
        s.unit_price as our_price,
        
        -- Competitor Context
        b.benchmark_product_name,
        cp.price as competitor_price,
        
        -- Calculated Feature: Price Difference
        (s.unit_price - cp.price) as price_diff,
        
        -- Weather Context
        w.temperature_c,
        w.condition as weather_condition,
        w.precipitation_mm

    FROM sales_items s
    -- 1. Link to Benchmark Product
    INNER JOIN benchmarks b ON s.category_name = b.olist_category_name
    
    -- 2. Link to Competitor Price History (Specific to that Day)
    INNER JOIN {{ ref('stg_competitor_prices') }} cp 
        ON b.benchmark_asin = cp.asin 
        AND s.sales_date = cp.scraped_date
        
    -- 3. Link to Weather History (Specific to that Day)
    LEFT JOIN {{ ref('stg_weather') }} w
        ON s.sales_date = w.weather_date
)

SELECT * FROM final_enrichment