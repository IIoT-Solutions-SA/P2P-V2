"""Base CRUD operations for all models."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from app.models.base import BaseModelWithSoftDelete

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base class for CRUD operations."""
    
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        
        Args:
            model: A SQLModel class
        """
        self.model = model
    
    async def get(
        self, 
        db: AsyncSession, 
        id: UUID,
        include_deleted: bool = False
    ) -> Optional[ModelType]:
        """Get a single record by ID."""
        query = select(self.model).where(self.model.id == id)
        
        # Handle soft delete if the model supports it
        if hasattr(self.model, 'is_deleted') and not include_deleted:
            query = query.where(self.model.is_deleted == False)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and filtering."""
        query = select(self.model)
        
        # Handle soft delete
        if hasattr(self.model, 'is_deleted') and not include_deleted:
            query = query.where(self.model.is_deleted == False)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
        
        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            order_field = getattr(self.model, order_by)
            if order_desc:
                query = query.order_by(order_field.desc())
            else:
                query = query.order_by(order_field)
        else:
            # Default ordering by created_at desc
            if hasattr(self.model, 'created_at'):
                query = query.order_by(self.model.created_at.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count(
        self,
        db: AsyncSession,
        *,
        include_deleted: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count records matching the criteria."""
        query = select(func.count()).select_from(self.model)
        
        # Handle soft delete
        if hasattr(self.model, 'is_deleted') and not include_deleted:
            query = query.where(self.model.is_deleted == False)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
        
        result = await db.execute(query)
        return result.scalar()
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType
    ) -> ModelType:
        """Create a new record."""
        # Convert Pydantic model to dict
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(exclude_unset=True)
        
        # Create the database object
        db_obj = self.model(**create_data)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record."""
        # Convert Pydantic model to dict
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # Update the object
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # Update the updated_at timestamp if it exists
        if hasattr(db_obj, 'updated_at'):
            db_obj.updated_at = datetime.utcnow()
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(
        self,
        db: AsyncSession,
        *,
        id: UUID,
        soft_delete: bool = True
    ) -> Optional[ModelType]:
        """Delete a record (soft delete by default)."""
        db_obj = await self.get(db, id=id)
        if not db_obj:
            return None
        
        if soft_delete and hasattr(db_obj, 'soft_delete'):
            # Soft delete
            db_obj.soft_delete()
            db.add(db_obj)
        else:
            # Hard delete
            await db.delete(db_obj)
        
        await db.commit()
        return db_obj
    
    async def restore(
        self,
        db: AsyncSession,
        *,
        id: UUID
    ) -> Optional[ModelType]:
        """Restore a soft-deleted record."""
        db_obj = await self.get(db, id=id, include_deleted=True)
        
        if not db_obj:
            return None
        
        if hasattr(db_obj, 'restore'):
            db_obj.restore()
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
        
        return db_obj
    
    async def get_by_field(
        self,
        db: AsyncSession,
        *,
        field_name: str,
        field_value: Any,
        include_deleted: bool = False
    ) -> Optional[ModelType]:
        """Get a single record by a specific field."""
        if not hasattr(self.model, field_name):
            raise ValueError(f"Model {self.model.__name__} has no field {field_name}")
        
        query = select(self.model).where(
            getattr(self.model, field_name) == field_value
        )
        
        # Handle soft delete
        if hasattr(self.model, 'is_deleted') and not include_deleted:
            query = query.where(self.model.is_deleted == False)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_multi_by_field(
        self,
        db: AsyncSession,
        *,
        field_name: str,
        field_value: Any,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[ModelType]:
        """Get multiple records by a specific field."""
        if not hasattr(self.model, field_name):
            raise ValueError(f"Model {self.model.__name__} has no field {field_name}")
        
        query = select(self.model).where(
            getattr(self.model, field_name) == field_value
        )
        
        # Handle soft delete
        if hasattr(self.model, 'is_deleted') and not include_deleted:
            query = query.where(self.model.is_deleted == False)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def exists(
        self,
        db: AsyncSession,
        *,
        id: UUID,
        include_deleted: bool = False
    ) -> bool:
        """Check if a record exists."""
        query = select(func.count()).select_from(self.model).where(
            self.model.id == id
        )
        
        # Handle soft delete
        if hasattr(self.model, 'is_deleted') and not include_deleted:
            query = query.where(self.model.is_deleted == False)
        
        result = await db.execute(query)
        count = result.scalar()
        return count > 0