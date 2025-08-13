import asyncio
import sys
import os
import json
import re

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from app.services.database_service import UseCaseService
from app.models.mongo_models import User as MongoUser, UseCase
from app.core.logging import setup_logging

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[\(\)]", "", text)
    text = re.sub(r"[\s\W_]+", "-", text)
    text = text.strip("-")
    return text

async def seed_usecases():
    """Wipes and seeds use case data from JSON, assuming users already exist."""
    logger = setup_logging()
    
    try:
        await db_manager.init_mongodb()
        logger.info("MongoDB connection established")

        # --- 1. FETCH EXISTING USERS ---
        logger.info("👥 Fetching existing users from the database...")
        existing_users = await MongoUser.find_all().to_list()
        if not existing_users:
            logger.error("❌ No users found in the database. Please run the `seed_db_users.py` script first.")
            return
        logger.info(f"👍 Found {len(existing_users)} users.")

        # --- 2. CLEANUP EXISTING USE CASE DATA ---
        logger.info("🧹 Wiping all existing use case data...")
        await UseCase.delete_all()
        logger.info("✅ Use case cleanup complete.")
        
        # --- 3. SEED FROM JSON FILE ---
        try:
            json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "use-cases.json")
            logger.info(f"Found {json_path}. Seeding from JSON...")
        
            with open(json_path, 'r', encoding='utf-8') as f:
                cases_json = json.load(f)
            
            logger.info(f"Found {len(cases_json)} use cases. Seeding from JSON...")
            
            # Map company names to user IDs for submitted_by
            company_to_user = {}
            for user in existing_users:
                if hasattr(user, 'company') and user.company:
                    company_to_user[user.company] = str(user.id)
            
            for case_json in cases_json:
                # Find submitter by company name
                company_name = case_json.get("factoryName", "")
                submitter = None
                for user in existing_users:
                    if hasattr(user, 'company') and user.company == company_name:
                        submitter = user
                        break
                
                # Fallback to first user if no match
                if not submitter:
                    submitter = existing_users[0]
                
                # Generate slugs for URL routing
                title_slug = slugify(case_json.get("title", ""))
                company_slug = slugify(case_json.get("factoryName", ""))
                
                # Create use case data structure
                db_case = {
                    "title": case_json.get("title"),
                    "problem_statement": case_json.get("description", ""),
                    "solution_description": case_json.get("executive_summary", case_json.get("description", "Solution details not provided.")),
                    "title_slug": title_slug,
                    "company_slug": company_slug,
                    "factory_name": case_json.get("factoryName"),
                    "region": case_json.get("city"),
                    "location": {"lat": case_json.get("latitude"), "lng": case_json.get("longitude")},
                    "category": case_json.get("category"),
                    "implementation_time": case_json.get("implementationTime"),
                    "impact_metrics": {"benefits": "; ".join(case_json.get("benefits", []))},
                    "submitted_by": str(submitter.id),
                    "published": True,
                    "view_count": 0,
                    "like_count": 0,
                    "bookmark_count": 0
                }
                
                # Add optional extended fields if present in JSON
                if case_json.get("roiPercentage"):
                    db_case["roi_percentage"] = case_json.get("roiPercentage")
                if isinstance(case_json.get("images"), list) and case_json.get("images"):
                    db_case["images"] = case_json.get("images")
                if case_json.get("executive_summary"):
                    db_case["executive_summary"] = case_json.get("executive_summary")
                if case_json.get("business_challenge"):
                    db_case["business_challenge"] = case_json.get("business_challenge")
                if case_json.get("solution_details"):
                    db_case["solution_details"] = case_json.get("solution_details")
                if case_json.get("implementation_details"):
                    db_case["implementation_details"] = case_json.get("implementation_details")
                if case_json.get("results"):
                    db_case["results"] = case_json.get("results")
                if case_json.get("technical_architecture"):
                    db_case["technical_architecture"] = case_json.get("technical_architecture")
                if case_json.get("future_roadmap"):
                    db_case["future_roadmap"] = case_json.get("future_roadmap")
                if case_json.get("lessons_learned"):
                    db_case["lessons_learned"] = case_json.get("lessons_learned")
                if case_json.get("contactPerson"):
                    db_case["contact_person"] = case_json.get("contactPerson")
                if case_json.get("contactTitle"):
                    db_case["contact_title"] = case_json.get("contactTitle")
                
                await UseCaseService.create_use_case(db_case)
            logger.info("✅ All use cases seeded from JSON with full detail data.")

        except FileNotFoundError:
            logger.error(f"❌ CRITICAL: Could not find use-cases.json. No use cases were seeded.")

        logger.info("🎉 Use case seeding completed successfully!")

    except Exception as e:
        logger.error(f"❌ Use case seeding script failed: {e}")
        raise
    finally:
        await db_manager.close_connections()
        logger.info("Database connections closed.")

if __name__ == "__main__":
    print("🌱 Starting use case seeding script...")
    asyncio.run(seed_usecases())
    print("🎉 Use case seeding completed!")
