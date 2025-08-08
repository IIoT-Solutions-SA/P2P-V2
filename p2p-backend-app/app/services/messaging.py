"""Messaging service for handling conversations and messages."""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from uuid import UUID
from sqlmodel import Session, select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload
from sqlalchemy import text

from app.models.message import (
    Message, MessageCreate, MessageUpdate, MessageResponse,
    Conversation, ConversationCreate, ConversationResponse,
    MessageAttachment, MessageRead, MessageReaction,
    MessageType, MessageStatus,
    ConversationListResponse, MessageListResponse,
    UnreadCountResponse, MessageSearchRequest
)
from app.models.user import User
from app.core.exceptions import NotFoundException, ForbiddenException
from app.core.logging import get_logger

logger = get_logger(__name__)
from app.services.notifications import NotificationService


class MessagingService:
    """Service for handling messaging operations."""
    
    @staticmethod
    async def get_or_create_conversation(
        db: Session,
        user_id: UUID,
        participant_id: UUID,
        organization_id: UUID
    ) -> Conversation:
        """Get existing conversation or create new one."""
        # Order participants consistently for unique constraint
        p1_id, p2_id = (user_id, participant_id) if str(user_id) < str(participant_id) else (participant_id, user_id)
        
        # Check for existing conversation
        statement = select(Conversation).where(
            and_(
                Conversation.participant1_id == p1_id,
                Conversation.participant2_id == p2_id,
                Conversation.organization_id == organization_id
            )
        )
        conversation = db.exec(statement).first()
        
        if not conversation:
            # Create new conversation
            conversation = Conversation(
                organization_id=organization_id,
                participant1_id=p1_id,
                participant2_id=p2_id
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            logger.info(f"Created new conversation {conversation.id} between {p1_id} and {p2_id}")
        
        return conversation
    
    @staticmethod
    async def send_message(
        db: Session,
        sender_id: UUID,
        message_data: MessageCreate,
        organization_id: UUID
    ) -> MessageResponse:
        """Send a new message."""
        # Get or create conversation
        conversation = await MessagingService.get_or_create_conversation(
            db, sender_id, message_data.recipient_id, organization_id
        )
        
        # Create message
        message = Message(
            conversation_id=conversation.id,
            sender_id=sender_id,
            recipient_id=message_data.recipient_id,
            organization_id=organization_id,
            content=message_data.content,
            content_type=message_data.content_type,
            parent_message_id=message_data.parent_message_id,
            metadata=message_data.metadata
        )
        db.add(message)
        
        # Update conversation's last message info
        conversation.last_message_id = message.id
        conversation.last_message_content = message.content[:100]  # First 100 chars
        conversation.last_message_at = message.created_at
        conversation.last_message_sender_id = sender_id
        
        # Update unread count for recipient
        if conversation.participant1_id == message_data.recipient_id:
            conversation.participant1_unread_count += 1
        else:
            conversation.participant2_unread_count += 1
        
        # Update thread count if this is a reply
        if message_data.parent_message_id:
            parent = db.get(Message, message_data.parent_message_id)
            if parent:
                parent.thread_count += 1
        
        db.commit()
        db.refresh(message)
        
        # Get sender info
        sender = db.get(User, sender_id)
        
        # Create notification for message recipient
        try:
            await NotificationService.create_message_notification(
                db, message, sender
            )
        except Exception as e:
            logger.warning(f"Failed to create message notification: {e}")
        
        return MessageResponse(
            **message.dict(),
            sender_name=f"{sender.first_name} {sender.last_name}" if sender else None,
            sender_title=sender.title if sender else None
        )
    
    @staticmethod
    async def get_conversations(
        db: Session,
        user_id: UUID,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 20,
        archived: bool = False
    ) -> ConversationListResponse:
        """Get user's conversations."""
        offset = (page - 1) * page_size
        
        # Build query
        statement = select(Conversation).where(
            and_(
                Conversation.organization_id == organization_id,
                or_(
                    Conversation.participant1_id == user_id,
                    Conversation.participant2_id == user_id
                ),
                Conversation.is_active == True
            )
        )
        
        # Filter by archive status
        if archived:
            statement = statement.where(
                or_(
                    and_(Conversation.participant1_id == user_id, Conversation.archived_by_participant1 == True),
                    and_(Conversation.participant2_id == user_id, Conversation.archived_by_participant2 == True)
                )
            )
        else:
            statement = statement.where(
                or_(
                    and_(Conversation.participant1_id == user_id, Conversation.archived_by_participant1 == False),
                    and_(Conversation.participant2_id == user_id, Conversation.archived_by_participant2 == False)
                )
            )
        
        # Order by last message
        statement = statement.order_by(desc(Conversation.last_message_at))
        
        # Get total count
        count_statement = select(func.count()).select_from(statement.subquery())
        total = db.exec(count_statement).one()
        
        # Get paginated results
        statement = statement.offset(offset).limit(page_size)
        conversations = db.exec(statement).all()
        
        # Build response
        conversation_responses = []
        for conv in conversations:
            # Get other participant
            other_participant_id = conv.participant2_id if conv.participant1_id == user_id else conv.participant1_id
            other_participant = db.get(User, other_participant_id)
            
            # Get unread count for current user
            unread_count = conv.participant1_unread_count if conv.participant1_id == user_id else conv.participant2_unread_count
            
            # Get last message if exists
            last_message = None
            if conv.last_message_id:
                msg = db.get(Message, conv.last_message_id)
                if msg:
                    sender = db.get(User, msg.sender_id)
                    last_message = MessageResponse(
                        **msg.dict(),
                        sender_name=f"{sender.first_name} {sender.last_name}" if sender else None,
                        sender_title=sender.title if sender else None
                    )
            
            conversation_responses.append(ConversationResponse(
                **conv.dict(),
                participant_name=f"{other_participant.first_name} {other_participant.last_name}" if other_participant else None,
                participant_title=other_participant.title if other_participant else None,
                unread_count=unread_count,
                last_message=last_message
            ))
        
        return ConversationListResponse(
            conversations=conversation_responses,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(offset + page_size) < total
        )
    
    @staticmethod
    async def get_messages(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
        page: int = 1,
        page_size: int = 50
    ) -> MessageListResponse:
        """Get messages in a conversation."""
        # Verify user is participant
        conversation = db.get(Conversation, conversation_id)
        if not conversation:
            raise NotFoundException(f"Conversation {conversation_id} not found")
        
        if user_id not in [conversation.participant1_id, conversation.participant2_id]:
            raise ForbiddenException("You are not a participant in this conversation")
        
        offset = (page - 1) * page_size
        
        # Get messages
        statement = select(Message).where(
            and_(
                Message.conversation_id == conversation_id,
                Message.is_deleted == False
            )
        ).order_by(desc(Message.created_at))
        
        # Get total count
        count_statement = select(func.count()).select_from(statement.subquery())
        total = db.exec(count_statement).one()
        
        # Get paginated results
        statement = statement.offset(offset).limit(page_size)
        messages = db.exec(statement).all()
        
        # Build response
        message_responses = []
        for msg in messages:
            sender = db.get(User, msg.sender_id)
            
            # Get attachments
            attachments = db.exec(
                select(MessageAttachment).where(MessageAttachment.message_id == msg.id)
            ).all()
            
            # Get reactions
            reactions_data = db.exec(
                select(MessageReaction.reaction, func.count(MessageReaction.id))
                .where(MessageReaction.message_id == msg.id)
                .group_by(MessageReaction.reaction)
            ).all()
            
            reactions = [{"emoji": r[0], "count": r[1]} for r in reactions_data]
            
            message_responses.append(MessageResponse(
                **msg.dict(),
                sender_name=f"{sender.first_name} {sender.last_name}" if sender else None,
                sender_title=sender.title if sender else None,
                attachments=[att.dict() for att in attachments],
                reactions=reactions
            ))
        
        # Mark messages as read for current user
        unread_messages = [m for m in messages if m.recipient_id == user_id and not m.is_read]
        for msg in unread_messages:
            msg.is_read = True
            msg.read_at = datetime.utcnow()
            msg.status = MessageStatus.READ
            
            # Add read receipt
            read_receipt = MessageRead(
                message_id=msg.id,
                user_id=user_id
            )
            db.add(read_receipt)
        
        # Update conversation unread count
        if conversation.participant1_id == user_id:
            conversation.participant1_unread_count = 0
        else:
            conversation.participant2_unread_count = 0
        
        db.commit()
        
        return MessageListResponse(
            messages=message_responses,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(offset + page_size) < total
        )
    
    @staticmethod
    async def mark_as_read(
        db: Session,
        message_id: UUID,
        user_id: UUID
    ) -> MessageResponse:
        """Mark a message as read."""
        message = db.get(Message, message_id)
        if not message:
            raise NotFoundException(f"Message {message_id} not found")
        
        if message.recipient_id != user_id:
            raise ForbiddenException("You are not the recipient of this message")
        
        if not message.is_read:
            message.is_read = True
            message.read_at = datetime.utcnow()
            message.status = MessageStatus.READ
            
            # Add read receipt
            read_receipt = MessageRead(
                message_id=message_id,
                user_id=user_id
            )
            db.add(read_receipt)
            
            # Update conversation unread count
            conversation = db.get(Conversation, message.conversation_id)
            if conversation:
                if conversation.participant1_id == user_id:
                    conversation.participant1_unread_count = max(0, conversation.participant1_unread_count - 1)
                else:
                    conversation.participant2_unread_count = max(0, conversation.participant2_unread_count - 1)
            
            db.commit()
            db.refresh(message)
        
        sender = db.get(User, message.sender_id)
        return MessageResponse(
            **message.dict(),
            sender_name=f"{sender.first_name} {sender.last_name}" if sender else None,
            sender_title=sender.title if sender else None
        )
    
    @staticmethod
    async def edit_message(
        db: Session,
        message_id: UUID,
        user_id: UUID,
        update_data: MessageUpdate
    ) -> MessageResponse:
        """Edit a message."""
        message = db.get(Message, message_id)
        if not message:
            raise NotFoundException(f"Message {message_id} not found")
        
        if message.sender_id != user_id:
            raise ForbiddenException("You can only edit your own messages")
        
        if message.is_deleted:
            raise ForbiddenException("Cannot edit deleted message")
        
        # Update message
        if update_data.content:
            message.content = update_data.content
            message.is_edited = True
            message.edited_at = datetime.utcnow()
            message.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(message)
        
        sender = db.get(User, user_id)
        return MessageResponse(
            **message.dict(),
            sender_name=f"{sender.first_name} {sender.last_name}" if sender else None,
            sender_title=sender.title if sender else None
        )
    
    @staticmethod
    async def delete_message(
        db: Session,
        message_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Soft delete a message."""
        message = db.get(Message, message_id)
        if not message:
            raise NotFoundException(f"Message {message_id} not found")
        
        if message.sender_id != user_id:
            raise ForbiddenException("You can only delete your own messages")
        
        message.is_deleted = True
        message.deleted_at = datetime.utcnow()
        message.deleted_by = user_id
        
        db.commit()
        
        return {"message": "Message deleted successfully"}
    
    @staticmethod
    async def get_unread_counts(
        db: Session,
        user_id: UUID,
        organization_id: UUID
    ) -> UnreadCountResponse:
        """Get unread message counts."""
        # Get all conversations where user is participant
        statement = select(Conversation).where(
            and_(
                Conversation.organization_id == organization_id,
                or_(
                    Conversation.participant1_id == user_id,
                    Conversation.participant2_id == user_id
                ),
                Conversation.is_active == True
            )
        )
        
        conversations = db.exec(statement).all()
        
        total_unread = 0
        conversations_with_unread = 0
        by_conversation = {}
        
        for conv in conversations:
            unread_count = conv.participant1_unread_count if conv.participant1_id == user_id else conv.participant2_unread_count
            if unread_count > 0:
                total_unread += unread_count
                conversations_with_unread += 1
                by_conversation[str(conv.id)] = unread_count
        
        return UnreadCountResponse(
            total_unread=total_unread,
            conversations_with_unread=conversations_with_unread,
            by_conversation=by_conversation
        )
    
    @staticmethod
    async def search_messages(
        db: Session,
        user_id: UUID,
        organization_id: UUID,
        search_params: MessageSearchRequest
    ) -> List[MessageResponse]:
        """Search messages."""
        statement = select(Message).join(Conversation).where(
            and_(
                Conversation.organization_id == organization_id,
                or_(
                    Conversation.participant1_id == user_id,
                    Conversation.participant2_id == user_id
                ),
                Message.is_deleted == False
            )
        )
        
        # Apply filters
        if search_params.query:
            statement = statement.where(Message.content.ilike(f"%{search_params.query}%"))
        
        if search_params.conversation_id:
            statement = statement.where(Message.conversation_id == search_params.conversation_id)
        
        if search_params.sender_id:
            statement = statement.where(Message.sender_id == search_params.sender_id)
        
        if search_params.content_type:
            statement = statement.where(Message.content_type == search_params.content_type)
        
        if search_params.date_from:
            statement = statement.where(Message.created_at >= search_params.date_from)
        
        if search_params.date_to:
            statement = statement.where(Message.created_at <= search_params.date_to)
        
        statement = statement.order_by(desc(Message.created_at)).limit(search_params.limit)
        
        messages = db.exec(statement).all()
        
        # Build response
        message_responses = []
        for msg in messages:
            sender = db.get(User, msg.sender_id)
            message_responses.append(MessageResponse(
                **msg.dict(),
                sender_name=f"{sender.first_name} {sender.last_name}" if sender else None,
                sender_title=sender.title if sender else None
            ))
        
        return message_responses
    
    @staticmethod
    async def add_reaction(
        db: Session,
        message_id: UUID,
        user_id: UUID,
        reaction: str
    ) -> Dict[str, Any]:
        """Add reaction to a message."""
        message = db.get(Message, message_id)
        if not message:
            raise NotFoundException(f"Message {message_id} not found")
        
        # Check if user already reacted with this emoji
        existing = db.exec(
            select(MessageReaction).where(
                and_(
                    MessageReaction.message_id == message_id,
                    MessageReaction.user_id == user_id,
                    MessageReaction.reaction == reaction
                )
            )
        ).first()
        
        if existing:
            # Remove reaction
            db.delete(existing)
            action = "removed"
        else:
            # Add reaction
            new_reaction = MessageReaction(
                message_id=message_id,
                user_id=user_id,
                reaction=reaction
            )
            db.add(new_reaction)
            action = "added"
        
        db.commit()
        
        return {"message": f"Reaction {action} successfully", "reaction": reaction}
    
    @staticmethod
    async def archive_conversation(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
        archive: bool = True
    ) -> Dict[str, Any]:
        """Archive or unarchive a conversation."""
        conversation = db.get(Conversation, conversation_id)
        if not conversation:
            raise NotFoundException(f"Conversation {conversation_id} not found")
        
        if user_id not in [conversation.participant1_id, conversation.participant2_id]:
            raise ForbiddenException("You are not a participant in this conversation")
        
        # Update archive status for user
        if conversation.participant1_id == user_id:
            conversation.archived_by_participant1 = archive
        else:
            conversation.archived_by_participant2 = archive
        
        db.commit()
        
        action = "archived" if archive else "unarchived"
        return {"message": f"Conversation {action} successfully"}