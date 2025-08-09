#!/usr/bin/env python3
"""
Seed script for MongoDB Use Cases collection.
Converts frontend use-cases.json data to proper MongoDB documents.
"""

import json
import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# Use case categories mapping from frontend to backend enums
CATEGORY_MAPPING = {
    "Quality Control": "quality",
    "Predictive Maintenance": "maintenance", 
    "Sustainability": "sustainability",
    "Process Optimization": "efficiency",
    "Factory Automation": "automation",
    "Energy Efficiency": "efficiency",
    "Supply Chain": "efficiency", 
    "Innovation & R&D": "innovation",
    "Training & Safety": "quality"
}

# Sample organization IDs (we'll create proper orgs in Task 3)
ORGANIZATION_IDS = [
    "550e8400-e29b-41d4-a716-446655440001",  # Advanced Electronics Co.
    "550e8400-e29b-41d4-a716-446655440002",  # Gulf Plastics Industries  
    "550e8400-e29b-41d4-a716-446655440003",  # Saudi Steel Works
    "550e8400-e29b-41d4-a716-446655440004",  # Arabian Food Processing
    "550e8400-e29b-41d4-a716-446655440005",  # Precision Manufacturing Ltd
    "550e8400-e29b-41d4-a716-446655440006",  # Eco-Green Industries
    "550e8400-e29b-41d4-a716-446655440007",  # Future Tech Manufacturing
    "550e8400-e29b-41d4-a716-446655440008",  # Secure Supply Co.
    "550e8400-e29b-41d4-a716-446655440009",  # Pharma Excellence Ltd
    "550e8400-e29b-41d4-a716-44665544000a",  # Safety First Industries
    "550e8400-e29b-41d4-a716-44665544000b",  # Eastern Industries
    "550e8400-e29b-41d4-a716-44665544000c",  # Red Sea Food Processing
    "550e8400-e29b-41d4-a716-44665544000d",  # Capital Manufacturing Hub
    "550e8400-e29b-41d4-a716-44665544000e",  # North Riyadh Logistics
    "550e8400-e29b-41d4-a716-44665544000f",  # South Valley Industries
]

# Sample user IDs (we'll create proper users in Task 4)
USER_IDS = [
    "450e8400-e29b-41d4-a716-446655440001",
    "450e8400-e29b-41d4-a716-446655440002", 
    "450e8400-e29b-41d4-a716-446655440003",
    "450e8400-e29b-41d4-a716-446655440004",
    "450e8400-e29b-41d4-a716-446655440005",
    "450e8400-e29b-41d4-a716-446655440006",
    "450e8400-e29b-41d4-a716-446655440007",
    "450e8400-e29b-41d4-a716-446655440008",
    "450e8400-e29b-41d4-a716-446655440009",
    "450e8400-e29b-41d4-a716-44665544000a",
    "450e8400-e29b-41d4-a716-44665544000b",
    "450e8400-e29b-41d4-a716-44665544000c",
    "450e8400-e29b-41d4-a716-44665544000d",
    "450e8400-e29b-41d4-a716-44665544000e",
    "450e8400-e29b-41d4-a716-44665544000f",
]

# Sample author names and titles for published_by
AUTHOR_DATA = [
    {"name": "Ahmed Al-Rashid", "title": "Production Manager"},
    {"name": "Sarah Al-Mansouri", "title": "Quality Engineer"},
    {"name": "Mohammed Al-Zahrani", "title": "Operations Director"},
    {"name": "Fatima Al-Otaibi", "title": "Process Engineer"},
    {"name": "Khalid Al-Ghamdi", "title": "Factory Manager"},
    {"name": "Noura Al-Saud", "title": "Innovation Lead"},
    {"name": "Omar Al-Harthi", "title": "Technical Director"},
    {"name": "Maryam Al-Dosari", "title": "Sustainability Manager"},
    {"name": "Abdulaziz Al-Rasheed", "title": "Plant Manager"},
    {"name": "Aisha Al-Mutairi", "title": "Quality Manager"},
    {"name": "Saud Al-Otaishan", "title": "Operations Manager"},
    {"name": "Reem Al-Harbi", "title": "Production Engineer"},
    {"name": "Hassan Al-Shehri", "title": "Manufacturing Director"},
    {"name": "Lina Al-Qasemi", "title": "Process Manager"},
    {"name": "Faisal Al-Najjar", "title": "Plant Engineer"},
]

def extract_metrics_from_benefits(benefits: List[str]) -> Dict[str, Any]:
    """Extract structured metrics from benefit strings."""
    metrics = []
    roi_data = {}
    
    for benefit in benefits:
        # Extract percentages and monetary values
        if "%" in benefit:
            parts = benefit.split("%")
            if len(parts) >= 2:
                try:
                    percentage = float(parts[0].split()[-1])
                    metric_name = " ".join(parts[0].split()[:-1])
                    metrics.append({
                        "name": metric_name,
                        "value": f"{percentage}%",
                        "improvement_percentage": percentage
                    })
                except (ValueError, IndexError):
                    # Fallback to string value
                    metrics.append({
                        "name": "Performance Improvement",
                        "value": benefit
                    })
        elif "SAR" in benefit or "$" in benefit or "K" in benefit or "M" in benefit:
            # This is likely ROI/savings data
            if "annual" in benefit.lower():
                roi_data["annual_return"] = benefit
            else:
                roi_data["total_investment"] = benefit
            
            metrics.append({
                "name": "Cost Savings",
                "value": benefit
            })
        else:
            # General benefit
            metrics.append({
                "name": "Operational Benefit", 
                "value": benefit
            })
    
    return {
        "metrics": metrics,
        "roi": roi_data if roi_data else None
    }

def map_category_to_industry(category: str, factory_name: str) -> str:
    """Map category and factory name to industry."""
    if "electronics" in factory_name.lower() or "tech" in factory_name.lower():
        return "Electronics & Technology"
    elif "plastic" in factory_name.lower() or "chemical" in factory_name.lower():
        return "Chemicals & Plastics"
    elif "steel" in factory_name.lower() or "metal" in factory_name.lower():
        return "Metals & Steel"
    elif "food" in factory_name.lower():
        return "Food & Beverage"
    elif "pharma" in factory_name.lower():
        return "Pharmaceuticals"
    elif "logistics" in factory_name.lower() or "supply" in factory_name.lower():
        return "Logistics & Supply Chain"
    else:
        return "Manufacturing General"

def extract_technologies_from_description(description: str, category: str) -> List[str]:
    """Extract technologies from description text."""
    tech_keywords = {
        "ai": ["AI", "artificial intelligence", "machine learning", "computer vision"],
        "iot": ["IoT", "sensors", "smart", "connected", "monitoring"],
        "automation": ["robotic", "automated", "automation", "RPA"],
        "analytics": ["analytics", "data", "dashboard", "reporting"],
        "cloud": ["cloud", "edge computing", "digital twin"],
        "blockchain": ["blockchain", "distributed ledger"],
        "ar_vr": ["AR", "VR", "augmented reality", "virtual reality"]
    }
    
    description_lower = description.lower()
    technologies = []
    
    for tech_category, keywords in tech_keywords.items():
        for keyword in keywords:
            if keyword.lower() in description_lower:
                if tech_category == "ai":
                    technologies.append("Artificial Intelligence")
                elif tech_category == "iot":
                    technologies.append("Internet of Things") 
                elif tech_category == "automation":
                    technologies.append("Process Automation")
                elif tech_category == "analytics":
                    technologies.append("Data Analytics")
                elif tech_category == "cloud":
                    technologies.append("Cloud Computing")
                elif tech_category == "blockchain":
                    technologies.append("Blockchain")
                elif tech_category == "ar_vr":
                    technologies.append("Augmented Reality")
                break
    
    return list(set(technologies))  # Remove duplicates

def generate_realistic_metrics(base_views: int) -> Dict[str, int]:
    """Generate realistic engagement metrics based on views."""
    return {
        "views": base_views,
        "unique_views": int(base_views * 0.8),  # 80% unique
        "likes": int(base_views * 0.05),        # 5% like rate
        "saves": int(base_views * 0.02),        # 2% save rate  
        "shares": int(base_views * 0.01),       # 1% share rate
        "inquiries": int(base_views * 0.003),   # 0.3% inquiry rate
    }

def convert_frontend_to_mongodb(frontend_data: List[Dict]) -> List[Dict]:
    """Convert frontend use case data to MongoDB format."""
    mongodb_documents = []
    
    for i, case in enumerate(frontend_data):
        # Extract metrics from benefits
        results_data = extract_metrics_from_benefits(case["benefits"])
        
        # Generate realistic engagement metrics
        base_views = 50 + (i * 25) + (hash(case["title"]) % 200)  # Pseudo-random but consistent
        engagement_metrics = generate_realistic_metrics(base_views)
        
        # Map frontend category to backend enum
        backend_category = CATEGORY_MAPPING.get(case["category"], "efficiency")
        
        # Extract technologies from description
        technologies = extract_technologies_from_description(case["description"], case["category"])
        
        # Create MongoDB document
        now = datetime.now(timezone.utc)
        created_date = now - timedelta(days=30 + (i * 2))  # Stagger creation dates
        published_date = created_date + timedelta(hours=2)  # Published 2 hours after creation
        
        # Match the existing simpler MongoDB schema
        document = {
            "submission_id": str(uuid.uuid4()),
            "title": case["title"],
            "organization_id": ORGANIZATION_IDS[i % len(ORGANIZATION_IDS)],
            "submitted_by": USER_IDS[i % len(USER_IDS)],
            
            # Basic Information
            "industry": map_category_to_industry(case["category"], case["factoryName"]),
            "technology": technologies,
            
            # Problem & Solution
            "problem_statement": f"Addressing {case['category'].lower()} challenges in {case['factoryName']}. {case['description']}",
            "solution": f"Implemented {case['title'].lower()} to achieve significant improvements. {case['implementationTime']}.",
            
            # Results & Outcomes
            "outcomes": {
                "benefits": case["benefits"],
                "metrics": results_data["metrics"],
                "roi": results_data.get("roi"),
                "implementation_time": case["implementationTime"]
            },
            
            # Vendor info (simplified)
            "vendor_info": {
                "technologies_used": technologies,
                "category": case["category"],
                "company": case["factoryName"]
            },
            
            # Media (empty for now)
            "media": [],
            
            # Location
            "location": {
                "city": case["city"],
                "coordinates": {
                    "lat": case["latitude"],
                    "lng": case["longitude"]
                }
            },
            
            # Tags
            "tags": [
                case["category"].lower().replace(" ", "_"),
                case["city"].lower(),
                "saudi_arabia",
                backend_category
            ],
            
            # Engagement metrics
            "views": engagement_metrics["views"],
            
            # Timestamps
            "created_at": created_date,
            "updated_at": created_date
        }
        
        mongodb_documents.append(document)
    
    return mongodb_documents

async def seed_use_cases():
    """Main seeding function."""
    
    # Load frontend data
    frontend_data_path = Path(__file__).parent.parent.parent / "p2p-frontend-app" / "src" / "data" / "use-cases.json"
    
    if not frontend_data_path.exists():
        print(f"❌ Frontend data file not found: {frontend_data_path}")
        return False
    
    with open(frontend_data_path, 'r', encoding='utf-8') as f:
        frontend_data = json.load(f)
    
    print(f"📊 Loaded {len(frontend_data)} use cases from frontend data")
    
    # Convert to MongoDB format
    mongodb_docs = convert_frontend_to_mongodb(frontend_data)
    print(f"🔄 Converted {len(mongodb_docs)} documents for MongoDB")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.p2p_sandbox
    collection = db.use_cases
    
    try:
        # Clear existing data
        result = await collection.delete_many({})
        print(f"🗑️  Cleared {result.deleted_count} existing use cases")
        
        # Insert new data
        if mongodb_docs:
            result = await collection.insert_many(mongodb_docs)
            print(f"✅ Inserted {len(result.inserted_ids)} use cases successfully")
            
            # Create indexes for performance (skip if they exist)
            try:
                await collection.create_index("organization_id")
                await collection.create_index("submitted_by")
                await collection.create_index("industry")
                await collection.create_index("created_at")
                print("📋 Created database indexes")
            except Exception as index_error:
                print(f"📋 Indexes may already exist: {index_error}")
                print("📋 Skipping index creation")
            
        return True
        
    except Exception as e:
        print(f"❌ Error seeding use cases: {e}")
        return False
    finally:
        client.close()

async def verify_seed():
    """Verify the seeded data."""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.p2p_sandbox
    collection = db.use_cases
    
    try:
        # Count documents
        total_count = await collection.count_documents({})
        recent_count = await collection.count_documents({"created_at": {"$gte": datetime.now(timezone.utc) - timedelta(days=60)}})
        tech_count = await collection.count_documents({"technology": {"$ne": []}})
        
        print(f"\n📈 Seeding Verification:")
        print(f"  Total use cases: {total_count}")
        print(f"  Recent (last 60 days): {recent_count}")
        print(f"  With technologies: {tech_count}")
        
        # Show sample document
        sample = await collection.find_one({})
        if sample:
            print(f"\n📋 Sample Document:")
            print(f"  Title: {sample['title']}")
            print(f"  Industry: {sample['industry']}")
            print(f"  Views: {sample['views']}")
            print(f"  Location: {sample['location']['city']}")
            print(f"  Technologies: {', '.join(sample['technology'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying seed: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    print("🌱 Starting Use Cases MongoDB Seeding...")
    
    # Run seeding
    success = asyncio.run(seed_use_cases())
    
    if success:
        print("\n🔍 Verifying seeded data...")
        asyncio.run(verify_seed())
        print("\n✅ Use Cases seeding completed successfully!")
    else:
        print("\n❌ Use Cases seeding failed!")
        exit(1)