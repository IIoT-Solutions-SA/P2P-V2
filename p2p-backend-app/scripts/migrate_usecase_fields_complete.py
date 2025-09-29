#!/usr/bin/env python3
"""
Complete migration script to ensure all use cases have required fields for production.

This script:
1. Populates missing subtitle and executive_summary fields
2. Ensures challenges_and_solutions structure is correct
3. Validates all required fields are present
4. Reports comprehensive migration status

Run inside Docker container:
    python scripts/migrate_usecase_fields_complete.py
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional, List, Dict
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

    # Add a descriptive prefix based on keywords
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
    elif "ai" in title.lower() or "ml" in title.lower():
        return f"AI/ML Innovation: {truncate_text(subtitle, 150)}"
    elif "iot" in title.lower():
        return f"IoT Integration: {truncate_text(subtitle, 150)}"
    elif "safety" in title.lower():
        return f"Safety Enhancement: {truncate_text(subtitle, 150)}"
    elif "energy" in title.lower():
        return f"Energy Management: {truncate_text(subtitle, 150)}"
    else:
        return f"Manufacturing Innovation: {truncate_text(subtitle, 150)}"


def generate_default_challenges() -> List[Dict[str, str]]:
    """Generate default challenges and solutions structure."""
    return [
        {
            "challenge": "Initial Implementation",
            "description": "Setting up the system and integrating with existing infrastructure",
            "solution": "Phased implementation approach with thorough testing at each stage",
            "outcome": "Successful deployment with minimal disruption to operations"
        }
    ]


async def migrate_use_cases():
    """Migrate use cases to ensure all required fields are present."""
    logger.info("\n" + "="*70)
    logger.info("COMPLETE USE CASE MIGRATION SCRIPT FOR PRODUCTION")
    logger.info("="*70)

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

        # Get all use cases
        all_use_cases = await UseCase.find_all().to_list()

        # Track statistics
        stats = {
            "missing_subtitle": 0,
            "missing_executive_summary": 0,
            "missing_challenges": 0,
            "invalid_challenges": 0,
            "total_updated": 0,
            "failed_updates": 0
        }

        # First pass: Count missing fields
        logger.info("\n🔍 Analyzing existing use cases...")
        for use_case in all_use_cases:
            if not use_case.subtitle or use_case.subtitle == "null" or use_case.subtitle == "":
                stats["missing_subtitle"] += 1

            if not use_case.executive_summary or use_case.executive_summary == "null" or use_case.executive_summary == "":
                stats["missing_executive_summary"] += 1

            if not use_case.challenges_and_solutions or len(use_case.challenges_and_solutions) == 0:
                stats["missing_challenges"] += 1
            elif not isinstance(use_case.challenges_and_solutions, list):
                stats["invalid_challenges"] += 1

        logger.info(f"  • {stats['missing_subtitle']} use cases missing subtitle")
        logger.info(f"  • {stats['missing_executive_summary']} use cases missing executive_summary")
        logger.info(f"  • {stats['missing_challenges']} use cases missing challenges_and_solutions")
        logger.info(f"  • {stats['invalid_challenges']} use cases with invalid challenges structure")

        # Second pass: Fix missing fields
        logger.info("\n🔧 Fixing missing fields...")
        for i, use_case in enumerate(all_use_cases, 1):
            needs_update = False
            updates_made = []

            # Fix subtitle
            if not use_case.subtitle or use_case.subtitle == "null" or use_case.subtitle == "":
                if use_case.title:
                    use_case.subtitle = generate_subtitle(use_case.title)
                    updates_made.append("subtitle")
                    needs_update = True
                else:
                    use_case.subtitle = "Manufacturing Use Case"
                    updates_made.append("subtitle (default)")
                    needs_update = True

            # Fix executive_summary
            if not use_case.executive_summary or use_case.executive_summary == "null" or use_case.executive_summary == "":
                if use_case.problem_statement:
                    use_case.executive_summary = truncate_text(use_case.problem_statement, 500)
                    updates_made.append("executive_summary (from problem_statement)")
                    needs_update = True
                elif hasattr(use_case, 'description') and use_case.description:
                    use_case.executive_summary = truncate_text(use_case.description, 500)
                    updates_made.append("executive_summary (from description)")
                    needs_update = True
                elif use_case.solution_description:
                    use_case.executive_summary = truncate_text(use_case.solution_description, 500)
                    updates_made.append("executive_summary (from solution)")
                    needs_update = True
                else:
                    if use_case.title:
                        use_case.executive_summary = f"This use case demonstrates {use_case.title}. It showcases innovative approaches to manufacturing challenges and delivers measurable business value."
                        updates_made.append("executive_summary (generated)")
                    else:
                        use_case.executive_summary = "This use case demonstrates innovative manufacturing solutions and best practices."
                        updates_made.append("executive_summary (default)")
                    needs_update = True

            # Fix challenges_and_solutions
            if not use_case.challenges_and_solutions or len(use_case.challenges_and_solutions) == 0:
                use_case.challenges_and_solutions = generate_default_challenges()
                updates_made.append("challenges_and_solutions (default)")
                needs_update = True
            elif not isinstance(use_case.challenges_and_solutions, list):
                use_case.challenges_and_solutions = generate_default_challenges()
                updates_made.append("challenges_and_solutions (fixed structure)")
                needs_update = True

            # Save if updated
            if needs_update:
                try:
                    await use_case.save()
                    stats["total_updated"] += 1

                    # Log updates for important use cases (first few)
                    if i <= 5:
                        logger.info(f"\n  Use Case {i}: {use_case.title[:50]}...")
                        for update in updates_made:
                            logger.info(f"    ✓ Updated {update}")
                    elif i == 6:
                        logger.info(f"  ... (showing first 5, continuing with remaining {total_use_cases - 5})")

                except Exception as e:
                    stats["failed_updates"] += 1
                    logger.error(f"  ❌ Failed to update use case {use_case.title[:30]}...: {e}")

        # Final verification
        logger.info("\n" + "="*70)
        logger.info("📋 MIGRATION SUMMARY")
        logger.info("="*70)
        logger.info(f"✅ Successfully updated: {stats['total_updated']} use cases")
        if stats["failed_updates"] > 0:
            logger.warning(f"❌ Failed updates: {stats['failed_updates']} use cases")

        # Re-check for any remaining issues
        logger.info("\n🔍 Final verification...")
        all_use_cases = await UseCase.find_all().to_list()
        remaining_issues = {
            "subtitle": 0,
            "executive_summary": 0,
            "challenges": 0
        }

        for use_case in all_use_cases:
            if not use_case.subtitle or use_case.subtitle == "null" or use_case.subtitle == "":
                remaining_issues["subtitle"] += 1
            if not use_case.executive_summary or use_case.executive_summary == "null" or use_case.executive_summary == "":
                remaining_issues["executive_summary"] += 1
            if not use_case.challenges_and_solutions or len(use_case.challenges_and_solutions) == 0:
                remaining_issues["challenges"] += 1

        if sum(remaining_issues.values()) == 0:
            logger.info("✅ ALL USE CASES NOW HAVE REQUIRED FIELDS!")
            logger.info("✅ Ready for production deployment")
        else:
            logger.warning("⚠️  Some issues remain:")
            if remaining_issues["subtitle"] > 0:
                logger.warning(f"  • {remaining_issues['subtitle']} use cases still missing subtitle")
            if remaining_issues["executive_summary"] > 0:
                logger.warning(f"  • {remaining_issues['executive_summary']} use cases still missing executive_summary")
            if remaining_issues["challenges"] > 0:
                logger.warning(f"  • {remaining_issues['challenges']} use cases still missing challenges_and_solutions")

        logger.info("\n" + "="*70)
        logger.info("Migration complete!")
        logger.info("="*70 + "\n")

    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(migrate_use_cases())
    sys.exit(exit_code)