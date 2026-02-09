SELECT
    asin,
    price,
    scraped_at,
    -- Create a simplified date column for joining
    DATE(scraped_at) as scraped_date
FROM {{ source('dynamic_pricing', 'competitor_prices') }}