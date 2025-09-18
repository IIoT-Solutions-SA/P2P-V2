# User Deletion Process - Complete Guide

## Overview
This document outlines the process for completely deleting a user from the P2P Manufacturing Platform. User data is stored across three different databases, and all must be cleaned for complete deletion.

**Date Created**: September 11, 2025  
**Purpose**: Manual user deletion and future implementation reference

## Database Architecture

The platform uses three databases:
1. **PostgreSQL (p2p_sandbox)** - Main application database
2. **PostgreSQL (supertokens)** - SuperTokens authentication database  
3. **MongoDB (p2p_sandbox)** - Document store for extended user profiles

## Database Credentials

```yaml
PostgreSQL:
  user: p2p_user
  password: iiot123
  main_database: p2p_sandbox
  auth_database: supertokens
  port: 5432

MongoDB:
  user: p2p_user
  password: iiot123
  database: p2p_sandbox
  authSource: admin
  port: 27017
```

## Manual Deletion Process

### Step 1: Identify User Records

#### Find user in PostgreSQL main database:
```bash
docker exec p2p-postgres psql -U p2p_user -d p2p_sandbox -c \
  "SELECT id, email, name, created_at FROM users WHERE email = 'user@example.com';"
```

#### Find user in SuperTokens database:
```bash
docker exec p2p-postgres psql -U p2p_user -d supertokens -c \
  "SELECT user_id, email FROM emailpassword_users WHERE email = 'user@example.com';"
```

#### Find user in MongoDB:
```bash
docker exec p2p-mongodb mongosh -u p2p_user -p iiot123 \
  --authenticationDatabase admin p2p_sandbox \
  --eval "db.users.find({email: 'user@example.com'}, {email: 1, name: 1, created_at: 1}).toArray()"
```

### Step 2: Delete from SuperTokens Database

The SuperTokens database stores authentication data across multiple tables. User IDs from SuperTokens are different from the main application user IDs.

```bash
# Get the SuperTokens user_id first
docker exec p2p-postgres psql -U p2p_user -d supertokens -c \
  "SELECT user_id FROM emailpassword_users WHERE email = 'user@example.com';"

# Delete from all SuperTokens tables (replace USER_ID with actual ID)
docker exec p2p-postgres psql -U p2p_user -d supertokens -c "
DELETE FROM all_auth_recipe_users WHERE user_id = 'USER_ID';
DELETE FROM emailpassword_users WHERE user_id = 'USER_ID';
DELETE FROM emailpassword_user_to_tenant WHERE user_id = 'USER_ID';
DELETE FROM emailverification_verified_emails WHERE user_id = 'USER_ID';
DELETE FROM session_info WHERE user_id = 'USER_ID';
DELETE FROM user_metadata WHERE user_id = 'USER_ID';
DELETE FROM user_roles WHERE user_id = 'USER_ID';
DELETE FROM user_last_active WHERE user_id = 'USER_ID';
DELETE FROM app_id_to_user_id WHERE user_id = 'USER_ID';
"
```

### Step 3: Delete from Main PostgreSQL Database

```bash
# Delete user sessions first (foreign key constraint)
docker exec p2p-postgres psql -U p2p_user -d p2p_sandbox -c \
  "DELETE FROM user_sessions WHERE user_id = (SELECT id FROM users WHERE email = 'user@example.com');"

# Delete the user record
docker exec p2p-postgres psql -U p2p_user -d p2p_sandbox -c \
  "DELETE FROM users WHERE email = 'user@example.com';"
```

### Step 4: Delete from MongoDB

```bash
# Delete user document
docker exec p2p-mongodb mongosh -u p2p_user -p iiot123 \
  --authenticationDatabase admin p2p_sandbox \
  --eval "db.users.deleteOne({email: 'user@example.com'})"

# Also delete any invitations sent by this user
docker exec p2p-mongodb mongosh -u p2p_user -p iiot123 \
  --authenticationDatabase admin p2p_sandbox \
  --eval "db.invitations.deleteMany({invited_by_email: 'user@example.com'})"
```

### Step 5: Verify Deletion

Run the identification queries from Step 1 again to confirm all records are deleted:

```bash
# Check PostgreSQL main
docker exec p2p-postgres psql -U p2p_user -d p2p_sandbox -c \
  "SELECT count(*) FROM users WHERE email = 'user@example.com';"  # Should return 0

# Check SuperTokens
docker exec p2p-postgres psql -U p2p_user -d supertokens -c \
  "SELECT count(*) FROM emailpassword_users WHERE email = 'user@example.com';"  # Should return 0

# Check MongoDB
docker exec p2p-mongodb mongosh -u p2p_user -p iiot123 \
  --authenticationDatabase admin p2p_sandbox \
  --eval "db.users.find({email: 'user@example.com'}).count()"  # Should return 0
```

## Batch Deletion Example

To delete multiple users at once (e.g., all test users with a specific pattern):

```bash
# Delete multiple users from SuperTokens
docker exec p2p-postgres psql -U p2p_user -d supertokens -c "
DELETE FROM all_auth_recipe_users WHERE user_id IN (
  SELECT user_id FROM emailpassword_users WHERE email LIKE '%@test.com'
);
DELETE FROM emailpassword_users WHERE email LIKE '%@test.com';
-- Continue for other tables...
"

# Delete from main PostgreSQL
docker exec p2p-postgres psql -U p2p_user -d p2p_sandbox -c \
  "DELETE FROM users WHERE email LIKE '%@test.com';"

# Delete from MongoDB
docker exec p2p-mongodb mongosh -u p2p_user -p iiot123 \
  --authenticationDatabase admin p2p_sandbox \
  --eval "db.users.deleteMany({email: /.*@test\.com$/})"
```

## SuperTokens Database Tables Reference

Key tables in the SuperTokens database that may contain user data:
- `all_auth_recipe_users` - Main user reference table
- `emailpassword_users` - Email/password authentication records
- `emailpassword_user_to_tenant` - Tenant associations
- `emailverification_verified_emails` - Email verification status
- `session_info` - Active user sessions
- `user_metadata` - Additional user metadata
- `user_roles` - User role assignments
- `user_last_active` - User activity tracking
- `app_id_to_user_id` - App to user ID mappings

## Important Notes

1. **Order Matters**: Always delete from SuperTokens first, then main PostgreSQL, then MongoDB
2. **Foreign Keys**: Delete related records (sessions, invitations) before deleting the user
3. **User IDs**: SuperTokens uses different user IDs than the main application
4. **Cascading**: Some deletions may cascade automatically depending on foreign key constraints
5. **Invitations**: Remember to clean up any invitations sent by the deleted user

## Future Implementation

For implementing user deletion in the application:

### API Endpoint Structure
```python
@router.delete("/api/v1/users/{user_email}")
async def delete_user(user_email: str, current_user: dict = Depends(get_current_user)):
    """
    Complete user deletion from all databases
    Admin only endpoint
    """
    # 1. Get SuperTokens user_id
    # 2. Delete from SuperTokens tables
    # 3. Delete from PostgreSQL main database
    # 4. Delete from MongoDB
    # 5. Return confirmation
```

### Service Layer Pattern
```python
class UserDeletionService:
    async def delete_user_completely(self, email: str):
        # 1. Delete from SuperTokens
        await self.delete_from_supertokens(email)
        
        # 2. Delete from PostgreSQL
        await self.delete_from_postgres(email)
        
        # 3. Delete from MongoDB
        await self.delete_from_mongodb(email)
        
        # 4. Clean up related data
        await self.cleanup_user_data(email)
```

## Testing Deletion

After implementing user deletion, test with:
1. Create a test user
2. Have them create some data (posts, invitations, etc.)
3. Delete the user
4. Verify all data is removed from all three databases
5. Ensure no orphaned records remain

---

*Last Updated: September 11, 2025*  
*Used for: Manual deletion of duplicate Hamza Feroze accounts*