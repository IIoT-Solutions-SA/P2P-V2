#!/usr/bin/env python3
"""
Migration script to populate missing subtitle and executive_summary fields in existing use cases.

This script:
1. Finds all use cases with null subtitle or executive_summary
2. Populates subtitle from title (truncated if needed)
3. Populates executive_summary from problem_statement or description
4. Reports the number of use cases updated

Run inside Docker container:
    python scripts/migrate_usecase_fields.py
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import logging
from beanie import init_beanie
import motor.motor_asyncio

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.mongo_models import UseCase, User as MongoUser, ForumPost, ForumReply, Organization, UserStats, UserActivity
from app.core.config import settings
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to max_length, ending at word boundary."""
    if len(text) <= max_length:
        return text

    # Find the last space before max_length
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')

    if last_space > 0:
        return truncated[:last_space] + "..."
    return truncated + "..."


def generate_subtitle(title: str) -> str:
    """Generate a subtitle from the title."""
    # Remove common prefixes/suffixes
    subtitle = title.replace("Implementation of ", "")
    subtitle = subtitle.replace("Case Study: ", "")
    subtitle = subtitle.replace("Use Case: ", "")

    # Add a descriptive prefix
    if "automation" in title.lower():
        return f"Manufacturing Automation: {truncate_text(subtitle, 150)}"
    elif "quality" in title.lower():
        return f"Quality Improvement: {truncate_text(subtitle, 150)}"
    elif "efficiency" in title.lower():
        return f"Efficiency Enhancement: {truncate_text(subtitle, 150)}"
    elif "digital" in title.lower():
        return f"Digital Transformation: {truncate_text(subtitle, 150)}"
    elif "maintenance" in title.lower():
        return f"Maintenance Optimization: {truncate_text(subtitle, 150)}"
    else:
        return f"Manufacturing Innovation: {truncate_text(subtitle, 150)}"


async def migrate_use_cases():
    """Migrate use cases to populate missing required fields."""
    logger.info("\n" + "="*60)
    logger.info("USE CASE FIELD MIGRATION SCRIPT")
    logger.info("="*60)

    try:
        # Connect to MongoDB
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
        db = client.p2p_sandbox

        # Initialize Beanie with document models
        await init_beanie(
            database=db,
            document_models=[UseCase, MongoUser, ForumPost, ForumReply, Organization, UserStats, UserActivity]
        )
        logger.info(f"✅ Connected to MongoDB: p2p_sandbox")

        # Count total use cases
        total_use_cases = await UseCase.count()
        logger.info(f"\n📊 Total use cases in database: {total_use_cases}")

        # Find use cases with missing fields
        use_cases_to_update = []

        # Get all use cases
        all_use_cases = await UseCase.find_all().to_list()

        missing_subtitle_count = 0
        missing_executive_count = 0

        for use_case in all_use_cases:
            if not use_case.subtitle or use_case.subtitle == "null" or use_case.subtitle == "":
                missing_subtitle_count += 1
            if not use_case.executive_summary or use_case.executive_summary == "null" or use_case.executive_summary == "":
                missing_executive_count += 1

        logger.info(f"\n🔍 Found {missing_subtitle_count} use cases with missing subtitle")
        logger.info(f"🔍 Found {missing_executive_count} use cases with missing executive_summary")

        updated_count = 0

        # Process each use case
        for use_case in all_use_cases:
            needs_update = False
            original_subtitle = use_case.subtitle
            original_executive = use_case.executive_summary

            # Check and fix subtitle
            if not use_case.subtitle or use_case.subtitle == "null" or use_case.subtitle == "":
                if use_case.title:
                    use_case.subtitle = generate_subtitle(use_case.title)
                    logger.info(f"\n📝 Use Case: {use_case.title[:50]}...")
                    logger.info(f"   Generated subtitle: {use_case.subtitle[:80]}...")
                    needs_update = True
                else:
                    # Fallback if no title
                    use_case.subtitle = "Manufacturing Use Case"
                    needs_update = True

            # Check and fix executive_summary
            if not use_case.executive_summary or use_case.executive_summary == "null" or use_case.executive_summary == "":
                # Try different fields as source
                if use_case.problem_statement:
                    use_case.executive_summary = truncate_text(use_case.problem_statement, 500)
                    logger.info(f"   Using problem_statement for executive_summary")
                    needs_update = True
                elif hasattr(use_case, 'description') and use_case.description:
                    use_case.executive_summary = truncate_text(use_case.description, 500)
                    logger.info(f"   Using description for executive_summary")
                    needs_update = True
                elif use_case.solution_description:
                    use_case.executive_summary = truncate_text(use_case.solution_description, 500)
                    logger.info(f"   Using solution_description for executive_summary")
                    needs_update = True
                else:
                    # Generate from title as last resort
                    if use_case.title:
                        use_case.executive_summary = f"This use case demonstrates {use_case.title}. " \
                                                    f"It showcases innovative approaches to manufacturing challenges."
                        logger.info(f"   Generated executive_summary from title")
                        needs_update = True
                    else:
                        use_case.executive_summary = "This use case demonstrates innovative manufacturing solutions."
                        needs_update = True

            # Save if updated
            if needs_update:
                try:
                    await use_case.save()
                    updated_count += 1
                    logger.info(f"   ✅ Updated successfully")
                except Exception as e:
                    logger.error(f"   ❌ Error updating: {e}")

        logger.info("\n" + "="*60)
        logger.info(f"✅ MIGRATION COMPLETE")
        logger.info(f"📊 Updated {updated_count} use cases")
        logger.info("="*60)

        # Verify the migration
        logger.info("\n🔍 Verification:")

        # Re-count missing fields
        all_use_cases = await UseCase.find_all().to_list()
        remaining_missing_subtitle = 0
        remaining_missing_executive = 0

        for use_case in all_use_cases:
            if not use_case.subtitle or use_case.subtitle == "null" or use_case.subtitle == "":
                remaining_missing_subtitle += 1
            if not use_case.executive_summary or use_case.executive_summary == "null" or use_case.executive_summary == "":
                remaining_missing_executive += 1

        if remaining_missing_subtitle == 0 and remaining_missing_executive == 0:
            logger.info("✅ All use cases now have valid subtitle and executive_summary fields!")
        else:
            logger.warning(f"⚠️  {remaining_missing_subtitle} use cases still missing subtitle")
            logger.warning(f"⚠️  {remaining_missing_executive} use cases still missing executive_summary")

    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(migrate_use_cases())
    sys.exit(exit_code)