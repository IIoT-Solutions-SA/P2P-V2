import asyncio
import sys
import os
import httpx
import re

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager, get_db
from app.models.mongo_models import User as MongoUser, Organization
from app.models.pg_models import User as PGUser
from app.core.logging import setup_logging
from sqlalchemy import select, delete

async def create_platform_user(email: str, password: str, first_name: str, last_name: str,
                               company_name: str, industry_sector: str, company_size: str, city: str,
                               logger=None) -> bool:
    """Create a full platform user (SuperTokens + our DBs) via custom signup."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/api/v1/auth/custom-signup",
                headers={"Content-Type": "application/json"},
                json={
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": email,
                    "password": password,
                    "companyName": company_name,
                    "industrySector": industry_sector,
                    "companySize": company_size,
                    "city": city
                }
            )
            if response.status_code == 200 and response.json().get("status") == "OK":
                logger and logger.info(f"✅ Created platform user: {email}")
                return True
        logger and logger.error(f"❌ Custom signup failed for {email}: {response.text}")
        return False
    except Exception as e:
        logger and logger.error(f"❌ Exception creating user {email}: {e}")
        return False

async def seed_users():
    """Wipes and seeds only the user and organization data."""
    logger = setup_logging()
    
    try:
        await db_manager.init_postgres()
        await db_manager.init_mongodb()
        db_session_gen = get_db()
        db = await anext(db_session_gen)

        logger.info("🧹 Wiping all existing user and organization data...")
        await MongoUser.delete_all()
        await Organization.delete_all()
        if (await db.execute(select(PGUser).limit(1))).first():
            await db.execute(delete(PGUser))
            await db.commit()
        logger.info("✅ User and organization cleanup complete.")
        
        # --- User data with diverse industries and companies ---
        test_users = [
            # --- Existing 8 Users (Role updated to Admin) ---
            {"email": "ahmed.faisal@advanced-electronics.com", "name": "Ahmed Al-Faisal", "first_name": "Ahmed", "last_name": "Al-Faisal", "password": "password123", "role": "admin", "company": "Advanced Electronics Co.", "title": "Organization Admin", "industry_sector": "Electronics", "company_size": "500+", "city": "Riyadh"},
            {"email": "sara.hassan@gulf-plastics.com", "name": "Sara Hassan", "first_name": "Sara", "last_name": "Hassan", "password": "password123", "role": "admin", "company": "Gulf Plastics Industries", "title": "Operations Lead", "industry_sector": "Plastics & Chemicals", "company_size": "200+", "city": "Dammam"},
            {"email": "mohammed.rashid@saudi-steel.com", "name": "Mohammed Rashid", "first_name": "Mohammed", "last_name": "Rashid", "password": "password123", "role": "admin", "company": "Saudi Steel Works", "title": "Factory Manager", "industry_sector": "Heavy Industry", "company_size": "1000+", "city": "Jubail"},
            {"email": "fatima.ali@arabian-food.com", "name": "Fatima Ali", "first_name": "Fatima", "last_name": "Ali", "password": "password123", "role": "admin", "company": "Arabian Food Processing", "title": "Supply Chain Director", "industry_sector": "Food & Beverage", "company_size": "300+", "city": "Jeddah"},
            {"email": "khalid.abdul@precision-mfg.com", "name": "Khalid Abdul", "first_name": "Khalid", "last_name": "Abdul", "password": "password123", "role": "admin", "company": "Precision Manufacturing Ltd", "title": "Automation Engineer", "industry_sector": "Automotive", "company_size": "150+", "city": "Riyadh"},
            {"email": "sarah.ahmed@pharma-excellence.com", "name": "Sarah Ahmed", "first_name": "Sarah", "last_name": "Ahmed", "password": "password123", "role": "admin", "company": "Pharma Excellence Ltd", "title": "Quality Manager", "industry_sector": "Pharmaceuticals", "company_size": "400+", "city": "Riyadh"},
            {"email": "mohammed.alshahri@secure-supply.com", "name": "Mohammed Al-Shahri", "first_name": "Mohammed", "last_name": "Al-Shahri", "password": "password123", "role": "admin", "company": "Secure Supply Co.", "title": "Logistics Head", "industry_sector": "Logistics", "company_size": "250+", "city": "Dammam"},
            {"email": "fatima.otaibi@safety-first.com", "name": "Fatima Al-Otaibi", "first_name": "Fatima", "last_name": "Al-Otaibi", "password": "password123", "role": "admin", "company": "Safety First Industries", "title": "Safety Officer", "industry_sector": "Safety & Training", "company_size": "120+", "city": "Riyadh"},
            
            # --- START: 10 NEW ADMIN USERS ---
            {"email": "hessa.alsabah@yanbu-smart.com", "name": "Hessa Al-Sabah", "first_name": "Hessa", "last_name": "Al-Sabah", "password": "password123", "role": "admin", "company": "Yanbu Smart Industries", "title": "Founder & CEO", "industry_sector": "Industrial IoT (IIoT)", "company_size": "10-50", "city": "Yanbu"},
            {"email": "faisal.alghamdi@redsea-logistics.com", "name": "Faisal Al-Ghamdi", "first_name": "Faisal", "last_name": "Al-Ghamdi", "password": "password123", "role": "admin", "company": "Red Sea Logistics", "title": "Head of Operations", "industry_sector": "Logistics", "company_size": "200-500", "city": "King Abdullah Economic City"},
            {"email": "nouf.almutawa@najd-dates.com", "name": "Nouf Al-Mutawa", "first_name": "Nouf", "last_name": "Al-Mutawa", "password": "password123", "role": "admin", "company": "Najd Dates Processing", "title": "Production Director", "industry_sector": "Food & Beverage", "company_size": "50-200", "city": "Qassim"},
            {"email": "tarek.mansour@alkhobar-mfg.com", "name": "Tarek Mansour", "first_name": "Tarek", "last_name": "Mansour", "password": "password123", "role": "admin", "company": "Al-Khobar Advanced Manufacturing", "title": "Digital Transformation Lead", "industry_sector": "Manufacturing", "company_size": "200-500", "city": "Al-Khobar"},
            {"email": "omar.bakr@ep-construction.com", "name": "Omar Bakr", "first_name": "Omar", "last_name": "Bakr", "password": "password123", "role": "admin", "company": "Eastern Province Construction Materials", "title": "Chief Engineer", "industry_sector": "Construction & Building Materials", "company_size": "500+", "city": "Dammam"},
            {"email": "aisha.aljameel@saudi-retail.com", "name": "Aisha Al-Jameel", "first_name": "Aisha", "last_name": "Al-Jameel", "password": "password123", "role": "admin", "company": "Saudi Retail Distribution Co.", "title": "Supply Chain Director", "industry_sector": "Retail & FMCG", "company_size": "1000+", "city": "Jeddah"},
            {"email": "sameer.khan@mea-integrators.com", "name": "Sameer Khan", "first_name": "Sameer", "last_name": "Khan", "password": "password123", "role": "admin", "company": "MEA Systems Integrators", "title": "Senior Project Manager", "industry_sector": "Technology & Integration", "company_size": "50-200", "city": "Riyadh"},
            {"email": "rania.alabdullah@agritech-sa.com", "name": "Rania Al-Abdullah", "first_name": "Rania", "last_name": "Al-Abdullah", "password": "password123", "role": "admin", "company": "Agri-Tech Solutions Arabia", "title": "Technical Director", "industry_sector": "Agriculture Technology", "company_size": "10-50", "city": "Al-Kharj"},
            {"email": "bandar.alharbi@gulf-plastics.com", "name": "Bandar Al-Harbi", "first_name": "Bandar", "last_name": "Al-Harbi", "password": "password123", "role": "admin", "company": "Gulf Plastics Industries", "title": "General Manager", "industry_sector": "Plastics & Chemicals", "company_size": "200+", "city": "Jubail"},
            {"email": "layla.iskandar@neom-solar.com", "name": "Layla Iskandar", "first_name": "Layla", "last_name": "Iskandar", "password": "password123", "role": "admin", "company": "NEOM Solar Power Systems", "title": "Operations Lead", "industry_sector": "Renewable Energy", "company_size": "50-200", "city": "Tabuk"}
            # --- END: 10 NEW ADMIN USERS ---
        ]
        
        created_users_count = 0
        logger.info(f"🚀 Creating {len(test_users)} users via custom-signup (includes org linkage)...")
        for user_data in test_users:
            ok = await create_platform_user(
                email=user_data["email"],
                password=user_data["password"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                company_name=user_data.get("company", ""),
                industry_sector=user_data.get("industry_sector", ""),
                company_size=user_data.get("company_size", ""),
                city=user_data.get("city", ""),
                logger=logger
            )
            if ok:
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