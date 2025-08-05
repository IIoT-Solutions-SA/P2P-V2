import asyncio
import sys
import os
import json
import random

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from app.services.database_service import UseCaseService
from app.models.mongo_models import UseCase, User as MongoUser
from app.core.logging import setup_logging

async def seed_usecases():
    """Wipes and seeds only the use case data, assuming users already exist."""
    logger = setup_logging()
    
    try:
        await db_manager.init_mongodb()

        logger.info("👥 Fetching existing users from the database...")
        existing_users = await MongoUser.find_all().to_list()
        if not existing_users:
            logger.error("❌ No users found. Please run `seed_db_users.py` first.")
            return
        logger.info(f"👍 Found {len(existing_users)} users.")

        logger.info("🧹 Wiping all existing use case data...")
        await UseCase.delete_all()
        logger.info("✅ Use case cleanup complete.")
        
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'use-cases.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                use_cases_from_json = json.load(f)
            logger.info(f"Found {len(use_cases_from_json)} use cases. Seeding from JSON...")

            company_to_user_map = {user.company: user for user in existing_users}

            for case_json in use_cases_from_json:
                submitter = company_to_user_map.get(case_json.get("factoryName"), random.choice(existing_users))
                
                # NEW: Generate random engagement stats
                views = random.randint(500, 7500)
                likes = random.randint(int(views * 0.05), int(views * 0.20)) # 5% to 20% of views
                bookmarks = random.randint(int(likes * 0.1), int(likes * 0.5)) # 10% to 50% of likes

                db_case = {
                    "title": case_json.get("title"),
                    "problem_statement": case_json.get("description"),
                    "solution_description": case_json.get("description"),
                    "factory_name": case_json.get("factoryName"),
                    "region": case_json.get("city"),
                    "location": {"lat": case_json.get("latitude"), "lng": case_json.get("longitude")},
                    "category": case_json.get("category"),
                    "implementation_time": case_json.get("implementationTime"),
                    "impact_metrics": {"benefits": "; ".join(case_json.get("benefits", []))},
                    "submitted_by": str(submitter.id),
                    "published": True,
                    # NEW: Add the stats to the object
                    "view_count": views,
                    "like_count": likes,
                    "bookmark_count": bookmarks
                }
                await UseCaseService.create_use_case(db_case)
            logger.info("✅ All 15 basic use cases seeded from JSON with engagement stats.")

        except FileNotFoundError:
            logger.error(f"❌ CRITICAL: Could not find {json_path}. No basic use cases were seeded.")

        # Seed and add stats to detailed use cases as well
        logger.info("🌱 Seeding 2 detailed enterprise use cases with engagement stats...")
        author1, author2 = existing_users[0], existing_users[1]

        detailed_use_cases_data = [
            {"title": "AI Quality Inspection System (Detailed View)", "factory_name": "Advanced Electronics Co.", "problem_statement": "High defect rate...", "solution_description": "Implemented an AI system...", "is_detailed_version": True, "published": True, "submitted_by": str(author1.id), "category": "Quality Control", "featured": True, "location": {"lat": 24.7136, "lng": 46.6753}, "view_count": random.randint(500, 7500), "like_count": random.randint(50, 500), "bookmark_count": random.randint(10, 100)},
            {"title": "Predictive Maintenance IoT System (Detailed View)", "factory_name": "Gulf Plastics Industries", "problem_statement": "Frequent downtime...", "solution_description": "Deployed IoT sensors...", "is_detailed_version": True, "published": True, "submitted_by": str(author2.id), "category": "Predictive Maintenance", "featured": True, "location": {"lat": 26.4207, "lng": 50.0888}, "view_count": random.randint(500, 7500), "like_count": random.randint(50, 500), "bookmark_count": random.randint(10, 100)}
        ]
        
        detailed_case_ids = {}
        for detailed_case_data in detailed_use_cases_data:
            created_detailed = await UseCaseService.create_use_case(detailed_case_data)
            detailed_case_ids[detailed_case_data["title"]] = str(created_detailed.id)
        logger.info("✅ Detailed use cases seeded.")

        logger.info("🔗 Linking basic and detailed use cases...")
        detailed_use_case_titles = { "AI Quality Inspection System": "AI Quality Inspection System (Detailed View)", "Predictive Maintenance IoT System": "Predictive Maintenance IoT System (Detailed View)" }
        
        linked_count = 0
        for basic_title, detailed_title in detailed_use_case_titles.items():
            basic_case = await UseCase.find_one(UseCase.title == basic_title)
            if basic_case and detailed_title in detailed_case_ids:
                basic_case.detailed_version_id = detailed_case_ids[detailed_title]
                basic_case.has_detailed_view = True
                await basic_case.save()
                
                detailed_case = await UseCase.get(detailed_case_ids[detailed_title])
                if detailed_case:
                    detailed_case.basic_version_id = str(basic_case.id)
                    await detailed_case.save()
                
                linked_count += 1
        logger.info(f"✅ Linked {linked_count} pairs of use cases.")

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