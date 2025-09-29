import asyncio
import sys
import os
import json
import re
from datetime import datetime

# Add the parent directories to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import db_manager
from app.services.database_service import UseCaseService
from app.models.mongo_models import User as MongoUser, UseCase
from app.core.logging import setup_logging

# USER CONFIGURATION
USER_EMAIL = "aadil@iiotsolutions.sa"  # UPDATE THIS WITH ACTUAL EMAIL
USER_NAME = "Aadil Feroze"
JSON_FILE = "aadil_usecases.json"

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[\(\)]", "", text)
    text = re.sub(r"[\s\W_]+", "-", text)
    text = text.strip("-")
    return text

async def seed_aadil_usecases():
    """Seeds use cases for Aadil Feroze from aadil_usecases.json"""
    logger = setup_logging()
    logger.info(f"🌱 Starting use case seeding for {USER_NAME}")

    try:
        await db_manager.init_mongodb()
        logger.info("MongoDB connection established")

        # --- 1. CHECK IF USER EXISTS ---
        logger.info(f"👤 Looking for user: {USER_EMAIL}")
        user = await MongoUser.find_one(MongoUser.email == USER_EMAIL)

        if not user:
            logger.error(f"❌ User not found: {USER_EMAIL}")
            logger.error(f"Please ensure {USER_NAME} exists in the database before running this script.")
            return

        logger.info(f"✅ Found user: {user.name} (ID: {user.id})")

        # --- 2. LOAD USE CASES FROM JSON ---
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), JSON_FILE)

        if not os.path.exists(json_path):
            logger.error(f"❌ JSON file not found: {json_path}")
            logger.info(f"Please create {JSON_FILE} with use case data.")
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            use_cases_data = json.load(f)

        if not use_cases_data:
            logger.warning(f"⚠️ No use cases found in {JSON_FILE}")
            return

        logger.info(f"📋 Found {len(use_cases_data)} use cases to seed")

        # --- 3. SEED USE CASES ---
        success_count = 0

        for idx, case_json in enumerate(use_cases_data, 1):
            try:
                title = case_json.get("title", f"Untitled Case {idx}")
                logger.info(f"  [{idx}/{len(use_cases_data)}] Processing: {title}")

                # Generate slugs
                title_slug = slugify(title)
                # Use the user's company for the slug, not the factory name
                company_slug = slugify(user.company) if hasattr(user, 'company') and user.company else "unknown-company"

                # Create use case document
                db_case = {
                    "title": title,
                    "problem_statement": case_json.get("description", ""),
                    "solution_description": case_json.get("executive_summary",
                                                         case_json.get("description", "Solution details not provided.")),
                    "title_slug": title_slug,
                    "company_slug": company_slug,
                    "factory_name": case_json.get("factoryName"),
                    "region": case_json.get("city"),
                    "location": {
                        "lat": case_json.get("latitude", 24.7136),
                        "lng": case_json.get("longitude", 46.6753)
                    },
                    "category": case_json.get("category", "General"),
                    "implementation_time": case_json.get("implementationTime"),
                    "impact_metrics": {"benefits": "; ".join(case_json.get("benefits", []))},
                    "submitted_by": str(user.id),  # Assign to Aadil
                    "published": True,
                    "view_count": 0,
                    "like_count": 0,
                    "bookmark_count": 0,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }

                # Add optional fields if present
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
                if case_json.get("challenges_and_solutions"):
                    db_case["challenges_and_solutions"] = case_json.get("challenges_and_solutions")

                # Create the use case
                await UseCaseService.create_use_case(db_case)
                logger.info(f"    ✅ Successfully created: {title}")
                success_count += 1

            except Exception as e:
                logger.error(f"    ❌ Failed to create use case '{title}': {str(e)}")
                continue

        # --- 4. SUMMARY ---
        logger.info("=" * 50)
        logger.info(f"🎉 Seeding complete for {USER_NAME}")
        logger.info(f"📊 Results: {success_count}/{len(use_cases_data)} use cases created successfully")

    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        raise
    finally:
        await db_manager.close_connections()
        logger.info("Database connections closed.")

if __name__ == "__main__":
    print(f"🌱 Starting use case seeding for {USER_NAME}...")
    print(f"📧 User email: {USER_EMAIL}")
    print(f"📁 JSON file: {JSON_FILE}")
    print("-" * 50)
    asyncio.run(seed_aadil_usecases())