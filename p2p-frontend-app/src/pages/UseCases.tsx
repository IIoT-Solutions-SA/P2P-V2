import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { 
  Search, 
  Filter, 
  Plus, 
  BookOpen, 
  Users, 
  Clock, 
  Eye,
  ThumbsUp,
  Star,
  CheckCircle,
  Zap,
  Tag,
  ArrowLeft,
  TrendingUp,
  Building2,
  Cog,
  Lightbulb,
  BarChart3,
  Wrench,
  AlertCircle,
  Loader2
} from "lucide-react"
import { useCasesApi, UseCase, UseCaseCategory, UseCaseStats } from '@/services/useCasesApi'

// Icon mapping for categories
const categoryIcons: { [key: string]: any } = {
  'all': BookOpen,
  'Factory Automation': Cog,
  'Quality Control': CheckCircle,
  'Predictive Maintenance': Wrench,
  'Process Optimization': TrendingUp,
  'Innovation & R&D': Lightbulb,
  'Sustainability': Building2,
  'default': BookOpen
}

export default function UseCases() {
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [searchQuery, setSearchQuery] = useState("")
  const [useCases, setUseCases] = useState<UseCase[]>([])
  const [categories, setCategories] = useState<UseCaseCategory[]>([])
  const [stats, setStats] = useState<UseCaseStats | null>(null)
  const [topContributors, setTopContributors] = useState<Array<{ company: string; use_case_count: number; rank: number }>>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    fetchInitialData()
  }, [])

  useEffect(() => {
    fetchUseCases()
  }, [selectedCategory, searchQuery, currentPage])

  const fetchInitialData = async () => {
    try {
      const [categoriesData, statsData, contributorsData] = await Promise.all([
        useCasesApi.getCategories(),
        useCasesApi.getStats(),
        useCasesApi.getTopContributors(3)
      ])
      
      setCategories([{ id: "all", name: "All Use Cases", description: "", icon: "BookOpen", color: "bg-slate-600", count: statsData.total_use_cases }, ...categoriesData])
      setStats(statsData)
      setTopContributors(contributorsData)
    } catch (err) {
      console.error('Failed to fetch initial data:', err)
      setError('Failed to load use cases data')
    }
  }

  const fetchUseCases = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await useCasesApi.getUseCases({
        category: selectedCategory === "all" ? undefined : selectedCategory,
        search: searchQuery || undefined,
        page: currentPage,
        limit: 10
      })
      setUseCases(response.use_cases)
      setTotalPages(response.pages)
    } catch (err) {
      console.error('Failed to fetch use cases:', err)
      setError('Failed to load use cases')
    } finally {
      setIsLoading(false)
    }
  }

  const handleLikeUseCase = async (id: string) => {
    try {
      await useCasesApi.likeUseCase(id)
      // Update the use case likes count in the local state
      setUseCases(prev => prev.map(uc => 
        uc.id === id ? { ...uc, likes: uc.likes + 1 } : uc
      ))
    } catch (err) {
      console.error('Failed to like use case:', err)
    }
  }

  const handleSaveUseCase = async (id: string) => {
    try {
      await useCasesApi.saveUseCase(id)
      // Update the use case saves count in the local state
      setUseCases(prev => prev.map(uc => 
        uc.id === id ? { ...uc, saves: uc.saves + 1 } : uc
      ))
    } catch (err) {
      console.error('Failed to save use case:', err)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="space-y-6">
            {/* Categories */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <h3 className="font-bold text-slate-900 text-lg mb-4">Categories</h3>
              {categories.length > 0 ? (
                <div className="space-y-2">
                  {categories.map((category) => {
                    const IconComponent = categoryIcons[category.name] || categoryIcons.default
                    return (
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
                          <div className="flex items-center space-x-2">
                            <IconComponent className="h-4 w-4" />
                            <span className="text-sm font-medium">{category.name}</span>
                          </div>
                          <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                            selectedCategory === category.id 
                              ? "bg-white/20 text-white" 
                              : "bg-slate-600 text-white"
                          }`}>
                            {category.count}
                          </span>
                        </div>
                      </button>
                    )
                  })
                }
                </div>
              ) : (
                <div className="text-center text-slate-500 py-4">
                  <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
                  Loading categories...
                </div>
              )}
            </div>

            {/* Use Case Stats */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <h3 className="font-bold text-slate-900 text-lg mb-4">Platform Stats</h3>
              {stats ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-600">Total Use Cases</p>
                      <p className="text-xl font-bold text-blue-600">{stats.total_use_cases}</p>
                    </div>
                    <div className="p-2 bg-blue-600 rounded-lg">
                      <BookOpen className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-600">Contributing Companies</p>
                      <p className="text-xl font-bold text-slate-600">{stats.contributing_companies}</p>
                    </div>
                    <div className="p-2 bg-slate-600 rounded-lg">
                      <Building2 className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-slate-600">Success Stories</p>
                      <p className="text-xl font-bold text-blue-500">{stats.success_stories}</p>
                    </div>
                    <div className="p-2 bg-blue-500 rounded-lg">
                      <Star className="h-6 w-6 text-white" />
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-slate-500 py-4">
                  <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
                  Loading stats...
                </div>
              )}
            </div>

            {/* Top Contributing Companies */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <h3 className="font-bold text-slate-900 text-lg mb-4">Top Contributors</h3>
              {topContributors.length > 0 ? (
                <div className="space-y-4">
                  {topContributors.map((contributor) => (
                    <div key={contributor.rank} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                          <span className="text-sm font-bold text-white">{contributor.company.charAt(0)}</span>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-slate-900">{contributor.company}</p>
                          <p className="text-xs text-slate-500">{contributor.use_case_count} use cases</p>
                        </div>
                      </div>
                      <div className="px-3 py-1 bg-slate-600 text-white text-sm font-bold rounded-lg">
                        #{contributor.rank}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-slate-500 py-4">
                  <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
                  Loading contributors...
                </div>
              )}
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Header Section */}
            <div className="bg-slate-800 rounded-2xl p-8 text-white">
              <div className="flex items-center space-x-3 mb-4">
                <BookOpen className="h-6 w-6 text-blue-400" />
                <span className="text-lg font-medium">Real-World Solutions</span>
              </div>
              <h1 className="text-3xl font-bold mb-3">Factory Success Stories & Use Cases</h1>
              <p className="text-slate-300 text-lg">Discover proven implementations, learn from industry leaders, and find solutions that work.</p>
            </div>

            {/* Search and Filters */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <div className="flex items-center space-x-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search use cases, companies, or solutions..."
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

            {/* Error State */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <span className="text-red-800">{error}</span>
              </div>
            )}

            {/* Loading State */}
            {isLoading && (
              <div className="text-center py-8">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
                <p className="text-slate-600">Loading use cases...</p>
              </div>
            )}

            {/* Use Cases */}
            {!isLoading && useCases.length > 0 && (
              <div className="space-y-6">
                {useCases.map((useCase) => (
                  <div key={useCase.id} className="bg-white rounded-2xl p-6 border border-slate-200 hover:shadow-md transition-all duration-300">
                    <div className="space-y-4">
                      {/* Use Case Header */}
                      <div className="flex items-start justify-between">
                        <div className="flex-1 space-y-3">
                          <div className="flex items-center space-x-2">
                            {useCase.featured && (
                              <Star className="h-4 w-4 text-blue-600 fill-current" />
                            )}
                            <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                              useCase.category === "Quality Control" ? "bg-blue-500 text-white" :
                              useCase.category === "Predictive Maintenance" ? "bg-slate-700 text-white" :
                              useCase.category === "Sustainability" ? "bg-blue-400 text-white" :
                              useCase.category === "Process Optimization" ? "bg-blue-700 text-white" :
                              "bg-slate-600 text-white"
                            }`}>
                              <Tag className="h-3 w-3 mr-1 inline" />
                              {useCase.category}
                            </span>
                            {useCase.verified && (
                              <CheckCircle className="h-4 w-4 text-blue-600" />
                            )}
                          </div>
                          <h3 className="text-xl font-bold text-slate-900 hover:text-blue-600 cursor-pointer">
                            {useCase.title}
                          </h3>
                          <div className="flex items-center space-x-4 text-sm text-slate-600">
                            <span className="font-medium">{useCase.company}</span>
                            <span>•</span>
                            <span>{useCase.industry}</span>
                            <span>•</span>
                            <span>{useCase.timeframe}</span>
                          </div>
                          <p className="text-slate-600 leading-relaxed">{useCase.description}</p>
                        </div>
                      </div>

                      {/* Results Grid */}
                      <div className="bg-slate-50 rounded-xl p-4">
                        <h4 className="font-semibold text-slate-900 mb-3">Key Results</h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          {Object.entries(useCase.results).map(([key, value], i) => (
                            <div key={i} className="text-center">
                              <div className="text-2xl font-bold text-blue-600">{value}</div>
                              <div className="text-xs text-slate-600 capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Tags */}
                      <div className="flex flex-wrap gap-2">
                        {useCase.tags.map((tag, i) => (
                          <span key={i} className="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded-full">
                            {tag}
                          </span>
                        ))}
                      </div>

                      {/* Use Case Footer */}
                      <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                        <div className="flex items-center space-x-6">
                          <div className="flex items-center space-x-1 text-sm text-slate-500">
                            <Eye className="h-4 w-4" />
                            <span>{useCase.views}</span>
                          </div>
                          <button 
                            onClick={() => handleLikeUseCase(useCase.id)}
                            className="flex items-center space-x-1 text-sm text-slate-500 hover:text-blue-600 transition-colors"
                          >
                            <ThumbsUp className="h-4 w-4" />
                            <span>{useCase.likes}</span>
                          </button>
                          <button 
                            onClick={() => handleSaveUseCase(useCase.id)}
                            className="flex items-center space-x-1 text-sm text-slate-500 hover:text-blue-600 transition-colors"
                          >
                            <BookOpen className="h-4 w-4" />
                            <span>{useCase.saves}</span>
                          </button>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                              <span className="text-xs font-bold text-white">
                                {useCase.published_by.charAt(0)}
                              </span>
                            </div>
                            <div>
                              <div className="flex items-center space-x-1">
                                <span className="text-sm font-semibold text-slate-900">{useCase.published_by}</span>
                                {useCase.verified && (
                                  <CheckCircle className="h-3 w-3 text-blue-600" />
                                )}
                              </div>
                              <span className="text-xs text-slate-500">{useCase.publisher_title}</span>
                            </div>
                          </div>
                          <div className="flex items-center space-x-1 text-xs text-slate-500">
                            <Clock className="h-3 w-3" />
                            <span>{new Date(useCase.published_date).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* No Results */}
            {!isLoading && useCases.length === 0 && !error && (
              <div className="text-center py-8">
                <BookOpen className="h-12 w-12 mx-auto mb-4 text-slate-400" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">No use cases found</h3>
                <p className="text-slate-600">Try adjusting your search or category filters</p>
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center space-x-4">
                <Button 
                  variant="outline" 
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage(prev => prev - 1)}
                  className="border-slate-300 text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                >
                  Previous
                </Button>
                <span className="text-sm text-slate-600">
                  Page {currentPage} of {totalPages}
                </span>
                <Button 
                  variant="outline" 
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage(prev => prev + 1)}
                  className="border-slate-300 text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                >
                  Next
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}