import os
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

def provision_real_database():
    print("🚀 [1/3] Loading REAL Education Dataset from Local CSV...")
    
    # Place the CSV you downloaded into your data/ folder, or change this string 
    # to perfectly match the location of your downloaded file!
    csv_path = "data/school_demographics.csv"
    
    print(f"📥 Reading local CSV data from: {csv_path}")
    # pandas natively parses the CSV from your hard drive
    df = pd.read_csv(csv_path)
    
    # Clean the column names to be BigQuery friendly (BigQuery hates spaces and % signs)
    df.columns = df.columns.str.replace(r'[^a-zA-Z0-9_]', '_', regex=True).str.lower()
    
    print(f"📊 Downloaded {len(df)} real school records. Formatting schema for Google Cloud...")
    
    # AI/SQL databases need clean numbers, so we fill missing holes with zeroes
    df = df.fillna(0)
    
    # Schema Configuration for your specific GCC Trial Account
    PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    DATASET_ID = "hackathon_education"
    TABLE_ID = "school_demographics"
    full_table_id = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    
    print("☁️ [2/3] Authenticating securely with Google Cloud BigQuery...")
    # This automatically uses the GOOGLE_APPLICATION_CREDENTIALS from your .env
    client = bigquery.Client(project=PROJECT_ID)
    
    # Build Dataset Container
    dataset = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
    dataset.location = "US"
    try:
        client.create_dataset(dataset, exists_ok=True)
        print(f"✅ Verified BigQuery Dataset: {DATASET_ID}")
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR CREATING DATASET: {e}")
        raise e

    print(f"⬆️ [3/3] Uploading DataFrame to BigQuery Table: {TABLE_ID}...")
    
    # WRITE_TRUNCATE means if you run this script twice, it replaces the old table
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    
    # Push data mathematically to Google Cloud
    job = client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
    job.result() # Pauses Python until the Cloud confirms it received the data
    
    table = client.get_table(full_table_id)
    print(f"🎉 SUCCESS! Wrote {table.num_rows} real records to physical BigQuery.")

if __name__ == "__main__":
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        print("❌ ERROR: GOOGLE_APPLICATION_CREDENTIALS not found in .env!")
    else:
        provision_real_database()
