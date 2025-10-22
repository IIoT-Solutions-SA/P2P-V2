#!/bin/bash
# Script to mark all existing users as email verified
# This is needed for users created before email verification was implemented

echo "======================================================================"
echo "Checking for unverified existing users..."
echo "======================================================================"

# Wait for databases to be ready
sleep 5

# Mark all existing users as email verified
PGPASSWORD=iiot123 psql -h postgres -U p2p_user -d supertokens -c "
INSERT INTO emailverification_verified_emails (app_id, user_id, email)
SELECT 'public', user_id, email
FROM emailpassword_users
WHERE user_id NOT IN (SELECT user_id FROM emailverification_verified_emails)
ON CONFLICT DO NOTHING;
" > /dev/null 2>&1

VERIFIED_COUNT=$(PGPASSWORD=iiot123 psql -h postgres -U p2p_user -d supertokens -t -c "SELECT COUNT(*) FROM emailverification_verified_emails;")

echo "✅ Total verified users: $VERIFIED_COUNT"
echo "======================================================================"
