import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { 
  Search, 
  Filter, 
  Plus, 
  MessageSquare, 
  Users, 
  Clock, 
  Eye,
  ThumbsUp,
  Pin,
  CheckCircle,
  Zap,
  Tag,
  ArrowLeft,
  TrendingUp,
  Star,
  Send,
  Heart,
  Share2,
  Bookmark,
  MoreVertical
} from "lucide-react"
import { useAuth } from '@/contexts/AuthContext'

interface Category {
  id: string
  name: string
  count: number
  color: string
}

interface Comment {
  id: number
  author: string
  authorTitle: string
  content: string
  timeAgo: string
  likes: number
  isVerified: boolean
  replies?: Comment[]
}

interface ForumPost {
  id: number
  title: string
  author: string
  authorTitle: string
  category: string
  content?: string
  replies: number
  views: number
  likes: number
  timeAgo: string
  isPinned: boolean
  hasBestAnswer: boolean
  isVerified: boolean
  excerpt: string
  comments?: Comment[]
}

// Hardcoded forum posts removed - now using real API data

export default function Forum() {
  const { user } = useAuth()
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedPost, setSelectedPost] = useState<ForumPost | null>(null)
  const [newComment, setNewComment] = useState("")
  const [likedPosts, setLikedPosts] = useState<number[]>([])
  const [likedComments, setLikedComments] = useState<number[]>([])
  
  // Real data state
  const [categories, setCategories] = useState<Category[]>([])
  const [forumPosts, setForumPosts] = useState<ForumPost[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingPosts, setLoadingPosts] = useState(false)
  const [forumStats, setForumStats] = useState({
    total_topics: 0,
    active_members: 0,
    helpful_answers: 0
  })
  const [topContributors, setTopContributors] = useState<Array<{
    name: string
    points: number
    avatar: string
    rank: number
  }>>([])
  const [loadingContributors, setLoadingContributors] = useState(true)

  // Fetch categories on component mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/forum/categories', {
          credentials: 'include'
        })
        if (response.ok) {
          const data = await response.json()
          setCategories(data.categories || [])
        }
      } catch (error) {
        console.error('Error fetching categories:', error)
        // Fallback to empty array
        setCategories([])
      }
    }
    
    if (user) {
      fetchCategories()
    }
  }, [user])

  // Fetch posts when category changes
  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoadingPosts(true)
        const response = await fetch(`http://localhost:8000/api/v1/forum/posts?category=${selectedCategory}&limit=20`, {
          credentials: 'include'
        })
        if (response.ok) {
          const data = await response.json()
          setForumPosts(data.posts || [])
        }
      } catch (error) {
        console.error('Error fetching posts:', error)
        setForumPosts([])
      } finally {
        setLoadingPosts(false)
        setLoading(false)
      }
    }
    
    if (user) {
      fetchPosts()
    }
  }, [user, selectedCategory])

  // Fetch forum stats
  useEffect(() => {
    const fetchForumStats = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/forum/stats', {
          credentials: 'include'
        })
        if (response.ok) {
          const data = await response.json()
          setForumStats(data)
        }
      } catch (error) {
        console.error('Error fetching forum stats:', error)
      }
    }
    
    if (user) {
      fetchForumStats()
    }
  }, [user])

  // Fetch top contributors
  useEffect(() => {
    const fetchTopContributors = async () => {
      try {
        setLoadingContributors(true)
        const response = await fetch('http://localhost:8000/api/v1/forum/contributors?limit=3', {
          credentials: 'include'
        })
        if (response.ok) {
          const data = await response.json()
          setTopContributors(data.contributors || [])
        }
      } catch (error) {
        console.error('Error fetching top contributors:', error)
        setTopContributors([])
      } finally {
        setLoadingContributors(false)
      }
    }
    
    if (user) {
      fetchTopContributors()
    }
  }, [user])

  const filteredPosts = forumPosts.filter(post => {
    const matchesSearch = post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         post.excerpt.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesSearch
  })

  // Function to fetch full post details with comments
  const handlePostClick = async (postId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/forum/posts/${postId}`, {
        credentials: 'include'
      })
      if (response.ok) {
        const fullPost = await response.json()
        setSelectedPost(fullPost)
      } else {
        console.error('Failed to fetch post details')
      }
    } catch (error) {
      console.error('Error fetching post details:', error)
    }
  }

  const handleLikePost = async (postId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/forum/posts/${postId}/like`, {
        method: 'POST',
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        // Update the post in the state with new like count
        setForumPosts(posts => posts.map(post => 
          post.id === postId 
            ? { ...post, likes: data.likes }
            : post
        ))
        
        // Update liked posts for UI feedback
        if (likedPosts.includes(postId as any)) {
          setLikedPosts(likedPosts.filter(id => id !== postId as any))
        } else {
          setLikedPosts([...likedPosts, postId as any])
        }
      }
    } catch (error) {
      console.error('Error liking post:', error)
    }
  }

  const handleLikeComment = (commentId: number) => {
    if (likedComments.includes(commentId)) {
      setLikedComments(likedComments.filter(id => id !== commentId))
    } else {
      setLikedComments([...likedComments, commentId])
    }
  }

  const handlePostComment = () => {
    if (newComment.trim()) {
      // In a real app, this would submit to backend
      console.log('Posting comment:', newComment)
      setNewComment('')
    }
  }

  if (selectedPost) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          {/* Back Button */}
          <Button 
            variant="ghost" 
            className="mb-6"
            onClick={() => setSelectedPost(null)}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Forum
          </Button>

          {/* Post Detail */}
          <div className="bg-white rounded-2xl p-8 border border-slate-200 mb-6">
            {/* Post Header */}
            <div className="mb-6">
              <div className="flex items-center space-x-2 mb-4">
                {selectedPost.isPinned && (
                  <Pin className="h-4 w-4 text-blue-600" />
                )}
                {selectedPost.hasBestAnswer && (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                )}
                <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                  selectedPost.category === "Automation" ? "bg-blue-100 text-blue-700" :
                  selectedPost.category === "Maintenance" ? "bg-yellow-100 text-yellow-700" :
                  selectedPost.category === "Quality Management" ? "bg-green-100 text-green-700" :
                  selectedPost.category === "Artificial Intelligence" ? "bg-purple-100 text-purple-700" :
                  "bg-gray-100 text-gray-700"
                }`}>
                  <Tag className="h-3 w-3 mr-1 inline" />
                  {selectedPost.category}
                </span>
              </div>
              <h1 className="text-2xl font-bold text-slate-900 mb-4">{selectedPost.title}</h1>
              
              {/* Author Info */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-white">
                      {selectedPost.author.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <div className="flex items-center space-x-1">
                      <span className="font-semibold text-slate-900">{selectedPost.author}</span>
                      {selectedPost.isVerified && (
                        <CheckCircle className="h-4 w-4 text-blue-600" />
                      )}
                    </div>
                    <span className="text-sm text-slate-500">{selectedPost.authorTitle}</span>
                  </div>
                </div>
                <span className="text-sm text-slate-500">{selectedPost.timeAgo}</span>
              </div>
            </div>

            {/* Post Content */}
            <div className="prose prose-slate max-w-none mb-6">
              <div className="whitespace-pre-line text-slate-700">
                {selectedPost.content || selectedPost.excerpt}
              </div>
            </div>

            {/* Post Actions */}
            <div className="flex items-center justify-between pt-6 border-t border-slate-200">
              <div className="flex items-center space-x-4">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleLikePost(selectedPost.id)}
                  className={likedPosts.includes(selectedPost.id) ? "text-blue-600" : ""}
                >
                  <ThumbsUp className={`h-4 w-4 mr-2 ${likedPosts.includes(selectedPost.id) ? "fill-current" : ""}`} />
                  {selectedPost.likes + (likedPosts.includes(selectedPost.id) ? 1 : 0)}
                </Button>
                <Button variant="ghost" size="sm">
                  <Share2 className="h-4 w-4 mr-2" />
                  Share
                </Button>
                <Button variant="ghost" size="sm">
                  <Bookmark className="h-4 w-4 mr-2" />
                  Save
                </Button>
              </div>
              <div className="flex items-center space-x-4 text-sm text-slate-500">
                <span>{selectedPost.views} views</span>
                <span>{selectedPost.comments?.length || selectedPost.replies} comments</span>
              </div>
            </div>
          </div>

          {/* Comments Section */}
          <div className="bg-white rounded-2xl p-8 border border-slate-200">
            <h2 className="text-xl font-bold text-slate-900 mb-6">
              Comments ({selectedPost.comments?.length || selectedPost.replies})
            </h2>

            {/* Add Comment */}
            <div className="mb-8">
              <div className="flex space-x-3">
                <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-sm font-bold text-white">
                    {user?.firstName?.charAt(0) || 'U'}
                  </span>
                </div>
                <div className="flex-1">
                  <Textarea
                    placeholder="Add your comment..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    className="min-h-[100px] mb-3"
                  />
                  <Button 
                    onClick={handlePostComment}
                    disabled={!newComment.trim()}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    <Send className="h-4 w-4 mr-2" />
                    Post Comment
                  </Button>
                </div>
              </div>
            </div>

            {/* Comments List */}
            <div className="space-y-6">
              {selectedPost.comments?.map((comment) => (
                <div key={comment.id} className="border-b border-slate-200 pb-6 last:border-0">
                  <div className="flex space-x-3">
                    <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-sm font-bold text-white">
                        {comment.author.charAt(0)}
                      </span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <div className="flex items-center space-x-1">
                            <span className="font-semibold text-slate-900">{comment.author}</span>
                            {comment.isVerified && (
                              <CheckCircle className="h-4 w-4 text-blue-600" />
                            )}
                          </div>
                          <span className="text-sm text-slate-500">{comment.authorTitle}</span>
                        </div>
                        <span className="text-sm text-slate-500">{comment.timeAgo}</span>
                      </div>
                      <p className="text-slate-700 mb-3">{comment.content}</p>
                      <div className="flex items-center space-x-4">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleLikeComment(comment.id)}
                          className={`text-sm ${likedComments.includes(comment.id) ? "text-blue-600" : ""}`}
                        >
                          <ThumbsUp className={`h-3 w-3 mr-1 ${likedComments.includes(comment.id) ? "fill-current" : ""}`} />
                          {comment.likes + (likedComments.includes(comment.id) ? 1 : 0)}
                        </Button>
                        <Button variant="ghost" size="sm" className="text-sm">
                          Reply
                        </Button>
                      </div>

                      {/* Nested Replies */}
                      {comment.replies && comment.replies.length > 0 && (
                        <div className="mt-4 ml-8 space-y-4">
                          {comment.replies.map((reply) => (
                            <div key={reply.id} className="flex space-x-3">
                              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                                <span className="text-xs font-bold text-white">
                                  {reply.author.charAt(0)}
                                </span>
                              </div>
                              <div className="flex-1">
                                <div className="flex items-center justify-between mb-1">
                                  <div className="flex items-center space-x-1">
                                    <span className="font-semibold text-sm text-slate-900">{reply.author}</span>
                                    {reply.isVerified && (
                                      <CheckCircle className="h-3 w-3 text-blue-600" />
                                    )}
                                  </div>
                                  <span className="text-xs text-slate-500">{reply.timeAgo}</span>
                                </div>
                                <p className="text-sm text-slate-700 mb-2">{reply.content}</p>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleLikeComment(reply.id)}
                                  className={`text-xs ${likedComments.includes(reply.id) ? "text-blue-600" : ""}`}
                                >
                                  <ThumbsUp className={`h-3 w-3 mr-1 ${likedComments.includes(reply.id) ? "fill-current" : ""}`} />
                                  {reply.likes + (likedComments.includes(reply.id) ? 1 : 0)}
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading forum...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="space-y-6">
            {/* Categories */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <h3 className="font-bold text-slate-900 text-lg mb-4">Categories</h3>
              <div className="space-y-2">
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={`w-full p-3 rounded-lg transition-colors ${
                      selectedCategory === category.id
                        ? "bg-blue-600 text-white"
                        : "hover:bg-slate-50 text-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{category.name}</span>
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                        selectedCategory === category.id 
                          ? "bg-white/20 text-white" 
                          : "bg-slate-600 text-white"
                      }`}>
                        {category.count}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Forum Stats */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <h3 className="font-bold text-slate-900 text-lg mb-4">Forum Stats</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-600">Total Topics</p>
                    <p className="text-xl font-bold text-blue-600">{forumStats.total_topics}</p>
                  </div>
                  <div className="p-2 bg-blue-600 rounded-lg">
                    <MessageSquare className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-600">Active Members</p>
                    <p className="text-xl font-bold text-slate-600">{forumStats.active_members}</p>
                  </div>
                  <div className="p-2 bg-slate-600 rounded-lg">
                    <Users className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-600">Helpful Answers</p>
                    <p className="text-xl font-bold text-blue-500">{forumStats.helpful_answers}</p>
                  </div>
                  <div className="p-2 bg-blue-500 rounded-lg">
                    <CheckCircle className="h-6 w-6 text-white" />
                  </div>
                </div>
              </div>
            </div>

            {/* Top Contributors */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <h3 className="font-bold text-slate-900 text-lg mb-4">Top Contributors</h3>
              <div className="space-y-4">
                {loadingContributors ? (
                  <div className="text-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
                    <p className="text-sm text-slate-500">Loading contributors...</p>
                  </div>
                ) : topContributors.length > 0 ? (
                  topContributors.map((contributor, i) => (
                    <div key={i} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                          <span className="text-sm font-bold text-white">{contributor.avatar}</span>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-slate-900">{contributor.name}</p>
                          <p className="text-xs text-slate-500">{contributor.points} points</p>
                        </div>
                      </div>
                      <div className="px-3 py-1 bg-slate-600 text-white text-sm font-bold rounded-lg">
                        #{contributor.rank}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-4">
                    <p className="text-sm text-slate-500">No contributors yet</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Search and Filters */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <div className="flex items-center space-x-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search in forum..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-900"
                  />
                </div>
                <Button variant="outline" className="border-slate-300 text-slate-700 hover:bg-slate-50">
                  <Filter className="h-4 w-4 mr-2" />
                  Filter
                </Button>
              </div>
            </div>

            {/* Forum Posts */}
            <div className="space-y-4">
              {loadingPosts ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-slate-600">Loading posts...</p>
                </div>
              ) : filteredPosts.length > 0 ? (
                filteredPosts.map((post) => (
                <div key={post.id} className="bg-white rounded-2xl p-6 border border-slate-200 hover:shadow-md transition-all duration-300">
                    <div className="space-y-4">
                      {/* Post Header */}
                      <div className="flex items-start justify-between">
                        <div className="flex-1 space-y-2">
                          <div className="flex items-center space-x-2">
                            {post.isPinned && (
                              <Pin className="h-4 w-4 text-blue-600" />
                            )}
                            {post.hasBestAnswer && (
                              <CheckCircle className="h-4 w-4 text-blue-600" />
                            )}
                            <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                              post.category === "Automation" ? "bg-blue-600 text-white" :
                              post.category === "Maintenance" ? "bg-slate-600 text-white" :
                              post.category === "Quality Management" ? "bg-blue-500 text-white" :
                              post.category === "Artificial Intelligence" ? "bg-slate-700 text-white" :
                              "bg-slate-500 text-white"
                            }`}>
                              <Tag className="h-3 w-3 mr-1 inline" />
                              {post.category}
                            </span>
                          </div>
                          <h3 
                            className="text-lg font-semibold text-slate-900 hover:text-blue-600 cursor-pointer"
                            onClick={() => handlePostClick(post.id)}
                          >
                            {post.title}
                          </h3>
                          <p className="text-sm text-slate-600">{post.excerpt}</p>
                        </div>
                      </div>

                      {/* Post Footer */}
                      <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                        <div className="flex items-center space-x-6">
                          <div className="flex items-center space-x-1 text-sm text-slate-500">
                            <MessageSquare className="h-4 w-4" />
                            <span>{post.replies}</span>
                          </div>
                          <div className="flex items-center space-x-1 text-sm text-slate-500">
                            <Eye className="h-4 w-4" />
                            <span>{post.views}</span>
                          </div>
                          <button 
                            onClick={() => handleLikePost(post.id)}
                            className={`flex items-center space-x-1 text-sm transition-colors ${
                              likedPosts.includes(post.id) ? "text-blue-600" : "text-slate-500 hover:text-blue-600"
                            }`}
                          >
                            <ThumbsUp className={`h-4 w-4 ${likedPosts.includes(post.id) ? "fill-current" : ""}`} />
                            <span>{post.likes + (likedPosts.includes(post.id) ? 1 : 0)}</span>
                          </button>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                              <span className="text-xs font-bold text-white">
                                {post.author.charAt(0)}
                              </span>
                            </div>
                            <div>
                              <div className="flex items-center space-x-1">
                                <span className="text-sm font-semibold text-slate-900">{post.author}</span>
                                {post.isVerified && (
                                  <CheckCircle className="h-3 w-3 text-blue-600" />
                                )}
                              </div>
                              <span className="text-xs text-slate-500">{post.authorTitle}</span>
                            </div>
                          </div>
                          <div className="flex items-center space-x-1 text-xs text-slate-500">
                            <Clock className="h-3 w-3" />
                            <span>{post.timeAgo}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
              ))
              ) : (
                <div className="text-center py-12">
                  <MessageSquare className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                  <p className="text-slate-600 text-lg font-medium mb-2">No posts found</p>
                  <p className="text-slate-500">Try selecting a different category or start a new discussion!</p>
                </div>
              )}
            </div>

            {/* Load More */}
            <div className="text-center">
              <Button variant="outline" className="border-slate-300 text-slate-700 hover:bg-slate-50">
                Load More
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}