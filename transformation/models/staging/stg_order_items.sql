SELECT
    order_id,
    product_id,
    price as unit_price
FROM {{ source('dynamic_pricing', 'order_items') }}