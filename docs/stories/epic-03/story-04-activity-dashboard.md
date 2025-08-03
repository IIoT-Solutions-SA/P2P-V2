# Story 4: Activity Dashboard

## Story Details
**Epic**: Epic 3 - Use Case Submission and Knowledge Management  
**Story Points**: 5  
**Priority**: High  
**Dependencies**: Epic 2 (Forum System), Epic 3 Stories 1-3, User Analytics

## User Story
**As a** platform user  
**I want** a personalized dashboard that shows my activity, engagement metrics, and relevant content recommendations  
**So that** I can track my contributions, stay updated on community activity, and discover content aligned with my interests

## Acceptance Criteria
- [ ] Personalized dashboard showing user's activity summary and statistics
- [ ] Recent activity feed: posts, replies, use cases, messages, file shares
- [ ] Engagement metrics: reputation score, contributions count, community ranking
- [ ] Notification center with categorized alerts (mentions, replies, approvals)
- [ ] Recommended content based on user interests and activity patterns
- [ ] Quick action shortcuts for common tasks (new post, submit use case)
- [ ] Calendar integration showing industry events and platform activities
- [ ] Goal tracking for user engagement and contribution targets
- [ ] Customizable dashboard layout with draggable widgets
- [ ] Mobile-optimized dashboard with essential metrics

## Technical Specifications

### 1. Dashboard Data Models

```python
# app/models/mongo_models.py
class UserActivity(Document):
    user_id: str
    activity_type: str  # post_created, reply_posted, use_case_submitted, file_shared, etc.
    activity_data: Dict[str, Any] = Field(default_factory=dict)
    # {"post_id": "...", "title": "...", "category": "..."}
    
    # Context
    target_id: Optional[str] = None  # ID of the related entity
    target_type: Optional[str] = None  # post, use_case, file, user
    
    # Metadata
    activity_score: int = 0  # Points earned for this activity
    is_visible: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "user_activities"
        indexes = [
            [("user_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)],
            [("activity_type", pymongo.ASCENDING)],
            [("target_id", pymongo.ASCENDING)],
            [("created_at", pymongo.DESCENDING)]
        ]

class UserStats(Document):
    user_id: str
    
    # Contribution Stats
    posts_count: int = 0
    replies_count: int = 0
    use_cases_count: int = 0
    files_shared_count: int = 0
    best_answers_count: int = 0
    
    # Engagement Stats
    total_upvotes_received: int = 0
    total_views_generated: int = 0
    profile_views: int = 0
    messages_sent: int = 0
    
    # Community Metrics
    reputation_score: int = 0
    community_rank: Optional[int] = None
    expertise_score: Dict[str, int] = Field(default_factory=dict)
    # {"manufacturing": 85, "quality_control": 92}
    
    # Time-based metrics
    this_month_activity: Dict[str, int] = Field(default_factory=dict)
    this_week_activity: Dict[str, int] = Field(default_factory=dict)
    streak_days: int = 0
    last_activity_date: Optional[datetime] = None
    
    # Goals and Achievements
    monthly_goals: Dict[str, int] = Field(default_factory=dict)
    # {"posts": 5, "use_cases": 2, "replies": 20}
    monthly_progress: Dict[str, int] = Field(default_factory=dict)
    
    achievements: List[Dict[str, Any]] = Field(default_factory=list)
    # [{"type": "first_post", "earned_at": "...", "description": "..."}]
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "user_stats"
        indexes = [
            [("user_id", pymongo.ASCENDING)],
            [("reputation_score", pymongo.DESCENDING)],
            [("community_rank", pymongo.ASCENDING)]
        ]

class DashboardWidget(Document):
    user_id: str
    widget_type: str  # activity_feed, stats, recommendations, calendar, goals
    widget_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Layout
    position: Dict[str, int] = Field(default_factory=dict)
    # {"x": 0, "y": 0, "width": 4, "height": 6}
    
    is_visible: bool = True
    is_default: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "dashboard_widgets"
        indexes = [
            [("user_id", pymongo.ASCENDING)]
        ]

class Notification(Document):
    user_id: str
    notification_type: str  # mention, reply, approval, achievement, system
    title: str
    content: str
    
    # Related Data
    related_id: Optional[str] = None
    related_type: Optional[str] = None  # post, use_case, message, user
    related_url: Optional[str] = None
    
    # Actor (who triggered the notification)
    actor_id: Optional[str] = None
    actor_name: Optional[str] = None
    actor_avatar: Optional[str] = None
    
    # Status
    is_read: bool = False
    read_at: Optional[datetime] = None
    
    # Priority and Category
    priority: str = "normal"  # low, normal, high, urgent
    category: str = "general"  # general, forum, use_case, messaging, system
    
    # Metadata
    data: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    class Settings:
        name = "notifications"
        indexes = [
            [("user_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)],
            [("is_read", pymongo.ASCENDING)],
            [("category", pymongo.ASCENDING)],
            [("expires_at", pymongo.ASCENDING)]
        ]
```

### 2. Dashboard API Endpoints

```python
# app/api/v1/endpoints/dashboard.py
@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    session: SessionContainer = Depends(verify_session())
):
    """Get user's dashboard data"""
    user_id = session.get_user_id()
    
    dashboard_data = await DashboardService.get_dashboard_data(user_id)
    return dashboard_data

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    session: SessionContainer = Depends(verify_session())
):
    """Get detailed user statistics"""
    user_id = session.get_user_id()
    
    stats = await DashboardService.get_user_stats(user_id)
    return UserStatsResponse.from_document(stats)

@router.get("/activity", response_model=List[ActivityResponse])
async def get_activity_feed(
    limit: int = Query(20, ge=1, le=50),
    activity_type: Optional[str] = Query(None),
    session: SessionContainer = Depends(verify_session())
):
    """Get user's recent activity"""
    user_id = session.get_user_id()
    
    activities = await DashboardService.get_activity_feed(user_id, limit, activity_type)
    return [ActivityResponse.from_document(activity) for activity in activities]

@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    category: Optional[str] = Query(None),
    unread_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=50),
    session: SessionContainer = Depends(verify_session())
):
    """Get user notifications"""
    user_id = session.get_user_id()
    
    notifications = await DashboardService.get_notifications(
        user_id, category, unread_only, limit
    )
    
    unread_count = await DashboardService.get_unread_notifications_count(user_id)
    
    return NotificationListResponse(
        notifications=[NotificationResponse.from_document(n) for n in notifications],
        unread_count=unread_count,
        total_count=len(notifications)
    )

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    session: SessionContainer = Depends(verify_session())
):
    """Mark notification as read"""
    user_id = session.get_user_id()
    
    await DashboardService.mark_notification_read(notification_id, user_id)
    return {"message": "Notification marked as read"}

@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    recommendation_type: Optional[str] = Query(None),  # content, users, use_cases
    limit: int = Query(10, ge=1, le=20),
    session: SessionContainer = Depends(verify_session())
):
    """Get personalized recommendations"""
    user_id = session.get_user_id()
    
    recommendations = await DashboardService.get_recommendations(
        user_id, recommendation_type, limit
    )
    return recommendations

@router.post("/widgets", response_model=WidgetResponse)
async def save_widget_config(
    widget_data: WidgetConfigRequest,
    session: SessionContainer = Depends(verify_session())
):
    """Save dashboard widget configuration"""
    user_id = session.get_user_id()
    
    widget = await DashboardService.save_widget_config(user_id, widget_data)
    return WidgetResponse.from_document(widget)

@router.post("/goals", response_model=GoalsResponse)
async def set_monthly_goals(
    goals_data: MonthlyGoalsRequest,
    session: SessionContainer = Depends(verify_session())
):
    """Set user's monthly goals"""
    user_id = session.get_user_id()
    
    stats = await DashboardService.set_monthly_goals(user_id, goals_data)
    return GoalsResponse.from_stats(stats)
```

### 3. Dashboard Service Implementation

```python
# app/services/dashboard_service.py
class DashboardService:
    @staticmethod
    async def get_dashboard_data(user_id: str) -> DashboardResponse:
        """Get comprehensive dashboard data"""
        
        # Get user stats
        user_stats = await DashboardService.get_user_stats(user_id)
        
        # Get recent activity
        recent_activity = await DashboardService.get_activity_feed(user_id, 10)
        
        # Get notifications
        notifications = await DashboardService.get_notifications(user_id, None, True, 5)
        unread_count = await DashboardService.get_unread_notifications_count(user_id)
        
        # Get recommendations
        recommendations = await DashboardService.get_recommendations(user_id, None, 5)
        
        # Get widget configurations
        widgets = await DashboardWidget.find(
            DashboardWidget.user_id == user_id,
            DashboardWidget.is_visible == True
        ).to_list()
        
        # Calculate achievements
        achievements = await DashboardService._check_new_achievements(user_id, user_stats)
        
        return DashboardResponse(
            user_stats=UserStatsResponse.from_document(user_stats),
            recent_activity=[ActivityResponse.from_document(a) for a in recent_activity],
            notifications=[NotificationResponse.from_document(n) for n in notifications],
            unread_notifications_count=unread_count,
            recommendations=recommendations,
            widgets=[WidgetResponse.from_document(w) for w in widgets],
            achievements=achievements
        )
    
    @staticmethod
    async def get_user_stats(user_id: str) -> UserStats:
        """Get or create user statistics"""
        stats = await UserStats.find_one(UserStats.user_id == user_id)
        
        if not stats:
            # Create initial stats
            stats = await DashboardService._calculate_initial_stats(user_id)
        else:
            # Update stats if needed
            await DashboardService._update_stats_if_needed(stats)
        
        return stats
    
    @staticmethod
    async def track_activity(
        user_id: str,
        activity_type: str,
        activity_data: Dict[str, Any],
        target_id: Optional[str] = None,
        target_type: Optional[str] = None,
        activity_score: int = 0
    ):
        """Track user activity"""
        
        # Create activity record
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            activity_data=activity_data,
            target_id=target_id,
            target_type=target_type,
            activity_score=activity_score
        )
        await activity.create()
        
        # Update user stats
        await DashboardService._update_user_stats(user_id, activity_type, activity_score)
        
        # Check for achievements
        user_stats = await UserStats.find_one(UserStats.user_id == user_id)
        if user_stats:
            await DashboardService._check_achievements(user_id, user_stats, activity_type)
    
    @staticmethod
    async def get_recommendations(
        user_id: str,
        recommendation_type: Optional[str] = None,
        limit: int = 10
    ) -> List[RecommendationResponse]:
        """Get personalized recommendations"""
        
        recommendations = []
        
        # Get user profile and interests
        user_profile = await UserProfile.find_one(UserProfile.user_id == user_id)
        if not user_profile:
            return recommendations
        
        # Content recommendations based on user interests
        if not recommendation_type or recommendation_type == "content":
            content_recs = await DashboardService._get_content_recommendations(
                user_id, user_profile, limit // 2
            )
            recommendations.extend(content_recs)
        
        # User recommendations based on similar interests
        if not recommendation_type or recommendation_type == "users":
            user_recs = await DashboardService._get_user_recommendations(
                user_id, user_profile, limit // 2
            )
            recommendations.extend(user_recs)
        
        # Use case recommendations
        if not recommendation_type or recommendation_type == "use_cases":
            use_case_recs = await DashboardService._get_use_case_recommendations(
                user_id, user_profile, limit // 2
            )
            recommendations.extend(use_case_recs)
        
        return recommendations[:limit]
    
    @staticmethod
    async def create_notification(
        user_id: str,
        notification_type: str,
        title: str,
        content: str,
        related_id: Optional[str] = None,
        related_type: Optional[str] = None,
        related_url: Optional[str] = None,
        actor_id: Optional[str] = None,
        priority: str = "normal",
        category: str = "general",
        data: Dict[str, Any] = None
    ):
        """Create notification for user"""
        
        # Get actor details if provided
        actor_name = None
        actor_avatar = None
        if actor_id:
            actor_profile = await UserProfile.find_one(UserProfile.user_id == actor_id)
            if actor_profile:
                actor_name = actor_profile.name
                actor_avatar = actor_profile.profile_picture_url
        
        # Create notification
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            content=content,
            related_id=related_id,
            related_type=related_type,
            related_url=related_url,
            actor_id=actor_id,
            actor_name=actor_name,
            actor_avatar=actor_avatar,
            priority=priority,
            category=category,
            data=data or {}
        )
        
        await notification.create()
        
        # Send real-time notification if user is online
        await DashboardService._send_realtime_notification(user_id, notification)
        
        logger.info(f"Notification created: {notification.id} for user {user_id}")
    
    @staticmethod
    async def _calculate_initial_stats(user_id: str) -> UserStats:
        """Calculate initial user statistics"""
        
        # Count posts
        posts_count = await ForumPost.count_documents({"author_id": user_id})
        
        # Count replies
        replies_count = await ForumReply.count_documents({"author_id": user_id})
        
        # Count use cases
        use_cases_count = await UseCase.count_documents({"author_id": user_id})
        
        # Count files shared
        files_count = await FileDocument.count_documents({"owner_id": user_id})
        
        # Count best answers
        best_answers_count = await ForumReply.count_documents({
            "author_id": user_id,
            "is_best_answer": True
        })
        
        # Calculate reputation from user profile
        user_profile = await UserProfile.find_one(UserProfile.user_id == user_id)
        reputation_score = user_profile.reputation_score if user_profile else 0
        
        # Create stats document
        stats = UserStats(
            user_id=user_id,
            posts_count=posts_count,
            replies_count=replies_count,
            use_cases_count=use_cases_count,
            files_shared_count=files_count,
            best_answers_count=best_answers_count,
            reputation_score=reputation_score,
            monthly_goals={
                "posts": 3,
                "use_cases": 1,
                "replies": 10
            }
        )
        
        await stats.create()
        return stats
    
    @staticmethod
    async def _get_content_recommendations(
        user_id: str,
        user_profile: UserProfile,
        limit: int
    ) -> List[RecommendationResponse]:
        """Get content recommendations based on user interests"""
        
        recommendations = []
        
        # Get posts in user's industry/interests
        relevant_posts = await ForumPost.find({
            "industry_sector": user_profile.industry_sector,
            "author_id": {"$ne": user_id},
            "status": "published"
        }).sort([("created_at", -1)]).limit(limit).to_list()
        
        for post in relevant_posts:
            recommendations.append(RecommendationResponse(
                type="forum_post",
                title=post.title,
                description=post.description[:200],
                url=f"/forum/posts/{post.id}",
                score=0.8,
                reason="Based on your industry sector"
            ))
        
        return recommendations
```

### 4. Frontend Dashboard Components

```typescript
// Dashboard.tsx
export default function Dashboard() {
  const { t } = useTranslation();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [widgets, setWidgets] = useState<Widget[]>([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/api/v1/dashboard');
      setDashboardData(response.data);
      setWidgets(response.data.widgets);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            {t('dashboard.welcome_back')}
          </h1>
          <p className="text-gray-600 mt-1">
            {t('dashboard.activity_summary')}
          </p>
        </div>

        {/* Quick Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title={t('dashboard.reputation')}
            value={dashboardData?.user_stats.reputation_score}
            icon={<Star className="h-6 w-6" />}
            change={+15}
            trend="up"
          />
          <StatsCard
            title={t('dashboard.contributions')}
            value={dashboardData?.user_stats.posts_count + dashboardData?.user_stats.replies_count}
            icon={<MessageSquare className="h-6 w-6" />}
            change={+3}
            trend="up"
          />
          <StatsCard
            title={t('dashboard.use_cases')}
            value={dashboardData?.user_stats.use_cases_count}
            icon={<FileText className="h-6 w-6" />}
            change={+1}
            trend="up"
          />
          <StatsCard
            title={t('dashboard.best_answers')}
            value={dashboardData?.user_stats.best_answers_count}
            icon={<Award className="h-6 w-6" />}
            change={+2}
            trend="up"
          />
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* Activity Feed */}
            <Card>
              <CardHeader>
                <CardTitle>{t('dashboard.recent_activity')}</CardTitle>
              </CardHeader>
              <CardContent>
                <ActivityFeed activities={dashboardData?.recent_activity || []} />
              </CardContent>
            </Card>

            {/* Progress Tracking */}
            <Card>
              <CardHeader>
                <CardTitle>{t('dashboard.monthly_goals')}</CardTitle>
              </CardHeader>
              <CardContent>
                <GoalsProgress 
                  goals={dashboardData?.user_stats.monthly_goals}
                  progress={dashboardData?.user_stats.monthly_progress}
                />
              </CardContent>
            </Card>

            {/* Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle>{t('dashboard.recommended_content')}</CardTitle>
              </CardHeader>
              <CardContent>
                <RecommendationsList recommendations={dashboardData?.recommendations || []} />
              </CardContent>
            </Card>
          </div>

          {/* Right Column */}
          <div className="space-y-8">
            {/* Notifications */}
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>{t('dashboard.notifications')}</CardTitle>
                  <Badge variant="secondary">
                    {dashboardData?.unread_notifications_count}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <NotificationsList 
                  notifications={dashboardData?.notifications || []}
                  onMarkRead={handleMarkNotificationRead}
                />
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>{t('dashboard.quick_actions')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button className="w-full" onClick={() => router.push('/forum/new-post')}>
                  <Plus className="h-4 w-4 mr-2" />
                  {t('dashboard.new_post')}
                </Button>
                <Button className="w-full" variant="outline" onClick={() => router.push('/use-cases/submit')}>
                  <FileText className="h-4 w-4 mr-2" />
                  {t('dashboard.submit_use_case')}
                </Button>
                <Button className="w-full" variant="outline" onClick={() => router.push('/files/upload')}>
                  <Upload className="h-4 w-4 mr-2" />
                  {t('dashboard.share_document')}
                </Button>
              </CardContent>
            </Card>

            {/* Community Ranking */}
            <Card>
              <CardHeader>
                <CardTitle>{t('dashboard.community_ranking')}</CardTitle>
              </CardHeader>
              <CardContent>
                <CommunityRanking 
                  currentRank={dashboardData?.user_stats.community_rank}
                  totalUsers={1000}
                />
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

// Supporting Components
function StatsCard({ title, value, icon, change, trend }) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-3xl font-bold">{value}</p>
          </div>
          <div className="text-blue-600">{icon}</div>
        </div>
        {change && (
          <div className={`flex items-center mt-2 text-sm ${
            trend === 'up' ? 'text-green-600' : 'text-red-600'
          }`}>
            {trend === 'up' ? (
              <TrendingUp className="h-4 w-4 mr-1" />
            ) : (
              <TrendingDown className="h-4 w-4 mr-1" />
            )}
            {Math.abs(change)} this month
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

## Implementation Steps

1. **Database Schema**
   - Create UserActivity, UserStats, DashboardWidget, and Notification models
   - Set up indexes for efficient dashboard queries
   - Implement activity tracking system

2. **Analytics Service**
   - Real-time activity tracking across all platform features
   - Statistical calculations and ranking algorithms
   - Achievement and goal tracking system

3. **Dashboard Backend**
   - Comprehensive dashboard API endpoints
   - Recommendation engine based on user behavior
   - Notification system with real-time updates

4. **Frontend Dashboard**
   - Responsive dashboard with customizable widgets
   - Real-time updates for notifications and activity
   - Mobile-optimized interface for key metrics

## Testing Checklist
- [ ] Dashboard loads quickly with accurate user statistics
- [ ] Activity tracking records all user actions correctly
- [ ] Notifications appear in real-time and mark as read properly
- [ ] Recommendations are relevant to user interests
- [ ] Goal tracking updates progress accurately
- [ ] Widget customization saves and persists correctly
- [ ] Mobile dashboard provides essential functionality
- [ ] Arabic/English content displays properly
- [ ] Performance is acceptable with large activity datasets

## Performance Considerations
- [ ] Efficient database queries for dashboard data aggregation
- [ ] Caching for frequently accessed user statistics
- [ ] Real-time notification optimization
- [ ] Lazy loading for activity feed pagination
- [ ] Background processing for recommendation calculations

## Dependencies
- All Epic 2 and Epic 3 stories for activity tracking
- Real-time notification infrastructure
- User analytics and behavior tracking
- Recommendation engine algorithms

## Notes
- Implement gamification elements to increase engagement
- Consider integration with external calendar systems
- Plan for A/B testing of dashboard layouts
- Design privacy controls for activity visibility
- Ensure scalable architecture for growing user base