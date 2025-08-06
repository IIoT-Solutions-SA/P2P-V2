#!/usr/bin/env python3
"""Debug script to identify the FileMetadata column conflict."""

import sys
import traceback

try:
    print("Testing individual model imports...")
    
    print("1. Importing BaseModel...")
    from app.models.base import BaseModel
    print("✓ BaseModel imported successfully")
    
    print("2. Importing enums...")
    from app.models.enums import UserRole, UserStatus
    print("✓ Enums imported successfully")
    
    print("3. Importing Organization model...")
    from app.models.organization import Organization
    print("✓ Organization imported successfully")
    
    print("4. Importing User model...")
    from app.models.user import User
    print("✓ User imported successfully")
    
    print("5. Importing FileMetadata model...")
    from app.models.file import FileMetadata
    print("✓ FileMetadata imported successfully")
    
    print("6. Importing UserInvitation model...")
    from app.models.invitation import UserInvitation
    print("✓ UserInvitation imported successfully")
    
    print("7. Testing model creation...")
    metadata = BaseModel.metadata
    print(f"Number of tables in metadata: {len(metadata.tables)}")
    
    print("Tables found:")
    for table_name in metadata.tables.keys():
        table = metadata.tables[table_name]
        print(f"  - {table_name}: columns = {list(table.columns.keys())}")
        
    print("✓ All models imported successfully!")
    
except Exception as e:
    print(f"❌ Error occurred: {e}")
    print(f"Error type: {type(e)}")
    traceback.print_exc()