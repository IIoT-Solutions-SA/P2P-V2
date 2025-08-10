import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
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
  Loader2,
  ArrowRight,
  Bookmark
} from "lucide-react";

// Interfaces remain the same
interface UseCase {
  id: string;
  title: string;
  title_slug: string; // This field is required
  company_slug: string;
  company: string;
  industry: string;
  category: string;
  description: string;
  results: { benefits: string; };
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
interface Category { id: string; name: string; count: number; }
interface Stats { totalUseCases: number; contributingCompanies: number; successStories: number; }
interface Contributor { name: string; cases: number; avatar: string; }

const categoryIcons: { [key: string]: React.ElementType } = {
  all: BookOpen, automation: Cog, quality: CheckCircle, maintenance: Wrench,
  efficiency: TrendingUp, innovation: Lightbulb, sustainability: Building2,
};

export default function UseCases() {
  const navigate = useNavigate(); // Hook for navigation

  // All state management remains the same
  const [categories, setCategories] = useState<Category[]>([]);
  const [useCases, setUseCases] = useState<UseCase[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [contributors, setContributors] = useState<Contributor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("newest");

  useEffect(() => {
    const fetchUseCasesData = async () => {
      try {
        setLoading(true);
        setError(null);
        const useCasesUrl = `http://localhost:8000/api/v1/use-cases?category=${selectedCategory}&search=${searchQuery}&sort_by=${sortBy}`;
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
      } finally {
        setLoading(false);
      }
    };
    fetchUseCasesData();
  }, [selectedCategory, searchQuery, sortBy]);

  const sortOptions = [
    { id: "newest", name: "Newest", icon: Clock },
    { id: "most_viewed", name: "Most Viewed", icon: TrendingUp },
    { id: "most_liked", name: "Most Liked", icon: ThumbsUp },
  ];

  const parseBenefits = (benefits: string) => {
    if (!benefits) return [];
    return benefits.split(';').map(benefit => {
        const parts = benefit.trim().split(' ');
        const value = parts[0];
        const label = parts.slice(1).join(' ');
        return { value, label };
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 font-sans">
      <div className="container mx-auto px-4 sm:px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <aside className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-100">
              <h3 className="font-bold text-slate-800 text-lg mb-4">Categories</h3>
              <div className="space-y-1">
                {categories.map((category) => {
                  const IconComponent = categoryIcons[category.id] || BookOpen;
                  return (
                    <button key={category.id} onClick={() => setSelectedCategory(category.id)} className={`w-full flex items-center justify-between p-3 rounded-lg transition-all duration-200 ${selectedCategory === category.id ? "bg-blue-600 text-white shadow-md" : "hover:bg-slate-100 text-slate-700"}`}>
                      <div className="flex items-center space-x-3"><IconComponent className="h-5 w-5" /><span className="text-sm font-semibold">{category.name}</span></div>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${selectedCategory === category.id ? "bg-white/20 text-white" : "bg-slate-200 text-slate-600"}`}>{category.count}</span>
                    </button>
                  )
                })}
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-100">
              <h3 className="font-bold text-slate-800 text-lg mb-4">Platform Stats</h3>
              <div className="space-y-4">
                {loading ? ( <Loader2 className="h-6 w-6 animate-spin text-blue-600" /> ) : stats && (
                  <>
                    <div className="flex items-center justify-between">
                      <div><p className="text-sm text-slate-500">Total Use Cases</p><p className="text-2xl font-bold text-blue-600">{stats.totalUseCases}</p></div>
                      <div className="p-3 bg-blue-100 rounded-lg"><BookOpen className="h-6 w-6 text-blue-600" /></div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div><p className="text-sm text-slate-500">Contributing Companies</p><p className="text-2xl font-bold text-slate-700">{stats.contributingCompanies}</p></div>
                      <div className="p-3 bg-slate-100 rounded-lg"><Building2 className="h-6 w-6 text-slate-600" /></div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div><p className="text-sm text-slate-500">Success Stories</p><p className="text-2xl font-bold text-amber-500">{stats.successStories}</p></div>
                      <div className="p-3 bg-amber-100 rounded-lg"><Star className="h-6 w-6 text-amber-500" /></div>
                    </div>
                  </>
                )}
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-100">
              <h3 className="font-bold text-slate-800 text-lg mb-4">Top Contributors</h3>
              <div className="space-y-4">
                {loading ? ( <Loader2 className="h-6 w-6 animate-spin text-blue-600" /> ) : contributors.map((company, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-slate-700 to-slate-900 rounded-full flex items-center justify-center"><span className="text-sm font-bold text-white">{company.avatar}</span></div>
                      <div><p className="text-sm font-semibold text-slate-800">{company.name}</p><p className="text-xs text-slate-500">{company.cases} use cases</p></div>
                    </div>
                    <div className="px-3 py-1 bg-slate-100 text-slate-600 text-sm font-bold rounded-lg">#{i + 1}</div>
                  </div>
                ))}
              </div>
            </div>
          </aside>
          <main className="lg:col-span-3 space-y-6">
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl shadow-lg p-8 text-white">
              <h1 className="text-4xl font-bold mb-2">Factory Success Stories</h1>
              <p className="text-slate-300 text-lg max-w-2xl">Discover proven implementations, learn from industry leaders, and find solutions that work.</p>
            </div>
            <div className="bg-white rounded-xl shadow-sm p-4 border border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex-1 w-full relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
                <input type="text" placeholder="Search use cases..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="w-full pl-12 pr-4 py-3 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
              <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-lg">
                {sortOptions.map((option) => (
                  <Button key={option.id} variant={sortBy === option.id ? "primary" : "ghost"} size="sm" onClick={() => setSortBy(option.id)} className={`rounded-md transition-all duration-200 ${sortBy === option.id ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-600'}`}>
                    <option.icon className="h-4 w-4 mr-2" />
                    {option.name}
                  </Button>
                ))}
              </div>
            </div>
            <div className="space-y-6">
              {loading && <div className="text-center p-10"><Loader2 className="h-8 w-8 mx-auto animate-spin text-blue-600" /></div>}
              {!loading && useCases.map((useCase) => (
                <div key={useCase.id} className="bg-white rounded-xl shadow-sm border border-slate-100 hover:shadow-lg hover:border-blue-200 transition-all duration-300 overflow-hidden cursor-pointer" onClick={() => navigate(`/usecases/${useCase.company_slug}/${useCase.title_slug}`)}>
                    <div className="p-6">
                        <div className="flex items-start justify-between">
                            <div className="flex-1 space-y-3">
                                <div className="flex items-center space-x-3">
                                    {useCase.featured && <span className="flex items-center text-xs font-semibold text-amber-600 bg-amber-100 px-2 py-1 rounded-full"><Star className="h-4 w-4 mr-1" /> Featured</span>}
                                    <span className="text-xs font-semibold text-blue-600 bg-blue-100 px-2 py-1 rounded-full">{useCase.category}</span>
                                </div>
                                <h3 className="text-xl font-bold text-slate-800">{useCase.title}</h3>
                                <div className="flex items-center flex-wrap gap-x-4 gap-y-1 text-sm text-slate-500">
                                    <span className="flex items-center"><Building2 className="h-4 w-4 mr-1.5 text-slate-400" />{useCase.company}</span>
                                    <span className="flex items-center"><Clock className="h-4 w-4 mr-1.5 text-slate-400" />{useCase.timeframe}</span>
                                </div>
                                <p className="text-slate-600 leading-relaxed pt-1" style={{wordBreak:'break-word', overflowWrap:'anywhere'}}>{useCase.description}</p>
                            </div>
                        </div>
                    </div>
                    <div className="bg-slate-50/70 px-6 py-4 border-t border-slate-100">
                        <h4 className="font-semibold text-slate-700 mb-3 text-sm">Key Results</h4>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                            {parseBenefits(useCase.results.benefits).map((stat, i) => (
                                <div key={i} className="bg-white p-3 rounded-lg border border-slate-200 text-center">
                                    <div className="text-2xl font-bold text-blue-600">{stat.value}</div>
                                    <div className="text-xs text-slate-500 capitalize">{stat.label}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className="flex items-center justify-between p-4">
                        <div className="flex items-center space-x-4 text-sm text-slate-500">
                            <span className="flex items-center" title="Views"><Eye className="h-4 w-4 mr-1.5" />{useCase.views}</span>
                            <span className="flex items-center" title="Likes"><ThumbsUp className="h-4 w-4 mr-1.5" />{useCase.likes}</span>
                            <span className="flex items-center" title="Saves"><Bookmark className="h-4 w-4 mr-1.5" />{useCase.saves}</span>
                        </div>
                        <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center"><span className="text-xs font-bold text-slate-600">{useCase.publishedBy.charAt(0)}</span></div>
                            <div>
                                <p className="text-sm font-semibold text-slate-800">{useCase.publishedBy}</p>
                                <p className="text-xs text-slate-500">{useCase.publisherTitle}</p>
                            </div>
                        </div>
                    </div>
                </div>
              ))}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
