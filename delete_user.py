#!/usr/bin/env python3
"""
Script to delete a user from all databases (PostgreSQL, MongoDB, and SuperTokens)
Usage: python delete_user.py <user_email>
"""

import sys
import asyncio
import psycopg2
from pymongo import MongoClient
import requests
from datetime import datetime

# Database connection settings (matching docker-compose)
POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'p2p_manufacturing',
    'user': 'p2puser',
    'password': 'p2ppassword'
}

MONGO_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'database': 'p2p_manufacturing'
}

SUPERTOKENS_API = 'http://localhost:3567'

def delete_from_postgres(email):
    """Delete user from PostgreSQL"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cur = conn.cursor()
        
        # First, get the user_id
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cur.fetchone()
        
        if result:
            user_id = result[0]
            print(f"Found PostgreSQL user with ID: {user_id}")
            
            # Delete from users table (this should cascade to related tables)
            cur.execute("DELETE FROM users WHERE email = %s", (email,))
            conn.commit()
            print(f"✅ Deleted user from PostgreSQL: {email}")
        else:
            print(f"⚠️ User not found in PostgreSQL: {email}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ PostgreSQL error: {e}")

def delete_from_mongodb(email):
    """Delete user from MongoDB"""
    try:
        client = MongoClient(f"mongodb://{MONGO_CONFIG['host']}:{MONGO_CONFIG['port']}/")
        db = client[MONGO_CONFIG['database']]
        
        # Delete from users collection
        result = db.users.delete_one({"email": email})
        if result.deleted_count > 0:
            print(f"✅ Deleted user from MongoDB: {email}")
        else:
            print(f"⚠️ User not found in MongoDB: {email}")
        
        # Also check and delete any invitations sent by this user
        invites_result = db.invitations.delete_many({"invited_by_email": email})
        if invites_result.deleted_count > 0:
            print(f"  - Deleted {invites_result.deleted_count} invitations sent by this user")
        
        client.close()
    except Exception as e:
        print(f"❌ MongoDB error: {e}")

def delete_from_supertokens(email):
    """Delete user from SuperTokens"""
    try:
        # First, get all users to find the one with matching email
        response = requests.get(
            f"{SUPERTOKENS_API}/recipe/dashboard/api/users",
            params={"limit": 1000}
        )
        
        if response.status_code == 200:
            users = response.json().get('users', [])
            user_id = None
            
            for user in users:
                # Check email in the user object
                user_email = None
                if 'email' in user:
                    user_email = user['email']
                elif 'emails' in user:
                    user_email = user['emails'][0] if user['emails'] else None
                
                if user_email == email:
                    user_id = user.get('id') or user.get('userId')
                    break
            
            if user_id:
                print(f"Found SuperTokens user with ID: {user_id}")
                
                # Delete the user
                delete_response = requests.delete(
                    f"{SUPERTOKENS_API}/recipe/dashboard/api/user",
                    params={"userId": user_id}
                )
                
                if delete_response.status_code == 200:
                    print(f"✅ Deleted user from SuperTokens: {email}")
                else:
                    print(f"⚠️ Failed to delete from SuperTokens: {delete_response.text}")
            else:
                print(f"⚠️ User not found in SuperTokens: {email}")
        else:
            print(f"❌ Failed to query SuperTokens: {response.text}")
            
    except Exception as e:
        print(f"❌ SuperTokens error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python delete_user.py <user_email>")
        print("Example: python delete_user.py john@example.com")
        sys.exit(1)
    
    email = sys.argv[1].strip().lower()
    
    print(f"\n🗑️ DELETING USER: {email}")
    print("=" * 50)
    
    # Confirm deletion
    confirm = input(f"\n⚠️ WARNING: This will permanently delete {email} from ALL databases.\nType 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        print("Deletion cancelled.")
        sys.exit(0)
    
    print("\nDeleting from all databases...")
    print("-" * 50)
    
    # Delete from each database
    delete_from_postgres(email)
    delete_from_mongodb(email)
    delete_from_supertokens(email)
    
    print("-" * 50)
    print("✅ Deletion process complete!\n")

if __name__ == "__main__":
    main()