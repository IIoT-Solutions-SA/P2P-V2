import asyncio
import sys
import os
import json
import random
import re

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from app.services.database_service import UseCaseService
from app.models.mongo_models import UseCase, User as MongoUser
from app.core.logging import setup_logging

def slugify(text: str) -> str:
    """
    Convert a string to a URL-friendly slug.
    Example: "AI Quality Inspection System" -> "ai-quality-inspection-system"
    """
    if not text:
        return ""
    text = text.lower()
    # Remove parentheses
    text = re.sub(r'[\(\)]', '', text)
    # Replace spaces and non-word chars with a hyphen
    text = re.sub(r'[\s\W_]+', '-', text)
    text = text.strip('-')
    return text

async def seed_usecases():
    """Wipes and seeds only the use case data, assuming users already exist."""
    logger = setup_logging()
    
    try:
        await db_manager.init_mongodb()

        logger.info("👥 Fetching existing users from the database...")
        existing_users = await MongoUser.find_all().to_list()
        if not existing_users:
            logger.error("❌ No users found. Please run the `seed_db_users.py` script first.")
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
                
                title = case_json.get("title")
                db_case = {
                    "title": title,
                    "title_slug": slugify(title), # Generate and add the slug
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
                    "view_count": random.randint(500, 7500),
                    "like_count": random.randint(50, 500),
                    "bookmark_count": random.randint(10, 100)
                }
                await UseCaseService.create_use_case(db_case)
            logger.info("✅ All 15 basic use cases seeded from JSON with slugs.")

        except FileNotFoundError:
            logger.error(f"❌ CRITICAL: Could not find {json_path}. No basic use cases were seeded.")

        logger.info("🌱 Seeding 2 detailed enterprise use cases with FULL data and slugs...")
        author1 = next((user for user in existing_users if "Advanced Electronics Co." in user.company), existing_users[0])
        author2 = next((user for user in existing_users if "Gulf Plastics Industries" in user.company), existing_users[1])

        detailed_use_cases_data = [
            {
                "title": "AI Quality Inspection System (Detailed View)",
                "subtitle": "Transforming PCB Manufacturing Through Computer Vision and Machine Learning",
                "problem_statement": "Computer vision system reduces defects by 85% in electronics manufacturing.",
                "solution_description": "Implementation of an AI-powered computer vision quality inspection system with machine learning algorithms for microscopic defect detection",
                "category": "Quality Control",
                "factory_name": "Advanced Electronics Co.",
                "implementation_time": "6 months implementation",
                "roi_percentage": "250% ROI in first year",
                "region": "Riyadh", "location": {"lat": 24.7136, "lng": 46.6753},
                "contact_person": "Ahmed Al-Faisal", "contact_title": "Operations Manager",
                "images": [
                    "https://images.unsplash.com/photo-1565043666747-69f6646db940?w=800&h=400&fit=crop",
                    "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&h=400&fit=crop",
                ],
                "executive_summary": "Advanced Electronics Co. faced critical quality control challenges with a 15% defect rate in PCB manufacturing, resulting in 450K annual losses. The implementation of an AI-powered computer vision quality inspection system achieved an 85% reduction in defects, 2.3M in annual cost savings, and 250% ROI in the first year.",
                "business_challenge": {
                    "industry_context": "The electronics manufacturing industry faces increasing pressure for zero-defect production due to complex PCB designs and stringent quality requirements.",
                    "specific_problems": [ "Manual inspection inconsistency with 15% defect rate", "Microscopic defects undetectable by human inspectors", "Production bottlenecks with 40% inspection time overhead" ],
                    "business_impact": { "financial_loss": "450K annually in waste", "customer_impact": "12% return rate, declining satisfaction", "operational_impact": "40% slower production", "compliance_risk": "Risk of losing automotive certification" }
                },
                "results": {
                    "quantitative_metrics": [
                        {"metric": "Defect Rate Reduction", "baseline": "15.0%", "current": "2.25%", "improvement": "85% reduction"},
                        {"metric": "Annual Cost Savings", "baseline": "450K losses", "current": "2.3M savings", "improvement": "2.75M swing"}
                    ],
                    "qualitative_impacts": ["Improved customer satisfaction scores from 7.2 to 9.1", "Enhanced employee confidence in quality processes"],
                    "roi_analysis": { "total_investment": "285,000", "annual_savings": "2,300,000", "payback_period": "1.5 months", "three_year_roi": "2,315%" }
                },
                "is_detailed_version": True, "published": True, "featured": True, "submitted_by": str(author1.id),
                "view_count": random.randint(5000, 15000), "like_count": random.randint(500, 1500), "bookmark_count": random.randint(100, 500)
            },
            {
                "title": "Predictive Maintenance IoT System (Detailed View)",
                "subtitle": "Revolutionary Equipment Monitoring Through Industrial IoT and Machine Learning",
                "problem_statement": "Smart sensors prevent equipment failures and reduce downtime significantly.",
                "solution_description": "Comprehensive IoT-based predictive maintenance system using vibration analysis, thermal imaging, and machine learning for proactive equipment maintenance.",
                "category": "Predictive Maintenance",
                "factory_name": "Gulf Plastics Industries",
                "implementation_time": "4 months implementation",
                "roi_percentage": "180% ROI in first year",
                "region": "Dammam", "location": {"lat": 26.4207, "lng": 50.0888},
                "contact_person": "Sara Hassan", "contact_title": "Team Member",
                "images": [
                    "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&h=400&fit=crop",
                    "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=400&fit=crop"
                ],
                "executive_summary": "Gulf Plastics Industries faced critical equipment reliability challenges with 35% unplanned downtime, causing 2.8M annual losses. The implementation of an IoT-based predictive maintenance system achieved a 60% reduction in downtime and a 25% increase in OEE.",
                "business_challenge": {
                    "industry_context": "The plastics manufacturing industry operates with complex, high-temperature machinery requiring continuous operation.",
                    "specific_problems": ["Unplanned downtime averaging 35%", "Reactive maintenance causing extended repair times", "Lack of visibility into equipment health"],
                    "business_impact": { "financial_loss": "2.8M annually in downtime", "customer_impact": "15% delivery delays", "operational_impact": "35% equipment availability" }
                },
                "results": {
                    "quantitative_metrics": [
                        {"metric": "Downtime Reduction", "baseline": "35%", "current": "14%", "improvement": "60% reduction"},
                        {"metric": "Maintenance Savings", "baseline": "N/A", "current": "1.8M annually", "improvement": "Significant savings"}
                    ],
                    "qualitative_impacts": ["Improved production planning", "Increased equipment lifespan", "Proactive maintenance scheduling"],
                    "roi_analysis": { "total_investment": "450,000", "annual_savings": "1,800,000", "payback_period": "3 months", "three_year_roi": "1100%" }
                },
                "is_detailed_version": True, "published": True, "featured": True, "submitted_by": str(author2.id),
                "view_count": random.randint(4000, 12000), "like_count": random.randint(400, 1200), "bookmark_count": random.randint(80, 400)
            }
        ]
        
        # Add slugs to detailed cases before creating them
        for detailed_case in detailed_use_cases_data:
            detailed_case["title_slug"] = slugify(detailed_case["title"])
        
        detailed_case_ids = {}
        for detailed_case_data in detailed_use_cases_data:
            created_detailed = await UseCaseService.create_use_case(detailed_case_data)
            detailed_case_ids[detailed_case_data["title"]] = str(created_detailed.id)
        logger.info("✅ Detailed use cases seeded with full data and slugs.")

        logger.info("🔗 Linking basic and detailed use cases...")
        detailed_use_case_titles = { 
            "AI Quality Inspection System": "AI Quality Inspection System (Detailed View)", 
            "Predictive Maintenance IoT System": "Predictive Maintenance IoT System (Detailed View)" 
        }
        
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
