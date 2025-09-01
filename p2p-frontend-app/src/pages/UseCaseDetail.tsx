import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { buildApiUrl } from '@/config/environment';
import { Button } from "@/components/ui/button";
import { DeleteConfirmModal } from "@/components/ui/DeleteConfirmModal";
import { 
  ArrowLeft, 
  Factory, 
  MapPin, 
  Calendar, 
  TrendingUp, 
  CheckCircle, 
  Users, 
  Download, 
  Share2,
  Bookmark,
  Eye,
  Clock,
  Award,
  BarChart3,
  Zap,
  Target,
  Wrench,
  Shield,
  Lightbulb,
  ImageIcon,
  Loader2,
  Edit,
  Trash2,
  MoreVertical
} from "lucide-react";
import { SaudiRiyalCurrency } from '@/components/SaudiRiyal';
import { useAuth } from '@/contexts/AuthContext';

// This interface matches the UseCase MongoDB model structure
interface DetailedUseCase {
  _id: string;
  title: string;
  submitted_by?: string;
  subtitle?: string;
  last_updated?: string;
  downloads?: number;
  status?: string;
  verified_by?: string;
  industry_tags?: string[];
  technology_tags?: string[];
  category?: string;
  factory_name?: string;
  implementation_time?: string;
  roi_percentage?: string;
  region?: string;
  location: { lat: number; lng: number };
  contact_person?: string;
  contact_title?: string;
  images: string[];
  executive_summary?: string;
  business_challenge?: {
    industry_context?: string;
    specific_problems?: string[];
    business_impact?: {
      financial_loss?: string;
      customer_impact?: string;
      operational_impact?: string;
      compliance_risk?: string;
    };
  };
  solution_details?: {
    selection_criteria?: string[];
    vendor_evaluation?: {
      process?: string;
      selected_vendor?: string;
      selection_reasons?: string[];
    };
    technology_components?: { component: string; details: string }[];
  };
  implementation_details?: {
    methodology?: string;
    total_budget?: string;
    total_duration?: string;
    project_team?: {
      internal?: { role: string; name: string; title: string }[];
      vendor?: { role: string; name: string; title: string }[];
    };
    phases?: { phase: string; duration: string; objectives: string[], keyActivities: string[], budget: string }[];
  };
  challenges_and_solutions: { challenge: string; description?: string; impact: string; solution: string; outcome: string }[];
  results?: {
    quantitative_metrics?: {
        metric: string;
        baseline: string;
        current: string;
        improvement: string;
    }[];
    qualitative_impacts?: string[];
    roi_analysis?: {
        total_investment?: string;
        annual_savings?: string;
        payback_period?: string;
        three_year_roi?: string;
    };
  };
  technical_architecture?: {
    system_overview?: string;
    components?: { layer: string; components: string[]; specifications: string }[];
    security_measures?: string[];
    scalability_design?: string[];
  };
  future_roadmap: { timeline: string; initiative: string; description: string; expected_benefit: string }[];
  lessons_learned: { category: string; lesson: string; description: string; recommendation: string }[];
  view_count: number;
  views: number;
  read_time?: string;
}

export default function UseCaseDetail() {
  const { company_slug, title_slug } = useParams<{ company_slug: string; title_slug: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [useCase, setUseCase] = useState<DetailedUseCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDropdown, setOpenDropdown] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);

  useEffect(() => {
    const fetchUseCaseDetail = async () => {
      if (!company_slug || !title_slug) return;
      try {
        setLoading(true);
        setError(null);
        const response = await fetch(buildApiUrl(`/api/v1/use-cases/${company_slug}/${title_slug}`), {
          credentials: 'include'
        });
        if (!response.ok) {
          throw new Error(`Failed to fetch use case details.`);
        }
        const data = await response.json();
        setUseCase(data);
        // Scroll to top when use case loads
        window.scrollTo(0, 0);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An unknown error occurred.");
      } finally {
        setLoading(false);
      }
    };
    fetchUseCaseDetail();
  }, [company_slug, title_slug]);

  const handleEditUseCase = () => {
    if (useCase) {
      // Navigate to submit page with edit parameter
      navigate(`/submit?edit=${useCase._id}`);
    }
  };

  const handleDeleteUseCase = () => {
    setDeleteModalOpen(true);
    setOpenDropdown(false);
  };

  const confirmDeleteUseCase = async () => {
    if (!useCase) return;

    try {
      const response = await fetch(buildApiUrl(`/api/v1/use-cases/${useCase._id}`), {
        method: 'DELETE',
        credentials: 'include'
      });

      if (response.ok) {
        // Show success message before navigation
        const successMessage = document.createElement('div');
        successMessage.innerHTML = `
          <div style="
            position: fixed; 
            top: 20px; 
            right: 20px; 
            background: #10B981; 
            color: white; 
            padding: 16px 20px; 
            border-radius: 8px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            font-weight: 500;
          ">
            ✅ Use case deleted successfully!
          </div>
        `;
        document.body.appendChild(successMessage);
        setTimeout(() => successMessage.remove(), 2000);
        
        // Navigate back to use cases list after brief delay
        setTimeout(() => navigate('/usecases'), 1500);
      } else {
        alert('❌ Failed to delete use case. Please try again.');
      }
    } catch (error) {
      console.error('Error deleting use case:', error);
      alert('❌ Network error. Please check your connection and try again.');
    }
  };

  const isUseCaseAuthor = (): boolean => {
    return !!(user && useCase && useCase.submitted_by && user.id === useCase.submitted_by);
  };

  // Handle clicking outside dropdown to close it
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (!target.closest('.relative')) {
        setOpenDropdown(false);
      }
    };

    if (openDropdown) {
      document.addEventListener('click', handleClickOutside);
    }

    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [openDropdown]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error || !useCase) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
            <h2 className="text-xl font-semibold text-red-600">{error ? "Error Loading Data" : "Use Case Not Found"}</h2>
            <p className="text-slate-600 mt-2">{error}</p>
            <Button onClick={() => navigate('/usecases')} className="mt-4">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Use Cases
            </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" style={{ wordBreak: 'break-word', overflowWrap: 'anywhere' }}>
      <div className="bg-white border-b border-gray-200 sticky top-0 z-20">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Button variant="ghost" onClick={() => navigate('/usecases')} className="flex items-center space-x-2 text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-4 w-4" />
            <span>Back to Use Cases</span>
          </Button>
          <div className="flex items-center space-x-3">
            <Button variant="outline" size="sm" className="flex items-center space-x-2"><Bookmark className="h-4 w-4" /><span className="hidden sm:block">Save</span></Button>
            <Button variant="outline" size="sm" className="flex items-center space-x-2"><Share2 className="h-4 w-4" /><span className="hidden sm:block">Share</span></Button>
            <Button variant="outline" size="sm" className="flex items-center space-x-2"><Download className="h-4 w-4" /><span className="hidden sm:block">Download PDF</span></Button>
            {isUseCaseAuthor() && (
              <div className="relative">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => setOpenDropdown(!openDropdown)}
                  className="flex items-center space-x-2"
                >
                  <MoreVertical className="h-4 w-4" />
                </Button>
                {openDropdown && (
                  <div className="absolute right-0 top-10 bg-white border-2 border-gray-200 rounded-xl shadow-xl z-10 min-w-[160px] overflow-hidden">
                    <button
                      onClick={() => {
                        handleEditUseCase();
                        setOpenDropdown(false);
                      }}
                      className="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-blue-50 flex items-center space-x-3 transition-colors group"
                    >
                      <div className="w-7 h-7 bg-blue-100 rounded-full flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                        <Edit className="h-4 w-4 text-blue-600" />
                      </div>
                      <span className="font-semibold">Edit Use Case</span>
                    </button>
                    <div className="h-px bg-gray-200 mx-2"></div>
                    <button
                      onClick={() => {
                        handleDeleteUseCase();
                        setOpenDropdown(false);
                      }}
                      className="w-full px-4 py-3 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-3 transition-colors group"
                    >
                      <div className="w-7 h-7 bg-red-100 rounded-full flex items-center justify-center group-hover:bg-red-200 transition-colors">
                        <Trash2 className="h-4 w-4 text-red-600" />
                      </div>
                      <span className="font-semibold">Delete Use Case</span>
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm mb-8 overflow-hidden">
            <div className="relative h-96 bg-gray-800">
              {useCase.images && useCase.images.length > 0 ? (
                <img src={useCase.images[0]} alt={useCase.title} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full bg-gradient-to-r from-blue-600 to-blue-800"></div>
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-blue-900/80 via-blue-800/50 to-transparent"></div>
              <div className="absolute top-0 left-0 right-0 p-8 text-white">
                <div className="max-w-7xl mx-auto">
                  {/* Metadata Section */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-x-6 gap-y-4 text-sm">
                    {useCase.status === 'verified' && (
                      <div className="flex items-center space-x-2 text-green-300">
                        <CheckCircle className="h-5 w-5" />
                        <span className="font-medium">Verified</span>
                      </div>
                    )}
                    {useCase.last_updated && (
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-5 w-5 text-gray-300" />
                        <span>{useCase.last_updated}</span>
                      </div>
                    )}
                    {useCase.read_time && (
                      <div className="flex items-center space-x-2">
                        <Clock className="h-5 w-5 text-gray-300" />
                        <span>{useCase.read_time}</span>
                      </div>
                    )}
                    {useCase.views !== undefined && (
                      <div className="flex items-center space-x-2">
                        <Eye className="h-5 w-5 text-gray-300" />
                        <span>{useCase.views.toLocaleString()} views</span>
                      </div>
                    )}
                    {useCase.downloads !== undefined && (
                      <div className="flex items-center space-x-2">
                        <Download className="h-5 w-5 text-gray-300" />
                        <span>{useCase.downloads.toLocaleString()} downloads</span>
                      </div>
                    )}
                  </div>
                  {useCase.verified_by && useCase.status === 'verified' && (
                    <div className="mt-4 flex items-center text-sm bg-green-200/90 text-green-900 p-3 rounded-lg max-w-2xl">
                      <Award className="h-5 w-5 mr-3 flex-shrink-0" />
                      <div>
                        <span className="font-semibold">Verified by:</span> {useCase.verified_by}
                      </div>
                    </div>
                  )}
                  {/* Tags Section */}
                  <div className="mt-4 flex flex-wrap gap-3 max-w-3xl" style={{wordBreak:'break-word'}}>
                    {useCase.industry_tags && useCase.industry_tags.map(tag => (
                      <span key={tag} className="bg-white/20 backdrop-blur-sm text-white text-xs font-medium px-3 py-1.5 rounded-lg flex items-center">
                        <Factory className="h-3.5 w-3.5 mr-1.5" /> {tag}
                      </span>
                    ))}
                    {useCase.technology_tags && useCase.technology_tags.map(tag => (
                      <span key={tag} className="bg-white/20 backdrop-blur-sm text-white text-xs font-medium px-3 py-1.5 rounded-lg flex items-center">
                        <Zap className="h-3.5 w-3.5 mr-1.5" /> {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              <div className="absolute bottom-0 left-0 right-0 p-8 text-white">
                <div className="max-w-7xl mx-auto">
                  <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl drop-shadow-lg">{useCase.title}</h1>
                  {useCase.subtitle && (
                    <p className="mt-3 text-xl text-blue-100 drop-shadow-md max-w-3xl">{useCase.subtitle}</p>
                  )}
                </div>
              </div>
            </div>
            <div className="p-8">
                 <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6" style={{wordBreak:'break-word'}}>
                {useCase.factory_name && (
                  <div className="flex items-center space-x-3"><Factory className="h-5 w-5 text-gray-500" /><div><p className="text-sm text-gray-500">Factory</p><p className="font-semibold text-gray-900">{useCase.factory_name}</p></div></div>
                )}
                {useCase.region && (
                  <div className="flex items-center space-x-3"><MapPin className="h-5 w-5 text-gray-500" /><div><p className="text-sm text-gray-500">Location</p><p className="font-semibold text-gray-900">{useCase.region}</p></div></div>
                )}
                {useCase.implementation_time && (
                  <div className="flex items-center space-x-3"><Clock className="h-5 w-5 text-gray-500" /><div><p className="text-sm text-gray-500">Implementation</p><p className="font-semibold text-gray-900">{useCase.implementation_time}</p></div></div>
                )}
                {useCase.roi_percentage && (
                  <div className="flex items-center space-x-3"><TrendingUp className="h-5 w-5 text-gray-500" /><div><p className="text-sm text-gray-500">ROI</p><p className="font-semibold text-gray-900">{useCase.roi_percentage}</p></div></div>
                )}
              </div>
              <div className="flex items-center justify-between pt-6 border-t border-gray-200">
                {useCase.contact_person && (
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-semibold text-sm">
                        {useCase.contact_person.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{useCase.contact_person}</p>
                      {useCase.contact_title && (
                        <p className="text-sm text-gray-500">{useCase.contact_title}</p>
                      )}
                    </div>
                  </div>
                )}
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  {useCase.read_time && (
                    <div className="flex items-center space-x-1"><Clock className="h-4 w-4" /><span>{useCase.read_time}</span></div>
                  )}
                  <div className="flex items-center space-x-1"><Eye className="h-4 w-4" /><span>{useCase.views || useCase.view_count || 0} views</span></div>
                </div>
              </div>
            </div>
          </div>

          {useCase.executive_summary && (
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center"><Lightbulb className="h-6 w-6 mr-3 text-blue-600" />Executive Summary</h2>
              <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-r-lg"><p className="text-lg text-gray-700 leading-relaxed">{useCase.executive_summary}</p></div>
            </div>
          )}

          {useCase.business_challenge && (
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center"><Target className="h-6 w-6 mr-3 text-red-600" />Business Challenge & Context</h2>
              <div className="space-y-6" style={{wordBreak:'break-word'}}>
                {useCase.business_challenge.industry_context && (
                  <div><h3 className="text-lg font-semibold text-gray-900 mb-3">Industry Context</h3><p className="text-gray-700 leading-relaxed">{useCase.business_challenge.industry_context}</p></div>
                )}
                {useCase.business_challenge.specific_problems && useCase.business_challenge.specific_problems.length > 0 && (
                  <div><h3 className="text-lg font-semibold text-gray-900 mb-3">Specific Problems</h3><div className="grid grid-cols-1 gap-3">{useCase.business_challenge.specific_problems.map((problem, index) => (<div key={index} className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg border border-red-200"><div className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div><p className="text-gray-700">{problem}</p></div>))}</div></div>
                )}
                {useCase.business_challenge.business_impact && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Business Impact</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {useCase.business_challenge.business_impact.financial_loss && (
                        <div className="p-4 bg-gray-50 rounded-lg">
                          <h4 className="font-medium text-gray-900 mb-2">Financial Loss</h4>
                          <p className="text-gray-700">{useCase.business_challenge.business_impact.financial_loss}</p>
                        </div>
                      )}
                      {useCase.business_challenge.business_impact.customer_impact && (
                        <div className="p-4 bg-gray-50 rounded-lg">
                          <h4 className="font-medium text-gray-900 mb-2">Customer Impact</h4>
                          <p className="text-gray-700">{useCase.business_challenge.business_impact.customer_impact}</p>
                        </div>
                      )}
                      {useCase.business_challenge.business_impact.operational_impact && (
                        <div className="p-4 bg-gray-50 rounded-lg">
                          <h4 className="font-medium text-gray-900 mb-2">Operational Impact</h4>
                          <p className="text-gray-700">{useCase.business_challenge.business_impact.operational_impact}</p>
                        </div>
                      )}
                      {useCase.business_challenge.business_impact.compliance_risk && (
                        <div className="p-4 bg-gray-50 rounded-lg">
                          <h4 className="font-medium text-gray-900 mb-2">Compliance Risk</h4>
                          <p className="text-gray-700">{useCase.business_challenge.business_impact.compliance_risk}</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {useCase.solution_details && (
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center"><Zap className="h-6 w-6 mr-3 text-yellow-600" />Solution Overview</h2>
              <div className="space-y-6">
                {useCase.solution_details.selection_criteria && useCase.solution_details.selection_criteria.length > 0 && (
                  <div><h3 className="text-lg font-semibold text-gray-900 mb-3">Selection Criteria</h3><div className="grid grid-cols-1 md:grid-cols-2 gap-3">{useCase.solution_details.selection_criteria.map((criteria, index) => (<div key={index} className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200"><CheckCircle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" /><p className="text-gray-700">{criteria}</p></div>))}</div></div>
                )}
                {useCase.solution_details.vendor_evaluation && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Vendor Evaluation</h3>
                    <div className="bg-gray-50 p-4 rounded-lg space-y-3" style={{wordBreak:'break-word'}}>
                      {useCase.solution_details.vendor_evaluation.process && (
                        <p className="text-gray-700"><span className="font-medium">Process:</span> {useCase.solution_details.vendor_evaluation.process}</p>
                      )}
                      {useCase.solution_details.vendor_evaluation.selected_vendor && (
                        <p className="text-gray-700"><span className="font-medium">Selected Vendor:</span> {useCase.solution_details.vendor_evaluation.selected_vendor}</p>
                      )}
                      {useCase.solution_details.vendor_evaluation.selection_reasons && useCase.solution_details.vendor_evaluation.selection_reasons.length > 0 && (
                        <div>
                          <span className="font-medium text-gray-900">Selection Reasons:</span>
                          <ul className="mt-2 space-y-1">
                            {useCase.solution_details.vendor_evaluation.selection_reasons.map((reason, index) => (
                              <li key={index} className="flex items-start space-x-2">
                                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                                <span className="text-gray-700">{reason}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                {useCase.solution_details.technology_components && useCase.solution_details.technology_components.length > 0 && (
                  <div><h3 className="text-lg font-semibold text-gray-900 mb-3">Technology Components</h3><div className="grid grid-cols-1 gap-4">{useCase.solution_details.technology_components.map((component, index) => (<div key={index} className="p-4 bg-blue-50 rounded-lg border border-blue-200"><h4 className="font-medium text-blue-900 mb-2">{component.component}</h4><p className="text-gray-700">{component.details}</p></div>))}</div></div>
                )}
              </div>
            </div>
          )}

          {useCase.implementation_details && (
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center"><Wrench className="h-6 w-6 mr-3 text-purple-600" />Implementation Journey</h2>
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {useCase.implementation_details.methodology && (
                    <div className="p-4 bg-purple-50 rounded-lg"><h3 className="font-semibold text-purple-900 mb-2">Methodology</h3><p className="text-gray-700">{useCase.implementation_details.methodology}</p></div>
                  )}
                  {(useCase.implementation_details.total_budget || useCase.implementation_details.total_duration) && (
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <h3 className="font-semibold text-purple-900 mb-2">Total Budget & Duration</h3>
                      <p className="text-gray-700">
                        {useCase.implementation_details.total_budget && <SaudiRiyalCurrency amount={useCase.implementation_details.total_budget} />}
                        {useCase.implementation_details.total_budget && useCase.implementation_details.total_duration && " over "}
                        {useCase.implementation_details.total_duration}
                      </p>
                    </div>
                  )}
                </div>
                
                {useCase.implementation_details.project_team && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Team</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {useCase.implementation_details.project_team.internal && useCase.implementation_details.project_team.internal.length > 0 && (
                        <div className="bg-blue-50 rounded-lg p-4">
                          <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
                            <Users className="h-4 w-4 mr-2" />
                            Internal Team
                          </h4>
                          <div className="space-y-3">
                            {useCase.implementation_details.project_team.internal.map((member, index) => (
                              <div key={index} className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-blue-200 rounded-full flex items-center justify-center">
                                  <span className="text-blue-700 font-semibold text-xs">
                                    {member.name.split(' ').map(n => n[0]).join('')}
                                  </span>
                                </div>
                                <div>
                                  <p className="font-medium text-gray-900 text-sm">{member.name}</p>
                                  <p className="text-xs text-gray-600">{member.title}</p>
                                  <p className="text-xs text-blue-700 font-medium">{member.role}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {useCase.implementation_details.project_team.vendor && useCase.implementation_details.project_team.vendor.length > 0 && (
                        <div className="bg-green-50 rounded-lg p-4">
                          <h4 className="font-semibold text-green-900 mb-3 flex items-center">
                            <Users className="h-4 w-4 mr-2" />
                            Vendor Team
                          </h4>
                          <div className="space-y-3">
                            {useCase.implementation_details.project_team.vendor.map((member, index) => (
                              <div key={index} className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-green-200 rounded-full flex items-center justify-center">
                                  <span className="text-green-700 font-semibold text-xs">
                                    {member.name.split(' ').map(n => n[0]).join('')}
                                  </span>
                                </div>
                                <div>
                                  <p className="font-medium text-gray-900 text-sm">{member.name}</p>
                                  <p className="text-xs text-gray-600">{member.title}</p>
                                  <p className="text-xs text-green-700 font-medium">{member.role}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                {useCase.implementation_details.phases && useCase.implementation_details.phases.length > 0 && (
                  <div><h3 className="text-lg font-semibold text-gray-900 mb-4">Implementation Phases</h3><div className="space-y-4">{useCase.implementation_details.phases.map((phase, index) => (<div key={index} className="border border-gray-200 rounded-lg p-4"><div className="flex items-center justify-between mb-3"><h4 className="font-semibold text-gray-900">{phase.phase}</h4><div className="flex items-center space-x-4 text-sm text-gray-600">{phase.duration && <span className="bg-blue-100 px-2 py-1 rounded">{phase.duration}</span>}{phase.budget && <span className="bg-green-100 px-2 py-1 rounded"><SaudiRiyalCurrency amount={phase.budget.replace(/[^\d,]/g, '')} /></span>}</div></div><div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">{phase.objectives && phase.objectives.length > 0 && <div><h5 className="font-medium text-gray-800 mb-1">Objectives:</h5><ul className="space-y-1">{phase.objectives.map((obj, i) => (<li key={i} className="flex items-start space-x-1"><div className="w-1 h-1 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div><span className="text-gray-600">{obj}</span></li>))}</ul></div>}{phase.keyActivities && phase.keyActivities.length > 0 && <div><h5 className="font-medium text-gray-800 mb-1">Key Activities:</h5><ul className="space-y-1">{phase.keyActivities.map((activity, i) => (<li key={i} className="flex items-start space-x-1"><div className="w-1 h-1 bg-purple-500 rounded-full mt-2 flex-shrink-0"></div><span className="text-gray-600">{activity}</span></li>))}</ul></div>}</div></div>))}</div></div>
                )}
              </div>
            </div>
          )}
          
          {/* Images Gallery */}
          {useCase.images && useCase.images.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <ImageIcon className="h-6 w-6 mr-3 text-purple-600" />
                Implementation Gallery
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {useCase.images.map((image, index) => (
                  <div key={index} className="group relative overflow-hidden rounded-xl border border-gray-200">
                    <img 
                      src={image} 
                      alt={`${useCase.title} - Image ${index + 1}`}
                      className="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300 flex items-center justify-center">
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                          <Eye className="h-5 w-5 text-gray-600" />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {useCase.challenges_and_solutions && useCase.challenges_and_solutions.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center"><Shield className="h-6 w-6 mr-3 text-orange-600" />Challenges & Solutions</h2>
              <div className="space-y-6">{useCase.challenges_and_solutions.map((item, index) => (<div key={index} className="border border-orange-200 rounded-lg p-6 bg-orange-50"><h3 className="text-lg font-semibold text-orange-900 mb-3">{item.challenge}</h3><div className="grid grid-cols-1 md:grid-cols-2 gap-4"><div>{item.description && <><h4 className="font-medium text-gray-900 mb-2">Challenge Description</h4><p className="text-gray-700 text-sm mb-3">{item.description}</p></>}<h4 className="font-medium text-gray-900 mb-2">Impact</h4><p className="text-red-600 text-sm">{item.impact}</p></div><div><h4 className="font-medium text-gray-900 mb-2">Solution</h4><p className="text-gray-700 text-sm mb-3">{item.solution}</p><h4 className="font-medium text-gray-900 mb-2">Outcome</h4><p className="text-green-600 text-sm">{item.outcome}</p></div></div></div>))}</div>
            </div>
          )}

          {useCase.results && (
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center"><BarChart3 className="h-6 w-6 mr-3 text-green-600" />Results & Impact Analysis</h2>
              <div className="space-y-8">
                {useCase.results.quantitative_metrics && useCase.results.quantitative_metrics.length > 0 && (
                  <div><h3 className="text-lg font-semibold text-gray-900 mb-4">Quantitative Metrics</h3><div className="grid grid-cols-1 md:grid-cols-2 gap-6">{useCase.results.quantitative_metrics.map((metric, index) => (<div key={index} className="p-4 bg-green-50 rounded-lg border border-green-200"><h4 className="font-semibold text-green-900 mb-2">{metric.metric}</h4><div className="space-y-2 text-sm"><div className="flex justify-between"><span className="text-gray-600">Baseline:</span><span className="font-medium text-gray-900">{metric.baseline}</span></div><div className="flex justify-between"><span className="text-gray-600">Current:</span><span className="font-medium text-gray-900">{metric.current}</span></div><div className="flex justify-between"><span className="text-gray-600">Improvement:</span><span className="font-bold text-green-600">{metric.improvement}</span></div></div></div>))}</div></div>
                )}
                
                {useCase.results.roi_analysis && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">ROI Analysis</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {useCase.results.roi_analysis.total_investment && (
                        <div className="p-4 bg-blue-50 rounded-lg text-center">
                          <div className="text-2xl font-bold text-blue-600"><SaudiRiyalCurrency amount={useCase.results.roi_analysis.total_investment} /></div>
                          <div className="text-sm text-gray-600">Total Investment</div>
                        </div>
                      )}
                      {useCase.results.roi_analysis.annual_savings && (
                        <div className="p-4 bg-green-50 rounded-lg text-center">
                          <div className="text-2xl font-bold text-green-600"><SaudiRiyalCurrency amount={useCase.results.roi_analysis.annual_savings} /></div>
                          <div className="text-sm text-gray-600">Annual Savings</div>
                        </div>
                      )}
                      {useCase.results.roi_analysis.three_year_roi && (
                        <div className="p-4 bg-purple-50 rounded-lg text-center">
                          <div className="text-2xl font-bold text-purple-600">{useCase.results.roi_analysis.three_year_roi}</div>
                          <div className="text-sm text-gray-600">3-Year ROI</div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                {useCase.results.qualitative_impacts && useCase.results.qualitative_impacts.length > 0 && (
                  <div><h3 className="text-lg font-semibold text-gray-900 mb-4">Qualitative Impacts</h3><div className="grid grid-cols-1 md:grid-cols-2 gap-3">{useCase.results.qualitative_impacts.map((impact, index) => (<div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg"><CheckCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" /><p className="text-gray-700">{impact}</p></div>))}</div></div>
                )}
              </div>
            </div>
          )}

          {/* Location & Implementation Details */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <MapPin className="h-6 w-6 mr-3 text-blue-600" />
              Implementation Details
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Location Information</h3>
                <div className="space-y-3">
                  {useCase.factory_name && (
                    <div className="flex items-center space-x-3">
                      <Factory className="h-5 w-5 text-gray-500" />
                      <div>
                        <p className="text-sm text-gray-500">Factory</p>
                        <p className="font-medium text-gray-900">{useCase.factory_name}</p>
                      </div>
                    </div>
                  )}
                  {useCase.region && (
                    <div className="flex items-center space-x-3">
                      <MapPin className="h-5 w-5 text-gray-500" />
                      <div>
                        <p className="text-sm text-gray-500">Region</p>
                        <p className="font-medium text-gray-900">{useCase.region}</p>
                      </div>
                    </div>
                  )}
                  {useCase.location && (
                    <div className="flex items-center space-x-3">
                      <div className="w-5 h-5 flex items-center justify-center">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Coordinates</p>
                        <p className="font-medium text-gray-900 font-mono text-sm">
                          {useCase.location.lat?.toFixed(4)}, {useCase.location.lng?.toFixed(4)}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Timeline</h3>
                <div className="space-y-3">
                  {useCase.implementation_time && (
                    <div className="flex items-center space-x-3">
                      <Clock className="h-5 w-5 text-gray-500" />
                      <div>
                        <p className="text-sm text-gray-500">Implementation Time</p>
                        <p className="font-medium text-gray-900">{useCase.implementation_time}</p>
                      </div>
                    </div>
                  )}
                  {useCase.roi_percentage && (
                    <div className="flex items-center space-x-3">
                      <TrendingUp className="h-5 w-5 text-gray-500" />
                      <div>
                        <p className="text-sm text-gray-500">Return on Investment</p>
                        <p className="font-medium text-gray-900">{useCase.roi_percentage}</p>
                      </div>
                    </div>
                  )}
                  {useCase.category && (
                    <div className="flex items-center space-x-3">
                      <Calendar className="h-5 w-5 text-gray-500" />
                      <div>
                        <p className="text-sm text-gray-500">Category</p>
                        <p className="font-medium text-gray-900">{useCase.category}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Technical Architecture */}
          {useCase.technical_architecture && (
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <Wrench className="h-6 w-6 mr-3 text-gray-600" />
                Technical Architecture
              </h2>
              
              <div className="space-y-6">
                {useCase.technical_architecture.system_overview && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">System Overview</h3>
                    <p className="text-gray-700 p-4 bg-gray-50 rounded-lg">{useCase.technical_architecture.system_overview}</p>
                  </div>
                )}
                
                {useCase.technical_architecture.components && useCase.technical_architecture.components.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Architecture Components</h3>
                    <div className="space-y-4">
                      {useCase.technical_architecture.components.map((component, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4">
                          <h4 className="font-semibold text-gray-900 mb-2">{component.layer}</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="font-medium text-gray-800">Components:</span>
                              <ul className="mt-1 space-y-1">
                                {component.components.map((comp, i) => (
                                  <li key={i} className="flex items-start space-x-1">
                                    <div className="w-1 h-1 bg-gray-500 rounded-full mt-2 flex-shrink-0"></div>
                                    <span className="text-gray-600">{comp}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                            <div>
                              <span className="font-medium text-gray-800">Specifications:</span>
                              <p className="text-gray-600 mt-1">{component.specifications}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {useCase.technical_architecture.security_measures && useCase.technical_architecture.security_measures.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Security Measures</h3>
                      <div className="space-y-2">
                        {useCase.technical_architecture.security_measures.map((measure, index) => (
                          <div key={index} className="flex items-start space-x-3 p-2 bg-red-50 rounded">
                            <Shield className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-700 text-sm">{measure}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {useCase.technical_architecture.scalability_design && useCase.technical_architecture.scalability_design.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Scalability Design</h3>
                      <div className="space-y-2">
                        {useCase.technical_architecture.scalability_design.map((design, index) => (
                          <div key={index} className="flex items-start space-x-3 p-2 bg-blue-50 rounded">
                            <TrendingUp className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-700 text-sm">{design}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            {useCase.future_roadmap && useCase.future_roadmap.length > 0 && (
              <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center"><Calendar className="h-6 w-6 mr-3 text-purple-600" />Future Roadmap</h2>
                <div className="space-y-4">{useCase.future_roadmap.map((item, index) => (<div key={index} className="border-l-4 border-purple-500 pl-4 py-2"><div className="flex items-center space-x-2 mb-1"><span className="text-sm font-medium text-purple-600 bg-purple-100 px-2 py-1 rounded">{item.timeline}</span></div><h4 className="font-semibold text-gray-900 mb-1">{item.initiative}</h4><p className="text-gray-600 text-sm mb-1">{item.description}</p><p className="text-purple-600 text-sm font-medium">{item.expected_benefit}</p></div>))}</div>
              </div>
            )}
            {useCase.lessons_learned && useCase.lessons_learned.length > 0 && (
              <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center"><Lightbulb className="h-6 w-6 mr-3 text-yellow-600" />Lessons Learned</h2>
                <div className="space-y-4">{useCase.lessons_learned.map((lesson, index) => (<div key={index} className="border border-gray-200 rounded-lg p-4"><div className="flex items-center space-x-2 mb-2"><span className="text-xs font-medium text-gray-600 bg-gray-100 px-2 py-1 rounded">{lesson.category}</span></div><h4 className="font-semibold text-gray-900 mb-2">{lesson.lesson}</h4><p className="text-gray-600 text-sm mb-2">{lesson.description}</p><div className="bg-yellow-50 p-3 rounded border-l-4 border-yellow-400"><p className="text-yellow-800 text-sm font-medium">Recommendation: {lesson.recommendation}</p></div></div>))}</div>
              </div>
            )}
          </div>

          {/* Contact & Follow-up */}
          {useCase.contact_person && (
            <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl p-8 text-white">
              <h2 className="text-2xl font-bold mb-4">Interested in Similar Implementation?</h2>
              <p className="text-blue-100 mb-6">
                Connect with {useCase.contact_person} {useCase.contact_title && `(${useCase.contact_title})`} {useCase.factory_name && `at ${useCase.factory_name}`} to learn more about this implementation 
                or discuss how similar solutions could benefit your operations.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button variant="secondary" className="flex items-center space-x-2">
                  <Users className="h-4 w-4" />
                  <span>Contact {useCase.contact_person}</span>
                </Button>
                {useCase.factory_name && (
                  <Button variant="outline" className="flex items-center space-x-2 text-white border-white hover:bg-white hover:text-blue-600">
                    <Factory className="h-4 w-4" />
                    <span>Visit Factory</span>
                  </Button>
                )}
                <Button variant="outline" className="flex items-center space-x-2 text-white border-white hover:bg-white hover:text-blue-600">
                  <Share2 className="h-4 w-4" />
                  <span>Share Case Study</span>
                </Button>
              </div>
            </div>
          )}

        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <DeleteConfirmModal
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        onConfirm={confirmDeleteUseCase}
        title="Delete Use Case?"
        message="Are you sure you want to delete this use case? This action cannot be undone and the use case will be permanently removed from the platform."
        itemName={useCase?.title}
      />
    </div>
  )
}
