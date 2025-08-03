# Story 3: Private Peer Messaging

## Story Details
**Epic**: Epic 3 - Use Case Submission and Knowledge Management  
**Story Points**: 6  
**Priority**: High  
**Dependencies**: Epic 1 (Project Foundation), User Verification System, WebSocket Infrastructure

## User Story
**As a** verified industry professional  
**I want** to have private conversations with other verified users  
**So that** I can discuss sensitive topics, share confidential information, and build professional relationships

## Acceptance Criteria
- [ ] Real-time messaging between verified users with message threading
- [ ] File sharing capabilities within conversations (documents, images)
- [ ] Message search functionality within conversations
- [ ] Conversation management: create, archive, delete, mute notifications
- [ ] Online/offline status indicators for participants
- [ ] Message read receipts and typing indicators
- [ ] Group messaging for project collaboration (up to 10 participants)
- [ ] Message encryption for sensitive conversations
- [ ] Notification system for new messages (email, in-app, push)
- [ ] Arabic/English language support with RTL layout

## Technical Specifications

### 1. Messaging Data Models

```python
# app/models/mongo_models.py
class Conversation(Document):
    # Basic Information
    title: Optional[str] = None  # For group conversations
    conversation_type: str = "direct"  # direct, group
    
    # Participants
    participants: List[str] = Field(default_factory=list)  # user_ids
    participant_details: List[Dict[str, Any]] = Field(default_factory=list)
    # [{"user_id": "...", "name": "...", "avatar": "...", "role": "member|admin"}]
    
    # Settings
    is_encrypted: bool = False
    allow_file_sharing: bool = True
    
    # Status
    is_active: bool = True
    is_archived: bool = False
    
    # Last Activity
    last_message_id: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_message_preview: Optional[str] = None
    
    # Metadata
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "conversations"
        indexes = [
            [("participants", pymongo.ASCENDING)],
            [("created_by", pymongo.ASCENDING)],
            [("last_message_at", pymongo.DESCENDING)],
            [("is_active", pymongo.ASCENDING)]
        ]

class Message(Document):
    # Basic Information
    conversation_id: str
    sender_id: str
    sender_name: str
    sender_avatar: Optional[str] = None
    
    # Content
    content: str
    message_type: str = "text"  # text, file, image, system
    language: str = "en"
    
    # Attachments
    attachments: List[Dict[str, str]] = Field(default_factory=list)
    # [{"type": "file", "url": "...", "filename": "...", "size": "..."}]
    
    # Threading
    reply_to_message_id: Optional[str] = None
    thread_id: Optional[str] = None
    
    # Status
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    
    # Delivery & Read Status
    delivered_to: List[Dict[str, datetime]] = Field(default_factory=list)
    # [{"user_id": "...", "delivered_at": "..."}]
    read_by: List[Dict[str, datetime]] = Field(default_factory=list)
    # [{"user_id": "...", "read_at": "..."}]
    
    # Encryption
    is_encrypted: bool = False
    encryption_key_id: Optional[str] = None
    
    # Timestamps
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "messages"
        indexes = [
            [("conversation_id", pymongo.ASCENDING), ("sent_at", pymongo.DESCENDING)],
            [("sender_id", pymongo.ASCENDING)],
            [("reply_to_message_id", pymongo.ASCENDING)],
            [("sent_at", pymongo.DESCENDING)]
        ]

class UserMessageSettings(Document):
    user_id: str
    
    # Conversation-specific settings
    conversation_settings: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    # {"conv_id": {"notifications_enabled": true, "last_read_at": "..."}}
    
    # Global settings
    email_notifications: bool = True
    push_notifications: bool = True
    sound_notifications: bool = True
    
    # Privacy
    allow_messages_from: str = "verified_only"  # anyone, verified_only, connections_only
    auto_accept_group_invites: bool = False
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "user_message_settings"
        indexes = [
            [("user_id", pymongo.ASCENDING)]
        ]
```

### 2. Real-time WebSocket Implementation

```python
# app/websockets/messaging.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

class MessageConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_status: Dict[str, str] = {}  # online, away, offline
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        self.user_status[user_id] = "online"
        
        # Notify contacts of online status
        await self._broadcast_status_change(user_id, "online")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                self.user_status[user_id] = "offline"
                # Schedule offline status broadcast after delay
    
    async def send_message_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove broken connections
                    self.active_connections[user_id].remove(connection)
    
    async def send_message_to_conversation(self, conversation_id: str, message: dict, exclude_user: str = None):
        # Get conversation participants
        conversation = await Conversation.find_one(Conversation.id == conversation_id)
        if conversation:
            for participant_id in conversation.participants:
                if participant_id != exclude_user:
                    await self.send_message_to_user(participant_id, message)
    
    async def send_typing_indicator(self, conversation_id: str, user_id: str, user_name: str):
        typing_message = {
            "type": "typing_start",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "user_name": user_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message_to_conversation(conversation_id, typing_message, exclude_user=user_id)

manager = MessageConnectionManager()

@router.websocket("/ws/messaging/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "typing_start":
                await manager.send_typing_indicator(
                    message_data["conversation_id"],
                    user_id,
                    message_data["user_name"]
                )
            elif message_data["type"] == "typing_stop":
                stop_message = {
                    "type": "typing_stop",
                    "conversation_id": message_data["conversation_id"],
                    "user_id": user_id
                }
                await manager.send_message_to_conversation(
                    message_data["conversation_id"], stop_message, exclude_user=user_id
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
```

### 3. Messaging API Endpoints

```python
# app/api/v1/endpoints/messaging.py
@router.get("/conversations", response_model=List[ConversationResponse])
async def get_user_conversations(
    limit: int = Query(50, ge=1, le=100),
    session: SessionContainer = Depends(verify_session())
):
    """Get user's conversations"""
    user_id = session.get_user_id()
    
    conversations = await MessagingService.get_user_conversations(user_id, limit)
    return [ConversationResponse.from_document(conv) for conv in conversations]

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreateRequest,
    session: SessionContainer = Depends(verify_session())
):
    """Create new conversation"""
    user_id = session.get_user_id()
    
    try:
        conversation = await MessagingService.create_conversation(user_id, conversation_data)
        return ConversationResponse.from_document(conversation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    message_data: MessageCreateRequest,
    session: SessionContainer = Depends(verify_session())
):
    """Send message to conversation"""
    user_id = session.get_user_id()
    
    try:
        message = await MessagingService.send_message(user_id, conversation_id, message_data)
        
        # Send real-time notification
        websocket_message = {
            "type": "new_message",
            "conversation_id": conversation_id,
            "message": MessageResponse.from_document(message).dict()
        }
        await manager.send_message_to_conversation(conversation_id, websocket_message, exclude_user=user_id)
        
        return MessageResponse.from_document(message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    before_message_id: Optional[str] = Query(None),
    session: SessionContainer = Depends(verify_session())
):
    """Get messages from conversation"""
    user_id = session.get_user_id()
    
    try:
        messages = await MessagingService.get_conversation_messages(
            user_id, conversation_id, limit, before_message_id
        )
        return [MessageResponse.from_document(msg) for msg in messages]
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/conversations/{conversation_id}/messages/{message_id}/read")
async def mark_message_read(
    conversation_id: str,
    message_id: str,
    session: SessionContainer = Depends(verify_session())
):
    """Mark message as read"""
    user_id = session.get_user_id()
    
    await MessagingService.mark_message_read(user_id, conversation_id, message_id)
    return {"message": "Message marked as read"}

@router.post("/conversations/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: str,
    session: SessionContainer = Depends(verify_session())
):
    """Archive conversation"""
    user_id = session.get_user_id()
    
    try:
        await MessagingService.archive_conversation(user_id, conversation_id)
        return {"message": "Conversation archived"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/search", response_model=List[MessageSearchResult])
async def search_messages(
    query: str = Query(..., min_length=2),
    conversation_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    session: SessionContainer = Depends(verify_session())
):
    """Search messages across conversations"""
    user_id = session.get_user_id()
    
    results = await MessagingService.search_messages(user_id, query, conversation_id, limit)
    return results
```

### 4. Messaging Service Implementation

```python
# app/services/messaging_service.py
class MessagingService:
    @staticmethod
    async def create_conversation(
        user_id: str, 
        conversation_data: ConversationCreateRequest
    ) -> Conversation:
        """Create new conversation"""
        
        # Validate participants
        participants = [user_id] + conversation_data.participant_ids
        participants = list(set(participants))  # Remove duplicates
        
        # Verify all participants are verified users
        for participant_id in participants:
            user_profile = await UserProfile.find_one(
                UserProfile.user_id == participant_id,
                UserProfile.verification_status == "verified"
            )
            if not user_profile:
                raise ValueError(f"User {participant_id} not found or not verified")
        
        # Check for existing direct conversation
        if conversation_data.conversation_type == "direct" and len(participants) == 2:
            existing = await Conversation.find_one({
                "conversation_type": "direct",
                "participants": {"$all": participants, "$size": 2}
            })
            if existing:
                return existing
        
        # Get participant details
        participant_details = []
        for participant_id in participants:
            user_profile = await UserProfile.find_one(UserProfile.user_id == participant_id)
            participant_details.append({
                "user_id": participant_id,
                "name": user_profile.name,
                "avatar": user_profile.profile_picture_url,
                "role": "admin" if participant_id == user_id else "member"
            })
        
        # Create conversation
        conversation = Conversation(
            title=conversation_data.title,
            conversation_type=conversation_data.conversation_type,
            participants=participants,
            participant_details=participant_details,
            is_encrypted=conversation_data.is_encrypted,
            created_by=user_id
        )
        
        await conversation.create()
        
        # Send system message
        await MessagingService._send_system_message(
            conversation.id,
            f"Conversation created by {participant_details[0]['name']}"
        )
        
        logger.info(f"Conversation created: {conversation.id} by user {user_id}")
        return conversation
    
    @staticmethod
    async def send_message(
        user_id: str,
        conversation_id: str,
        message_data: MessageCreateRequest
    ) -> Message:
        """Send message to conversation"""
        
        # Verify user is participant
        conversation = await Conversation.find_one(
            Conversation.id == conversation_id,
            Conversation.participants.in_([user_id])
        )
        if not conversation:
            raise PermissionError("Not authorized to send messages to this conversation")
        
        # Get sender details
        user_profile = await UserProfile.find_one(UserProfile.user_id == user_id)
        
        # Create message
        message = Message(
            conversation_id=conversation_id,
            sender_id=user_id,
            sender_name=user_profile.name,
            sender_avatar=user_profile.profile_picture_url,
            content=message_data.content,
            message_type=message_data.message_type,
            language=message_data.language,
            attachments=message_data.attachments,
            reply_to_message_id=message_data.reply_to_message_id,
            is_encrypted=conversation.is_encrypted
        )
        
        await message.create()
        
        # Update conversation
        conversation.last_message_id = message.id
        conversation.last_message_at = message.sent_at
        conversation.last_message_preview = message.content[:100]
        conversation.updated_at = datetime.utcnow()
        await conversation.save()
        
        # Send notifications to other participants
        await MessagingService._send_message_notifications(conversation, message, user_id)
        
        logger.info(f"Message sent: {message.id} in conversation {conversation_id}")
        return message
    
    @staticmethod
    async def search_messages(
        user_id: str,
        query: str,
        conversation_id: Optional[str] = None,
        limit: int = 20
    ) -> List[MessageSearchResult]:
        """Search messages across user's conversations"""
        
        # Get user's conversations
        user_conversations = await Conversation.find(
            Conversation.participants.in_([user_id])
        ).to_list()
        
        conversation_ids = [conv.id for conv in user_conversations]
        
        # Build search query
        search_filter = {
            "conversation_id": {"$in": conversation_ids},
            "is_deleted": False,
            "$text": {"$search": query}
        }
        
        if conversation_id:
            search_filter["conversation_id"] = conversation_id
        
        # Execute search
        messages = await Message.find(search_filter).sort([
            ("score", {"$meta": "textScore"}),
            ("sent_at", -1)
        ]).limit(limit).to_list()
        
        # Format results
        results = []
        for message in messages:
            conversation = next(
                (conv for conv in user_conversations if conv.id == message.conversation_id),
                None
            )
            
            results.append(MessageSearchResult(
                message_id=message.id,
                conversation_id=message.conversation_id,
                conversation_title=conversation.title if conversation else "Unknown",
                content=message.content,
                sender_name=message.sender_name,
                sent_at=message.sent_at,
                relevance_score=message.score if hasattr(message, 'score') else 0
            ))
        
        return results
    
    @staticmethod
    async def _send_message_notifications(
        conversation: Conversation,
        message: Message,
        sender_id: str
    ):
        """Send notifications to conversation participants"""
        for participant in conversation.participants:
            if participant != sender_id:
                # Get user notification settings
                settings = await UserMessageSettings.find_one(
                    UserMessageSettings.user_id == participant
                )
                
                if settings and settings.email_notifications:
                    await NotificationService.send_new_message_email(
                        participant, conversation, message
                    )
                
                # Send push notification
                await NotificationService.send_push_notification(
                    participant,
                    f"New message from {message.sender_name}",
                    message.content[:100]
                )
```

### 5. Frontend Messaging Interface

```typescript
// MessagingInterface.tsx
export default function MessagingInterface() {
  const { t } = useTranslation();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [typingUsers, setTypingUsers] = useState<string[]>([]);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    // Establish WebSocket connection
    const websocket = new WebSocket(`ws://localhost:8000/ws/messaging/${userId}`);
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };
    
    setWs(websocket);
    
    return () => websocket.close();
  }, []);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'new_message':
        if (data.conversation_id === activeConversation) {
          setMessages(prev => [...prev, data.message]);
        }
        updateConversationPreview(data.conversation_id, data.message);
        break;
      
      case 'typing_start':
        setTypingUsers(prev => [...prev, data.user_name]);
        break;
      
      case 'typing_stop':
        setTypingUsers(prev => prev.filter(name => name !== data.user_name));
        break;
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !activeConversation) return;

    try {
      const response = await api.post(`/api/v1/messaging/conversations/${activeConversation}/messages`, {
        content: newMessage,
        message_type: 'text',
        language: 'en'
      });

      setMessages(prev => [...prev, response.data]);
      setNewMessage('');
    } catch (error) {
      toast.error(t('messaging.send_failed'));
    }
  };

  const handleTyping = () => {
    if (ws && activeConversation) {
      ws.send(JSON.stringify({
        type: 'typing_start',
        conversation_id: activeConversation,
        user_name: currentUser.name
      }));
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Conversations List */}
      <div className="w-1/3 bg-white border-r border-gray-200">
        <ConversationList
          conversations={conversations}
          activeConversation={activeConversation}
          onSelectConversation={setActiveConversation}
        />
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {activeConversation ? (
          <>
            <ChatHeader conversation={activeConversation} />
            <MessageList
              messages={messages}
              typingUsers={typingUsers}
            />
            <MessageInput
              value={newMessage}
              onChange={setNewMessage}
              onSend={sendMessage}
              onTyping={handleTyping}
            />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-gray-500">{t('messaging.select_conversation')}</p>
          </div>
        )}
      </div>
    </div>
  );
}
```

## Implementation Steps

1. **WebSocket Infrastructure**
   - Set up WebSocket connections for real-time messaging
   - Implement connection management and user presence
   - Add typing indicators and message delivery

2. **Database Schema**
   - Create Conversation, Message, and UserMessageSettings models
   - Set up indexes for efficient message querying
   - Implement message search capabilities

3. **Backend Services**
   - MessagingService for conversation and message management
   - Real-time notification system
   - File sharing integration

4. **Frontend Components**
   - Real-time messaging interface with WebSocket integration
   - Conversation management and message threading
   - Mobile-responsive chat interface

## Testing Checklist
- [ ] Real-time messaging works across multiple browser tabs
- [ ] Message delivery and read receipts function correctly
- [ ] File sharing within conversations works properly
- [ ] Conversation archiving and management functions
- [ ] Search finds relevant messages accurately
- [ ] Notifications send correctly for new messages
- [ ] Group conversations support multiple participants
- [ ] Arabic/English content displays with proper layout
- [ ] Mobile interface provides good user experience

## Performance Considerations
- [ ] WebSocket connection pooling and management
- [ ] Message pagination for large conversations
- [ ] Efficient database queries for message history
- [ ] Real-time notification optimization
- [ ] File sharing performance with large attachments

## Dependencies
- WebSocket infrastructure setup
- User verification system operational
- File sharing service configured
- Push notification service available

## Notes
- Implement message encryption for sensitive conversations
- Consider integration with external communication tools
- Plan for message retention and archival policies
- Design scalable architecture for high message volume
- Ensure compliance with communication privacy regulations