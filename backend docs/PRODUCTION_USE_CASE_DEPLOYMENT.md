# Production Use Case Deployment Plan

## Current State
- **Total Use Cases**: ~40
  - 15 AI-generated use cases (from initial seeding)
  - 20 KACST use cases (Aadil, Amro, Hamza, Firas, Hamad, Abdulrahman - from individual JSONs)
  - 5 user-submitted use cases (keep these!)

## Deployment Steps

### Step 1: Backup Current Data
```bash
# Inside Docker container
docker exec -it p2p-backend-app-1 bash
python scripts/backup_usecases.py  # Create this if needed
```

### Step 2: Remove Old KACST Use Cases
```bash
# This removes the 20 KACST use cases that were individually seeded
python scripts/remove_usecases.py
```

### Step 3: Re-seed KACST Use Cases
**IMPORTANT**: Seed BEFORE migration so the new seeds get proper data from JSON

```bash
cd scripts/usecases

# Run each seed script individually
python seed_aadil.py
python seed_abdulrahman.py
python seed_amro.py
python seed_firas.py
python seed_hamad.py
python seed_hamza.py
```

### Step 4: Run Complete Migration
```bash
# Use the COMPLETE migration script to fix ALL use cases including newly seeded ones
python scripts/migrate_usecase_fields_complete.py
```

This will fix:
- Missing subtitle fields (even on newly seeded use cases)
- Missing executive_summary fields
- Any other structural issues
- Validate all required fields are present

### Step 5: Verify Deployment
```bash
# Check total count
python -c "
import asyncio
from app.models.mongo_models import UseCase
from app.core.database import db_manager

async def count():
    await db_manager.init_mongodb()
    count = await UseCase.find_all().count()
    print(f'Total use cases: {count}')
    await db_manager.close_connections()

asyncio.run(count())
"
```

## Important Notes

1. **User-submitted use cases are preserved** - The scripts only remove seeded content, not user-created content

2. **JSON files are ready** - All JSON files have been updated with:
   - `challenges_and_solutions` field with real challenges
   - Proper structure for all fields
   - Executive summaries

3. **CORRECT ORDER** (Important!):
   - Remove old KACST seeds FIRST
   - Re-seed KACST use cases SECOND
   - Run migration LAST (to fix subtitle and other fields on ALL use cases)

4. **The seed scripts have been fixed** to include `challenges_and_solutions` in the database (fixed in commit from earlier today)

## Files Used
- `/scripts/remove_usecases.py` - Removes KACST seeded use cases
- `/scripts/migrate_usecase_fields_complete.py` - Complete migration for all fields
- `/scripts/usecases/seed_*.py` - Individual seed scripts (6 files)
- `/scripts/usecases/*_usecases.json` - JSON data files (6 files)

## Expected Result
After deployment:
- ~40 use cases total:
  - 15 AI-generated (untouched)
  - 20 KACST re-seeded with proper data
  - 5 user-created (preserved)
- All use cases have proper subtitle fields
- All use cases have challenges and solutions
- No duplicate KACST use cases