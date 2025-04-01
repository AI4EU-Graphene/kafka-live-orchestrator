import asyncio
import aiohttp
import pandas as pd
import os
import json
from datetime import datetime, timedelta
from kafka import KafkaProducer

# --- CONFIGURATION ---
BASE_URL = "https://www.smartgriddashboard.com/DashboardService.svc/data"
KAFKA_TOPIC = "raw_data"
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
REGION = "ALL"
AREA = "demandactual"
FIELDNAME = "SYSTEM_DEMAND"
DAYS_BACK = 180

# --- OUTPUT FOLDER ---
OUTPUT_DIR = "Downloaded_Data"
os.makedirs(OUTPUT_DIR, exist_ok=True)
COMBINED_FILE = os.path.join(OUTPUT_DIR, "Combined_ALL_ROI_NI_pivoted_24.csv")

# --- KAFKA PRODUCER ---
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

async def fetch_chunk(session, start, end):
    params = {
        "area": AREA,
        "region": REGION,
        "datefrom": start.strftime("%d-%b-%Y 00:00"),
        "dateto": end.strftime("%d-%b-%Y 23:59")
    }
    try:
        async with session.get(BASE_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get("Rows", [])
    except Exception as e:
        print(f"Error fetching chunk {start} to {end}: {e}")
        return []

async def fetch_data():
    today = datetime.today()
    start_date = today - timedelta(days=DAYS_BACK)

    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(0, DAYS_BACK, 7):  # Weekly chunks
            chunk_start = start_date + timedelta(days=i)
            chunk_end = min(chunk_start + timedelta(days=6), today)
            tasks.append(fetch_chunk(session, chunk_start, chunk_end))

        results = await asyncio.gather(*tasks)
        all_rows = [item for sublist in results for item in sublist if "Value" in item and item["Value"] is not None]
        return all_rows

def transform_data(raw_rows):
    data = [
        {
            "Timestamp": row["EffectiveTime"],
            "Type": row["FieldName"],
            "Region": row["Region"],
            "Value": row["Value"]
        }
        for row in raw_rows
    ]
    df = pd.DataFrame(data)
    if df.empty:
        raise ValueError("No valid rows with 'Value' found in the data.")

    pivot_df = df.pivot_table(index="Timestamp", columns="Type", values="Value", aggfunc="mean").reset_index()
    return pivot_df

def send_to_kafka(df):
    for _, row in df.iterrows():
        message = row.to_dict()
        producer.send(KAFKA_TOPIC, value=message)
    producer.flush()

def fetch_and_send_demand_data():
    if os.path.exists(COMBINED_FILE):
        print("🟡 Data already exists. Skipping download.")
        return "skipped"

    print("🟢 Downloading fresh data...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    raw_data = loop.run_until_complete(fetch_data())

    df = transform_data(raw_data)
    df.to_csv(COMBINED_FILE, index=False)
    print(f"✅ Saved CSV: {COMBINED_FILE}")

    send_to_kafka(df)
    print(f"✅ Published {len(df)} messages to Kafka topic '{KAFKA_TOPIC}'")
    return "success"

if __name__ == "__main__":
    fetch_and_send_demand_data()
