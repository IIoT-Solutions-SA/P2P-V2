#!/usr/bin/env python3
"""
Seed script for PostgreSQL Users table.
Creates realistic users from author profiles found in forum and use case data.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
import random

# Add the parent directory to the path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.organization import Organization
from app.models.enums import UserRole, UserStatus

# User profiles extracted from forum and use case data
USER_PROFILES = [
    {
        "id": "450e8400-e29b-41d4-a716-446655440001",
        "first_name": "Sarah",
        "last_name": "Ahmed",
        "email": "sarah.ahmed@advanced-electronics.sa",
        "job_title": "Production Engineer",
        "department": "Manufacturing Operations",
        "bio": "Experienced production engineer specializing in smart manufacturing and IoT sensor integration.",
        "organization_name": "Advanced Electronics Co.",
        "role": UserRole.MEMBER
    },
    {
        "id": "450e8400-e29b-41d4-a716-446655440002",
        "first_name": "Mohammed",
        "last_name": "Al-Rashid",
        "email": "mohammed.rashid@precision-mfg.sa",
        "job_title": "IoT Specialist",
        "department": "Technology Solutions",
        "bio": "IoT and automation specialist with 8+ years experience implementing industrial sensor networks.",
        "organization_name": "Precision Manufacturing Ltd",
        "role": UserRole.MEMBER
    },
    {
        "id": "450e8400-e29b-41d4-a716-446655440003",
        "first_name": "Fatima",
        "last_name": "Hassan",
        "email": "fatima.hassan@arabian-food.sa",
        "job_title": "Quality Manager",
        "department": "Quality Assurance",
        "bio": "Quality control expert specializing in AI-powered inspection systems for food processing.",
        "organization_name": "Arabian Food Processing",
        "role": UserRole.MEMBER
    },
    {
        "id": "450e8400-e29b-41d4-a716-446655440004",
        "first_name": "Ahmed",
        "last_name": "Al-Zahrani",
        "email": "ahmed.alzahrani@south-valley.sa",
        "job_title": "Factory Owner",
        "department": "Executive Management",
        "bio": "Factory owner and entrepreneur focused on digital transformation and team development.",
        "organization_name": "South Valley Industries",
        "role": UserRole.ADMIN
    },
    {
        "id": "450e8400-e29b-41d4-a716-446655440005",
        "first_name": "Mohammed",
        "last_name": "Al-Shahri",
        "email": "mohammed.shahri@gulf-plastics.com",
        "job_title": "Operations Manager",
        "department": "Operations",
        "bio": "Operations manager with proven track record in predictive maintenance and cost reduction.",
        "organization_name": "Gulf Plastics Industries",
        "role": UserRole.MEMBER
    },
    {
        "id": "450e8400-e29b-41d4-a716-446655440006",
        "first_name": "Fatima",
        "last_name": "Al-Otaibi",
        "email": "fatima.otaibi@eastern-industries.sa",
        "job_title": "Factory Owner",
        "department": "Executive Management",
        "bio": "Factory owner specializing in electrical equipment manufacturing and smart inventory systems.",
        "organization_name": "Eastern Industries",
        "role": UserRole.ADMIN
    },
    {
        "id": "450e8400-e29b-41d4-a716-446655440007",
        "first_name": "Khalid",
        "last_name": "Al-Ghamdi",
        "email": "khalid.ghamdi@pharma-excellence.sa",
        "job_title": "Quality Engineer",
        "department": "Quality Control",
        "bio": "Quality engineer with expertise in AI-powered quality inspection for pharmaceutical packaging.",
        "organization_name": "Pharma Excellence Ltd",
        "role": UserRole.MEMBER
    },
    {
        "id": "450e8400-e29b-41d4-a716-446655440008",
        "first_name": "Ahmed",
        "last_name": "Al-Rasheed",
        "email": "ahmed.rasheed@saudi-steel.sa",
        "job_title": "Plant Manager",
        "department": "Manufacturing Operations",
        "bio": "Plant manager overseeing steel production operations with focus on automation and robotics.",
        "organization_name": "Saudi Steel Works",
        "role": UserRole.MEMBER
    },
    {
        "id": "450e8400-e29b-41d4-a716-446655440009",
        "first_name": "Sarah",
        "last_name": "Al-Mansouri",
        "email": "sarah.mansouri@eco-green.sa",
        "job_title": "Quality Engineer", 
        "department": "Quality Assurance",
        "bio": "Sustainability-focused quality engineer implementing green manufacturing practices.",
        "organization_name": "Eco-Green Industries",
        "role": UserRole.MEMBER
    },
    {
        "id": "450e8400-e29b-41d4-a716-44665544000a",
        "first_name": "Mohammed",
        "last_name": "Al-Zahrani",
        "email": "mohammed.zahrani@future-tech.sa",
        "job_title": "Operations Director",
        "department": "Operations",
        "bio": "Operations director leading Industry 4.0 transformation initiatives and digital innovation.",
        "organization_name": "Future Tech Manufacturing",
        "role": UserRole.MEMBER
    },
    {
        "id": "450e8400-e29b-41d4-a716-44665544000b",
        "first_name": "Noura",
        "last_name": "Al-Saud",
        "email": "noura.alsaud@secure-supply.sa",
        "job_title": "Innovation Lead",
        "department": "Research & Development",
        "bio": "Innovation leader driving smart logistics and supply chain technology adoption.",
        "organization_name": "Secure Supply Co.",
        "role": UserRole.MEMBER
    },
    {
        "id": "450e8400-e29b-41d4-a716-44665544000c",
        "first_name": "Omar",
        "last_name": "Al-Harthi",
        "email": "omar.harthi@safety-first.sa",
        "job_title": "Technical Director",
        "department": "Engineering",
        "bio": "Technical director specializing in industrial safety systems and predictive analytics.",
        "organization_name": "Safety First Industries",
        "role": UserRole.MEMBER
    },
    {
        "id": "450e8400-e29b-41d4-a716-44665544000d",
        "first_name": "Maryam",
        "last_name": "Al-Dosari",
        "email": "maryam.dosari@redsea-food.sa",
        "job_title": "Sustainability Manager",
        "department": "Sustainability",
        "bio": "Sustainability manager focusing on eco-friendly food processing and cold chain optimization.",
        "organization_name": "Red Sea Food Processing",
        "role": UserRole.MEMBER
    },
    {
        "id": "450e8400-e29b-41d4-a716-44665544000e",
        "first_name": "Aisha",
        "last_name": "Al-Mutairi",
        "email": "aisha.mutairi@capital-mfg.sa",
        "job_title": "Quality Manager",
        "department": "Quality Assurance",
        "bio": "Quality manager promoting shared manufacturing excellence across SME community.",
        "organization_name": "Capital Manufacturing Hub",
        "role": UserRole.MEMBER
    },
    {
        "id": "450e8400-e29b-41d4-a716-44665544000f",
        "first_name": "Saud",
        "last_name": "Al-Otaishan",
        "email": "saud.otaishan@north-riyadh-logistics.sa",
        "job_title": "Operations Manager",
        "department": "Operations",
        "bio": "Operations manager implementing smart warehousing and automated material handling systems.",
        "organization_name": "North Riyadh Logistics",
        "role": UserRole.MEMBER
    }
]

# Additional users to reach a good sample size
ADDITIONAL_USERS = [
    {
        "first_name": "Reem", "last_name": "Al-Harbi", 
        "job_title": "Production Engineer", "department": "Manufacturing"
    },
    {
        "first_name": "Hassan", "last_name": "Al-Shehri",
        "job_title": "Manufacturing Director", "department": "Operations"
    },
    {
        "first_name": "Lina", "last_name": "Al-Qasemi",
        "job_title": "Process Manager", "department": "Process Engineering"
    },
    {
        "first_name": "Faisal", "last_name": "Al-Najjar",
        "job_title": "Plant Engineer", "department": "Engineering"
    },
    {
        "first_name": "Nadia", "last_name": "Al-Faraj",
        "job_title": "Quality Specialist", "department": "Quality Control"
    },
    {
        "first_name": "Yousef", "last_name": "Al-Hamad",
        "job_title": "Automation Engineer", "department": "Engineering"
    },
    {
        "first_name": "Layla", "last_name": "Al-Khalil",
        "job_title": "Data Analyst", "department": "IT & Analytics"
    },
    {
        "first_name": "Tariq", "last_name": "Al-Rashid",
        "job_title": "Maintenance Manager", "department": "Maintenance"
    },
    {
        "first_name": "Hala", "last_name": "Al-Sabah",
        "job_title": "Supply Chain Manager", "department": "Logistics"
    },
    {
        "first_name": "Majid", "last_name": "Al-Thani",
        "job_title": "Safety Engineer", "department": "Safety & Compliance"
    }
]

def generate_supertokens_id() -> str:
    """Generate a realistic SuperTokens user ID."""
    return f"st-{uuid.uuid4().hex[:16]}"

def generate_phone_number() -> str:
    """Generate a Saudi Arabian phone number."""
    prefixes = ["+966-11", "+966-12", "+966-13", "+966-14", "+966-17"]
    prefix = random.choice(prefixes)
    number = f"{random.randint(200, 999)}-{random.randint(1000, 9999)}"
    return f"{prefix}-{number}"

def create_email(first_name: str, last_name: str, org_name: str) -> str:
    """Create email based on name and organization."""
    # Clean organization name for domain
    domain_part = org_name.lower()
    domain_part = domain_part.replace(" ", "-")
    domain_part = domain_part.replace(".", "")
    domain_part = domain_part.replace("co", "")
    domain_part = domain_part.replace("ltd", "")
    domain_part = domain_part.replace("industries", "ind")
    domain_part = domain_part.replace("manufacturing", "mfg")
    domain_part = domain_part.replace("processing", "proc")
    domain_part = domain_part.strip("-")
    
    if not domain_part.endswith(".sa"):
        domain_part += ".sa"
    
    first_clean = first_name.lower().replace(" ", "")
    last_clean = last_name.lower().replace(" ", "").replace("-", "")
    
    return f"{first_clean}.{last_clean}@{domain_part}"

def create_bio(job_title: str, department: str, org_name: str) -> str:
    """Create a realistic bio based on job title and department."""
    experience_years = random.randint(3, 15)
    
    bio_templates = [
        f"{job_title} with {experience_years}+ years of experience in {department.lower()}. Passionate about driving innovation and operational excellence.",
        f"Experienced {job_title.lower()} specializing in digital transformation and process optimization within {department.lower()}.",
        f"Dedicated {job_title.lower()} focused on implementing cutting-edge solutions in {department.lower()} operations.",
        f"{job_title} leading {department.lower()} initiatives with expertise in automation and smart manufacturing technologies."
    ]
    
    return random.choice(bio_templates)

async def get_organization_mapping(session) -> Dict[str, uuid.UUID]:
    """Get mapping of organization names to IDs."""
    result = await session.execute(select(Organization.id, Organization.name))
    orgs = result.all()
    return {org.name: org.id for org in orgs}

async def clear_existing_users(session):
    """Clear existing user data."""
    
    # Clear users (this will cascade to related data due to foreign keys)
    await session.execute(delete(User))
    await session.commit()
    print("🗑️  Cleared existing user data")

async def seed_primary_users(session, org_mapping: Dict[str, uuid.UUID]):
    """Create users from predefined profiles."""
    
    users = []
    
    for user_data in USER_PROFILES:
        org_id = org_mapping.get(user_data["organization_name"])
        if not org_id:
            print(f"⚠️  Warning: Organization '{user_data['organization_name']}' not found, skipping user {user_data['first_name']} {user_data['last_name']}")
            continue
        
        # Determine user status (most users are active)
        status = UserStatus.ACTIVE if random.random() > 0.1 else UserStatus.PENDING
        email_verified = status == UserStatus.ACTIVE
        
        user = User(
            id=uuid.UUID(user_data["id"]),
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=user_data["email"],
            phone_number=generate_phone_number(),
            job_title=user_data["job_title"],
            department=user_data["department"],
            bio=user_data["bio"],
            role=user_data["role"],
            status=status,
            organization_id=org_id,
            supertokens_user_id=generate_supertokens_id(),
            email_verified=email_verified,
            email_verified_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)) if email_verified else None,
            email_notifications_enabled=True,
            forum_notifications_enabled=True,
            message_notifications_enabled=True,
            created_at=datetime.utcnow() - timedelta(days=random.randint(30, 400)),
            updated_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
        )
        
        users.append(user)
    
    session.add_all(users)
    await session.commit()
    
    print(f"✅ Created {len(users)} primary users from author profiles")
    return users

async def seed_additional_users(session, org_mapping: Dict[str, uuid.UUID]):
    """Create additional users to populate all organizations."""
    
    users = []
    org_ids = list(org_mapping.values())
    
    for i, user_data in enumerate(ADDITIONAL_USERS):
        # Assign to organizations cyclically
        org_id = org_ids[i % len(org_ids)]
        org_name = next(name for name, id in org_mapping.items() if id == org_id)
        
        # Generate email
        email = create_email(user_data["first_name"], user_data["last_name"], org_name)
        
        # Generate bio
        bio = create_bio(user_data["job_title"], user_data["department"], org_name)
        
        # Determine role (mostly members, some admins)
        role = UserRole.ADMIN if user_data["job_title"].lower() in ["director", "manager"] and random.random() > 0.7 else UserRole.MEMBER
        
        # Status (most active)
        status = UserStatus.ACTIVE if random.random() > 0.15 else UserStatus.PENDING
        email_verified = status == UserStatus.ACTIVE
        
        user = User(
            id=uuid.uuid4(),
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            email=email,
            phone_number=generate_phone_number(),
            job_title=user_data["job_title"],
            department=user_data["department"],
            bio=bio,
            role=role,
            status=status,
            organization_id=org_id,
            supertokens_user_id=generate_supertokens_id(),
            email_verified=email_verified,
            email_verified_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)) if email_verified else None,
            email_notifications_enabled=random.choice([True, False]),
            forum_notifications_enabled=random.choice([True, False]),
            message_notifications_enabled=random.choice([True, True, False]),  # Bias towards True
            created_at=datetime.utcnow() - timedelta(days=random.randint(30, 200)),
            updated_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
        )
        
        users.append(user)
    
    session.add_all(users)
    await session.commit()
    
    print(f"✅ Created {len(users)} additional users")
    return users

async def verify_users(session):
    """Verify the seeded user data."""
    
    from sqlalchemy import func, select
    
    # Count users by status
    total_result = await session.execute(select(func.count(User.id)))
    total_count = total_result.scalar()
    
    active_result = await session.execute(
        select(func.count(User.id)).where(User.status == UserStatus.ACTIVE)
    )
    active_count = active_result.scalar()
    
    admin_result = await session.execute(
        select(func.count(User.id)).where(User.role == UserRole.ADMIN)
    )
    admin_count = admin_result.scalar()
    
    verified_result = await session.execute(
        select(func.count(User.id)).where(User.email_verified == True)
    )
    verified_count = verified_result.scalar()
    
    print(f"\n📈 User Seeding Verification:")
    print(f"  Total Users: {total_count}")
    print(f"  Active: {active_count}")
    print(f"  Admins: {admin_count}")
    print(f"  Email Verified: {verified_count}")
    
    # Count by organization
    org_user_result = await session.execute(
        select(Organization.name, func.count(User.id))
        .join(User, User.organization_id == Organization.id)
        .group_by(Organization.name)
        .order_by(func.count(User.id).desc())
        .limit(5)
    )
    org_users = org_user_result.all()
    
    if org_users:
        print(f"\n🏢 Top Organizations by User Count:")
        for org_name, user_count in org_users:
            print(f"  {org_name}: {user_count} users")
    
    # Show sample user
    sample_result = await session.execute(select(User).limit(1))
    sample_user = sample_result.scalar_one_or_none()
    
    if sample_user:
        print(f"\n👤 Sample User:")
        print(f"  Name: {sample_user.full_name}")
        print(f"  Email: {sample_user.email}")
        print(f"  Job Title: {sample_user.job_title}")
        print(f"  Department: {sample_user.department}")
        print(f"  Role: {sample_user.role}")
        print(f"  Status: {sample_user.status}")
        print(f"  Email Verified: {sample_user.email_verified}")

async def seed_users_main():
    """Main seeding function."""
    print("👥 Starting User PostgreSQL Seeding...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Get organization mapping
            print("🏢 Loading organizations...")
            org_mapping = await get_organization_mapping(session)
            print(f"📋 Found {len(org_mapping)} organizations")
            
            # Clear existing data
            await clear_existing_users(session)
            
            # Create primary users from author profiles
            print("👤 Creating users from author profiles...")
            primary_users = await seed_primary_users(session, org_mapping)
            
            # Create additional users
            print("👥 Creating additional users...")
            additional_users = await seed_additional_users(session, org_mapping)
            
            total_users = len(primary_users) + len(additional_users)
            print(f"✅ User seeding completed successfully! Created {total_users} users")
            
            # Verify data
            print("\n🔍 Verifying seeded data...")
            await verify_users(session)
            
            return True
            
        except Exception as e:
            print(f"❌ Error seeding users: {e}")
            await session.rollback()
            return False

if __name__ == "__main__":
    print("🌱 Starting User Seeding...")
    
    success = asyncio.run(seed_users_main())
    
    if success:
        print("\n✅ User seeding completed successfully!")
    else:
        print("\n❌ User seeding failed!")
        exit(1)