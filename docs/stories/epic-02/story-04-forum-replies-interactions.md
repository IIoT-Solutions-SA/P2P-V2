# Story 4: Forum Replies and Interactions

## Story Details
**Epic**: Epic 2 - Core MVP Features  
**Story Points**: 6  
**Priority**: High  
**Dependencies**: Story 2 (Forum System), Story 3 (Post Creation)

## User Story
**As a** forum participant (Factory Owner, Plant Engineer, Operations Manager)  
**I want** to reply to posts and interact with other users' content through upvoting and comments  
**So that** I can provide help, ask clarifying questions, and build professional relationships with peers

## Acceptance Criteria
- [ ] Users can reply to posts with rich text formatting and attachments
- [ ] Reply threading shows conversation hierarchy clearly (nested replies)
- [ ] Users can upvote helpful replies to increase their visibility
- [ ] Reply editing and deletion functionality for authors
- [ ] Notification system alerts users of new replies to their posts
- [ ] Reply sorting options: chronological, most upvoted, newest first
- [ ] @ mentions notify users when referenced in replies
- [ ] Reply drafts auto-save to prevent content loss
- [ ] Mobile-optimized interface for easy interaction
- [ ] Arabic/English language support for all reply content

## Technical Specifications

### 1. Reply Data Model

```python
# Update app/models/mongo_models.py
class ForumReply(Document):
    # Basic Information
    post_id: str
    parent_reply_id: Optional[str] = None  # For threaded replies
    author_id: str
    author_name: str
    author_avatar: Optional[str] = None
    author_verification_status: str = "pending"
    
    # Content
    content: str
    language: str = "en"
    attachments: List[Dict[str, str]] = Field(default_factory=list)
    
    # Engagement
    upvote_count: int = 0
    mention_user_ids: List[str] = Field(default_factory=list)
    
    # Status
    status: str = "published"  # published, edited, deleted
    is_best_answer: bool = False
    
    # Threading
    reply_level: int = 0  # 0 = top level, 1 = reply to post, 2+ = nested
    reply_path: str = ""  # For efficient threading queries
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "forum_replies"
        indexes = [
            [("post_id", pymongo.ASCENDING)],
            [("parent_reply_id", pymongo.ASCENDING)],
            [("author_id", pymongo.ASCENDING)],
            [("created_at", pymongo.ASCENDING)],
            [("upvote_count", pymongo.DESCENDING)],
            [("reply_path", pymongo.ASCENDING)]
        ]
```

### 2. API Endpoints

```python
# app/api/v1/endpoints/replies.py
@router.post("/posts/{post_id}/replies", response_model=ReplyResponse)
async def create_reply(
    post_id: str,
    reply_data: ReplyCreateRequest,
    session: SessionContainer = Depends(verify_session())
):
    """Create a new reply"""
    user_id = session.get_user_id()
    
    try:
        reply = await ReplyService.create_reply(user_id, post_id, reply_data)
        return await ReplyService.get_reply_response(reply.id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/posts/{post_id}/replies", response_model=List[ReplyResponse])
async def get_post_replies(
    post_id: str,
    sort_by: str = Query("chronological", description="Sort by: chronological, upvotes, newest"),
    limit: int = Query(50, ge=1, le=100),
    session: Optional[SessionContainer] = Depends(verify_session(session_required=False))
):
    """Get replies for a post"""
    user_id = session.get_user_id() if session else None
    replies = await ReplyService.get_post_replies(post_id, sort_by, limit, user_id)
    return replies

@router.put("/replies/{reply_id}", response_model=ReplyResponse)
async def update_reply(
    reply_id: str,
    reply_data: ReplyUpdateRequest,
    session: SessionContainer = Depends(verify_session())
):
    """Update a reply"""
    user_id = session.get_user_id()
    reply = await ReplyService.update_reply(reply_id, user_id, reply_data)
    return await ReplyService.get_reply_response(reply.id, user_id)

@router.post("/replies/{reply_id}/upvote")
async def upvote_reply(
    reply_id: str,
    session: SessionContainer = Depends(verify_session())
):
    """Upvote a reply"""
    user_id = session.get_user_id()
    result = await ReplyService.toggle_upvote(reply_id, user_id)
    return {"message": "Vote recorded", "upvoted": result}
```

### 3. Frontend Reply Component

```typescript
// frontend/src/components/Forum/ReplyList.tsx
export default function ReplyList({ postId }: { postId: string }) {
  const [replies, setReplies] = useState<Reply[]>([]);
  const [sortBy, setSortBy] = useState('chronological');
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchReplies();
  }, [postId, sortBy]);
  
  const fetchReplies = async () => {
    try {
      const response = await api.get(`/api/v1/posts/${postId}/replies?sort_by=${sortBy}`);
      setReplies(response.data);
    } catch (error) {
      console.error('Failed to fetch replies:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleUpvote = async (replyId: string) => {
    try {
      await api.post(`/api/v1/replies/${replyId}/upvote`);
      // Update local state
      setReplies(prev => prev.map(reply => 
        reply.id === replyId 
          ? { ...reply, upvote_count: reply.upvote_count + 1, user_upvoted: !reply.user_upvoted }
          : reply
      ));
    } catch (error) {
      console.error('Upvote failed:', error);
    }
  };
  
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">{replies.length} Replies</h3>
        <Select value={sortBy} onValueChange={setSortBy}>
          <SelectTrigger className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="chronological">Chronological</SelectItem>
            <SelectItem value="upvotes">Most Upvoted</SelectItem>
            <SelectItem value="newest">Newest First</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      {replies.map(reply => (
        <ReplyCard 
          key={reply.id} 
          reply={reply} 
          onUpvote={handleUpvote}
          onReply={handleReplyToReply}
        />
      ))}
    </div>
  );
}
```

## Implementation Steps

1. **Database Schema**
   - Create ForumReply model with threading support
   - Set up indexes for efficient querying
   - Implement reply path for nested replies

2. **Backend Services**
   - ReplyService for CRUD operations
   - Notification service for reply alerts
   - Upvoting system with user tracking

3. **Frontend Components**
   - Reply list with threading visualization
   - Reply editor with rich text support
   - Upvoting interface with real-time updates

4. **Notification System**
   - Email notifications for new replies
   - In-app notification badges
   - @ mention detection and alerts

## Testing Checklist
- [ ] Reply creation works with rich content
- [ ] Threading displays correctly with proper nesting
- [ ] Upvoting updates counts in real-time
- [ ] Notifications sent for new replies
- [ ] Reply editing preserves formatting
- [ ] @ mentions trigger notifications
- [ ] Mobile interface is responsive
- [ ] Arabic/English content displays properly
- [ ] Reply sorting functions correctly
- [ ] Draft auto-saving prevents data loss

## Dependencies
- Story 2 (Forum System) completed
- Story 3 (Post Creation) completed
- Notification service configured

## Notes
- Implement rate limiting for reply creation
- Consider reply moderation tools
- Plan for abuse reporting system
- Optimize threading performance for deep conversations