#!/usr/bin/env python3
"""
Seeds the 6 team members who authored the 19 comprehensive use cases.
These users are from IIoT Solutions team and must exist before seeding their use cases.
"""
import asyncio
import sys
import os
import httpx

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from app.models.mongo_models import User as MongoUser
from app.core.logging import setup_logging

async def create_platform_user(email: str, password: str, first_name: str, last_name: str,
                               company_name: str, industry_sector: str, company_size: str, city: str,
                               job_title: str,
                               logger=None) -> bool:
    """Create a full platform user (SuperTokens + our DBs) via custom signup."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://backend:8000/api/v1/auth/custom-signup",
                headers={"Content-Type": "application/json"},
                json={
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": email,
                    "password": password,
                    "companyName": company_name,
                    "industrySector": industry_sector,
                    "companySize": company_size,
                    "city": city,
                    "jobTitle": job_title
                }
            )

            if response.status_code == 200:
                logger and logger.info(f"✅ User {email} created successfully via custom signup")
                return True
            else:
                logger and logger.error(f"❌ Custom signup failed for {email}: {response.text}")
                return False
    except Exception as e:
        logger and logger.error(f"❌ Exception creating user {email}: {e}")
        return False

async def seed_team_members():
    """Seeds the 6 IIoT Solutions team members who own the 19 use cases."""
    logger = setup_logging()
    logger.info("🌱 Starting team members seeding...")

    try:
        await db_manager.init_mongodb()
        logger.info("MongoDB connection established")

        # Team members for the 19 comprehensive use cases
        team_members = [
            {
                "email": "aadil@iiotsolutions.sa",
                "first_name": "Aadil",
                "last_name": "Feroze",
                "password": "password123",
                "role": "admin",
                "company": "IIoT Solutions",
                "title": "Chief Technology Officer",
                "industry_sector": "Industrial IoT (IIoT)",
                "company_size": "10-50",
                "city": "Riyadh"
            },
            {
                "email": "amro@iiotsolutions.sa",
                "first_name": "Amro",
                "last_name": "Abouzied",
                "password": "password123",
                "role": "member",
                "company": "IIoT Solutions",
                "title": "Solutions Architect",
                "industry_sector": "Industrial IoT (IIoT)",
                "company_size": "10-50",
                "city": "Riyadh"
            },
            {
                "email": "hamza@iiotsolutions.sa",
                "first_name": "Hamza",
                "last_name": "Feroze",
                "password": "password123",
                "role": "member",
                "company": "IIoT Solutions",
                "title": "AI Developer",
                "industry_sector": "Industrial IoT (IIoT)",
                "company_size": "10-50",
                "city": "Riyadh"
            },
            {
                "email": "abdulrahman@iiotsolutions.sa",
                "first_name": "Abdulrahman",
                "last_name": "Bajabir",
                "password": "password123",
                "role": "member",
                "company": "IIoT Solutions",
                "title": "Junior Developer",
                "industry_sector": "Industrial IoT (IIoT)",
                "company_size": "10-50",
                "city": "Riyadh"
            },
            {
                "email": "firas@iiotsolutions.sa",
                "first_name": "Firas",
                "last_name": "Al-Siddiqi",
                "password": "password123",
                "role": "member",
                "company": "IIoT Solutions",
                "title": "Business Development Manager",
                "industry_sector": "Industrial IoT (IIoT)",
                "company_size": "10-50",
                "city": "Riyadh"
            },
            {
                "email": "hamad@iiotsolutions.sa",
                "first_name": "Hamad",
                "last_name": "Ali",
                "password": "password123",
                "role": "member",
                "company": "IIoT Solutions",
                "title": "Operations Manager",
                "industry_sector": "Industrial IoT (IIoT)",
                "company_size": "10-50",
                "city": "Riyadh"
            }
        ]

        created_count = 0
        skipped_count = 0

        for member_data in team_members:
            # Check if user already exists
            existing_user = await MongoUser.find_one(MongoUser.email == member_data["email"])

            if existing_user:
                logger.info(f"⏭️  User {member_data['email']} already exists, skipping...")
                skipped_count += 1
                continue

            # Create the user
            ok = await create_platform_user(
                email=member_data["email"],
                password=member_data["password"],
                first_name=member_data["first_name"],
                last_name=member_data["last_name"],
                company_name=member_data["company"],
                industry_sector=member_data["industry_sector"],
                company_size=member_data["company_size"],
                city=member_data["city"],
                job_title=member_data["title"],
                logger=logger
            )

            if ok:
                created_count += 1

        logger.info(f"✅ Team member seeding complete!")
        logger.info(f"   Created: {created_count}")
        logger.info(f"   Skipped: {skipped_count}")

    except Exception as e:
        logger.error(f"❌ Team member seeding failed: {e}")
        raise
    finally:
        await db_manager.close_connections()
        logger.info("Database connections closed.")

if __name__ == "__main__":
    print("🌱 Starting IIoT Solutions team members seeding...")
    asyncio.run(seed_team_members())
    print("🎉 Team members seeding completed!")
