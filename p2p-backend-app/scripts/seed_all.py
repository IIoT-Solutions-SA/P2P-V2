#!/usr/bin/env python3
"""
Master seed script with reset capabilities.
Orchestrates all database seeding in the correct order with dependency management.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the parent directory to the path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.session import AsyncSessionLocal
from app.core.config import settings

# Seeding order (dependencies matter!)
SEEDING_ORDER = [
    {
        "name": "Organizations",
        "script": "seed_organizations.py",
        "description": "Create organizations from factory names (required for users and forum topics)",
        "database": "postgresql"
    },
    {
        "name": "Users",
        "script": "seed_users.py", 
        "description": "Create users from author profiles (required for forum topics/posts)",
        "database": "postgresql"
    },
    {
        "name": "SuperTokens Users",
        "script": "seed_supertokens_users.py",
        "description": "Create actual SuperTokens users and link with database users",
        "database": "supertokens"
    },
    {
        "name": "Use Cases",
        "script": "seed_use_cases.py",
        "description": "Seed MongoDB use cases from frontend data",
        "database": "mongodb"
    },
    {
        "name": "Forum Categories",
        "script": "seed_forum.py",
        "description": "Create forum categories (topics/posts creation ready but skipped until users exist)",
        "database": "postgresql"
    }
]

class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text: str):
    """Print a colored header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print(f"{text.center(60)}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text: str):
    """Print success message in green."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """Print error message in red."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text: str):
    """Print info message in blue."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_step(step: int, total: int, text: str):
    """Print step indicator."""
    print(f"{Colors.BOLD}{Colors.MAGENTA}[{step}/{total}] {text}{Colors.END}")

async def check_database_connections():
    """Verify database connections before seeding."""
    print_step(0, 0, "Checking database connections...")
    
    success = True
    
    # Check PostgreSQL
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        print_success("PostgreSQL connection verified")
    except Exception as e:
        print_error(f"PostgreSQL connection failed: {e}")
        success = False
    
    # Check MongoDB
    try:
        client = AsyncIOMotorClient(str(settings.MONGODB_URL))
        await client.admin.command('ping')
        client.close()
        print_success("MongoDB connection verified")
    except Exception as e:
        print_error(f"MongoDB connection failed: {e}")
        success = False
    
    return success

async def clear_all_databases():
    """Clear all data from both PostgreSQL and MongoDB."""
    print_step(0, 0, "Clearing all databases...")
    
    success = True
    
    # Clear PostgreSQL tables in correct order (reverse foreign key dependency)
    try:
        async with AsyncSessionLocal() as session:
            print_info("Clearing PostgreSQL tables...")
            
            # Forum tables (in dependency order)
            tables_to_clear = [
                "forum_topic_views",
                "forum_post_likes", 
                "forum_topic_likes",
                "forum_posts",
                "forum_topics",
                "forum_categories",
                "users",
                "organizations"
            ]
            
            for table in tables_to_clear:
                try:
                    await session.execute(text(f"DELETE FROM {table}"))
                    print(f"  🗑️  Cleared {table}")
                except Exception as e:
                    print_warning(f"Could not clear {table}: {e}")
            
            await session.commit()
            print_success("PostgreSQL tables cleared")
            
    except Exception as e:
        print_error(f"PostgreSQL clearing failed: {e}")
        success = False
    
    # Clear MongoDB collections
    try:
        client = AsyncIOMotorClient(str(settings.MONGODB_URL))
        db = client[settings.MONGODB_DB_NAME]
        
        print_info("Clearing MongoDB collections...")
        
        collections_to_clear = ["use_cases", "use_case_views", "use_case_likes", "use_case_saves"]
        
        for collection_name in collections_to_clear:
            try:
                collection = db[collection_name]
                result = await collection.delete_many({})
                print(f"  🗑️  Cleared {collection_name} ({result.deleted_count} documents)")
            except Exception as e:
                print_warning(f"Could not clear {collection_name}: {e}")
        
        client.close()
        print_success("MongoDB collections cleared")
        
    except Exception as e:
        print_error(f"MongoDB clearing failed: {e}")
        success = False
    
    return success

async def run_seed_directly(seed_name: str) -> tuple[bool, str]:
    """Run seed functions directly instead of as subprocess."""
    try:
        output_lines = []
        
        if seed_name == "Organizations":
            # Import and run organizations seeding
            from seed_organizations import seed_organizations_main
            success = await seed_organizations_main()
            output_lines = [f"Organizations seeded: {success}"]
            
        elif seed_name == "Users":
            # Import and run users seeding
            from seed_users import seed_users_main
            success = await seed_users_main()
            output_lines = [f"Users seeded: {success}"]
            
        elif seed_name == "SuperTokens Users":
            # Import and run SuperTokens users linking
            from link_supertokens_users import main as link_users_main
            success = await link_users_main()
            output_lines = [f"SuperTokens users linked: {success}"]
            
        elif seed_name == "Use Cases":
            # Import and run use cases seeding
            from seed_use_cases import seed_use_cases, verify_seed
            success = await seed_use_cases()
            if success:
                await verify_seed()
            output_lines = [f"Use cases seeded: {success}"]
            
        elif seed_name == "Forum Categories":
            # Import and run forum seeding
            from seed_forum import seed_forum
            success = await seed_forum()
            output_lines = [f"Forum categories seeded: {success}"]
            
        else:
            return False, f"Unknown seed: {seed_name}"
        
        return success, "\n".join(output_lines)
        
    except Exception as e:
        return False, f"Direct seeding failed: {str(e)}"

async def seed_all_data():
    """Run all seeding scripts in the correct order."""
    print_header("🌱 DATABASE SEEDING")
    
    total_steps = len(SEEDING_ORDER)
    successful_seeds = []
    failed_seeds = []
    
    for i, seed_config in enumerate(SEEDING_ORDER, 1):
        print_step(i, total_steps, f"Seeding {seed_config['name']}")
        print_info(f"Description: {seed_config['description']}")
        
        print(f"  🔄 Running {seed_config['name']} seeding...")
        
        success, output = await run_seed_directly(seed_config["name"])
        
        if success:
            print_success(f"{seed_config['name']} seeding completed")
            successful_seeds.append(seed_config["name"])
            
            # Show key output lines (avoid spam)
            output_lines = output.strip().split('\n')
            key_lines = [line for line in output_lines if any(indicator in line for indicator in ['✅', '📈', '📋', '⏭️'])]
            for line in key_lines[-3:]:  # Show last 3 key lines
                print(f"    {line}")
        else:
            print_error(f"{seed_config['name']} seeding failed")
            failed_seeds.append(seed_config["name"])
            
            # Show error details
            error_lines = output.strip().split('\n')
            for line in error_lines[-5:]:  # Show last 5 lines of error
                if line.strip():
                    print(f"    {Colors.RED}{line}{Colors.END}")
        
        print()  # Add spacing between seeds
    
    # Summary
    print_header("📊 SEEDING SUMMARY")
    
    if successful_seeds:
        print_success(f"Successfully seeded: {', '.join(successful_seeds)}")
    
    if failed_seeds:
        print_error(f"Failed to seed: {', '.join(failed_seeds)}")
    
    return len(failed_seeds) == 0

async def verify_all_data():
    """Verify data was seeded correctly across all databases."""
    print_header("🔍 DATA VERIFICATION")
    
    verification_results = {}
    
    # PostgreSQL verification
    try:
        async with AsyncSessionLocal() as session:
            print_info("Verifying PostgreSQL data...")
            
            # Check key tables
            tables_to_check = [
                ("organizations", "Organizations"),
                ("users", "Users"), 
                ("forum_categories", "Forum Categories")
            ]
            
            for table, display_name in tables_to_check:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                verification_results[display_name] = count
                print(f"  📋 {display_name}: {count} records")
    
    except Exception as e:
        print_error(f"PostgreSQL verification failed: {e}")
        verification_results["PostgreSQL"] = "FAILED"
    
    # MongoDB verification
    try:
        client = AsyncIOMotorClient(str(settings.MONGODB_URL))
        db = client[settings.MONGODB_DB_NAME]
        
        print_info("Verifying MongoDB data...")
        
        use_cases_count = await db.use_cases.count_documents({})
        verification_results["Use Cases"] = use_cases_count
        print(f"  📋 Use Cases: {use_cases_count} documents")
        
        client.close()
        
    except Exception as e:
        print_error(f"MongoDB verification failed: {e}")
        verification_results["MongoDB"] = "FAILED"
    
    # Summary
    total_records = sum(v for v in verification_results.values() if isinstance(v, int))
    print_success(f"Total records seeded: {total_records}")
    
    return verification_results

def print_usage():
    """Print usage information."""
    print(f"""
{Colors.BOLD}P2P Database Seeding Script{Colors.END}

{Colors.UNDERLINE}Usage:{Colors.END}
    python seed_all.py [command]

{Colors.UNDERLINE}Commands:{Colors.END}
    seed        - Run all seeding scripts in correct order (default)
    reset       - Clear all databases then run seeding
    clear       - Clear all databases only (no seeding)
    verify      - Verify existing data without seeding
    help        - Show this help message

{Colors.UNDERLINE}Examples:{Colors.END}
    python seed_all.py                # Seed all data
    python seed_all.py reset          # Reset databases and seed fresh data
    python seed_all.py clear          # Clear all data only
    python seed_all.py verify         # Check what data exists

{Colors.UNDERLINE}Seeding Order:{Colors.END}""")
    
    for i, seed_config in enumerate(SEEDING_ORDER, 1):
        print(f"    {i}. {seed_config['name']} ({seed_config['database']})")
        print(f"       {seed_config['description']}")

async def main():
    """Main execution function."""
    
    # Parse command line arguments
    command = sys.argv[1] if len(sys.argv) > 1 else "seed"
    
    if command == "help":
        print_usage()
        return
    
    print_header(f"🚀 P2P DATABASE SEEDING - {command.upper()}")
    
    # Check database connections
    print_step(1, 3, "Checking database connections")
    if not await check_database_connections():
        print_error("Database connection check failed. Please check your connections.")
        sys.exit(1)
    
    # Handle different commands
    if command == "clear":
        print_step(2, 2, "Clearing all databases")
        success = await clear_all_databases()
        
        if success:
            print_success("All databases cleared successfully!")
        else:
            print_error("Database clearing failed!")
            sys.exit(1)
            
    elif command == "verify":
        print_step(2, 2, "Verifying existing data")
        results = await verify_all_data()
        print_success("Data verification completed!")
        
    elif command in ["seed", "reset"]:
        step_count = 3 if command == "seed" else 4
        
        if command == "reset":
            print_step(2, step_count, "Clearing all databases")
            if not await clear_all_databases():
                print_error("Database clearing failed!")
                sys.exit(1)
        
        print_step(step_count - 1, step_count, "Seeding all data")
        success = await seed_all_data()
        
        if not success:
            print_error("Some seeding operations failed!")
            sys.exit(1)
        
        print_step(step_count, step_count, "Verifying seeded data")
        results = await verify_all_data()
        
        print_header("🎉 SEEDING COMPLETED")
        print_success("All database seeding completed successfully!")
        print_info("The P2P platform is now ready with realistic test data.")
        
    else:
        print_error(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Seeding interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Seeding failed with unexpected error: {e}")
        sys.exit(1)