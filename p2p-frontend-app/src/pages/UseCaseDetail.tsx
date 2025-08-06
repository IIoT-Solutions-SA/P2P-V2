import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { 
  ArrowLeft, 
  Factory, 
  MapPin, 
  Clock, 
  TrendingUp, 
  Download, 
  Share2,
  Bookmark,
  Loader2,
  Lightbulb,
  Target
} from "lucide-react";

// The DetailedUseCase interface should be defined here or imported
interface DetailedUseCase {
  id: string;
  title: string;
  subtitle: string;
  category: string;
  factory_name: string;
  implementation_time: string;
  roi_percentage: string;
  region: string;
  images: string[];
  executive_summary: string;
  business_challenge: {
    industry_context: string;
    specific_problems: string[];
  };
  // Add other fields as they exist in your detailed model
}

export default function UseCaseDetail() {
  const { slug } = useParams<{ slug: string }>(); // Get slug from URL
  const navigate = useNavigate(); // Hook for navigation

  const [useCase, setUseCase] = useState<DetailedUseCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUseCaseDetail = async () => {
      if (!slug) return;
      try {
        setLoading(true);
        setError(null);
        const response = await fetch(`http://localhost:8000/api/v1/use-cases/by-slug/${slug}`, {
          credentials: 'include'
        });
        if (!response.ok) {
          throw new Error(`Failed to fetch use case details.`);
        }
        const data = await response.json();
        setUseCase(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An unknown error occurred.");
      } finally {
        setLoading(false);
      }
    };

    fetchUseCaseDetail();
  }, [slug]);

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
            <h2 className="text-xl font-semibold text-red-600">{error ? "Error" : "Use Case Not Found"}</h2>
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
    <div className="min-h-screen bg-slate-50 font-sans">
      <div className="sticky top-0 bg-white/80 backdrop-blur-lg border-b border-slate-200 z-10">
        <div className="container mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <Button variant="ghost" onClick={() => navigate('/usecases')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Use Cases
          </Button>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm"><Bookmark className="h-4 w-4 mr-2" />Save</Button>
            <Button variant="outline" size="sm"><Share2 className="h-4 w-4 mr-2" />Share</Button>
            <Button><Download className="h-4 w-4 mr-2" />Download PDF</Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 sm:px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <header className="mb-8">
            <p className="text-blue-600 font-semibold mb-2">{useCase.category}</p>
            <h1 className="text-4xl font-bold text-slate-900 leading-tight">{useCase.title}</h1>
            <p className="text-xl text-slate-500 mt-3">{useCase.subtitle}</p>
            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div className="flex items-center space-x-2"><Factory className="h-5 w-5 text-slate-400" /><span>{useCase.factory_name}</span></div>
                <div className="flex items-center space-x-2"><MapPin className="h-5 w-5 text-slate-400" /><span>{useCase.region}</span></div>
                <div className="flex items-center space-x-2"><Clock className="h-5 w-5 text-slate-400" /><span>{useCase.implementation_time}</span></div>
                <div className="flex items-center space-x-2"><TrendingUp className="h-5 w-5 text-slate-400" /><span>{useCase.roi_percentage}</span></div>
            </div>
          </header>

          <section className="bg-white rounded-xl border border-slate-200 p-8 mb-8 shadow-sm">
            <h2 className="text-2xl font-bold text-slate-800 mb-4 flex items-center"><Lightbulb className="h-6 w-6 mr-3 text-blue-500" />Executive Summary</h2>
            <p className="text-slate-600 leading-relaxed">{useCase.executive_summary}</p>
          </section>

          <section className="bg-white rounded-xl border border-slate-200 p-8 mb-8 shadow-sm">
            <h2 className="text-2xl font-bold text-slate-800 mb-6 flex items-center"><Target className="h-6 w-6 mr-3 text-red-500" />Business Challenge</h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-slate-700 mb-2">Industry Context</h3>
                <p className="text-slate-600">{useCase.business_challenge.industry_context}</p>
              </div>
              <div>
                <h3 className="font-semibold text-slate-700 mb-2">Specific Problems</h3>
                <ul className="list-disc list-inside space-y-1 text-slate-600">
                  {useCase.business_challenge.specific_problems.map((problem, i) => <li key={i}>{problem}</li>)}
                </ul>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
