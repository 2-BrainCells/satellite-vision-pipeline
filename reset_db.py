import asyncio
import asyncpg
from app import DATABASE_URL

async def reset():
    print(f"Connecting to {DATABASE_URL}...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        print("Clearing all data from 'aois' and 'alerts' tables...")
        # TRUNCATE empties the tables, RESTART IDENTITY resets the IDs back to 1, CASCADE handles foreign keys.
        await conn.execute("TRUNCATE TABLE alerts, aois RESTART IDENTITY CASCADE;")
        
        print("\nSUCCESS! All database history has been permanently deleted.")
        print("You are now ready to start completely fresh!")
        
        await conn.close()
    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == '__main__':
    asyncio.run(reset())
