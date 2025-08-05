import asyncio
import asyncpg

async def create_database():
    try:
        # Connect to the default 'postgres' database to run the CREATE DATABASE command
        conn = await asyncpg.connect(
            user='p2p_user',
            password='iiot123',
            database='postgres', # Connect to the default db
            host='localhost',
            port=5432
        )

        # Check if the 'supertokens' database already exists
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = 'supertokens'")

        if not exists:
            print("Database 'supertokens' does not exist. Creating it now...")
            await conn.execute('CREATE DATABASE supertokens')
            print("✅ Database 'supertokens' created successfully.")
        else:
            print("✅ Database 'supertokens' already exists.")

        await conn.close()

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(create_database())