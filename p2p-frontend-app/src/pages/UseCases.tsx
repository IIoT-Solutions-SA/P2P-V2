import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"

import { 
  Search, 
  Filter, 
  BookOpen, 
  Star,
  CheckCircle,
  Tag,
  TrendingUp,
  Building2,
  Cog,
  Lightbulb,
  Wrench,
  Eye,
  ThumbsUp,
  Clock,
  Loader2
} from "lucide-react"

// Define interfaces for the data we expect from the API
interface UseCase {
  id: string;
  title: string;
  company: string;
  industry: string;
  category: string;
  description: string;
  results: Record<string, string>;
  timeframe: string;
  views: number;
  likes: number;
  saves: number;
  verified: boolean;
  featured: boolean;
  tags: string[];
  publishedBy: string;
  publisherTitle: string;
  publishedDate: string;
}

interface Category {
  id: string;
  name: string;
  count: number;
}

interface Stats {
    totalUseCases: number;
    contributingCompanies: number;
    successStories: number;
}

interface Contributor {
    name: string;
    cases: number;
    avatar: string;
}

// Map category IDs to their respective icons
const categoryIcons: { [key: string]: React.ElementType } = {
  all: BookOpen,
  automation: Cog,
  quality: CheckCircle,
  maintenance: Wrench,
  efficiency: TrendingUp,
  innovation: Lightbulb,
  sustainability: Building2,
};

export default function UseCases() {
  // State for dynamic data
  const [categories, setCategories] = useState<Category[]>([]);
  const [useCases, setUseCases] = useState<UseCase[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [contributors, setContributors] = useState<Contributor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // State for filters
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  // NEW: State for sorting
  const [sortBy, setSortBy] = useState("newest");

  useEffect(() => {
    const fetchUseCasesData = async () => {
      try {
        setLoading(true);
        setError(null);

        // UPDATED: Construct the API URL with the new sort parameter
        const useCasesUrl = `http://localhost:8000/api/v1/use-cases?category=${selectedCategory}&search=${searchQuery}&sort_by=${sortBy}`;

        // Fetch all data in parallel using the full URL and credentials
        const [categoriesRes, useCasesRes, statsRes, contributorsRes] = await Promise.all([
          fetch('http://localhost:8000/api/v1/use-cases/categories', { credentials: 'include' }),
          fetch(useCasesUrl, { credentials: 'include' }),
          fetch('http://localhost:8000/api/v1/use-cases/stats', { credentials: 'include' }),
          fetch('http://localhost:8000/api/v1/use-cases/contributors', { credentials: 'include' })
        ]);

        if (!categoriesRes.ok || !useCasesRes.ok || !statsRes.ok || !contributorsRes.ok) {
            throw new Error('Failed to fetch data from the server.');
        }

        setCategories(await categoriesRes.json());
        setUseCases(await useCasesRes.json());
        setStats(await statsRes.json());
        setContributors(await contributorsRes.json());

      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred.');
        console.error("Failed to fetch use cases data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchUseCasesData();
  }, [selectedCategory, searchQuery, sortBy]); // Refetch data when filters change

  
  
  // This computed value will update automatically when `useCases` state changes.
  const filteredUseCases = useCases;

  const sortOptions = [
    { id: "newest", name: "Newest", icon: Clock },
    { id: "most_viewed", name: "Most Viewed", icon: TrendingUp },
    { id: "most_liked", name: "Most Liked", icon: ThumbsUp },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
          {/* Sidebar */}
          <div className="space-y-6">
            {/* Categories */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <h3 className="font-bold text-slate-900 text-lg mb-4">Categories</h3>
              <div className="space-y-2">
                {categories.map((category) => {
                  const IconComponent = categoryIcons[category.id] || BookOpen;
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
                })}
              </div>
            </div>

            {/* Use Case Stats */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <h3 className="font-bold text-slate-900 text-lg mb-4">Platform Stats</h3>
              <div className="space-y-4">
                {loading ? (
                    <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
                ) : stats && (
                  <>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-slate-600">Total Use Cases</p>
                        <p className="text-xl font-bold text-blue-600">{stats.totalUseCases}</p>
                      </div>
                      <div className="p-2 bg-blue-600 rounded-lg">
                        <BookOpen className="h-6 w-6 text-white" />
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-slate-600">Contributing Companies</p>
                        <p className="text-xl font-bold text-slate-600">{stats.contributingCompanies}</p>
                      </div>
                      <div className="p-2 bg-slate-600 rounded-lg">
                        <Building2 className="h-6 w-6 text-white" />
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-slate-600">Success Stories</p>
                        <p className="text-xl font-bold text-blue-500">{stats.successStories}</p>
                      </div>
                      <div className="p-2 bg-blue-500 rounded-lg">
                        <Star className="h-6 w-6 text-white" />
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Top Contributing Companies */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <h3 className="font-bold text-slate-900 text-lg mb-4">Top Contributors</h3>
              <div className="space-y-4">
                {loading ? (
                    <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
                ) : contributors.map((company, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                        <span className="text-sm font-bold text-white">{company.avatar}</span>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-slate-900">{company.name}</p>
                        <p className="text-xs text-slate-500">{company.cases} use cases</p>
                      </div>
                    </div>
                    <div className="px-3 py-1 bg-slate-600 text-white text-sm font-bold rounded-lg">
                      #{i + 1}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            <div className="bg-slate-800 rounded-2xl p-8 text-white">
              <div className="flex items-center space-x-3 mb-4">
                <BookOpen className="h-6 w-6 text-blue-400" />
                <span className="text-lg font-medium">Real-World Solutions</span>
              </div>
              <h1 className="text-3xl font-bold mb-3">Factory Success Stories & Use Cases</h1>
              <p className="text-slate-300 text-lg">Discover proven implementations, learn from industry leaders, and find solutions that work.</p>
            </div>

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
              {/* NEW: Sort By Options */}
          <div className="flex items-center space-x-2 bg-white p-2 rounded-xl border border-slate-200">
            <span className="text-sm font-semibold text-slate-600 px-2">Sort by:</span>
            {sortOptions.map((option) => (
              <Button
                key={option.id}
                variant={sortBy === option.id ? "default" : "ghost"}
                size="sm"
                onClick={() => setSortBy(option.id)}
                className="rounded-lg"
              >
                <option.icon className="h-4 w-4 mr-2" />
                {option.name}
              </Button>
            ))}
          </div>
            </div>

            {/* Use Cases List */}
            <div className="space-y-6">
              {loading && (
                <div className="text-center p-10">
                  <Loader2 className="h-8 w-8 mx-auto animate-spin text-blue-600" />
                  <p className="mt-2 text-slate-600">Loading Use Cases...</p>
                </div>
              )}
              {error && <p className="text-center text-red-600">{error}</p>}
              {!loading && !error && filteredUseCases.map((useCase) => (
                <div key={useCase.id} className="bg-white rounded-2xl p-6 border border-slate-200 hover:shadow-md transition-all duration-300">
                    <div className="space-y-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 space-y-3">
                          <div className="flex items-center space-x-2">
                            {useCase.featured && (
                              <Star className="h-4 w-4 text-blue-600 fill-current" />
                            )}
                            <span className={`text-xs px-3 py-1 rounded-full font-medium bg-blue-500 text-white`}>
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
                      <div className="flex flex-wrap gap-2">
                        {useCase.tags.map((tag, i) => (
                          <span key={i} className="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded-full">
                            {tag}
                          </span>
                        ))}
                      </div>
                      <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                        <div className="flex items-center space-x-6">
                          <div className="flex items-center space-x-1 text-sm text-slate-500">
                            <Eye className="h-4 w-4" />
                            <span>{useCase.views}</span>
                          </div>
                          <div className="flex items-center space-x-1 text-sm text-slate-500">
                            <ThumbsUp className="h-4 w-4" />
                            <span>{useCase.likes}</span>
                          </div>
                          <div className="flex items-center space-x-1 text-sm text-slate-500">
                            <BookOpen className="h-4 w-4" />
                            <span>{useCase.saves}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                              <span className="text-xs font-bold text-white">
                                {useCase.publishedBy.charAt(0)}
                              </span>
                            </div>
                            <div>
                              <div className="flex items-center space-x-1">
                                <span className="text-sm font-semibold text-slate-900">{useCase.publishedBy}</span>
                                {useCase.verified && (
                                  <CheckCircle className="h-3 w-3 text-blue-600" />
                                )}
                              </div>
                              <span className="text-xs text-slate-500">{useCase.publisherTitle}</span>
                            </div>
                          </div>
                          <div className="flex items-center space-x-1 text-xs text-slate-500">
                            <Clock className="h-3 w-3" />
                            <span>{useCase.publishedDate}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                </div>
              ))}
              {!loading && !error && filteredUseCases.length === 0 && (
                <div className="text-center p-10 bg-white rounded-2xl">
                    <p className="text-slate-600">No use cases found matching your criteria.</p>
                </div>
              )}
            </div>
            <div className="text-center">
              <Button variant="outline" className="border-slate-300 text-slate-700 hover:bg-slate-50">
                Load More Use Cases
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}