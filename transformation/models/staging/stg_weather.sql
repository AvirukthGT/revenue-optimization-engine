SELECT
    date as weather_date,
    temperature_c,
    precipitation_mm,
    condition
FROM {{ source('dynamic_pricing', 'weather') }}