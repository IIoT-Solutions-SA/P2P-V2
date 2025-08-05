import asyncio
import sys
import os
import random

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from app.services.database_service import ForumService
from app.models.mongo_models import User as MongoUser, ForumPost, ForumReply
from app.core.logging import setup_logging

async def seed_forums():
    """Wipes and seeds only the forum data, assuming users already exist."""
    logger = setup_logging()
    
    try:
        await db_manager.init_mongodb()

        # --- 1. FETCH EXISTING USERS ---
        logger.info("👥 Fetching existing users from the database...")
        existing_users = await MongoUser.find_all().to_list()
        if not existing_users:
            logger.error("❌ No users found in the database. Please run the `seed_db_users.py` script first.")
            return
        logger.info(f"👍 Found {len(existing_users)} users.")

        # --- 2. CLEANUP EXISTING FORUM DATA ---
        logger.info("🧹 Wiping all existing forum posts and replies...")
        await ForumPost.delete_all()
        await ForumReply.delete_all()
        logger.info("✅ Forum cleanup complete.")

        # --- 3. DEFINE FORUM CONTENT AND AUTHORS ---
        
        # Helper to map user names from data to actual user objects
        forum_authors = {user.name: user for user in existing_users}

        # The detailed forum post data
        forum_posts_data = [
            {
                "title": "How to improve production line efficiency using sensors?",
                "author": "Sarah Ahmed",
                "category": "Automation",
                "content": """We're currently operating a medium-scale electronics manufacturing facility and facing several challenges in real-time monitoring of our production lines.""",
                "tags": ["automation", "sensors", "iot", "quality-control", "sme"],
                "comments": [
                    {
                        "author": "Ahmed Al-Faisal",
                        "content": "We implemented a similar solution last year using industrial-grade sensors from Siemens. ROI was visible within 6 months.",
                        "replies": [
                            {
                                "author": "Sarah Ahmed",
                                "content": "Thanks for sharing! What was the approximate cost per sensor? And did you face any integration challenges with legacy equipment?",
                            }
                        ]
                    },
                    {
                        "author": "Fatima Ali",
                        "content": "Consider starting with vision-based quality inspection systems. We use cameras with AI models to detect defects.",
                    }
                ]
            },
            {
                "title": "My experience implementing predictive maintenance in a plastic factory",
                "author": "Mohammed Al-Shahri",
                "category": "Maintenance",
                "content": """Sharing my experience implementing a predictive maintenance system and how it saved 30% of maintenance costs.""",
                "tags": ["predictive-maintenance", "plastic-manufacturing", "cost-reduction", "ml"],
                "comments": []
            },
            {
                "title": "Best smart inventory management systems for small factories?",
                "author": "Fatima Al-Otaibi",
                "category": "Quality Management",
                "content": """Looking for a suitable inventory management system for a small factory that produces electrical equipment.""",
                "tags": ["inventory-management", "small-factory", "electrical-equipment", "erp"],
                "comments": []
            },
            {
                "title": "Challenges of implementing AI in quality inspection",
                "author": "Khalid Abdul",
                "category": "Artificial Intelligence",
                "content": """We're facing difficulties in training AI models to inspect product defects in our manufacturing process.""",
                "tags": ["artificial-intelligence", "quality-inspection", "computer-vision", "tensorflow"],
                "comments": []
            }
        ]

        sample_replies = {
            "Maintenance": ["Predictive maintenance saved us 30% on maintenance costs in the first year.", "Start with vibration analysis on rotating equipment - highest ROI."],
            "Quality Management": ["Vision-based inspection systems with AI are very cost-effective.", "Consider implementing Six Sigma methodology alongside your tech solutions."],
            "Artificial Intelligence": ["Training data quality is crucial for AI model success. Garbage in, garbage out.", "Edge AI devices reduce latency and improve real-time decision making."],
            "Automation": ["We used Siemens sensors and saw ROI in 6 months. Start with critical machines."]
        }
        
        # --- 4. SEED FORUM POSTS AND REPLIES ---
        logger.info("🌱 Seeding forum posts and replies...")
        created_posts_count = 0
        for post_data in forum_posts_data:
            author_user = forum_authors.get(post_data["author"], random.choice(existing_users))

            post = await ForumService.create_post(
                author_id=str(author_user.id),
                title=post_data["title"],
                content=post_data["content"],
                category=post_data["category"],
                tags=post_data.get("tags", [])
            )

            # Create specific comments and nested replies if they exist
            comments_data = post_data.get("comments", [])
            for comment_data in comments_data:
                comment_author_user = forum_authors.get(comment_data["author"], random.choice(existing_users))
                comment = await ForumService.create_reply(
                    post_id=str(post.id),
                    author_id=str(comment_author_user.id),
                    content=comment_data["content"]
                )

                for reply_data in comment_data.get("replies", []):
                    reply_author_user = forum_authors.get(reply_data["author"], random.choice(existing_users))
                    
                    # Create the nested reply directly to set the parent_id
                    nested_reply = ForumReply(
                        post_id=str(post.id),
                        parent_id=str(comment.id),
                        author_id=str(reply_author_user.id),
                        content=reply_data["content"]
                    )
                    await nested_reply.save()
            
            # If no specific comments, create random ones
            if not comments_data:
                reply_pool = sample_replies.get(post_data["category"], ["This is a very interesting topic. Following for more updates."])
                num_replies = random.randint(2, 4)
                for _ in range(num_replies):
                    # Ensure the author is not replying to their own post
                    possible_authors = [u for u in existing_users if u.id != author_user.id]
                    reply_author = random.choice(possible_authors if possible_authors else existing_users)

                    await ForumService.create_reply(
                        post_id=str(post.id),
                        author_id=str(reply_author.id),
                        content=random.choice(reply_pool)
                    )

            created_posts_count += 1
        
        logger.info(f"✅ Successfully seeded {created_posts_count} forum threads with replies.")

    except Exception as e:
        logger.error(f"❌ Forum seeding script failed: {e}")
        raise
    finally:
        await db_manager.close_connections()
        logger.info("Database connections closed.")

if __name__ == "__main__":
    print("🌱 Starting forum seeding script...")
    print("   (This assumes users have already been seeded)")
    asyncio.run(seed_forums())
    print("🎉 Forum seeding completed!")