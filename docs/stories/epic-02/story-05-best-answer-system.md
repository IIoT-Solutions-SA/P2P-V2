# Story 5: Best Answer System

## Story Details
**Epic**: Epic 2 - Core MVP Features  
**Story Points**: 4  
**Priority**: Medium  
**Dependencies**: Story 3 (Post Creation), Story 4 (Replies)

## User Story
**As a** forum post author  
**I want** to mark the most helpful reply as the best answer  
**So that** future readers can quickly find the solution and contributors get recognition for their expertise

## Acceptance Criteria
- [ ] Post authors can mark one reply as "best answer"
- [ ] Best answers are prominently displayed at the top of replies section
- [ ] Best answer status affects user reputation scores positively
- [ ] Visual indicators clearly distinguish best answers from regular replies
- [ ] Best answer selection can be changed by the original post author
- [ ] Search results prioritize posts with marked best answers
- [ ] Best answer authors receive notification of selection
- [ ] Best answer badge appears on user profiles
- [ ] Analytics track best answer rates by category and user
- [ ] Best answers are highlighted in forum overviews

## Technical Specifications

### 1. Database Schema Updates

```python
# Update ForumPost model
class ForumPost(Document):
    # ... existing fields ...
    has_best_answer: bool = False
    best_answer_id: Optional[str] = None
    best_answer_selected_at: Optional[datetime] = None

# Update ForumReply model  
class ForumReply(Document):
    # ... existing fields ...
    is_best_answer: bool = False
    best_answer_selected_at: Optional[datetime] = None

# Update UserProfile model
class UserProfile(Document):
    # ... existing fields ...
    best_answers_count: int = 0
    best_answers_this_month: int = 0
```

### 2. API Endpoints

```python
@router.post("/posts/{post_id}/best-answer/{reply_id}")
async def mark_best_answer(
    post_id: str,
    reply_id: str,
    session: SessionContainer = Depends(verify_session())
):
    """Mark a reply as the best answer"""
    user_id = session.get_user_id()
    
    try:
        result = await BestAnswerService.mark_best_answer(post_id, reply_id, user_id)
        return {"message": "Best answer marked successfully", "best_answer_id": reply_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/posts/{post_id}/best-answer")
async def unmark_best_answer(
    post_id: str,
    session: SessionContainer = Depends(verify_session())
):
    """Remove best answer marking"""
    user_id = session.get_user_id()
    
    try:
        await BestAnswerService.unmark_best_answer(post_id, user_id)
        return {"message": "Best answer removed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
```

### 3. Best Answer Service

```python
class BestAnswerService:
    @staticmethod
    async def mark_best_answer(post_id: str, reply_id: str, user_id: str):
        """Mark a reply as best answer"""
        # Verify post ownership
        post = await ForumPost.find_one(ForumPost.id == post_id)
        if not post:
            raise ValueError("Post not found")
        
        if post.author_id != user_id:
            raise PermissionError("Only post author can mark best answer")
        
        # Verify reply exists and belongs to post
        reply = await ForumReply.find_one(
            ForumReply.id == reply_id,
            ForumReply.post_id == post_id
        )
        if not reply:
            raise ValueError("Reply not found")
        
        # Remove previous best answer if exists
        if post.best_answer_id:
            await BestAnswerService._remove_previous_best_answer(post.best_answer_id)
        
        # Mark new best answer
        reply.is_best_answer = True
        reply.best_answer_selected_at = datetime.utcnow()
        await reply.save()
        
        # Update post
        post.has_best_answer = True
        post.best_answer_id = reply_id
        post.best_answer_selected_at = datetime.utcnow()
        await post.save()
        
        # Update reply author's reputation
        await BestAnswerService._update_author_reputation(reply.author_id, "add")
        
        # Send notification to reply author
        await NotificationService.send_best_answer_notification(
            reply.author_id, post.title, post_id
        )
        
        return True
    
    @staticmethod
    async def _update_author_reputation(author_id: str, action: str):
        """Update user reputation for best answer"""
        user_profile = await UserProfile.find_one(UserProfile.user_id == author_id)
        if user_profile:
            if action == "add":
                user_profile.reputation_score += 10  # Best answer worth 10 points
                user_profile.best_answers_count += 1
                user_profile.best_answers_this_month += 1
            elif action == "remove":
                user_profile.reputation_score = max(0, user_profile.reputation_score - 10)
                user_profile.best_answers_count = max(0, user_profile.best_answers_count - 1)
            
            await user_profile.save()
```

### 4. Frontend Best Answer Component

```typescript
// BestAnswerButton.tsx
interface BestAnswerButtonProps {
  postId: string;
  replyId: string;
  isBestAnswer: boolean;
  isPostAuthor: boolean;
  onToggle: () => void;
}

export function BestAnswerButton({ 
  postId, 
  replyId, 
  isBestAnswer, 
  isPostAuthor, 
  onToggle 
}: BestAnswerButtonProps) {
  const { t } = useTranslation();
  
  const handleClick = async () => {
    try {
      if (isBestAnswer) {
        await api.delete(`/api/v1/posts/${postId}/best-answer`);
      } else {
        await api.post(`/api/v1/posts/${postId}/best-answer/${replyId}`);
      }
      onToggle();
    } catch (error) {
      console.error('Best answer toggle failed:', error);
    }
  };
  
  if (!isPostAuthor && !isBestAnswer) {
    return null; // Only show to post authors or if already marked
  }
  
  return (
    <div className="flex items-center space-x-2">
      {isBestAnswer ? (
        <Badge className="bg-green-100 text-green-800 border-green-300">
          <Star className="h-3 w-3 mr-1 fill-current" />
          {t('forum.best_answer')}
        </Badge>
      ) : isPostAuthor ? (
        <Button
          variant="outline"
          size="sm"
          onClick={handleClick}
          className="text-green-600 border-green-300 hover:bg-green-50"
        >
          <Star className="h-3 w-3 mr-1" />
          {t('forum.mark_best_answer')}
        </Button>
      ) : null}
    </div>
  );
}
```

## Implementation Steps

1. **Database Updates**
   - Add best answer fields to post and reply models
   - Update user reputation tracking
   - Create indexes for best answer queries

2. **Backend Service**
   - Implement BestAnswerService
   - Add notification system for best answer selection
   - Update reputation calculation logic

3. **Frontend Components**
   - Best answer button component
   - Visual indicators for best answers
   - Best answer highlights in reply lists

4. **Analytics**
   - Track best answer selection rates
   - Monitor user reputation changes
   - Analyze community engagement metrics

## Testing Checklist
- [ ] Post authors can mark/unmark best answers
- [ ] Best answers display prominently
- [ ] Reputation updates correctly
- [ ] Notifications sent to reply authors
- [ ] Visual indicators work properly
- [ ] Search prioritizes posts with best answers
- [ ] Only one best answer per post allowed
- [ ] Best answer selection is persistent
- [ ] Mobile interface works properly

## Dependencies
- Story 3 (Post Creation) completed
- Story 4 (Replies) completed  
- Notification service implemented

## Notes
- Consider gamification elements for best answers
- Implement abuse prevention for best answer farming
- Plan for best answer leaderboards
- Consider best answer quality metrics