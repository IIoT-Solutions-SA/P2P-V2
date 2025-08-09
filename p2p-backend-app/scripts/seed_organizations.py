#!/usr/bin/env python3
"""
Seed script for PostgreSQL Organizations table.
Creates organizations from factory names found in frontend data.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path
import sys

# Add the parent directory to the path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete
from app.db.session import AsyncSessionLocal
from app.models.organization import Organization
from app.models.enums import OrganizationStatus, IndustryType

# Organization data based on factory names from use cases
ORGANIZATIONS_DATA = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Advanced Electronics Co.",
        "name_arabic": "شركة الإلكترونيات المتقدمة",
        "description": "Leading electronics manufacturing company specializing in AI-powered quality inspection systems and smart manufacturing solutions.",
        "email": "info@advanced-electronics.sa",
        "phone_number": "+966-11-456-7890",
        "website": "https://advanced-electronics.sa",
        "city": "Riyadh",
        "state_province": "Riyadh Region",
        "postal_code": "11564",
        "industry_type": IndustryType.MANUFACTURING,
        "company_size": "51-200",
        "registration_number": "CR-1010123456",
        "tax_id": "300123456700003"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "name": "Gulf Plastics Industries",
        "name_arabic": "صناعات البلاستيك الخليجية",
        "description": "Major plastics manufacturer implementing predictive maintenance and IoT solutions for enhanced operational efficiency.",
        "email": "contact@gulf-plastics.com",
        "phone_number": "+966-13-234-5678",
        "website": "https://gulf-plastics.com",
        "city": "Dammam",
        "state_province": "Eastern Province",
        "postal_code": "31421",
        "industry_type": IndustryType.MANUFACTURING,
        "company_size": "201-500",
        "registration_number": "CR-1013234567",
        "tax_id": "300234567800003"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "name": "Saudi Steel Works",
        "name_arabic": "أعمال الصلب السعودية",
        "description": "Integrated steel manufacturing facility utilizing advanced automation and robotic systems for increased productivity.",
        "email": "admin@saudi-steel.sa",
        "phone_number": "+966-14-345-6789",
        "website": "https://saudi-steel.sa",
        "city": "Yanbu",
        "state_province": "Al Madinah Region",
        "postal_code": "46455",
        "industry_type": IndustryType.MANUFACTURING,
        "company_size": "501-1000",
        "registration_number": "CR-1014345678",
        "tax_id": "300345678900003"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440004",
        "name": "Arabian Food Processing",
        "name_arabic": "معالجة الأغذية العربية",
        "description": "Food processing company implementing smart inventory management and quality control systems for enhanced food safety.",
        "email": "info@arabian-food.sa",
        "phone_number": "+966-12-456-7890",
        "website": "https://arabian-food.sa",
        "city": "Jeddah",
        "state_province": "Makkah Region",
        "postal_code": "21442",
        "industry_type": IndustryType.MANUFACTURING,
        "company_size": "101-200",
        "registration_number": "CR-1012456789",
        "tax_id": "300456789000003"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440005",
        "name": "Precision Manufacturing Ltd",
        "name_arabic": "شركة التصنيع الدقيق المحدودة",
        "description": "Precision engineering company specializing in high-tech manufacturing solutions and advanced automation systems.",
        "email": "contact@precision-mfg.sa",
        "phone_number": "+966-11-567-8901",
        "website": "https://precision-mfg.sa",
        "city": "Riyadh",
        "state_province": "Riyadh Region",
        "postal_code": "11623",
        "industry_type": IndustryType.MANUFACTURING,
        "company_size": "51-100",
        "registration_number": "CR-1011567890",
        "tax_id": "300567890100003"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440006",
        "name": "Eco-Green Industries",
        "name_arabic": "الصناعات الإيكولوجية الخضراء",
        "description": "Sustainable manufacturing company focusing on green technologies and energy-efficient production processes.",
        "email": "info@eco-green.sa",
        "phone_number": "+966-11-678-9012",
        "website": "https://eco-green.sa",
        "city": "Riyadh",
        "state_province": "Riyadh Region",
        "postal_code": "11564",
        "industry_type": IndustryType.ENERGY,
        "company_size": "11-50",
        "registration_number": "CR-1011678901",
        "tax_id": "300678901200003"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440007",
        "name": "Future Tech Manufacturing",
        "name_arabic": "تصنيع التقنيات المستقبلية",
        "description": "Technology-driven manufacturing company implementing AI, IoT, and blockchain solutions for Industry 4.0 transformation.",
        "email": "hello@future-tech.sa",
        "phone_number": "+966-11-789-0123",
        "website": "https://future-tech.sa",
        "city": "Riyadh",
        "state_province": "Riyadh Region",
        "postal_code": "11564",
        "industry_type": IndustryType.TECHNOLOGY,
        "company_size": "51-200",
        "registration_number": "CR-1011789012",
        "tax_id": "300789012300003"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440008",
        "name": "Secure Supply Co.",
        "name_arabic": "شركة التوريد الآمن",
        "description": "Supply chain and logistics company utilizing advanced tracking systems and smart inventory management solutions.",
        "email": "info@secure-supply.sa",
        "phone_number": "+966-11-890-1234",
        "website": "https://secure-supply.sa",
        "city": "Riyadh",
        "state_province": "Riyadh Region",
        "postal_code": "11564",
        "industry_type": IndustryType.LOGISTICS,
        "company_size": "11-50",
        "registration_number": "CR-1011890123",
        "tax_id": "300890123400003"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440009",
        "name": "Pharma Excellence Ltd",
        "name_arabic": "شركة التميز الدوائي المحدودة",
        "description": "Pharmaceutical manufacturing company implementing AI-powered quality inspection and automated production systems.",
        "email": "contact@pharma-excellence.sa",
        "phone_number": "+966-12-901-2345",
        "website": "https://pharma-excellence.sa",
        "city": "Mecca",
        "state_province": "Makkah Region",
        "postal_code": "21955",
        "industry_type": IndustryType.HEALTHCARE,
        "company_size": "101-200",
        "registration_number": "CR-1012901234",
        "tax_id": "300901234500003"
    },
    {
        "id": "550e8400-e29b-41d4-a716-44665544000a",
        "name": "Safety First Industries",
        "name_arabic": "صناعات السلامة أولاً",
        "description": "Industrial safety equipment manufacturer focusing on smart monitoring systems and predictive safety analytics.",
        "email": "safety@safety-first.sa",
        "phone_number": "+966-11-012-3456",
        "website": "https://safety-first.sa",
        "city": "Riyadh",
        "state_province": "Riyadh Region",
        "postal_code": "11564",
        "industry_type": IndustryType.MANUFACTURING,
        "company_size": "11-50",
        "registration_number": "CR-1011012345",
        "tax_id": "300012345600003"
    },
    {
        "id": "550e8400-e29b-41d4-a716-44665544000b",
        "name": "Eastern Industries",
        "name_arabic": "الصناعات الشرقية",
        "description": "Diversified industrial conglomerate implementing digital transformation across multiple manufacturing sectors.",
        "email": "info@eastern-industries.sa",
        "phone_number": "+966-13-123-4567",
        "website": "https://eastern-industries.sa",
        "city": "Dammam",
        "state_province": "Eastern Province",
        "postal_code": "31421",
        "industry_type": IndustryType.MANUFACTURING,
        "company_size": "1000+",
        "registration_number": "CR-1013123456",
        "tax_id": "300123456700004"
    },
    {
        "id": "550e8400-e29b-41d4-a716-44665544000c",
        "name": "Red Sea Food Processing",
        "name_arabic": "معالجة أغذية البحر الأحمر",
        "description": "Seafood processing company utilizing advanced cold chain management and AI-powered quality control systems.",
        "email": "info@redsea-food.sa",
        "phone_number": "+966-12-234-5678",
        "website": "https://redsea-food.sa",
        "city": "Jeddah",
        "state_province": "Makkah Region",
        "postal_code": "21442",
        "industry_type": IndustryType.MANUFACTURING,
        "company_size": "51-100",
        "registration_number": "CR-1012234567",
        "tax_id": "300234567800004"
    },
    {
        "id": "550e8400-e29b-41d4-a716-44665544000d",
        "name": "Capital Manufacturing Hub",
        "name_arabic": "مركز التصنيع الرأسمالي",
        "description": "Manufacturing hub providing shared smart manufacturing facilities and Industry 4.0 technologies to SMEs.",
        "email": "hub@capital-mfg.sa",
        "phone_number": "+966-11-345-6789",
        "website": "https://capital-mfg.sa",
        "city": "Riyadh",
        "state_province": "Riyadh Region",
        "postal_code": "11564",
        "industry_type": IndustryType.MANUFACTURING,
        "company_size": "201-500",
        "registration_number": "CR-1011345678",
        "tax_id": "300345678900004"
    },
    {
        "id": "550e8400-e29b-41d4-a716-44665544000e",
        "name": "North Riyadh Logistics",
        "name_arabic": "لوجستيات شمال الرياض",
        "description": "Logistics and warehousing company implementing smart inventory management and automated material handling systems.",
        "email": "ops@north-riyadh-logistics.sa",
        "phone_number": "+966-11-456-7890",
        "website": "https://north-riyadh-logistics.sa",
        "city": "Riyadh",
        "state_province": "Riyadh Region",
        "postal_code": "13241",
        "industry_type": IndustryType.LOGISTICS,
        "company_size": "101-200",
        "registration_number": "CR-1011456789",
        "tax_id": "300456789000004"
    },
    {
        "id": "550e8400-e29b-41d4-a716-44665544000f",
        "name": "South Valley Industries",
        "name_arabic": "صناعات الوادي الجنوبي",
        "description": "Multi-sector manufacturing company specializing in process optimization and energy-efficient production technologies.",
        "email": "contact@south-valley.sa",
        "phone_number": "+966-17-567-8901",
        "website": "https://south-valley.sa",
        "city": "Abha",
        "state_province": "Aseer Region",
        "postal_code": "62521",
        "industry_type": IndustryType.MANUFACTURING,
        "company_size": "51-200",
        "registration_number": "CR-1017567890",
        "tax_id": "300567890100004"
    }
]

def get_trial_end_date() -> datetime:
    """Get trial end date (30 days from now)."""
    return datetime.utcnow() + timedelta(days=30)

def get_company_size_limits(company_size: str) -> tuple[int, int, int]:
    """Get max users, use cases, and storage based on company size."""
    size_mappings = {
        "1-10": (5, 25, 5),
        "11-50": (15, 100, 25),
        "51-100": (25, 200, 50),
        "101-200": (50, 500, 100),
        "201-500": (100, 1000, 200),
        "501-1000": (200, 2000, 500),
        "1000+": (500, 5000, 1000)
    }
    return size_mappings.get(company_size, (10, 50, 10))

async def clear_existing_organizations(session):
    """Clear existing organization data."""
    
    # Clear organizations (this will cascade to related data due to foreign keys)
    await session.execute(delete(Organization))
    await session.commit()
    print("🗑️  Cleared existing organization data")

async def seed_organizations(session):
    """Create organizations from factory names."""
    
    organizations = []
    
    for org_data in ORGANIZATIONS_DATA:
        # Get company size limits
        max_users, max_use_cases, max_storage = get_company_size_limits(org_data["company_size"])
        
        organization = Organization(
            id=uuid.UUID(org_data["id"]),
            name=org_data["name"],
            name_arabic=org_data["name_arabic"],
            description=org_data["description"],
            email=org_data["email"],
            phone_number=org_data["phone_number"],
            website=org_data["website"],
            address_line_1=f"Industrial Area, {org_data['city']}",
            city=org_data["city"],
            state_province=org_data["state_province"],
            postal_code=org_data["postal_code"],
            country="SA",
            industry_type=org_data["industry_type"],
            company_size=org_data["company_size"],
            registration_number=org_data["registration_number"],
            tax_id=org_data["tax_id"],
            status=OrganizationStatus.ACTIVE,  # Most are active
            trial_ends_at=None,  # Active organizations don't have trial end dates
            subscription_tier="professional" if org_data["company_size"] in ["201-500", "501-1000", "1000+"] else "standard",
            max_users=max_users,
            max_use_cases=max_use_cases,
            max_storage_gb=max_storage,
            allow_public_use_cases=True,
            require_use_case_approval=False,
            created_at=datetime.utcnow() - timedelta(days=365),  # Organizations created 1 year ago
            updated_at=datetime.utcnow() - timedelta(days=30)   # Last updated 30 days ago
        )
        
        organizations.append(organization)
    
    # Add a few trial organizations for testing
    trial_orgs = [
        {
            "name": "Innovation Startup Ltd",
            "name_arabic": "شركة الابتكار الناشئة المحدودة",
            "description": "Emerging technology startup exploring AI and IoT solutions for manufacturing.",
            "email": "hello@innovation-startup.sa",
            "city": "Riyadh",
            "state_province": "Riyadh Region",
            "industry_type": IndustryType.TECHNOLOGY,
            "company_size": "1-10",
            "status": OrganizationStatus.TRIAL,
            "subscription_tier": "basic"
        },
        {
            "name": "Green Manufacturing Co",
            "name_arabic": "شركة التصنيع الأخضر",
            "description": "Sustainable manufacturing company testing eco-friendly production methods.",
            "email": "info@green-mfg.sa",
            "city": "Jeddah",
            "state_province": "Makkah Region",
            "industry_type": IndustryType.ENERGY,
            "company_size": "11-50",
            "status": OrganizationStatus.TRIAL,
            "subscription_tier": "standard"
        }
    ]
    
    for trial_data in trial_orgs:
        max_users, max_use_cases, max_storage = get_company_size_limits(trial_data["company_size"])
        
        trial_org = Organization(
            id=uuid.uuid4(),
            name=trial_data["name"],
            name_arabic=trial_data["name_arabic"],
            description=trial_data["description"],
            email=trial_data["email"],
            phone_number="+966-11-000-0000",
            website=None,
            address_line_1=f"Business District, {trial_data['city']}",
            city=trial_data["city"],
            state_province=trial_data["state_province"],
            postal_code="11564",
            country="SA",
            industry_type=trial_data["industry_type"],
            company_size=trial_data["company_size"],
            registration_number=None,
            tax_id=None,
            status=trial_data["status"],
            trial_ends_at=get_trial_end_date(),
            subscription_tier=trial_data["subscription_tier"],
            max_users=max_users,
            max_use_cases=max_use_cases,
            max_storage_gb=max_storage,
            allow_public_use_cases=True,
            require_use_case_approval=False,
            created_at=datetime.utcnow() - timedelta(days=15),  # Created 15 days ago
            updated_at=datetime.utcnow() - timedelta(days=1)    # Updated yesterday
        )
        
        organizations.append(trial_org)
    
    # Insert all organizations
    session.add_all(organizations)
    await session.commit()
    
    print(f"✅ Created {len(organizations)} organizations")
    print(f"   - {len(ORGANIZATIONS_DATA)} active organizations")
    print(f"   - {len(trial_orgs)} trial organizations")

async def verify_organizations(session):
    """Verify the seeded organization data."""
    
    # Count organizations by status
    from sqlalchemy import func, select
    
    total_result = await session.execute(select(func.count(Organization.id)))
    total_count = total_result.scalar()
    
    active_result = await session.execute(
        select(func.count(Organization.id)).where(Organization.status == OrganizationStatus.ACTIVE)
    )
    active_count = active_result.scalar()
    
    trial_result = await session.execute(
        select(func.count(Organization.id)).where(Organization.status == OrganizationStatus.TRIAL)
    )
    trial_count = trial_result.scalar()
    
    # Count by industry
    manufacturing_result = await session.execute(
        select(func.count(Organization.id)).where(Organization.industry_type == IndustryType.MANUFACTURING)
    )
    manufacturing_count = manufacturing_result.scalar()
    
    print(f"\n📈 Organization Seeding Verification:")
    print(f"  Total Organizations: {total_count}")
    print(f"  Active: {active_count}")
    print(f"  Trial: {trial_count}")
    print(f"  Manufacturing: {manufacturing_count}")
    
    # Show sample organization
    sample_result = await session.execute(select(Organization).limit(1))
    sample_org = sample_result.scalar_one_or_none()
    
    if sample_org:
        print(f"\n📋 Sample Organization:")
        print(f"  Name: {sample_org.name}")
        print(f"  Arabic: {sample_org.name_arabic}")
        print(f"  Industry: {sample_org.industry_type}")
        print(f"  City: {sample_org.city}")
        print(f"  Status: {sample_org.status}")
        print(f"  Max Users: {sample_org.max_users}")
        print(f"  Max Use Cases: {sample_org.max_use_cases}")

async def seed_organizations_main():
    """Main seeding function."""
    print("🏢 Starting Organization PostgreSQL Seeding...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Clear existing data
            await clear_existing_organizations(session)
            
            # Create organizations
            print("🏭 Creating organizations from factory names...")
            await seed_organizations(session)
            
            print("✅ Organization seeding completed successfully!")
            
            # Verify data
            print("\n🔍 Verifying seeded data...")
            await verify_organizations(session)
            
            return True
            
        except Exception as e:
            print(f"❌ Error seeding organizations: {e}")
            await session.rollback()
            return False

if __name__ == "__main__":
    print("🌱 Starting Organization Seeding...")
    
    success = asyncio.run(seed_organizations_main())
    
    if success:
        print("\n✅ Organization seeding completed successfully!")
    else:
        print("\n❌ Organization seeding failed!")
        exit(1)