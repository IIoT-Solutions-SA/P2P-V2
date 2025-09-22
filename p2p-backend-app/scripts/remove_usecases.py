import asyncio
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from app.models.mongo_models import UseCase
from app.core.logging import setup_logging

# List of all use case titles to remove (19 total)
USE_CASE_TITLES = [
    # Aadil's use cases
    "Robotic 3D Printer Farm for Drone Arm Production",
    "Digital Simulation for Drone Production Line Optimization",
    "Smart Locker for Raw Material Tracking",

    # Amro's use cases
    "Assembly Workstation",
    "Demanufacturing Workstation",
    "Robotic Inspection Station for Drone Arm Dimensional Accuracy",

    # Hamza's use cases
    "AI-Powered Drone Arm Color Verification Station",
    "ROS2-Based Autonomous Mobile Robot (AMR) Fleet for Factory Logistics",
    "Vision-Assisted Packing Workstation",  # Fixed: Added missing comma
    "Cobot Palletizing Station for Packaged Drones",

    # Abdulrahman's use cases
    "Smart Factory OEE Revolution with Real-Time IoT Analytics",
    "AI-Driven Performance Command Center for Manufacturing Excellence",
    "Next-Generation Shop Floor Intelligence System",

    # Firas's use cases
    "Real-Time Production Visibility Dashboard",
    "Smart Energy Analytics for Sustainable Manufacturing",
    "Digital Bridge: Modernizing Legacy Manufacturing Systems",

    # Hamad Ali's use cases
    "AI-Powered Quality Assurance Revolution",
    "Intelligent Safety Monitoring & Compliance System",
    "Comprehensive Energy Optimization Platform"
]

async def remove_use_cases():
    """Removes all specific use cases from the database"""
    logger = setup_logging()
    logger.info(f"🗑️  Starting removal of {len(USE_CASE_TITLES)} use cases...")

    try:
        await db_manager.init_mongodb()
        logger.info("MongoDB connection established")

        total_removed = 0

        for title in USE_CASE_TITLES:
            logger.info(f"  Searching for: {title}")

            # Find use cases with this title
            use_cases = await UseCase.find(UseCase.title == title).to_list()

            if use_cases:
                for use_case in use_cases:
                    await use_case.delete()
                    logger.info(f"    ✅ Deleted: {title} (ID: {use_case.id})")
                    total_removed += 1
            else:
                logger.warning(f"    ⚠️  Not found: {title}")

        logger.info("=" * 50)
        logger.info(f"🎯 Removal complete!")
        logger.info(f"📊 Total use cases removed: {total_removed}/{len(USE_CASE_TITLES)}")

        if total_removed < len(USE_CASE_TITLES):
            logger.warning(f"⚠️  Some use cases were not found. This is normal if they weren't seeded yet.")

    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        raise
    finally:
        await db_manager.close_connections()
        logger.info("Database connections closed.")

if __name__ == "__main__":
    print(f"🗑️  Starting removal of {len(USE_CASE_TITLES)} use cases...")
    print("This will remove:")
    print("  - 3 use cases from Aadil")
    print("  - 3 use cases from Amro")
    print("  - 4 use cases from Hamza")
    print("  - 3 use cases from Abdulrahman")
    print("  - 3 use cases from Firas")
    print("  - 3 use cases from Hamad Ali")
    print("-" * 50)

    # Ask for confirmation
    response = input("Are you sure you want to remove these use cases? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        asyncio.run(remove_use_cases())
    else:
        print("❌ Removal cancelled.")