#!/usr/bin/env python3
"""
Seed script for PostgreSQL Forum tables.
Converts frontend Forum.tsx data to proper PostgreSQL records.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path
import sys

# Add the parent directory to the path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete, func
from app.db.session import get_db, AsyncSessionLocal
from app.models.forum import ForumCategory, ForumTopic, ForumPost, ForumTopicLike, ForumPostLike, ForumTopicView
from app.models.enums import ForumCategoryType

# Sample organization IDs (consistent with use cases)
ORGANIZATION_IDS = [
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002",
    "550e8400-e29b-41d4-a716-446655440003",
    "550e8400-e29b-41d4-a716-446655440004",
]

# Sample user IDs (consistent with use cases)
USER_IDS = [
    "450e8400-e29b-41d4-a716-446655440001",
    "450e8400-e29b-41d4-a716-446655440002", 
    "450e8400-e29b-41d4-a716-446655440003",
    "450e8400-e29b-41d4-a716-446655440004",
    "450e8400-e29b-41d4-a716-446655440005",
    "450e8400-e29b-41d4-a716-446655440006",
]

# Forum categories from frontend
CATEGORIES_DATA = [
    {"id": "automation", "name": "Automation", "count": 42, "color": "bg-blue-100", "type": ForumCategoryType.AUTOMATION},
    {"id": "quality", "name": "Quality Management", "count": 38, "color": "bg-green-100", "type": ForumCategoryType.QUALITY_MANAGEMENT},
    {"id": "maintenance", "name": "Maintenance", "count": 29, "color": "bg-yellow-100", "type": ForumCategoryType.MAINTENANCE},
    {"id": "ai", "name": "Artificial Intelligence", "count": 25, "color": "bg-purple-100", "type": ForumCategoryType.ARTIFICIAL_INTELLIGENCE},
    {"id": "iot", "name": "Internet of Things", "count": 22, "color": "bg-orange-100", "type": ForumCategoryType.IOT},
    {"id": "general", "name": "General Discussion", "count": 10, "color": "bg-gray-100", "type": ForumCategoryType.GENERAL},
]

# Forum posts from frontend with detailed data
FORUM_POSTS_DATA = [
    {
        "title": "How to improve production line efficiency using sensors?",
        "author": "Sarah Ahmed",
        "author_title": "Production Engineer - Jeddah", 
        "category": "automation",
        "replies": 12,
        "views": 234,
        "likes": 8,
        "time_ago": "2 hours ago",
        "is_pinned": True,
        "has_best_answer": False,
        "is_verified": True,
        "excerpt": "We're facing challenges in monitoring operations on the production line and want to implement smart solutions...",
        "content": """We're currently operating a medium-scale electronics manufacturing facility and facing several challenges in real-time monitoring of our production lines.

**Current Challenges:**
- Manual quality checks causing delays
- Difficulty tracking production metrics in real-time
- Limited visibility into equipment performance
- High rate of undetected defects reaching final inspection

**What We're Looking For:**
- Sensor recommendations for real-time monitoring
- Integration with existing equipment
- Cost-effective solutions suitable for SMEs
- Success stories from similar implementations

Has anyone successfully implemented IoT sensors in their production lines? What were the key considerations and ROI achieved?""",
        "comments": [
            {
                "author": "Mohammed Al-Rashid",
                "author_title": "IoT Specialist - Riyadh",
                "content": "We implemented a similar solution last year using industrial-grade sensors from Siemens. The key is to start small with critical points in your production line. We started with temperature and vibration sensors on our most critical machines and expanded from there. ROI was visible within 6 months.",
                "time_ago": "1 hour ago",
                "likes": 5,
                "is_verified": True,
                "replies": [
                    {
                        "author": "Sarah Ahmed",
                        "author_title": "Production Engineer - Jeddah",
                        "content": "Thanks for sharing! What was the approximate cost per sensor? And did you face any integration challenges with legacy equipment?",
                        "time_ago": "45 minutes ago",
                        "likes": 2,
                        "is_verified": True
                    },
                    {
                        "author": "Mohammed Al-Rashid",
                        "author_title": "IoT Specialist - Riyadh",
                        "content": "Sensors ranged from SAR 500-2000 depending on type. For legacy equipment, we used edge computing devices as intermediaries. Happy to share more details if you DM me.",
                        "time_ago": "30 minutes ago",
                        "likes": 3,
                        "is_verified": True
                    }
                ]
            },
            {
                "author": "Fatima Hassan",
                "author_title": "Quality Manager - Dammam",
                "content": "Consider starting with vision-based quality inspection systems. We use cameras with AI models to detect defects. Much more cost-effective than traditional sensors for quality control. Local company TechVision SA provides excellent solutions.",
                "time_ago": "50 minutes ago",
                "likes": 4,
                "is_verified": True,
                "replies": []
            },
            {
                "author": "Ahmed Al-Zahrani",
                "author_title": "Factory Owner - Mecca",
                "content": "Before investing in sensors, ensure your team is ready for the digital transformation. We made the mistake of implementing too quickly without proper training. Now we have a phased approach: 1) Team training, 2) Pilot project, 3) Full implementation.",
                "time_ago": "30 minutes ago",
                "likes": 8,
                "is_verified": True,
                "replies": []
            }
        ]
    },
    {
        "title": "My experience implementing predictive maintenance in a plastic factory",
        "author": "Mohammed Al-Shahri",
        "author_title": "Operations Manager - Riyadh",
        "category": "maintenance", 
        "replies": 18,
        "views": 456,
        "likes": 15,
        "time_ago": "4 hours ago",
        "is_pinned": False,
        "has_best_answer": True,
        "is_verified": True,
        "excerpt": "Sharing my experience implementing a predictive maintenance system and how it saved 30% of maintenance costs...",
        "content": """After 2 years of running predictive maintenance in our plastic manufacturing facility, I wanted to share our journey and lessons learned.

**Background:**
- 150-person plastic manufacturing facility in Riyadh
- Previously reactive maintenance approach
- High unplanned downtime costs

**Implementation:**
- Started with vibration monitoring on critical extruders
- Gradually added temperature and pressure sensors
- Integrated with our existing ERP system
- Team training was crucial

**Results after 18 months:**
- 30% reduction in maintenance costs
- 45% decrease in unplanned downtime
- Equipment lifespan extended by 20%
- ROI achieved in 14 months

**Key Success Factors:**
1. Start small and scale gradually
2. Invest heavily in team training
3. Choose sensors that integrate well
4. Don't neglect data analysis capabilities

Happy to answer any questions about our implementation!""",
        "comments": []
    },
    {
        "title": "Best smart inventory management systems for small factories?",
        "author": "Fatima Al-Otaibi",
        "author_title": "Factory Owner - Dammam",
        "category": "quality",
        "replies": 9,
        "views": 189,
        "likes": 6,
        "time_ago": "Yesterday",
        "is_pinned": False,
        "has_best_answer": False,
        "is_verified": True,
        "excerpt": "Looking for a suitable inventory management system for a small factory that produces electrical equipment...",
        "content": """We're a small electrical equipment factory (40 employees) in Dammam looking to upgrade our inventory management system.

**Current Situation:**
- Manual inventory tracking with Excel sheets
- Frequent stockouts of critical components
- Overstock of slow-moving items
- Difficulty tracking raw material usage

**Requirements:**
- Easy to use for non-technical staff
- Integration with existing accounting system
- Real-time inventory tracking
- Mobile app for warehouse staff
- Budget: Under SAR 100K for implementation

**Questions:**
1. Which systems have you successfully implemented in similar-sized facilities?
2. What were the hidden costs we should be aware of?
3. How long did implementation typically take?

Any recommendations would be greatly appreciated!""",
        "comments": []
    },
    {
        "title": "Challenges of implementing AI in quality inspection",
        "author": "Khalid Al-Ghamdi",
        "author_title": "Quality Engineer - Mecca",
        "category": "ai",
        "replies": 22,
        "views": 678,
        "likes": 19,
        "time_ago": "2 days ago",
        "is_pinned": False,
        "has_best_answer": True,
        "is_verified": True,
        "excerpt": "We're facing difficulties in training AI models to inspect product defects...",
        "content": """We've been working on implementing AI-powered quality inspection for our pharmaceutical packaging line, but are facing several challenges.

**Our Setup:**
- High-resolution cameras at critical inspection points
- Various lighting conditions throughout the day
- Multiple product types and packaging formats
- Need to detect subtle defects (scratches, dents, misalignments)

**Challenges Faced:**
1. **Training Data:** Collecting enough defective samples for training
2. **False Positives:** System flagging good products as defective
3. **Lighting Variations:** Performance degrades with lighting changes
4. **Processing Speed:** Need real-time inspection at line speed

**Current Status:**
- 75% accuracy on test data
- Too many false positives for production use
- Considering switching vendors

**Questions for the Community:**
1. What accuracy rates are others achieving?
2. How do you handle the training data challenge?
3. Any recommendations for reliable AI vision vendors in Saudi Arabia?
4. What's a reasonable timeline for this type of implementation?

Looking forward to learning from others' experiences!""",
        "comments": []
    }
]

def parse_time_ago_to_datetime(time_ago: str) -> datetime:
    """Convert time ago string to datetime."""
    now = datetime.utcnow()
    
    if "hour" in time_ago:
        hours = int(time_ago.split()[0])
        return now - timedelta(hours=hours)
    elif "minute" in time_ago:
        minutes = int(time_ago.split()[0])
        return now - timedelta(minutes=minutes)
    elif "day" in time_ago or "Yesterday" in time_ago:
        if "Yesterday" in time_ago:
            days = 1
        else:
            days = int(time_ago.split()[0])
        return now - timedelta(days=days)
    else:
        return now - timedelta(hours=2)  # Default

def get_category_uuid(category_name: str, categories: List[ForumCategory]) -> str:
    """Get category UUID by name."""
    for cat in categories:
        if cat.category_type.value == category_name:
            return str(cat.id)
    return str(categories[0].id)  # Fallback to first category

async def seed_categories(session) -> List[ForumCategory]:
    """Create forum categories."""
    categories = []
    
    for i, cat_data in enumerate(CATEGORIES_DATA):
        category = ForumCategory(
            id=uuid.uuid4(),
            name=cat_data["name"],
            description=f"Discussion about {cat_data['name'].lower()} in manufacturing",
            category_type=cat_data["type"],
            color_class=cat_data["color"],
            is_active=True,
            sort_order=i,
            topics_count=cat_data["count"],
            posts_count=cat_data["count"] * 3,  # Rough estimate
            created_at=datetime.utcnow() - timedelta(days=90),
            updated_at=datetime.utcnow() - timedelta(days=1)
        )
        categories.append(category)
    
    session.add_all(categories)
    await session.commit()
    
    return categories

async def seed_topics_and_posts(session, categories: List[ForumCategory]):
    """Create forum topics and posts with replies."""
    
    # Skip actual topic/post creation until users and organizations exist (Tasks 3 & 4)
    print("⏭️ Skipping topic and post creation due to missing users/organizations...")
    print("📝 Note: Will create topics and posts after completing Tasks 3 & 4")
    return

async def seed_engagement_data(session):
    """Create likes and views for topics and posts."""
    
    # Skip engagement data creation since we skipped topics/posts
    print("⏭️ Skipping engagement data creation (no topics/posts to engage with)")
    return

async def clear_existing_data(session):
    """Clear existing forum data."""
    
    # Delete in proper order to handle foreign key constraints
    await session.execute(delete(ForumTopicView))
    await session.execute(delete(ForumPostLike))
    await session.execute(delete(ForumTopicLike))
    await session.execute(delete(ForumPost))
    await session.execute(delete(ForumTopic))
    await session.execute(delete(ForumCategory))
    
    await session.commit()
    print("🗑️  Cleared existing forum data")

async def verify_seed_data(session):
    """Verify the seeded forum data."""
    
    # Count categories
    categories_result = await session.execute(select(func.count(ForumCategory.id)))
    categories_count = categories_result.scalar()
    
    # Count topics
    topics_result = await session.execute(select(func.count(ForumTopic.id)))
    topics_count = topics_result.scalar()
    
    # Count posts
    posts_result = await session.execute(select(func.count(ForumPost.id)))
    posts_count = posts_result.scalar()
    
    # Count likes
    topic_likes_result = await session.execute(select(func.count(ForumTopicLike.id)))
    topic_likes_count = topic_likes_result.scalar()
    
    post_likes_result = await session.execute(select(func.count(ForumPostLike.id)))
    post_likes_count = post_likes_result.scalar()
    
    # Count views
    views_result = await session.execute(select(func.count(ForumTopicView.id)))
    views_count = views_result.scalar()
    
    print(f"\n📈 Forum Seeding Verification:")
    print(f"  Categories: {categories_count}")
    print(f"  Topics: {topics_count}")
    print(f"  Posts: {posts_count}")
    print(f"  Topic Likes: {topic_likes_count}")
    print(f"  Post Likes: {post_likes_count}")
    print(f"  Topic Views: {views_count}")
    
    # Show sample topic
    sample_topic_result = await session.execute(
        select(ForumTopic).limit(1)
    )
    sample_topic = sample_topic_result.scalar_one_or_none()
    
    if sample_topic:
        print(f"\n📋 Sample Topic:")
        print(f"  Title: {sample_topic.title}")
        print(f"  Views: {sample_topic.views_count}")
        print(f"  Posts: {sample_topic.posts_count}")
        print(f"  Likes: {sample_topic.likes_count}")
        print(f"  Pinned: {sample_topic.is_pinned}")

async def seed_forum():
    """Main seeding function."""
    print("🌱 Starting Forum PostgreSQL Seeding...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Clear existing data
            await clear_existing_data(session)
            
            # Create categories
            print("📂 Creating forum categories...")
            categories = await seed_categories(session)
            print(f"✅ Created {len(categories)} forum categories")
            
            # Create topics and posts
            print("💬 Creating forum topics and posts...")
            await seed_topics_and_posts(session, categories)
            
            # Create engagement data
            print("❤️ Creating engagement data...")
            await seed_engagement_data(session)
            
            print("✅ Forum seeding completed successfully!")
            
            # Verify data
            print("\n🔍 Verifying seeded data...")
            await verify_seed_data(session)
            
            return True
            
        except Exception as e:
            print(f"❌ Error seeding forum: {e}")
            await session.rollback()
            return False
            
        finally:
            await session.close()

if __name__ == "__main__":
    success = asyncio.run(seed_forum())
    
    if success:
        print("\n✅ Forum seeding completed successfully!")
    else:
        print("\n❌ Forum seeding failed!")
        exit(1)