WITH source_data AS (
    SELECT * FROM {{ source('dynamic_pricing', 'order_items') }}
)

SELECT
    order_id,
    product_id,
    -- 1. CURRENCY FIX: 
    -- In 2017, 1 USD = ~3.2 BRL. Let's convert Olist prices to USD.
    (price / 3.2) as unit_price,
    
    freight_value
FROM source_data
-- 2. "JUNK" FILTER:
-- Only keep items that cost more than 150 BRL (~$45 USD).
-- This removes phone cases, mousepads, and cheap cables.
WHERE price > 150