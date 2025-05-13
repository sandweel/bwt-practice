import socket
import time
import sys
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
RETRIES = 5
DELAY = 1

for i in range(RETRIES):
    try:
        with socket.create_connection((DB_HOST, DB_PORT), timeout=2):
            print("✅ Database is available.")
            sys.exit(0)
    except OSError:
        print(f"⏳ Attempt {i + 1}/{RETRIES}: PostgreSQL not available at {DB_HOST}:{DB_PORT}, retrying in {DELAY}s...")
        time.sleep(DELAY)

print("❌ Could not connect to the database. Exiting.")
sys.exit(1)
