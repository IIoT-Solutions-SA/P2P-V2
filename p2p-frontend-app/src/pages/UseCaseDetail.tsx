import React from 'react'
import { Button } from "@/components/ui/button"
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
  DollarSign,
  Wrench,
  Shield,
  Lightbulb,
  Image as ImageIcon
} from "lucide-react"
import SaudiRiyal, { SaudiRiyalCurrency, SaudiRiyalFallback } from '@/components/SaudiRiyal'

interface UseCaseDetailProps {
  useCaseId?: number
  onBack?: () => void
}

// Comprehensive use case data structure - enhanced for detailed white paper
const sampleUseCase = {
  // Basic Information
  id: 1,
  title: "AI Quality Inspection System Reduces Defects by 85%",
  subtitle: "Transforming PCB Manufacturing Through Computer Vision and Machine Learning",
  description: "Computer vision system reduces defects by 85% in electronics manufacturing. Our factory implemented an advanced AI-powered quality inspection system that uses machine learning algorithms to detect microscopic defects in PCB manufacturing, resulting in significant improvements in product quality and customer satisfaction.",
  category: "Quality Control",
  factoryName: "Advanced Electronics Co.",
  implementationTime: "6 months implementation",
  roiPercentage: "250% ROI in first year",
  
  // Location Information
  city: "Riyadh",
  latitude: 24.7136,
  longitude: 46.6753,
  
  // Contact Information
  contactPerson: "Ahmed Al-Faisal",
  contactTitle: "Operations Manager",
  
  // Images
  images: [
    "https://images.unsplash.com/photo-1565043666747-69f6646db940?w=800&h=400&fit=crop",
    "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&h=400&fit=crop",
    "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=400&fit=crop",
    "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=800&h=400&fit=crop"
  ],
  
  // Executive Summary
  executiveSummary: "Advanced Electronics Co. faced critical quality control challenges with a 15% defect rate in PCB manufacturing, resulting in 450K annual losses and declining customer satisfaction. The implementation of an AI-powered computer vision quality inspection system achieved an 85% reduction in defects, 2.3M in annual cost savings, and 250% ROI in the first year. This case study details the 6-month implementation journey, technical architecture, challenges overcome, and lessons learned.",
  
  // Business Challenge & Context
  businessChallenge: {
    industryContext: "The electronics manufacturing industry faces increasing pressure for zero-defect production due to complex PCB designs, miniaturization trends, and stringent quality requirements from automotive and aerospace sectors.",
    specificProblems: [
      "Manual inspection inconsistency across shifts with 15% defect rate",
      "Microscopic defects undetectable by human inspectors causing field failures",
      "Production bottlenecks with 40% inspection time overhead",
      "High customer return rates (12%) damaging brand reputation",
      "Inability to meet ISO 9001 and automotive IATF 16949 standards"
    ],
    businessImpact: {
      financialLoss: "450K annually in waste, rework, and returns",
      customerImpact: "12% return rate, declining satisfaction scores",
      operationalImpact: "40% slower production, inconsistent quality",
      complianceRisk: "Risk of losing automotive certification"
    },
    strategicDrivers: [
      "Pressure from automotive clients for zero-defect delivery",
      "Need to scale production while maintaining quality",
      "Regulatory compliance requirements",
      "Competitive advantage through quality leadership"
    ]
  },
  
  // Solution Overview
  solution: {
    selectionCriteria: [
      "Real-time processing capability (>50 units/minute)",
      "99%+ accuracy for defect detection",
      "Integration with existing production line",
      "Scalability across multiple product lines",
      "ROI achievement within 18 months"
    ],
    vendorEvaluation: {
      process: "6-month vendor evaluation process including PoC testing",
      vendorsConsidered: ["VisionTech Systems", "InspectAI Solutions", "QualityVision Pro"],
      selectedVendor: "VisionTech Systems",
      selectionReasons: [
        "Superior accuracy in PoC testing (99.7% vs 97.2% average)",
        "Proven experience in electronics manufacturing",
        "Comprehensive support and training program",
        "Flexible licensing model",
        "Strong reference customers"
      ]
    },
    technologyComponents: [
      {
        component: "Hardware Platform",
        details: "4x 4K industrial cameras with specialized LED lighting systems and conveyor integration"
      },
      {
        component: "AI/ML Engine",
        details: "Custom-trained convolutional neural networks using TensorFlow framework with 50,000+ labeled images"
      },
      {
        component: "Edge Computing",
        details: "NVIDIA Jetson AGX Xavier units for real-time processing with <100ms latency"
      },
      {
        component: "Integration Layer",
        details: "RESTful APIs connecting to existing MES and ERP systems for seamless data flow"
      }
    ]
  },
  
  // Implementation Journey
  implementation: {
    methodology: "Agile implementation with weekly sprints and continuous stakeholder feedback",
    projectTeam: {
      internal: [
        { role: "Project Sponsor", name: "Sarah Al-Mahmoud", title: "Plant Manager" },
        { role: "Technical Lead", name: "Ahmed Al-Faisal", title: "Operations Manager" },
        { role: "Quality Lead", name: "Mohammed Rashid", title: "QC Supervisor" },
        { role: "IT Integration", name: "Fatima Hassan", title: "IT Manager" }
      ],
      vendor: [
        { role: "Implementation Manager", name: "Dr. James Chen", title: "Senior Solutions Architect" },
        { role: "ML Engineer", name: "Lisa Wang", title: "AI Specialist" },
        { role: "Support Engineer", name: "Mike Rodriguez", title: "Technical Support" }
      ]
    },
    phases: [
      {
        phase: "Phase 1: Discovery & Planning",
        duration: "4 weeks",
        objectives: ["Current state analysis", "Requirements definition", "Technical architecture design"],
        deliverables: ["Requirements document", "System architecture", "Implementation plan"],
        keyActivities: [
          "Production line analysis and defect pattern study",
          "Stakeholder interviews and requirements gathering",
          "Technical infrastructure assessment",
          "Risk assessment and mitigation planning"
        ],
        budget: "45,000",
        resources: "2 internal + 1 vendor team member"
      },
      {
        phase: "Phase 2: System Development & Training",
        duration: "12 weeks",
        objectives: ["AI model development", "Hardware installation", "System integration"],
        deliverables: ["Trained AI models", "Installed hardware", "Integrated system"],
        keyActivities: [
          "Collection and labeling of 50,000+ training images",
          "AI model development and validation testing",
          "Hardware procurement and installation",
          "Integration with existing MES/ERP systems"
        ],
        budget: "180,000",
        resources: "4 internal + 3 vendor team members"
      },
      {
        phase: "Phase 3: Testing & Validation",
        duration: "6 weeks",
        objectives: ["System validation", "Performance tuning", "User training"],
        deliverables: ["Validated system", "Trained operators", "Performance reports"],
        keyActivities: [
          "Parallel testing with manual inspection",
          "Accuracy validation across product variants",
          "Performance optimization and tuning",
          "Operator training and certification"
        ],
        budget: "35,000",
        resources: "6 internal + 2 vendor team members"
      },
      {
        phase: "Phase 4: Production Deployment",
        duration: "4 weeks",
        objectives: ["Full production deployment", "Knowledge transfer", "Support handover"],
        deliverables: ["Production system", "Documentation", "Support procedures"],
        keyActivities: [
          "Phased rollout to full production",
          "Performance monitoring and optimization",
          "Knowledge transfer and documentation",
          "Support handover and warranty activation"
        ],
        budget: "25,000",
        resources: "3 internal + 1 vendor team member"
      }
    ],
    totalBudget: "285,000",
    totalDuration: "26 weeks"
  },
  
  // Challenges & Solutions
  challengesAndSolutions: [
    {
      challenge: "Data Quality and Labeling",
      description: "Initial AI model accuracy was only 89% due to insufficient and poorly labeled training data",
      impact: "Delayed timeline by 3 weeks and threatened project success",
      solution: "Implemented systematic data collection process with expert labelers and expanded training dataset to 50,000+ images",
      outcome: "Achieved 99.7% accuracy and established ongoing data collection process"
    },
    {
      challenge: "Operator Resistance",
      description: "Production operators feared job displacement and were reluctant to adopt the new system",
      impact: "Slow adoption and initial resistance to using system outputs",
      solution: "Comprehensive change management including training, job role evolution, and involvement in system improvement",
      outcome: "High operator engagement and advocacy for system expansion"
    },
    {
      challenge: "Integration Complexity",
      description: "Legacy MES system had limited API capabilities requiring custom integration development",
      impact: "Additional development time and complexity in data flow",
      solution: "Developed custom middleware with robust error handling and manual fallback procedures",
      outcome: "Seamless integration with 99.9% uptime and automatic failover"
    },
    {
      challenge: "Lighting Variability",
      description: "Inconsistent lighting conditions throughout the day affected system accuracy",
      impact: "Accuracy dropped to 94% during certain times of day",
      solution: "Installed specialized LED lighting system with automated calibration and compensation algorithms",
      outcome: "Consistent 99.7% accuracy across all lighting conditions"
    }
  ],
  
  // Results & Impact Analysis
  results: {
    quantitativeMetrics: [
      {
        metric: "Defect Rate Reduction",
        baseline: "15.0%",
        current: "2.25%",
        improvement: "85% reduction",
        measurementMethod: "Monthly quality audits over 12 months"
      },
      {
        metric: "Customer Returns",
        baseline: "12.0%",
        current: "2.1%",
        improvement: "82.5% reduction",
        measurementMethod: "Customer return tracking and analysis"
      },
      {
        metric: "Inspection Speed",
        baseline: "20 units/minute",
        current: "50 units/minute",
        improvement: "150% increase",
        measurementMethod: "Production line throughput measurement"
      },
      {
        metric: "Annual Cost Savings",
        baseline: "450K losses",
        current: "2.3M savings",
        improvement: "2.75M swing",
        measurementMethod: "Financial analysis of waste, rework, and returns"
      }
    ],
    qualitativeImpacts: [
      "Improved customer satisfaction scores from 7.2 to 9.1",
      "Enhanced employee confidence in quality processes",
      "Faster response to quality issues and root cause analysis",
      "Improved competitive positioning in automotive sector",
      "Foundation for digital transformation initiatives"
    ],
    roiAnalysis: {
      totalInvestment: "285,000",
      annualSavings: "2,300,000",
      paybackPeriod: "1.5 months",
      threeYearROI: "2,315%",
      npvCalculation: "6.2M (3-year NPV at 8% discount rate)"
    }
  },
  
  // Technical Architecture
  technicalArchitecture: {
    systemOverview: "Multi-tier architecture with edge computing for real-time processing and cloud connectivity for monitoring and updates",
    components: [
      {
        layer: "Acquisition Layer",
        components: ["4K Industrial Cameras", "LED Lighting Systems", "Conveyor Sensors"],
        specifications: "Allied Vision Mako cameras, 3000K/5000K LED arrays, photoelectric sensors"
      },
      {
        layer: "Processing Layer", 
        components: ["Edge Computing Units", "AI/ML Engine", "Image Processing"],
        specifications: "NVIDIA Jetson AGX Xavier, TensorFlow 2.8, OpenCV 4.5"
      },
      {
        layer: "Integration Layer",
        components: ["MES Connector", "ERP Integration", "Quality Database"],
        specifications: "RESTful APIs, PostgreSQL database, MQTT messaging"
      },
      {
        layer: "Monitoring Layer",
        components: ["Dashboard", "Analytics", "Alerting"],
        specifications: "Real-time web dashboard, Grafana analytics, email/SMS alerts"
      }
    ],
    securityMeasures: [
      "Network segmentation with dedicated VLAN",
      "Encrypted data transmission using TLS 1.3",
      "Role-based access control and authentication",
      "Regular security updates and vulnerability assessments"
    ],
    scalabilityDesign: [
      "Modular architecture supporting additional production lines",
      "Cloud-based model training and deployment pipeline",
      "Containerized deployment using Docker",
      "Horizontal scaling capability for increased throughput"
    ]
  },
  
  // Future Roadmap
  futureRoadmap: [
    {
      timeline: "Q2 2024",
      initiative: "Expansion to Assembly Line",
      description: "Deploy system to final assembly inspection with component placement verification",
      expectedBenefit: "Additional 30% quality improvement"
    },
    {
      timeline: "Q3 2024", 
      initiative: "Predictive Quality Analytics",
      description: "Implement predictive models to forecast quality trends and prevent issues",
      expectedBenefit: "Proactive quality management"
    },
    {
      timeline: "Q4 2024",
      initiative: "Multi-Site Deployment",
      description: "Roll out to 3 additional manufacturing facilities",
      expectedBenefit: "Enterprise-wide quality standardization"
    },
    {
      timeline: "Q1 2025",
      initiative: "Supplier Network Integration",
      description: "Share quality insights with key suppliers for upstream improvement",
      expectedBenefit: "Supply chain quality enhancement"
    }
  ],
  
  // Lessons Learned & Recommendations
  lessonsLearned: [
    {
      category: "Technical",
      lesson: "Data Quality is Foundation",
      description: "Invest heavily in high-quality, diverse training data from the beginning. Poor data quality will undermine even the best algorithms.",
      recommendation: "Allocate 30-40% of project time to data collection and labeling"
    },
    {
      category: "Organizational",
      lesson: "Change Management is Critical",
      description: "Technical success requires organizational adoption. Early engagement and clear communication about role evolution prevents resistance.",
      recommendation: "Include change management specialist in project team from day one"
    },
    {
      category: "Vendor Management",
      lesson: "Proof of Concept is Essential",
      description: "Real-world testing with actual production data revealed significant differences between vendor claims and reality.",
      recommendation: "Insist on comprehensive PoC with your actual production data"
    },
    {
      category: "Integration",
      lesson: "Legacy System Complexity",
      description: "Integration with legacy systems always takes longer than expected. Plan for custom development.",
      recommendation: "Add 50% buffer to integration timeline and budget"
    }
  ],
  
  // Additional metadata
  publishedDate: "March 15, 2024",
  lastUpdated: "March 20, 2024",
  readTime: "18 min read",
  views: "2,847",
  downloads: "342",
  status: "verified",
  verifiedBy: "Dr. Khalid Al-Rashid, Manufacturing Excellence Institute",
  industryTags: ["Electronics", "PCB Manufacturing", "Quality Control", "AI/ML"],
  technologyTags: ["Computer Vision", "TensorFlow", "Edge Computing", "Industrial IoT"]
}

export default function UseCaseDetail({ useCaseId = 1, onBack }: UseCaseDetailProps) {
  const useCase = sampleUseCase // In real app, would fetch by useCaseId

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <Button 
              variant="ghost" 
              onClick={onBack}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Use Cases</span>
            </Button>
            
            <div className="flex items-center space-x-3">
              <Button variant="outline" size="sm" className="flex items-center space-x-2">
                <Bookmark className="h-4 w-4" />
                <span className="hidden sm:block">Save</span>
              </Button>
              <Button variant="outline" size="sm" className="flex items-center space-x-2">
                <Share2 className="h-4 w-4" />
                <span className="hidden sm:block">Share</span>
              </Button>
              <Button variant="outline" size="sm" className="flex items-center space-x-2">
                <Download className="h-4 w-4" />
                <span className="hidden sm:block">Download PDF</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto">
          
          {/* Header Section */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm mb-8 overflow-hidden">
            <div className="relative h-64 bg-gradient-to-r from-blue-600 to-blue-800">
              <img 
                src={useCase.images[0]} 
                alt={useCase.title}
                className="w-full h-full object-cover opacity-30"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-blue-900/80 to-blue-800/60"></div>
              <div className="absolute bottom-6 left-6 right-6 text-white">
                <div className="flex items-center space-x-2 mb-3">
                  <span className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm font-medium">
                    {useCase.category}
                  </span>
                  <span className="px-3 py-1 bg-green-500/80 backdrop-blur-sm rounded-full text-sm font-medium flex items-center space-x-1">
                    <Award className="h-3 w-3" />
                    <span>Verified Success</span>
                  </span>
                </div>
                <h1 className="text-3xl font-bold leading-tight mb-2">
                  {useCase.title}
                </h1>
              </div>
            </div>
            
            <div className="p-8">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                <div className="flex items-center space-x-3">
                  <Factory className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Factory</p>
                    <p className="font-semibold text-gray-900">{useCase.factoryName}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <MapPin className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Location</p>
                    <p className="font-semibold text-gray-900">{useCase.city}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Clock className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">Implementation</p>
                    <p className="font-semibold text-gray-900">{useCase.implementationTime}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <TrendingUp className="h-5 w-5 text-gray-500" />
                  <div>
                    <p className="text-sm text-gray-500">ROI</p>
                    <p className="font-semibold text-gray-900">{useCase.roiPercentage}</p>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between pt-6 border-t border-gray-200">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-semibold text-sm">
                        {useCase.contactPerson.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{useCase.contactPerson}</p>
                      <p className="text-sm text-gray-500">{useCase.contactTitle}</p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center space-x-1">
                    <Clock className="h-4 w-4" />
                    <span>{useCase.readTime}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Eye className="h-4 w-4" />
                    <span>{useCase.views} views</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Executive Summary */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
              <Lightbulb className="h-6 w-6 mr-3 text-blue-600" />
              Executive Summary
            </h2>
            <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-r-lg">
              <p className="text-lg text-gray-700 leading-relaxed">
                Advanced Electronics Co. faced critical quality control challenges with a 15% defect rate in PCB manufacturing, resulting in <SaudiRiyalCurrency amount="450K" className="font-semibold" /> annual losses and declining customer satisfaction. The implementation of an AI-powered computer vision quality inspection system achieved an 85% reduction in defects, <SaudiRiyalCurrency amount="2.3M" className="font-semibold" /> in annual cost savings, and 250% ROI in the first year. This case study details the 6-month implementation journey, technical architecture, challenges overcome, and lessons learned.
              </p>
            </div>
          </div>

          {/* Business Challenge & Context */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <Target className="h-6 w-6 mr-3 text-red-600" />
              Business Challenge & Context
            </h2>
            
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Industry Context</h3>
                <p className="text-gray-700 leading-relaxed">{useCase.businessChallenge.industryContext}</p>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Specific Problems</h3>
                <div className="grid grid-cols-1 gap-3">
                  {useCase.businessChallenge.specificProblems.map((problem, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg border border-red-200">
                      <div className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                      <p className="text-gray-700">{problem}</p>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Business Impact</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">Financial Loss</h4>
                    <p className="text-gray-700"><SaudiRiyalCurrency amount="450K" /> annually in waste, rework, and returns</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">Customer Impact</h4>
                    <p className="text-gray-700">{useCase.businessChallenge.businessImpact.customerImpact}</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">Operational Impact</h4>
                    <p className="text-gray-700">{useCase.businessChallenge.businessImpact.operationalImpact}</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-2">Compliance Risk</h4>
                    <p className="text-gray-700">{useCase.businessChallenge.businessImpact.complianceRisk}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Solution Overview */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <Zap className="h-6 w-6 mr-3 text-yellow-600" />
              Solution Overview
            </h2>
            
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Selection Criteria</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {useCase.solution.selectionCriteria.map((criteria, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                      <CheckCircle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                      <p className="text-gray-700">{criteria}</p>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Vendor Evaluation</h3>
                <div className="bg-gray-50 p-4 rounded-lg space-y-3">
                  <p className="text-gray-700"><span className="font-medium">Process:</span> {useCase.solution.vendorEvaluation.process}</p>
                  <p className="text-gray-700"><span className="font-medium">Selected Vendor:</span> {useCase.solution.vendorEvaluation.selectedVendor}</p>
                  <div>
                    <span className="font-medium text-gray-900">Selection Reasons:</span>
                    <ul className="mt-2 space-y-1">
                      {useCase.solution.vendorEvaluation.selectionReasons.map((reason, index) => (
                        <li key={index} className="flex items-start space-x-2">
                          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                          <span className="text-gray-700">{reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Technology Components</h3>
                <div className="grid grid-cols-1 gap-4">
                  {useCase.solution.technologyComponents.map((component, index) => (
                    <div key={index} className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <h4 className="font-medium text-blue-900 mb-2">{component.component}</h4>
                      <p className="text-gray-700">{component.details}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Implementation Journey */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <Wrench className="h-6 w-6 mr-3 text-purple-600" />
              Implementation Journey
            </h2>
            
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 bg-purple-50 rounded-lg">
                  <h3 className="font-semibold text-purple-900 mb-2">Methodology</h3>
                  <p className="text-gray-700">{useCase.implementation.methodology}</p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <h3 className="font-semibold text-purple-900 mb-2">Total Budget & Duration</h3>
                  <p className="text-gray-700"><SaudiRiyalCurrency amount="285,000" /> over {useCase.implementation.totalDuration}</p>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Implementation Phases</h3>
                <div className="space-y-4">
                  {useCase.implementation.phases.map((phase, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-semibold text-gray-900">{phase.phase}</h4>
                        <div className="flex items-center space-x-4 text-sm text-gray-600">
                          <span className="bg-blue-100 px-2 py-1 rounded">{phase.duration}</span>
                          <span className="bg-green-100 px-2 py-1 rounded"><SaudiRiyalCurrency amount={phase.budget.replace(/[^\d,]/g, '')} /></span>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <h5 className="font-medium text-gray-800 mb-1">Objectives:</h5>
                          <ul className="space-y-1">
                            {phase.objectives.map((obj, i) => (
                              <li key={i} className="flex items-start space-x-1">
                                <div className="w-1 h-1 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                                <span className="text-gray-600">{obj}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h5 className="font-medium text-gray-800 mb-1">Key Activities:</h5>
                          <ul className="space-y-1">
                            {phase.keyActivities.map((activity, i) => (
                              <li key={i} className="flex items-start space-x-1">
                                <div className="w-1 h-1 bg-purple-500 rounded-full mt-2 flex-shrink-0"></div>
                                <span className="text-gray-600">{activity}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Images Gallery */}
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

          {/* Challenges & Solutions */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <Shield className="h-6 w-6 mr-3 text-orange-600" />
              Challenges & Solutions
            </h2>
            
            <div className="space-y-6">
              {useCase.challengesAndSolutions.map((item, index) => (
                <div key={index} className="border border-orange-200 rounded-lg p-6 bg-orange-50">
                  <h3 className="text-lg font-semibold text-orange-900 mb-3">{item.challenge}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Challenge Description</h4>
                      <p className="text-gray-700 text-sm mb-3">{item.description}</p>
                      <h4 className="font-medium text-gray-900 mb-2">Impact</h4>
                      <p className="text-red-600 text-sm">{item.impact}</p>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Solution</h4>
                      <p className="text-gray-700 text-sm mb-3">{item.solution}</p>
                      <h4 className="font-medium text-gray-900 mb-2">Outcome</h4>
                      <p className="text-green-600 text-sm">{item.outcome}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Results & Impact Analysis */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <BarChart3 className="h-6 w-6 mr-3 text-green-600" />
              Results & Impact Analysis
            </h2>
            
            <div className="space-y-8">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Quantitative Metrics</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {useCase.results.quantitativeMetrics.map((metric, index) => (
                    <div key={index} className="p-4 bg-green-50 rounded-lg border border-green-200">
                      <h4 className="font-semibold text-green-900 mb-2">{metric.metric}</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Baseline:</span>
                          <span className="font-medium text-gray-900">
                            {metric.metric === "Annual Cost Savings" ? <SaudiRiyalCurrency amount="450K" /> : metric.baseline}
                            {metric.metric === "Annual Cost Savings" ? " losses" : ""}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Current:</span>
                          <span className="font-medium text-gray-900">
                            {metric.metric === "Annual Cost Savings" ? <SaudiRiyalCurrency amount="2.3M" /> : metric.current}
                            {metric.metric === "Annual Cost Savings" ? " savings" : ""}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Improvement:</span>
                          <span className="font-bold text-green-600">
                            {metric.metric === "Annual Cost Savings" ? <SaudiRiyalCurrency amount="2.75M" /> : metric.improvement}
                            {metric.metric === "Annual Cost Savings" ? " swing" : ""}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">ROI Analysis</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg text-center">
                    <div className="text-2xl font-bold text-blue-600"><SaudiRiyalCurrency amount="285,000" /></div>
                    <div className="text-sm text-gray-600">Total Investment</div>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg text-center">
                    <div className="text-2xl font-bold text-green-600"><SaudiRiyalCurrency amount="2,300,000" /></div>
                    <div className="text-sm text-gray-600">Annual Savings</div>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg text-center">
                    <div className="text-2xl font-bold text-purple-600">{useCase.results.roiAnalysis.threeYearROI}</div>
                    <div className="text-sm text-gray-600">3-Year ROI</div>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Qualitative Impacts</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {useCase.results.qualitativeImpacts.map((impact, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                      <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                      <p className="text-gray-700">{impact}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

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
                  <div className="flex items-center space-x-3">
                    <Factory className="h-5 w-5 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">Factory</p>
                      <p className="font-medium text-gray-900">{useCase.factoryName}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <MapPin className="h-5 w-5 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">City</p>
                      <p className="font-medium text-gray-900">{useCase.city}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-5 h-5 flex items-center justify-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Coordinates</p>
                      <p className="font-medium text-gray-900 font-mono text-sm">
                        {useCase.latitude.toFixed(4)}, {useCase.longitude.toFixed(4)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Timeline</h3>
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <Clock className="h-5 w-5 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">Implementation Time</p>
                      <p className="font-medium text-gray-900">{useCase.implementationTime}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <TrendingUp className="h-5 w-5 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">Return on Investment</p>
                      <p className="font-medium text-gray-900">{useCase.roiPercentage}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Calendar className="h-5 w-5 text-gray-500" />
                    <div>
                      <p className="text-sm text-gray-500">Category</p>
                      <p className="font-medium text-gray-900">{useCase.category}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Technical Architecture */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <Wrench className="h-6 w-6 mr-3 text-gray-600" />
              Technical Architecture
            </h2>
            
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">System Overview</h3>
                <p className="text-gray-700 p-4 bg-gray-50 rounded-lg">{useCase.technicalArchitecture.systemOverview}</p>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Architecture Components</h3>
                <div className="space-y-4">
                  {useCase.technicalArchitecture.components.map((component, index) => (
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
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Security Measures</h3>
                  <div className="space-y-2">
                    {useCase.technicalArchitecture.securityMeasures.map((measure, index) => (
                      <div key={index} className="flex items-start space-x-3 p-2 bg-red-50 rounded">
                        <Shield className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700 text-sm">{measure}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Scalability Design</h3>
                  <div className="space-y-2">
                    {useCase.technicalArchitecture.scalabilityDesign.map((design, index) => (
                      <div key={index} className="flex items-start space-x-3 p-2 bg-blue-50 rounded">
                        <TrendingUp className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700 text-sm">{design}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Future Roadmap & Lessons Learned */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <Calendar className="h-6 w-6 mr-3 text-purple-600" />
                Future Roadmap
              </h2>
              <div className="space-y-4">
                {useCase.futureRoadmap.map((item, index) => (
                  <div key={index} className="border-l-4 border-purple-500 pl-4 py-2">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-sm font-medium text-purple-600 bg-purple-100 px-2 py-1 rounded">{item.timeline}</span>
                    </div>
                    <h4 className="font-semibold text-gray-900 mb-1">{item.initiative}</h4>
                    <p className="text-gray-600 text-sm mb-1">{item.description}</p>
                    <p className="text-purple-600 text-sm font-medium">{item.expectedBenefit}</p>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <Lightbulb className="h-6 w-6 mr-3 text-yellow-600" />
                Lessons Learned
              </h2>
              <div className="space-y-4">
                {useCase.lessonsLearned.map((lesson, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-xs font-medium text-gray-600 bg-gray-100 px-2 py-1 rounded">{lesson.category}</span>
                    </div>
                    <h4 className="font-semibold text-gray-900 mb-2">{lesson.lesson}</h4>
                    <p className="text-gray-600 text-sm mb-2">{lesson.description}</p>
                    <div className="bg-yellow-50 p-3 rounded border-l-4 border-yellow-400">
                      <p className="text-yellow-800 text-sm font-medium">Recommendation: {lesson.recommendation}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Contact & Follow-up */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl p-8 text-white">
            <h2 className="text-2xl font-bold mb-4">Interested in Similar Implementation?</h2>
            <p className="text-blue-100 mb-6">
              Connect with {useCase.contactPerson} ({useCase.contactTitle}) at {useCase.factoryName} to learn more about this implementation 
              or discuss how similar solutions could benefit your operations.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Button variant="secondary" className="flex items-center space-x-2">
                <Users className="h-4 w-4" />
                <span>Contact {useCase.contactPerson}</span>
              </Button>
              <Button variant="outline" className="flex items-center space-x-2 text-white border-white hover:bg-white hover:text-blue-600">
                <Factory className="h-4 w-4" />
                <span>Visit Factory</span>
              </Button>
              <Button variant="outline" className="flex items-center space-x-2 text-white border-white hover:bg-white hover:text-blue-600">
                <Share2 className="h-4 w-4" />
                <span>Share Case Study</span>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}