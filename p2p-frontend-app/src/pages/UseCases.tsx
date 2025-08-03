import { useState } from "react"
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
  Wrench
} from "lucide-react"

const categories = [
  { id: "all", name: "All Use Cases", count: 89, color: "bg-slate-600", icon: BookOpen },
  { id: "automation", name: "Factory Automation", count: 24, color: "bg-blue-600", icon: Cog },
  { id: "quality", name: "Quality Control", count: 18, color: "bg-blue-500", icon: CheckCircle },
  { id: "maintenance", name: "Predictive Maintenance", count: 16, color: "bg-slate-700", icon: Wrench },
  { id: "efficiency", name: "Process Optimization", count: 15, color: "bg-blue-700", icon: TrendingUp },
  { id: "innovation", name: "Innovation & R&D", count: 12, color: "bg-slate-500", icon: Lightbulb },
  { id: "sustainability", name: "Sustainability", count: 8, color: "bg-blue-400", icon: Building2 }
]

const useCases = [
  {
    id: 1,
    title: "AI-Powered Quality Inspection System Reduces Defects by 85%",
    company: "Advanced Manufacturing Co.",
    industry: "Electronics Manufacturing",
    category: "Quality Control",
    description: "Implementation of computer vision and machine learning for automated quality inspection, resulting in significant defect reduction and cost savings.",
    results: {
      defectReduction: "85%",
      costSavings: "$2.3M annually",
      efficiency: "40% faster inspection"
    },
    timeframe: "6 months implementation",
    views: 1247,
    likes: 89,
    saves: 156,
    verified: true,
    featured: true,
    tags: ["AI", "Computer Vision", "Quality Control", "Automation"],
    publishedBy: "Sarah Al-Mahmoud",
    publisherTitle: "Quality Engineering Director",
    publishedDate: "2 weeks ago"
  },
  {
    id: 2,
    title: "Predictive Maintenance Reduces Downtime by 60% in Plastic Factory",
    company: "Gulf Plastics Industries",
    industry: "Plastics Manufacturing", 
    category: "Predictive Maintenance",
    description: "IoT sensors and analytics implementation to predict equipment failures before they occur, dramatically reducing unplanned downtime.",
    results: {
      downtimeReduction: "60%",
      maintenanceSavings: "$1.8M annually",
      productivity: "25% increase"
    },
    timeframe: "4 months implementation",
    views: 892,
    likes: 67,
    saves: 124,
    verified: true,
    featured: false,
    tags: ["IoT", "Predictive Analytics", "Maintenance", "Sensors"],
    publishedBy: "Mohammed Al-Rashid",
    publisherTitle: "Operations Manager",
    publishedDate: "1 month ago"
  },
  {
    id: 3,
    title: "Energy Management System Cuts Factory Costs by 30%",
    company: "Saudi Steel Works",
    industry: "Steel Manufacturing",
    category: "Sustainability",
    description: "Smart energy monitoring and optimization system that automatically adjusts power consumption based on production schedules and energy pricing.",
    results: {
      energySavings: "30%",
      costReduction: "$950K annually",
      carbonReduction: "40% less emissions"
    },
    timeframe: "3 months implementation",
    views: 634,
    likes: 45,
    saves: 89,
    verified: true,
    featured: false,
    tags: ["Energy Management", "Sustainability", "Smart Systems", "Cost Reduction"],
    publishedBy: "Fatima Al-Zahra",
    publisherTitle: "Sustainability Director",
    publishedDate: "3 weeks ago"
  },
  {
    id: 4,
    title: "Automated Inventory Management Optimizes Supply Chain",
    company: "Arabian Food Processing",
    industry: "Food & Beverage",
    category: "Process Optimization",
    description: "RFID-based automated inventory tracking with demand forecasting to optimize stock levels and reduce waste.",
    results: {
      inventoryOptimization: "45%",
      wasteReduction: "35%",
      stockouts: "90% reduction"
    },
    timeframe: "5 months implementation",
    views: 456,
    likes: 32,
    saves: 67,
    verified: true,
    featured: false,
    tags: ["RFID", "Inventory Management", "Supply Chain", "Automation"],
    publishedBy: "Omar Al-Khalil",
    publisherTitle: "Supply Chain Manager",
    publishedDate: "1 week ago"
  }
]

export default function UseCases() {
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [searchQuery, setSearchQuery] = useState("")

  const filteredUseCases = useCases.filter(useCase => {
    const matchesCategory = selectedCategory === "all" || useCase.category === selectedCategory
    const matchesSearch = useCase.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         useCase.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         useCase.company.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

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
                  const IconComponent = category.icon
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
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-600">Total Use Cases</p>
                    <p className="text-xl font-bold text-blue-600">89</p>
                  </div>
                  <div className="p-2 bg-blue-600 rounded-lg">
                    <BookOpen className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-600">Contributing Companies</p>
                    <p className="text-xl font-bold text-slate-600">34</p>
                  </div>
                  <div className="p-2 bg-slate-600 rounded-lg">
                    <Building2 className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-600">Success Stories</p>
                    <p className="text-xl font-bold text-blue-500">67</p>
                  </div>
                  <div className="p-2 bg-blue-500 rounded-lg">
                    <Star className="h-6 w-6 text-white" />
                  </div>
                </div>
              </div>
            </div>

            {/* Top Contributing Companies */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <h3 className="font-bold text-slate-900 text-lg mb-4">Top Contributors</h3>
              <div className="space-y-4">
                {[
                  { name: "Advanced Manufacturing Co.", cases: 12, avatar: "A" },
                  { name: "Gulf Industries", cases: 8, avatar: "G" },
                  { name: "Saudi Steel Works", cases: 6, avatar: "S" }
                ].map((company, i) => (
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

            {/* Use Cases */}
            <div className="space-y-6">
              {filteredUseCases.map((useCase) => (
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
            </div>

            {/* Load More */}
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