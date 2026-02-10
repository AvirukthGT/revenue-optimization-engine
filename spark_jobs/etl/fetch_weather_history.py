import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry

# 1. Setup Client
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# 2. Define Request (Melbourne, Past 90 Days)
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": -23.5505,   # <--- Updated for Sao Paulo
    "longitude": -46.6333,  # <--- Updated for Sao Paulo
    "start_date": "2025-11-01", 
    "end_date": "2026-02-09",
    "daily": ["temperature_2m_max", "precipitation_sum"],
    "timezone": "America/Sao_Paulo" # <--- Updated Timezone
}

# 3. Fetch Data
responses = openmeteo.weather_api(url, params=params)
response = responses[0]

# 4. Process into CSV
daily = response.Daily()
daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
daily_precipitation_sum = daily.Variables(1).ValuesAsNumpy()

dates = pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)

weather_df = pd.DataFrame({
	"date": dates,
	"city": "Sao Paulo",
	"temperature_c": daily_temperature_2m_max,
	"precipitation_mm": daily_precipitation_sum
})

# Add a simple condition label
weather_df['condition'] = weather_df['precipitation_mm'].apply(lambda x: 'Rain' if x > 1.0 else 'Clear')

# Save
weather_df.to_csv("weather_history.csv", index=False)
print("Weather history generated: weather_history.csv")