import asyncio
import sys
import os
import httpx

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager, get_db
from app.services.database_service import UserService
from app.models.mongo_models import User as MongoUser
from app.models.pg_models import User as PGUser
from app.core.logging import setup_logging
from sqlalchemy import select, delete

async def create_supertokens_user(email: str, password: str, first_name: str, last_name: str, logger):
    """Create a user via SuperTokens API and return the user ID"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/api/v1/auth/signup",
                headers={"Content-Type": "application/json"},
                json={
                    "formFields": [
                        {"id": "email", "value": email},
                        {"id": "password", "value": password},
                        {"id": "firstName", "value": first_name},
                        {"id": "lastName", "value": last_name}
                    ]
                }
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "OK":
                    supertokens_user_id = result["user"]["id"]
                    logger.info(f"✅ Created SuperTokens user: {email} (ID: {supertokens_user_id})")
                    return supertokens_user_id
        logger.error(f"❌ SuperTokens signup failed for {email}: {response.text}")
        return None
    except Exception as e:
        logger.error(f"❌ Exception creating SuperTokens user {email}: {e}")
        return None

async def seed_users():
    """Wipes and seeds only the user data."""
    logger = setup_logging()
    
    try:
        await db_manager.init_postgres()
        await db_manager.init_mongodb()
        db_session_gen = get_db()
        db = await anext(db_session_gen)

        logger.info("🧹 Wiping all existing user data...")
        await MongoUser.delete_all()
        if (await db.execute(select(PGUser).limit(1))).first():
            await db.execute(delete(PGUser))
            await db.commit()
        logger.info("✅ User cleanup complete.")
        
        # --- User data with diverse industries and companies ---
        test_users = [
            {"email": "ahmed.faisal@advanced-electronics.com", "name": "Ahmed Al-Faisal", "first_name": "Ahmed", "last_name": "Al-Faisal", "password": "password123", "role": "admin", "company": "Advanced Electronics Co.", "title": "Organization Admin", "industry_sector": "Electronics"},
            {"email": "sara.hassan@gulf-plastics.com", "name": "Sara Hassan", "first_name": "Sara", "last_name": "Hassan", "password": "password123", "role": "member", "company": "Gulf Plastics Industries", "title": "Team Member", "industry_sector": "Plastics & Chemicals"},
            {"email": "mohammed.rashid@saudi-steel.com", "name": "Mohammed Rashid", "first_name": "Mohammed", "last_name": "Rashid", "password": "password123", "role": "admin", "company": "Saudi Steel Works", "title": "Factory Manager", "industry_sector": "Heavy Industry"},
            {"email": "fatima.ali@arabian-food.com", "name": "Fatima Ali", "first_name": "Fatima", "last_name": "Ali", "password": "password123", "role": "member", "company": "Arabian Food Processing", "title": "Supply Chain Lead", "industry_sector": "Food & Beverage"},
            {"email": "khalid.abdul@precision-mfg.com", "name": "Khalid Abdul", "first_name": "Khalid", "last_name": "Abdul", "password": "password123", "role": "member", "company": "Precision Manufacturing Ltd", "title": "Automation Engineer", "industry_sector": "Automotive"},
            {"email": "sarah.ahmed@pharma-excellence.com", "name": "Sarah Ahmed", "first_name": "Sarah", "last_name": "Ahmed", "password": "password123", "role": "member", "company": "Pharma Excellence Ltd", "title": "Quality Manager", "industry_sector": "Pharmaceuticals"},
            {"email": "mohammed.alshahri@secure-supply.com", "name": "Mohammed Al-Shahri", "first_name": "Mohammed", "last_name": "Al-Shahri", "password": "password123", "role": "member", "company": "Secure Supply Co.", "title": "Logistics Head", "industry_sector": "Logistics"},
            {"email": "fatima.otaibi@safety-first.com", "name": "Fatima Al-Otaibi", "first_name": "Fatima", "last_name": "Al-Otaibi", "password": "password123", "role": "member", "company": "Safety First Industries", "title": "Safety Officer", "industry_sector": "Safety & Training"},
        ]
        
        created_users_count = 0
        logger.info(f"🚀 Creating {len(test_users)} users...")
        for user_data in test_users:
            # Extract data for each function call
            st_data = {k: v for k, v in user_data.items() if k in ["email", "password", "first_name", "last_name"]}
            pg_data = {k: v for k, v in user_data.items() if k in ["name", "email", "role"]}
            mongo_data = {k: v for k, v in user_data.items() if k in ["email", "name", "role", "company", "title", "industry_sector"]}

            # Create SuperTokens user
            supertokens_id = await create_supertokens_user(logger=logger, **st_data)
            if not supertokens_id:
                logger.warning(f"Skipping DB creation for {user_data['email']} due to SuperTokens failure.")
                continue
            
            # Create PostgreSQL and MongoDB users
            await UserService.create_user_pg(db, supertokens_id=supertokens_id, **pg_data)
            await UserService.create_user_mongo(**mongo_data)
            created_users_count += 1

        logger.info(f"✅ Successfully created {created_users_count} users across all databases.")

    except Exception as e:
        logger.error(f"❌ User seeding script failed: {e}")
        raise
    finally:
        await db_manager.close_connections()
        logger.info("Database connections closed.")

if __name__ == "__main__":
    print("🌱 Starting user-only seeding script...")
    asyncio.run(seed_users())
    print("🎉 User seeding completed!")