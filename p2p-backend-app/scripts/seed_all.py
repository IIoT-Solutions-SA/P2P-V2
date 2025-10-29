#!/usr/bin/env python3
"""
Master seeding script - runs all seed scripts in the correct order.
Usage: python scripts/seed_all.py
"""
import asyncio
import sys
import os
import asyncpg

# Add the parent directory and usecases directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
usecases_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'usecases')
sys.path.append(usecases_dir)

# Import all seed functions
from seed_db_users import seed_users
from seed_team_members import seed_team_members
from verify_existing_users import verify_existing_users
from seed_forums import seed_forums
from seed_usecases import seed_usecases
from seed_user_activities import seed_user_activities

# Import migration for use-cases.json
from migrate_usecase_fields_complete import migrate_use_cases

# Import individual usecase seed functions
from seed_aadil import seed_aadil_usecases
from seed_amro import seed_amro_usecases
from seed_hamza import seed_hamza_usecases
from seed_abdulrahman import seed_abdulrahman_usecases
from seed_firas import seed_firas_usecases
from seed_hamad import seed_hamad_usecases

async def create_supertokens_database():
    """Create the supertokens database if it doesn't exist."""
    try:
        # Connect to default postgres database
        conn = await asyncpg.connect(
            user='p2p_user',
            password='iiot123',
            database='postgres',
            host='postgres',
            port=5432
        )

        # Check if supertokens database exists
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = 'supertokens'")

        if not exists:
            print("  Creating 'supertokens' database...")
            await conn.execute('CREATE DATABASE supertokens')
            print("  ✅ Database 'supertokens' created successfully.")
        else:
            print("  ✅ Database 'supertokens' already exists.")

        await conn.close()

    except Exception as e:
        print(f"  ⚠️  Could not verify/create supertokens database: {e}")
        print("  (May already exist from Docker init script)")

async def seed_all():
    """Run all seed scripts in the correct order."""
    print("\n" + "="*70)
    print("🌱 STARTING COMPLETE DATABASE SEEDING")
    print("   24 Users + 34 Use Cases + Forums + Activities")
    print("="*70 + "\n")

    try:
        # Step 0: Ensure supertokens database exists
        print("\n🗄️  Step 0/13: Verifying database setup...")
        print("-" * 70)
        await create_supertokens_database()
        print()

        # Step 1: Seed users first (required for everything else)
        print("\n📝 Step 1/13: Seeding users (18 demo users)...")
        print("-" * 70)
        await seed_users()
        print("✅ Users seeded successfully!\n")

        # Step 2: Seed team members (6 IIoT Solutions team)
        print("\n👥 Step 2/13: Seeding team members (6 team members)...")
        print("-" * 70)
        await seed_team_members()
        print("✅ Team members seeded successfully!\n")

        # Step 3: Verify all users' emails
        print("\n🔐 Step 3/13: Verifying all user emails...")
        print("-" * 70)
        await verify_existing_users()
        print("✅ All users verified!\n")

        # Step 4: Seed forums (requires users)
        print("\n💬 Step 4/13: Seeding forums...")
        print("-" * 70)
        await seed_forums()
        print("✅ Forums seeded successfully!\n")

        # Step 5: Seed initial 15 use cases from use-cases.json
        print("\n📚 Step 5/13: Seeding initial 15 use cases from use-cases.json...")
        print("-" * 70)
        await seed_usecases()
        print("✅ Initial 15 use cases seeded!\n")

        # Step 6-11: Seed 19 use cases from 6 team members
        print("\n📚 Step 6-11/13: Seeding 19 comprehensive team use cases...")
        print("-" * 70)

        print("\n  6/13: Seeding Aadil's use cases (3 use cases)...")
        await seed_aadil_usecases()
        print("  ✅ Aadil's use cases seeded!\n")

        print("  7/13: Seeding Amro's use cases (3 use cases)...")
        await seed_amro_usecases()
        print("  ✅ Amro's use cases seeded!\n")

        print("  8/13: Seeding Hamza's use cases (4 use cases)...")
        await seed_hamza_usecases()
        print("  ✅ Hamza's use cases seeded!\n")

        print("  9/13: Seeding Abdulrahman's use cases (3 use cases)...")
        await seed_abdulrahman_usecases()
        print("  ✅ Abdulrahman's use cases seeded!\n")

        print("  10/13: Seeding Firas's use cases (3 use cases)...")
        await seed_firas_usecases()
        print("  ✅ Firas's use cases seeded!\n")

        print("  11/13: Seeding Hamad's use cases (3 use cases)...")
        await seed_hamad_usecases()
        print("  ✅ Hamad's use cases seeded!\n")

        print("✅ All 19 team use cases seeded successfully!\n")

        # Step 12: Migrate ALL 34 use cases to add missing fields
        print("\n🔧 Step 12/13: Migrating ALL 34 use cases (adding subtitle, challenges_and_solutions)...")
        print("-" * 70)
        await migrate_use_cases()
        print("✅ All use cases migration complete!\n")

        # Step 13: Seed user activities (requires users, forums, and use cases)
        print("\n🎯 Step 13/13: Seeding user activities...")
        print("-" * 70)
        await seed_user_activities()
        print("✅ User activities seeded successfully!\n")

        print("\n" + "="*70)
        print("🎉 ALL SEEDING COMPLETE!")
        print("   ✅ 24 Users (18 demo + 6 team members)")
        print("   ✅ 34 Use Cases (15 migrated + 19 comprehensive)")
        print("   ✅ Forums & Discussions")
        print("   ✅ User Activities")
        print("="*70 + "\n")

    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ SEEDING FAILED: {e}")
        print("="*70 + "\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(seed_all())
