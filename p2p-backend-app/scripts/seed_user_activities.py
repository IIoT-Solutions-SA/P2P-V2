"""
Seed User Activities and Stats
Creates realistic user activity data for dashboard testing
"""

import asyncio
import sys
import os
import random
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager
from app.services.user_activity_service import UserActivityService
from app.models.mongo_models import (
    User, ForumPost, ForumReply, UseCase, 
    UserActivity, UserStats, UserBookmark, DraftPost
)
from app.core.logging import setup_logging
import logging

async def seed_user_activities():
    """Seed realistic user activities and stats for existing users"""
    logger = setup_logging()
    
    try:
        # Initialize MongoDB connection
        await db_manager.init_mongodb()
        logger.info("Connected to MongoDB for user activity seeding")
        
        # Get all existing users
        users = await User.find_all().to_list()
        if not users:
            logger.error("No users found! Run seed_db.py first")
            return
            
        logger.info(f"Found {len(users)} users for activity seeding")
        
        # Get all existing forum posts and use cases for activities
        forum_posts = await ForumPost.find_all().to_list()
        forum_replies = await ForumReply.find_all().to_list()
        use_cases = await UseCase.find_all().to_list()
        
        logger.info(f"Found {len(forum_posts)} posts, {len(forum_replies)} replies, {len(use_cases)} use cases")
        
        # Clear existing activity data
        logger.info("🧹 Cleaning up existing user activity data...")
        await UserActivity.delete_all()
        await UserStats.delete_all()
        await UserBookmark.delete_all()
        await DraftPost.delete_all()
        logger.info("✅ Cleaned up existing user activity data")
        
        # Generate activities for each user
        for user in users:
            logger.info(f"Generating activities for {user.name}...")
            
            # Generate forum post activities (questions asked)
            user_posts = [post for post in forum_posts if post.author_id == str(user.id)]
            for post in user_posts:
                await UserActivityService.log_activity(
                    user_id=str(user.id),
                    activity_type="question",
                    target_id=str(post.id),
                    target_title=post.title,
                    target_category=post.category,
                    description=f"Asked: {post.title}"
                )
                
            # Generate forum reply activities (answers given)
            user_replies = [reply for reply in forum_replies if reply.author_id == str(user.id)]
            for reply in user_replies:
                # Find the post this reply belongs to
                parent_post = next((p for p in forum_posts if str(p.id) == reply.post_id), None)
                if parent_post:
                    await UserActivityService.log_activity(
                        user_id=str(user.id),
                        activity_type="answer",
                        target_id=str(reply.id),
                        target_title=parent_post.title,
                        target_category=parent_post.category,
                        description=f"Answered: {parent_post.title}"
                    )
            
            # Generate use case activities
            user_use_cases = [uc for uc in use_cases if uc.submitted_by == str(user.id)]
            for use_case in user_use_cases:
                await UserActivityService.log_activity(
                    user_id=str(user.id),
                    activity_type="usecase",
                    target_id=str(use_case.id),
                    target_title=use_case.title,
                    target_category=use_case.industry_tags[0] if use_case.industry_tags else "General",
                    description=f"Submitted use case: {use_case.title}"
                )
            
            # Generate some random bookmarks (users bookmark other people's content)
            other_users_posts = [post for post in forum_posts if post.author_id != str(user.id)]
            other_users_use_cases = [uc for uc in use_cases if uc.submitted_by != str(user.id)]
            
            # Bookmark 2-5 random items
            bookmark_count = random.randint(2, 5)
            bookmark_targets = random.sample(other_users_posts + other_users_use_cases, min(bookmark_count, len(other_users_posts + other_users_use_cases)))
            
            for target in bookmark_targets:
                if isinstance(target, ForumPost):
                    await UserActivityService.add_bookmark(
                        user_id=str(user.id),
                        target_type="forum_post",
                        target_id=str(target.id),
                        target_title=target.title,
                        target_category=target.category
                    )
                elif isinstance(target, UseCase):
                    await UserActivityService.add_bookmark(
                        user_id=str(user.id),
                        target_type="use_case",
                        target_id=str(target.id),
                        target_title=target.title,
                        target_category=target.industry_tags[0] if target.industry_tags else "General"
                    )
            
            # Generate some draft posts
            draft_count = random.randint(1, 3)
            for i in range(draft_count):
                draft_titles = [
                    "How to optimize manufacturing processes?",
                    "AI implementation challenges in SMEs",
                    "Quality control best practices",
                    "Digital transformation roadmap",
                    "IoT sensor selection guide",
                    "Predictive maintenance strategies"
                ]
                
                draft_contents = [
                    "I'm working on implementing new manufacturing processes and need advice on optimization strategies...",
                    "Our company is exploring AI solutions but facing implementation challenges. What are the key considerations?",
                    "Looking for best practices in quality control systems for manufacturing environments...",
                    "Planning our digital transformation journey. What steps should we prioritize?",
                    "Need guidance on selecting the right IoT sensors for our production line monitoring...",
                    "Evaluating predictive maintenance approaches. What has worked well for similar companies?"
                ]
                
                await UserActivityService.create_draft_post(
                    user_id=str(user.id),
                    title=random.choice(draft_titles),
                    content=random.choice(draft_contents),
                    post_type="forum_post",
                    category=random.choice(["Automation", "Quality Management", "Artificial Intelligence", "Maintenance"])
                )
            
            # Add some additional random activities with timestamps spread over the last 30 days
            additional_activities = random.randint(3, 8)
            for _ in range(additional_activities):
                activity_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
                
                # Create a UserActivity directly with custom timestamp
                activity_types = ["like", "bookmark", "comment"]
                target_item = random.choice(forum_posts + use_cases)
                
                activity = UserActivity(
                    user_id=str(user.id),
                    activity_type=random.choice(activity_types),
                    target_id=str(target_item.id),
                    target_title=target_item.title,
                    target_category=getattr(target_item, 'category', target_item.industry_tags[0] if hasattr(target_item, 'industry_tags') and target_item.industry_tags else "General"),
                    description=f"Interacted with: {target_item.title}",
                    created_at=activity_date
                )
                await activity.insert()
            
            logger.info(f"✅ Generated activities for {user.name}")
        
        # Recalculate stats for all users
        logger.info("📊 Calculating user statistics...")
        for user in users:
            stats = await UserActivityService.recalculate_user_stats(str(user.id))
            if stats:
                logger.info(f"📈 {user.name}: {stats.reputation_score} reputation, {stats.activity_level:.1f}% activity")
        
        logger.info("🎉 User activity seeding completed successfully!")
        
        # Display summary
        total_activities = await UserActivity.find_all().count()
        total_bookmarks = await UserBookmark.find_all().count()
        total_drafts = await DraftPost.find_all().count()
        total_stats = await UserStats.find_all().count()
        
        logger.info(f"📊 Summary:")
        logger.info(f"   - {total_activities} user activities created")
        logger.info(f"   - {total_bookmarks} bookmarks created")  
        logger.info(f"   - {total_drafts} draft posts created")
        logger.info(f"   - {total_stats} user stat profiles created")
        
    except Exception as e:
        logger.error(f"❌ User activity seeding failed: {e}")
        raise
    finally:
        # Clean up database connections
        await db_manager.close_connections()
        logger.info("Database connections closed")

if __name__ == "__main__":
    print("🚀 Starting user activity and stats seeding...")
    asyncio.run(seed_user_activities())
    print("🎉 User activity seeding completed!")