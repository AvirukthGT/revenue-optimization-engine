SELECT
    order_id,
    customer_id,
    order_status,
    -- TIME TRAVEL LOGIC:
    -- Shifting dates forward by ~2800 days to match scraped data range
    DATEADD(day, 2800, order_purchase_timestamp) as order_purchase_timestamp
FROM {{ source('dynamic_pricing', 'orders') }}
WHERE order_status = 'delivered'