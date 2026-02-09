WITH sales_joined AS (
    SELECT 
        DATE(o.order_purchase_timestamp) as sales_date,
        p.category_name,
        SUM(oi.unit_price) as total_revenue,
        COUNT(DISTINCT o.order_id) as total_orders
    FROM {{ ref('stg_orders') }} o
    JOIN {{ ref('stg_order_items') }} oi ON o.order_id = oi.order_id
    JOIN {{ ref('stg_products') }} p ON oi.product_id = p.product_id
    GROUP BY 1, 2
),

benchmarks AS (
    SELECT * FROM {{ ref('category_benchmarks') }}
),

final_dataset AS (
    SELECT
        s.sales_date,
        s.category_name,
        s.total_revenue,
        s.total_orders,
        
        -- Competitor Data
        b.benchmark_product_name,
        cp.price as competitor_price,
        
        -- Weather Data
        w.temperature_c,
        w.condition as weather_condition
        
    FROM sales_joined s
    -- 1. Filter to only categories we track
    JOIN benchmarks b ON s.category_name = b.olist_category_name
    
    -- 2. Join Competitor Prices (on Date + ASIN)
    LEFT JOIN {{ ref('stg_competitor_prices') }} cp 
        ON b.benchmark_asin = cp.asin 
        AND s.sales_date = cp.scraped_date
        
    -- 3. Join Weather (on Date)
    LEFT JOIN {{ ref('stg_weather') }} w
        ON s.sales_date = w.weather_date
)

SELECT * FROM final_dataset
WHERE competitor_price IS NOT NULL -- Removing days where we have no price history
ORDER BY sales_date DESC