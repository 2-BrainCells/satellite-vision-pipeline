import asyncio
import asyncpg
from urllib.parse import urlparse
import sys

# Replace with your actual postgres connection string
# E.g., postgresql://username:password@localhost:5432/satellite_db
DB_URL = "postgresql://postgres:Hello@localhost:5432/satellite_db"

async def init_db():
    print(f"Attempting to connect to {DB_URL}...")
    try:
        conn = await asyncpg.connect(DB_URL)
    except Exception as e:
        print(f"Error connecting to database. Please ensure PostgreSQL is running and the URL is correct.")
        print(f"Details: {e}")
        # Hint for creating db if it doesn't exist
        print("\nIf the database 'satellite_db' does not exist, create it using pgAdmin or a SQL client.")
        sys.exit(1)
        
    print("Executing schema setup...")
    try:
        with open("../database/schema.sql", "r") as f:
            schema_sql = f.read()
        await conn.execute(schema_sql)
        print("Schema successfully applied!")
    except Exception as e:
        print(f"Error creating schema: {e}")
        print("Ensure that the PostGIS extension is installed on your PostgreSQL server.")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(init_db())
