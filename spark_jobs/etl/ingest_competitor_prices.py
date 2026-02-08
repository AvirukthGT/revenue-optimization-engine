import requests
import json
import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType
from datetime import datetime
from dotenv import load_dotenv

# 1. Load Environment Variables (API Keys)
load_dotenv()
API_KEY = os.getenv("SCRAPINGDOG_API_KEY")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")

# 2. Define the Target (For this test, we hardcode one Amazon ASIN)
# In the full pipeline, this list will come from your Olist database.
TARGET_PRODUCT_ASIN = "B0D1XD1ZV3" # Example: A Seiko Watch
TARGET_MARKETPLACE = "amazon.com"

def get_spark_session():
    """
    Creates a Spark Session with AWS S3 support.
    We need to download the 'hadoop-aws' jar at runtime to talk to S3.
    """
    return SparkSession.builder \
        .appName("CompetitorPricingIngestion") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4") \
        .config("spark.hadoop.fs.s3a.access.key", AWS_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", AWS_SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
        .getOrCreate()

def fetch_price(asin):
    """
    Hits the ScrapingDog API to get Amazon data.
    """
    url = "https://api.scrapingdog.com/scrape"
    params = {
        "api_key": API_KEY,
        "url": f"https://www.amazon.com/dp/{asin}",
        "dynamic": "false" # Set to true if Amazon blocks us (uses credits)
    }
    
    print(f"Fetching data for ASIN: {asin}...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # Note: In a real project, we would parse the HTML here with BeautifulSoup.
        # For simplicity, we will assume we get the raw HTML and simulate extraction
        # OR if you use ScrapingDog's 'Amazon Product API', you get JSON.
        # Let's mock the return for this specific test to ensure Spark works.
        return {
            "asin": asin,
            "price": 199.99, # Mocked for connection test
            "currency": "USD",
            "scraped_at": datetime.now()
        }
    else:
        print(f"Failed to fetch. Status: {response.status_code}")
        print(f"Error Message: {response.text}") # <--- ADD THIS LINE
        return None

def main():
    spark = get_spark_session()
    
    # 3. Fetch Data
    data = fetch_price(TARGET_PRODUCT_ASIN)
    
    if data:
        # 4. Create DataFrame
        # We explicitly define schema to be safe
        schema = StructType([
            StructField("asin", StringType(), True),
            StructField("price", FloatType(), True),
            StructField("currency", StringType(), True),
            StructField("scraped_at", TimestampType(), True)
        ])
        
        df = spark.createDataFrame([data], schema=schema)
        df.show()
        
        # 5. Write to S3 (Parquet format is best for Snowflake)
        # Using 'append' so we build history over time
        s3_path = f"s3a://{S3_BUCKET}/competitors/pricing/"
        print(f"Writing data to {s3_path}...")
        
        df.write.mode("append").parquet(s3_path)
        print("Success! Data written to S3.")
        
    spark.stop()

if __name__ == "__main__":
    main()