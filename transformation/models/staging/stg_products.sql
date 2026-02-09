SELECT
    product_id,
    product_category_name as category_name
FROM {{ source('dynamic_pricing', 'products') }}