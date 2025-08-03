# 4. Core Data Models

## User
- id, name, email, role, industry_sector, location, expertise_tags, verified, language_preference, timestamps

## ForumPost
- id, author_id, title, content, category, attachments, best_answer_id, status, timestamps

## ForumReply
- id, post_id, author_id, content, attachments, upvotes, timestamps

## UseCase
- id, submitted_by, title, problem_statement, solution_description, vendor_info, cost_estimate, impact_metrics, industry_tags, region, location {lat, lng}, bookmarks, published, featured

## MessageThread
- id, user_ids, messages [{sender_id, content, timestamp}]

## TrainingPost
- id, creator_id, title, description, skill_topic, location, schedule, interested_users, matched_provider_id

---