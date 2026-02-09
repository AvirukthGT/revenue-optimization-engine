import random
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType
import os
from dotenv import load_dotenv

# Let's get this party started by loading the config
load_dotenv()
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")

# --- KNOBS AND DIALS ---
NUM_DAYS_HISTORY = 90
PRODUCTS = [
    # Laptops
    {"asin": "B08N5M7S6K", "base_price": 999.00}, {"asin": "B09J1LPLCP", "base_price": 1999.00},
    {"asin": "B09H22V47W", "base_price": 950.00}, {"asin": "B08X1W9G7P", "base_price": 1200.00},
    {"asin": "B09R65RN43", "base_price": 1400.00},
    # Headphones
    {"asin": "B08N5KWB9H", "base_price": 348.00}, {"asin": "B0988KZVG6", "base_price": 329.00},
    {"asin": "B0D1XD1ZV3", "base_price": 169.00}, {"asin": "B07G4C6XW5", "base_price": 250.00},
    {"asin": "B0935D8H93", "base_price": 199.00},
    # Cameras
    {"asin": "B08HMS1D9S", "base_price": 399.00}, {"asin": "B08KSM5C6X", "base_price": 2499.00},
    {"asin": "B08L5TNJHG", "base_price": 1999.00}, {"asin": "B08J5F3G18", "base_price": 2498.00},
    {"asin": "B01M14ATO0", "base_price": 599.00},
    # Smart Home
    {"asin": "B07H65KP63", "base_price": 39.99}, {"asin": "B08F6WARW7", "base_price": 99.99},
    {"asin": "B08W8G87ZJ", "base_price": 179.99}, {"asin": "B07XJ8C8F5", "base_price": 199.99},
    {"asin": "B07WHD2H75", "base_price": 35.98},
    # Wearables
    {"asin": "B09G9FPHP6", "base_price": 599.00}, {"asin": "B09V3HMKS5", "base_price": 799.00},
    {"asin": "B09T8F2C7K", "base_price": 399.00}, {"asin": "B08H73456P", "base_price": 699.00},
    {"asin": "B07WHQY27X", "base_price": 149.95}
]

def get_spark_session():
    return SparkSession.builder \
        .appName("BackfillHistory") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4") \
        .config("spark.hadoop.fs.s3a.access.key", AWS_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", AWS_SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
        .getOrCreate()

def generate_history():
    data = []
    end_date = datetime.now()
    
    print(f"Generating {NUM_DAYS_HISTORY} days of history for {len(PRODUCTS)} products...")

    for product in PRODUCTS:
        current_price = product['base_price']
        
        for i in range(NUM_DAYS_HISTORY):
            # Back to the future... wait, no, back to the past.
            date_point = end_date - timedelta(days=i)
            
            # Make the price wiggle a bit (Random Walk)
            # Shake it up by +/- 2% because stability is for statues
            change_percent = random.uniform(-0.02, 0.02)
            current_price = current_price * (1 + change_percent)
            
            # FLASH SALE! Everything must go! (well, 5% off anyway)
            if i % 14 == 0:
                current_price = current_price * 0.95
                
            # Whoa there, let's not give it away for free. Floor is 50%.
            if current_price < (product['base_price'] * 0.5):
                current_price = product['base_price'] * 0.5

            data.append({
                "asin": product['asin'],
                "price": round(current_price, 2),
                "currency": "USD",
                "scraped_at": date_point
            })
            
    return data

def main():
    spark = get_spark_session()
    
    # 1. Cook up some fake history
    historical_data = generate_history()
    
    # 2. Stuff it into a DataFrame
    schema = StructType([
        StructField("asin", StringType(), True),
        StructField("price", FloatType(), True),
        StructField("currency", StringType(), True),
        StructField("scraped_at", TimestampType(), True)
    ])
    
    df = spark.createDataFrame(historical_data, schema=schema)
    
    print(f"Generated {df.count()} rows. Sample:")
    df.show(5)
    
    # 3. Yeet to S3 (Parquet)
    # Stashing strictly historical data in its own folder to avoid timeline paradoxes.
    s3_path = f"s3a://{S3_BUCKET}/competitors/pricing/" 
    
    print(f"Writing backfill data to {s3_path}...")
    df.write.mode("append").parquet(s3_path)
    print("Backfill Complete!")
    
    spark.stop()

if __name__ == "__main__":
    main()