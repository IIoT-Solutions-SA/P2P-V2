"""
Quick script to add forum replies to existing posts
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from app.models.mongo_models import ForumPost, ForumReply, User as MongoUser
from app.services.database_service import ForumService
from bson import ObjectId
import random

async def add_forum_replies():
    """Add realistic forum replies to existing posts"""
    try:
        # Initialize database connections
        await db_manager.init_mongodb()
        print("🚀 Connected to MongoDB")
        
        # Get all existing posts
        posts = await ForumPost.find_all().to_list()
        print(f"📝 Found {len(posts)} forum posts")
        
        # Get all users to use as reply authors
        users = await MongoUser.find_all().to_list()
        print(f"👥 Found {len(users)} users")
        
        if len(posts) == 0 or len(users) == 0:
            print("❌ No posts or users found. Run the main seed script first.")
            return
        
        # Sample replies for different topics
        sample_replies = {
            "automation": [
                "We implemented a similar solution using Siemens sensors. The ROI was visible within 6 months.",
                "Consider starting with temperature and vibration sensors on critical machines first.",
                "Edge computing devices work great as intermediaries for legacy equipment integration.",
                "What's your budget per sensor? This greatly affects the technology choices.",
                "Make sure your team is trained before implementing. We learned this the hard way!"
            ],
            "quality": [
                "Vision-based inspection systems with AI are very cost-effective for quality control.",
                "We use cameras with machine learning models to detect defects automatically.",
                "Local company TechVision SA provides excellent quality inspection solutions.",
                "Statistical process control combined with IoT gives great results.",
                "Consider implementing Six Sigma methodology alongside your tech solutions."
            ],
            "maintenance": [
                "Predictive maintenance saved us 30% on maintenance costs in the first year.",
                "Start with vibration analysis on rotating equipment - highest ROI.",
                "Oil analysis combined with temperature monitoring works wonders.",
                "Don't forget to train your maintenance team on the new systems.",
                "We use ThingWorx platform for our predictive maintenance dashboard."
            ],
            "ai": [
                "Training data quality is crucial for AI model success. Garbage in, garbage out.",
                "Consider using transfer learning to speed up your model development.",
                "Edge AI devices reduce latency and improve real-time decision making.",
                "OpenCV and TensorFlow work great for industrial vision applications.",
                "Make sure you have proper data labeling before training your models."
            ],
            "iot": [
                "LoRaWAN is excellent for long-range, low-power sensor networks in factories.",
                "Consider security from day one - industrial IoT attacks are increasing.",
                "MQTT broker setup is crucial for reliable IoT data transmission.",
                "Azure IoT Hub scales well for industrial applications.",
                "Don't forget about data storage costs - IoT generates massive amounts of data."
            ]
        }
        
        # Create replies for each post
        total_replies_created = 0
        for post in posts:
            try:
                # Determine reply category based on post category
                category_key = post.category.lower().replace(" ", "_")
                if "automation" in category_key:
                    replies_pool = sample_replies["automation"]
                elif "quality" in category_key:
                    replies_pool = sample_replies["quality"] 
                elif "maintenance" in category_key:
                    replies_pool = sample_replies["maintenance"]
                elif "artificial" in category_key or "ai" in category_key:
                    replies_pool = sample_replies["ai"]
                elif "iot" in category_key or "internet" in category_key:
                    replies_pool = sample_replies["iot"]
                else:
                    replies_pool = sample_replies["automation"]  # Default
                
                # Create 2-4 replies per post
                num_replies = random.randint(2, 4)
                for i in range(num_replies):
                    # Pick a random user (but not the post author if possible)
                    available_users = [u for u in users if str(u.id) != post.author_id]
                    if not available_users:
                        available_users = users
                    
                    reply_author = random.choice(available_users)
                    reply_content = random.choice(replies_pool)
                    
                    # Create the reply
                    reply = await ForumService.create_reply(
                        post_id=str(post.id),
                        author_id=str(reply_author.id),
                        content=reply_content,
                        is_best_answer=(i == 0 and random.random() < 0.3)  # 30% chance first reply is best
                    )
                    
                    # Add some random upvotes
                    reply.upvotes = random.randint(0, 8)
                    await reply.save()
                    
                    total_replies_created += 1
                    print(f"✅ Created reply by {reply_author.name} on '{post.title[:50]}...'")
                
                # Update post reply count and best answer status
                post_replies = await ForumReply.find(ForumReply.post_id == str(post.id)).to_list()
                post.reply_count = len(post_replies)
                post.has_best_answer = any(r.is_best_answer for r in post_replies)
                await post.save()
                
            except Exception as e:
                print(f"❌ Error creating replies for post '{post.title}': {e}")
        
        print(f"🎉 Created {total_replies_created} forum replies successfully!")
        
        # Close connections
        await db_manager.close_connections()
        print("✅ Database connections closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'db_manager' in locals():
            await db_manager.close_connections()

if __name__ == "__main__":
    asyncio.run(add_forum_replies())