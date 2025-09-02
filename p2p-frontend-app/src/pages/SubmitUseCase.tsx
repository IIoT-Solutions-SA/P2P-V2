import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { buildApiUrl } from '@/config/environment'
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { 
  Factory, 
  MapPin, 
  Upload, 
  CheckCircle, 
  Plus,
  X,
  Save,
  Target,
  Zap,
  Wrench,
  Shield,
  BarChart3,
  Users
} from "lucide-react"
import LocationPicker from '@/components/LocationPicker'
import ImageUpload from '@/components/ImageUpload'

// Enhanced form validation schema matching the detailed use case structure
const formSchema = z.object({
  // Basic Information
  title: z.string()
    .min(10, "Title must be at least 10 characters")
    .max(100, "Title must not exceed 100 characters"),
  subtitle: z.string()
    .min(10, "Subtitle must be at least 10 characters")
    .max(150, "Subtitle must not exceed 150 characters"),
  description: z.string()
    .min(50, "Description must be at least 50 characters")
    .max(500, "Description must not exceed 500 characters"),
  category: z.string().min(1, "Please select a category"),
  factoryName: z.string()
    .min(2, "Factory name must be at least 2 characters")
    .max(80, "Factory name must not exceed 80 characters"),
  
  // Location
  city: z.string()
    .min(2, "City name must be at least 2 characters")
    .max(50, "City name must not exceed 50 characters"),
  latitude: z.number()
    .min(-90, "Invalid latitude")
    .max(90, "Invalid latitude"),
  longitude: z.number()
    .min(-180, "Invalid longitude")
    .max(180, "Invalid longitude"),
    
  // Business Challenge
  industryContext: z.string()
    .min(50, "Industry context must be at least 50 characters")
    .max(500, "Industry context must not exceed 500 characters"),
  specificProblems: z.array(z.string().min(10, "Problem must be at least 10 characters"))
    .min(2, "Please add at least 2 problems")
    .max(5, "Maximum 5 problems allowed"),
  financialLoss: z.string()
    .min(5, "Financial impact description must be at least 5 characters"),
  
  // Solution Overview
  selectionCriteria: z.array(z.string().min(10, "Criteria must be at least 10 characters"))
    .min(2, "Please add at least 2 selection criteria")
    .max(5, "Maximum 5 criteria allowed"),
  selectedVendor: z.string()
    .min(2, "Vendor name is required"),
  technologyComponents: z.array(z.string().min(20, "Component description must be at least 20 characters"))
    .min(1, "Please add at least 1 technology component")
    .max(4, "Maximum 4 components allowed"),
    
  // Implementation
  implementationTime: z.string()
    .min(3, "Implementation time is required"),
  totalBudget: z.string()
    .min(3, "Total budget is required"),
  methodology: z.string()
    .min(20, "Methodology description must be at least 20 characters"),
    
  // Results
  quantitativeResults: z.array(z.object({
    metric: z.string().min(5, "Metric name required"),
    baseline: z.string().min(2, "Baseline value required"),
    current: z.string().min(2, "Current value required"),
    improvement: z.string().min(2, "Improvement value required")
  })).min(2, "Please add at least 2 quantitative results").max(4, "Maximum 4 results allowed"),
  
  roiPercentage: z.string().optional(),
  annualSavings: z.string().optional(),
  
  // Challenges & Solutions
  challengesSolutions: z.array(z.object({
    challenge: z.string().min(10, "Challenge name required"),
    description: z.string().min(20, "Challenge description required"),
    solution: z.string().min(20, "Solution description required"),
    outcome: z.string().min(10, "Outcome description required")
  })).min(1, "Please add at least 1 challenge").max(4, "Maximum 4 challenges allowed"),
  
  // Contact & Media
  contactPerson: z.string().optional(),
  contactTitle: z.string().optional(),
  images: z.array(z.instanceof(File))
    .min(1, "Please upload at least 1 image")
    .max(5, "Maximum 5 images allowed")
})

type FormData = z.infer<typeof formSchema>

const categories = [
  { value: "Quality Control", label: "Quality Control" },
  { value: "Predictive Maintenance", label: "Predictive Maintenance" },
  { value: "Factory Automation", label: "Factory Automation" },
  { value: "Artificial Intelligence", label: "Artificial Intelligence" },
  { value: "Sustainability", label: "Sustainability" },
  { value: "Process Optimization", label: "Process Optimization" },
  { value: "Supply Chain", label: "Supply Chain" },
  { value: "Innovation & R&D", label: "Innovation & R&D" },
  { value: "Training & Safety", label: "Training & Safety" },
  { value: "Energy Efficiency", label: "Energy Efficiency" }
]

export default function SubmitUseCase() {
  const [searchParams] = useSearchParams()
  const editUseCaseId = searchParams.get('edit')
  const isEditMode = !!editUseCaseId

  const [currentStep, setCurrentStep] = useState(1)
  const [uploadedImages, setUploadedImages] = useState<File[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [isLoadingExistingData, setIsLoadingExistingData] = useState(false)

  
  // State for dynamic arrays
  const [specificProblems, setSpecificProblems] = useState<string[]>(["", ""])
  const [selectionCriteria, setSelectionCriteria] = useState<string[]>(["", ""])
  const [technologyComponents, setTechnologyComponents] = useState<string[]>([""])
  // Vendor evaluation (optional)
  const [vendorProcess, setVendorProcess] = useState<string>("")
  const [vendorSelectionReasons, setVendorSelectionReasons] = useState<string[]>([])
  // Project team (optional)
  const [projectTeamInternal, setProjectTeamInternal] = useState<Array<{ role: string; name: string; title: string }>>([
    { role: "", name: "", title: "" }
  ])
  const [projectTeamVendor, setProjectTeamVendor] = useState<Array<{ role: string; name: string; title: string }>>([
    { role: "", name: "", title: "" }
  ])
  // Phases (optional)
  const [phases, setPhases] = useState<Array<{ phase: string; duration: string; objectives: string[]; keyActivities: string[]; budget: string }>>([
    { phase: "", duration: "", objectives: [""], keyActivities: [""], budget: "" }
  ])
  // Qualitative impacts (optional)
  const [qualitativeImpacts, setQualitativeImpacts] = useState<string[]>([])
  // Tags (optional)
  const [industryTags, setIndustryTags] = useState<string[]>([])
  const [technologyTags, setTechnologyTags] = useState<string[]>([])
  // Technical Architecture
  const [systemOverview, setSystemOverview] = useState<string>("")
  const [architectureComponents, setArchitectureComponents] = useState<Array<{layer: string, components: string[], specifications: string}>>([
    { layer: "", components: [""], specifications: "" }
  ])
  const [securityMeasures, setSecurityMeasures] = useState<string[]>([""])
  const [scalabilityDesign, setScalabilityDesign] = useState<string[]>([""])
  // ROI extras (optional)
  const [roiTotalInvestment, setRoiTotalInvestment] = useState<string>("")
  const [roiThreeYearRoi, setRoiThreeYearRoi] = useState<string>("")
  const [quantitativeResults, setQuantitativeResults] = useState<Array<{
    metric: string
    baseline: string
    current: string
    improvement: string
  }>>([
    { metric: "", baseline: "", current: "", improvement: "" },
    { metric: "", baseline: "", current: "", improvement: "" }
  ])
  const [challengesSolutions, setChallengesSolutions] = useState<Array<{
    challenge: string
    description: string
    solution: string
    outcome: string
  }>>([
    { challenge: "", description: "", solution: "", outcome: "" }
  ])

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      // Basic Information
      title: "",
      subtitle: "",
      description: "",
      category: "",
      factoryName: "",
      
      // Location
      city: "",
      latitude: 24.7136, // Default to Riyadh
      longitude: 46.6753,
      
      // Business Challenge
      industryContext: "",
      specificProblems: ["", ""],
      financialLoss: "",
      
      // Solution Overview
      selectionCriteria: ["", ""],
      selectedVendor: "",
      technologyComponents: [""],
      
      // Implementation
      implementationTime: "",
      totalBudget: "",
      methodology: "",
      
      // Results
      quantitativeResults: [
        { metric: "", baseline: "", current: "", improvement: "" },
        { metric: "", baseline: "", current: "", improvement: "" }
      ],
      roiPercentage: "",
      annualSavings: "",
      
      // Challenges & Solutions
      challengesSolutions: [
        { challenge: "", description: "", solution: "", outcome: "" }
      ],
      
      // Contact & Media
      contactPerson: "",
      contactTitle: "",
      images: []
    }
  })

  // Fetch existing use case data when in edit mode
  useEffect(() => {
    if (isEditMode && editUseCaseId) {
      const fetchExistingUseCase = async () => {
        setIsLoadingExistingData(true)
        try {
          const response = await fetch(buildApiUrl(`/api/v1/use-cases/by-id/${editUseCaseId}`), {
            credentials: 'include'
          })
          if (!response.ok) {
            throw new Error('Failed to fetch use case data')
          }
          const data = await response.json()
          
          // Pre-populate form fields with existing data
          form.setValue('title', data.title || '')
          form.setValue('subtitle', data.subtitle || '')
          form.setValue('description', data.executive_summary || '')
          form.setValue('category', data.category || '')
          form.setValue('factoryName', data.factory_name || '')
          form.setValue('city', data.location?.city || '')
          form.setValue('latitude', data.location?.lat || 24.7136)
          form.setValue('longitude', data.location?.lng || 46.6753)
          
          // Business Challenge
          form.setValue('industryContext', data.business_challenge?.industry_context || '')
          form.setValue('financialLoss', data.business_challenge?.business_impact?.financial_loss || '')
          
          // Pre-populate dynamic arrays with existing data
          if (data.business_challenge?.specific_problems?.length > 0) {
            const problems = data.business_challenge.specific_problems
            setSpecificProblems(problems.length < 2 ? [...problems, ""] : problems)
            form.setValue('specificProblems', problems.length < 2 ? [...problems, ""] : problems)
          }
          
          if (data.solution_details?.selection_criteria?.length > 0) {
            const criteria = data.solution_details.selection_criteria
            setSelectionCriteria(criteria.length < 2 ? [...criteria, ""] : criteria)
            form.setValue('selectionCriteria', criteria.length < 2 ? [...criteria, ""] : criteria)
          }
          
          form.setValue('selectedVendor', data.solution_details?.vendor_evaluation?.selected_vendor || '')
          
          if (data.solution_details?.technology_components?.length > 0) {
            const components = data.solution_details.technology_components.map((comp: string | { component: string; details: string }) => 
              typeof comp === 'string' ? comp : `${comp.component}: ${comp.details}`
            )
            setTechnologyComponents(components.length === 0 ? [""] : components)
            form.setValue('technologyComponents', components.length === 0 ? [""] : components)
          }
          
          // Implementation
          form.setValue('implementationTime', data.implementation_time || '')
          form.setValue('totalBudget', data.implementation_details?.total_budget || '')
          form.setValue('methodology', data.implementation_details?.methodology || '')
          
          // Results
          if (data.results?.quantitative_results?.length > 0) {
            const results = data.results.quantitative_results
            setQuantitativeResults(results.length < 2 ? [...results, { metric: "", baseline: "", current: "", improvement: "" }] : results)
            form.setValue('quantitativeResults', results.length < 2 ? [...results, { metric: "", baseline: "", current: "", improvement: "" }] : results)
          }
          
          form.setValue('roiPercentage', data.roi_percentage || '')
          form.setValue('annualSavings', data.results?.annual_savings || '')
          
          // Challenges & Solutions
          if (data.results?.challenges_solutions?.length > 0) {
            const challenges = data.results.challenges_solutions
            setChallengesSolutions(challenges)
            form.setValue('challengesSolutions', challenges)
          }
          
          // Contact
          form.setValue('contactPerson', data.contact_person || '')
          form.setValue('contactTitle', data.contact_title || '')
          
          // Note: Images would need special handling for edit mode since they're already uploaded
          // For now, we'll show them but won't pre-populate the file upload
          
        } catch (error) {
          console.error('Error fetching existing use case:', error)
        } finally {
          setIsLoadingExistingData(false)
        }
      }
      
      fetchExistingUseCase()
    }
  }, [isEditMode, editUseCaseId, form])

  const steps = [
    { number: 1, title: "Basic Information", icon: Factory },
    { number: 2, title: "Business Challenge", icon: Target },
    { number: 3, title: "Solution & Implementation", icon: Zap },
    { number: 4, title: "Technical Architecture", icon: Wrench },
    { number: 5, title: "Results & Challenges", icon: BarChart3 },
    { number: 6, title: "Location & Contact", icon: MapPin },
    { number: 7, title: "Review & Submit", icon: CheckCircle }
  ]

  // Helper functions for dynamic arrays
  // legacy benefit helpers removed

  // Helper functions for dynamic arrays
  const addSpecificProblem = () => {
    if (specificProblems.length < 5) {
      const updated = [...specificProblems, ""]
      setSpecificProblems(updated)
      form.setValue('specificProblems', updated)
    }
  }

  const removeSpecificProblem = (index: number) => {
    if (specificProblems.length > 2) {
      const updated = specificProblems.filter((_, i) => i !== index)
      setSpecificProblems(updated)
      form.setValue('specificProblems', updated)
    }
  }

  const updateSpecificProblem = (index: number, value: string) => {
    const updated = [...specificProblems]
    updated[index] = value
    setSpecificProblems(updated)
    form.setValue('specificProblems', updated)
  }

  const addSelectionCriteria = () => {
    if (selectionCriteria.length < 5) {
      const updated = [...selectionCriteria, ""]
      setSelectionCriteria(updated)
      form.setValue('selectionCriteria', updated)
    }
  }

  const removeSelectionCriteria = (index: number) => {
    if (selectionCriteria.length > 2) {
      const updated = selectionCriteria.filter((_, i) => i !== index)
      setSelectionCriteria(updated)
      form.setValue('selectionCriteria', updated)
    }
  }

  const updateSelectionCriteria = (index: number, value: string) => {
    const updated = [...selectionCriteria]
    updated[index] = value
    setSelectionCriteria(updated)
    form.setValue('selectionCriteria', updated)
  }

  const addTechnologyComponent = () => {
    if (technologyComponents.length < 4) {
      const updated = [...technologyComponents, ""]
      setTechnologyComponents(updated)
      form.setValue('technologyComponents', updated)
    }
  }

  const removeTechnologyComponent = (index: number) => {
    if (technologyComponents.length > 1) {
      const updated = technologyComponents.filter((_, i) => i !== index)
      setTechnologyComponents(updated)
      form.setValue('technologyComponents', updated)
    }
  }

  const updateTechnologyComponent = (index: number, value: string) => {
    const updated = [...technologyComponents]
    updated[index] = value
    setTechnologyComponents(updated)
    form.setValue('technologyComponents', updated)
  }

  const handleLocationSelect = (lat: number, lng: number) => {
    form.setValue('latitude', lat)
    form.setValue('longitude', lng)
  }

  const handleImagesUpdate = (files: File[]) => {
    setUploadedImages(files)
    form.setValue('images', files)
  }

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true)
    try {
      // TODO: upload images and get URLs. For now, fake URLs using filenames
      const imageUrls = uploadedImages.map(file => `https://cdn.example.com/${encodeURIComponent(file.name)}`)

      const payload = {
        // Basic Information
        title: data.title,
        subtitle: data.subtitle,
        description: data.description,
        category: data.category,
        factoryName: data.factoryName,

        // Location
        city: data.city,
        latitude: form.getValues('latitude'),
        longitude: form.getValues('longitude'),

        // Business Challenge
        industryContext: data.industryContext,
        specificProblems: specificProblems,
        financialLoss: data.financialLoss,

        // Solution Overview
        selectionCriteria: selectionCriteria,
        selectedVendor: data.selectedVendor,
        technologyComponents: technologyComponents,
        // Vendor evaluation (optional)
        vendorProcess,
        vendorSelectionReasons,

        // Implementation
        implementationTime: data.implementationTime,
        totalBudget: data.totalBudget,
        methodology: data.methodology,
        // Project team & phases (optional)
        projectTeamInternal,
        projectTeamVendor,
        phases,

        // Results
        quantitativeResults: quantitativeResults,
        roiPercentage: data.roiPercentage || undefined,
        annualSavings: data.annualSavings || undefined,
        qualitativeImpacts,
        roiTotalInvestment: roiTotalInvestment || undefined,
        roiThreeYearRoi: roiThreeYearRoi || undefined,

        // Challenges & Solutions
        challengesSolutions: challengesSolutions,

        // Contact & Media
        contactPerson: data.contactPerson || undefined,
        contactTitle: data.contactTitle || undefined,
        images: imageUrls,
        // Tags
        industryTags,
        technologyTags,
      }

      // Use PUT for edit mode, POST for create mode
      const url = isEditMode 
        ? buildApiUrl(`/api/v1/use-cases/${editUseCaseId}`)
        : buildApiUrl('/api/v1/use-cases')
      
      const method = isEditMode ? 'PUT' : 'POST'

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `${isEditMode ? 'Update' : 'Submission'} failed`)
      }
      setIsSubmitted(true)
    } catch (error) {
      console.error(`Error ${isEditMode ? 'updating' : 'submitting'} use case:`, error)
    } finally {
      setIsSubmitting(false)
    }
  }

  // Step gating: fields to validate per step
  const stepFields: Record<number, (keyof FormData | string)[]> = {
    1: ['title', 'subtitle', 'description', 'category', 'factoryName'],
    2: ['industryContext', 'specificProblems', 'financialLoss'],
    3: ['selectionCriteria', 'selectedVendor', 'technologyComponents', 'implementationTime', 'totalBudget', 'methodology'],
    4: [], // Technical Architecture is optional
    5: ['quantitativeResults', 'challengesSolutions'],
    6: ['city', 'latitude', 'longitude', 'images'],
    7: []
  }

  const handleNext = async () => {
    const fields = stepFields[currentStep] || []
    let hasValidationErrors = false
    
    // For step validation, we need to manually validate dynamic arrays
    // since they're not automatically synced with form state
    if (currentStep === 2) {
      // Validate specific problems
      const validProblems = specificProblems.filter(p => p.trim().length >= 10).length >= 2
      if (!validProblems) {
        let message = "Please add at least 2 problems"
        if (specificProblems.length >= 2) {
          // Check which problems are too short
          const shortProblems: string[] = []
          specificProblems.forEach((p, i) => {
            if (p.trim().length > 0 && p.trim().length < 10) {
              shortProblems.push(`Problem ${i + 1} needs ${10 - p.trim().length} more characters`)
            }
          })
          if (shortProblems.length > 0) {
            message = shortProblems[0]
          } else {
            message = "Each problem must be at least 10 characters"
          }
        }
        form.setError('specificProblems', { 
          type: 'manual',
          message: message 
        })
        hasValidationErrors = true
      } else {
        form.clearErrors('specificProblems')
      }
    }
    
    if (currentStep === 3) {
      // Validate selection criteria
      const validCriteria = selectionCriteria.filter(c => c.trim().length >= 10).length >= 2
      if (!validCriteria) {
        let message = "Please add at least 2 selection criteria"
        if (selectionCriteria.length >= 2) {
          // Check which criteria are too short
          const shortCriteria: string[] = []
          selectionCriteria.forEach((c, i) => {
            if (c.trim().length > 0 && c.trim().length < 10) {
              shortCriteria.push(`Criteria ${i + 1} needs ${10 - c.trim().length} more characters`)
            }
          })
          if (shortCriteria.length > 0) {
            message = shortCriteria[0]
          } else {
            message = "Each criteria must be at least 10 characters"
          }
        }
        form.setError('selectionCriteria', { 
          type: 'manual',
          message: message 
        })
        hasValidationErrors = true
      } else {
        form.clearErrors('selectionCriteria')
      }
      
      // Validate technology components
      const validComponents = technologyComponents.filter(c => c.trim().length >= 20).length >= 1
      if (!validComponents) {
        let message = "Please add at least 1 technology component"
        if (technologyComponents.length >= 1) {
          // Check which components are too short
          const shortComponents: string[] = []
          technologyComponents.forEach((c, i) => {
            if (c.trim().length > 0 && c.trim().length < 20) {
              shortComponents.push(`Component ${i + 1} needs ${20 - c.trim().length} more characters`)
            }
          })
          if (shortComponents.length > 0) {
            message = shortComponents[0]
          } else {
            message = "Each component description must be at least 20 characters"
          }
        }
        form.setError('technologyComponents', { 
          type: 'manual',
          message: message 
        })
        hasValidationErrors = true
      } else {
        form.clearErrors('technologyComponents')
      }
    }
    
    if (currentStep === 5) {
      // Validate quantitative results
      const validResults = quantitativeResults.filter(r => 
        r.metric.trim().length >= 5 && 
        r.baseline.trim().length >= 2 && 
        r.current.trim().length >= 2 && 
        r.improvement.trim().length >= 2
      ).length >= 2
      if (!validResults) {
        form.setError('quantitativeResults', { 
          type: 'manual',
          message: "Please add at least 2 quantitative results with all fields filled"
        })
        hasValidationErrors = true
      } else {
        form.clearErrors('quantitativeResults')
      }
      
      // Validate challenges & solutions
      const validChallenges = challengesSolutions.filter(c => 
        c.challenge.trim().length >= 10 && 
        c.description.trim().length >= 20 && 
        c.solution.trim().length >= 20 && 
        c.outcome.trim().length >= 10
      ).length >= 1
      
      if (!validChallenges) {
        // More specific error message
        const hasAnyChallenges = challengesSolutions.some(c => 
          c.challenge.trim().length > 0 || 
          c.description.trim().length > 0 || 
          c.solution.trim().length > 0 || 
          c.outcome.trim().length > 0
        )
        
        let message = "Please add at least 1 challenge with all fields filled"
        if (hasAnyChallenges) {
          // Check which specific fields are invalid
          const invalidFields: string[] = []
          challengesSolutions.forEach((c, i) => {
            if (c.challenge.trim().length > 0 && c.challenge.trim().length < 10) {
              invalidFields.push(`Challenge ${i + 1} name needs ${10 - c.challenge.trim().length} more characters`)
            }
            if (c.description.trim().length > 0 && c.description.trim().length < 20) {
              invalidFields.push(`Challenge ${i + 1} description needs ${20 - c.description.trim().length} more characters`)
            }
            if (c.solution.trim().length > 0 && c.solution.trim().length < 20) {
              invalidFields.push(`Challenge ${i + 1} solution needs ${20 - c.solution.trim().length} more characters`)
            }
            if (c.outcome.trim().length > 0 && c.outcome.trim().length < 10) {
              invalidFields.push(`Challenge ${i + 1} outcome needs ${10 - c.outcome.trim().length} more characters`)
            }
          })
          
          if (invalidFields.length > 0) {
            message = invalidFields[0] // Show the first validation error
          } else {
            message = "Challenge requirements: Name (10+ chars), Description (20+ chars), Solution (20+ chars), Outcome (10+ chars)"
          }
        }
        
        form.setError('challengesSolutions', { 
          type: 'manual',
          message: message 
        })
        hasValidationErrors = true
      } else {
        form.clearErrors('challengesSolutions')
      }
    }

    if (currentStep === 6) {
      // Validate images
      if (uploadedImages.length < 1) {
        form.setError('images', { 
          type: 'manual',
          message: "Please upload at least 1 image"
        })
        hasValidationErrors = true
      } else {
        form.clearErrors('images')
      }
    }

    const valid = await form.trigger(fields as (keyof FormData)[], { shouldFocus: true })
    if (!valid || hasValidationErrors) {
      return
    }
    if (currentStep < 7) setCurrentStep(currentStep + 1)
  }

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1)
  }

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-lg max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mb-4">
            {isEditMode ? 'Use Case Updated Successfully!' : 'Use Case Submitted Successfully!'}
          </h1>
          <p className="text-slate-600 mb-6">
            {isEditMode 
              ? 'Your use case has been updated successfully and the changes are now live.'
              : 'Thank you for sharing your factory success story. Our team will review your submission and it will be published on the platform soon.'
            }
          </p>
          <Button 
            onClick={() => window.location.href = '/usecases'} 
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {isEditMode ? 'View Use Cases' : 'Browse Use Cases'}
          </Button>
        </div>
      </div>
    )
  }

  // Show loading overlay while fetching existing data
  if (isLoadingExistingData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-lg text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Loading Use Case Data...</h2>
          <p className="text-slate-600">Please wait while we fetch your existing data.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="container mx-auto px-6 py-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-slate-900 mb-4">
              {isEditMode ? 'Edit Your Success Story' : 'Submit Your Success Story'}
            </h1>
            <p className="text-xl text-slate-600">
              {isEditMode 
                ? 'Update your factory transformation story' 
                : 'Share your factory\'s transformation with the community'
              }
            </p>
          </div>

          {/* Progress Steps */}
          <div className="flex items-center justify-center space-x-8">
            {steps.map((step, index) => {
              const IconComponent = step.icon
              const isActive = currentStep === step.number
              const isCompleted = currentStep > step.number
              
              return (
                <div key={step.number} className="flex items-center">
                  <div className={`flex items-center space-x-3 ${isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-slate-400'}`}>
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${
                      isActive 
                        ? 'border-blue-600 bg-blue-50' 
                        : isCompleted 
                        ? 'border-green-600 bg-green-50' 
                        : 'border-slate-300 bg-white'
                    }`}>
                      {isCompleted ? (
                        <CheckCircle className="h-5 w-5" />
                      ) : (
                        <IconComponent className="h-5 w-5" />
                      )}
                    </div>
                    <div className="hidden sm:block">
                      <div className="font-medium">{step.title}</div>
                    </div>
                  </div>
                  {index < steps.length - 1 && (
                    <div className={`hidden sm:block w-16 h-0.5 mx-4 ${
                      currentStep > step.number ? 'bg-green-600' : 'bg-slate-300'
                    }`} />
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Form Content */}
      <div className="container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
              
              {/* Step 1: Basic Information */}
              {currentStep === 1 && (
                <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                  <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
                    <Factory className="h-6 w-6 mr-3 text-blue-600" />
                    Basic Information
                  </h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <FormField
                      control={form.control}
                      name="title"
                      render={({ field }) => (
                        <FormItem className="md:col-span-2">
                          <FormLabel>Use Case Title <span className="text-gray-500">(10-100 chars)</span></FormLabel>
                          <FormControl>
                            <Input 
                              placeholder="e.g., AI Quality Inspection System Reduces Defects by 85%" 
                              {...field} 
                            />
                          </FormControl>
                          <FormDescription>
                            A clear, compelling title that describes your success story
                          </FormDescription>
                          <div className="text-xs text-gray-500 mt-1">{field.value?.length || 0}/100 characters</div>
                          <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="subtitle"
                      render={({ field }) => (
                        <FormItem className="md:col-span-2">
                          <FormLabel>Subtitle <span className="text-gray-500">(10-150 chars)</span></FormLabel>
                          <FormControl>
                            <Input 
                              placeholder="e.g., Transforming PCB Manufacturing Through Computer Vision and Machine Learning" 
                              {...field} 
                            />
                          </FormControl>
                          <FormDescription>
                            A descriptive subtitle explaining the technology or approach used
                          </FormDescription>
                          <div className="text-xs text-gray-500 mt-1">{field.value?.length || 0}/150 characters</div>
                          <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="category"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Category</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select a category" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent className="z-[9999] bg-white border-2 border-slate-200 shadow-2xl max-h-[300px] overflow-y-auto">
                              {categories.map((category) => (
                                <SelectItem 
                                  key={category.value} 
                                  value={category.value}
                                  className="hover:bg-blue-50 hover:text-blue-900 cursor-pointer p-3 border-b border-slate-100 last:border-b-0"
                                >
                                  {category.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="factoryName"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Factory Name <span className="text-gray-500">(2-80 chars)</span></FormLabel>
                          <FormControl>
                            <Input placeholder="e.g., Advanced Electronics Co." {...field} />
                          </FormControl>
                          <div className="text-xs text-gray-500 mt-1">{field.value?.length || 0}/80 characters</div>
                          <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="description"
                      render={({ field }) => (
                        <FormItem className="md:col-span-2">
                          <FormLabel>Executive Summary <span className="text-gray-500">(50-500 chars)</span></FormLabel>
                          <FormControl>
                            <Textarea 
                              placeholder="Provide an executive summary covering the problem, solution, and key results achieved..."
                              className="min-h-[120px]"
                              {...field} 
                            />
                          </FormControl>
                          <FormDescription>
                            A comprehensive summary of your implementation and its business impact
                          </FormDescription>
                          <div className="text-xs text-gray-500 mt-1">{field.value?.length || 0}/500 characters</div>
                          <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>
              )}

              {/* Step 2: Business Challenge */}
              {currentStep === 2 && (
                <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                  <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
                    <Target className="h-6 w-6 mr-3 text-red-600" />
                    Business Challenge & Context
                  </h2>
                  
                  <div className="space-y-6">
                    <FormField
                      control={form.control}
                      name="industryContext"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Industry Context <span className="text-gray-500">(50-500 chars)</span></FormLabel>
                          <FormControl>
                            <Textarea 
                              placeholder="Describe the broader industry challenges and trends that motivated this implementation..."
                              className="min-h-[100px]"
                              {...field} 
                            />
                          </FormControl>
                          <FormDescription>
                            Explain the industry pressures and market conditions driving the need for this solution
                          </FormDescription>
                          <div className="text-xs text-gray-500 mt-1">{field.value?.length || 0}/500 characters</div>
                          <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                        </FormItem>
                      )}
                    />

                    <div>
                      <FormLabel className="text-base font-semibold">Specific Problems Addressed</FormLabel>
                      <FormDescription className="mb-4">
                        List the specific operational problems that needed to be solved (minimum 2)
                      </FormDescription>
                      <div className="space-y-3">
                        {specificProblems.map((problem, index) => (
                          <div key={index} className="space-y-2">
                            <div className="flex items-center space-x-3">
                              <Input
                                placeholder={`Problem ${index + 1} (e.g., Manual inspection inconsistency with 15% defect rate)`}
                                value={problem}
                                onChange={(e) => updateSpecificProblem(index, e.target.value)}
                                className="flex-1"
                              />
                            {specificProblems.length > 2 && (
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => removeSpecificProblem(index)}
                                className="text-red-600 hover:text-red-700"
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            )}
                            </div>
                            <div className="text-xs text-gray-500 ml-1">{problem.length}/10 characters minimum</div>
                          </div>
                        ))}
                        
                        {specificProblems.length < 5 && (
                          <Button
                            type="button"
                            variant="outline"
                            onClick={addSpecificProblem}
                            className="flex items-center space-x-2"
                          >
                            <Plus className="h-4 w-4" />
                            <span>Add Another Problem</span>
                          </Button>
                        )}
                      </div>
                      {/* Show validation error for specific problems */}
                      {form.formState.errors.specificProblems && (
                        <div className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2">
                          {form.formState.errors.specificProblems.message || "Please add at least 2 problems (minimum 10 characters each)"}
                        </div>
                      )}
                    </div>

                    <FormField
                      control={form.control}
                      name="financialLoss"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Financial Impact <span className="text-gray-500">(min 5 chars)</span></FormLabel>
                          <FormControl>
                            <Input 
                              placeholder="e.g., 450K annually in waste, rework, and returns"
                              {...field} 
                            />
                          </FormControl>
                          <FormDescription>
                            Quantify the financial impact of the problems (losses, inefficiencies, opportunity costs)
                          </FormDescription>
                          <div className="text-xs text-gray-500 mt-1">{field.value?.length || 0}/5 characters</div>
                          <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>
              )}

              {/* Step 3: Solution & Implementation */}
              {currentStep === 3 && (
                <div className="space-y-8">
                  {/* Solution Overview */}
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                    <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
                      <Zap className="h-6 w-6 mr-3 text-yellow-600" />
                      Solution Overview
                    </h2>
                    
                    <div className="space-y-6">
                      <div>
                        <FormLabel className="text-base font-semibold">Selection Criteria</FormLabel>
                        <FormDescription className="mb-4">
                          What criteria did you use to evaluate and select this solution? (minimum 2)
                        </FormDescription>
                        <div className="space-y-3">
                          {selectionCriteria.map((criteria, index) => (
                            <div key={index} className="space-y-2">
                              <div className="flex items-center space-x-3">
                                <Input
                                  placeholder={`Criteria ${index + 1} (e.g., Real-time processing capability >50 units/minute)`}
                                  value={criteria}
                                  onChange={(e) => updateSelectionCriteria(index, e.target.value)}
                                  className="flex-1"
                                />
                                {selectionCriteria.length > 2 && (
                                  <Button
                                    type="button"
                                    variant="outline"
                                    size="sm"
                                    onClick={() => removeSelectionCriteria(index)}
                                    className="text-red-600 hover:text-red-700"
                                  >
                                    <X className="h-4 w-4" />
                                  </Button>
                                )}
                              </div>
                              <div className="text-xs text-gray-500 ml-1">{criteria.length}/10 characters minimum</div>
                            </div>
                          ))}
                          
                          {selectionCriteria.length < 5 && (
                            <Button
                              type="button"
                              variant="outline"
                              onClick={addSelectionCriteria}
                              className="flex items-center space-x-2"
                            >
                              <Plus className="h-4 w-4" />
                              <span>Add Another Criteria</span>
                            </Button>
                          )}
                        </div>
                        {/* Show validation error for selection criteria */}
                        {form.formState.errors.selectionCriteria && (
                          <div className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2">
                            {form.formState.errors.selectionCriteria.message || "Please add at least 2 selection criteria (minimum 10 characters each)"}
                          </div>
                        )}
                      </div>

                      <FormField
                        control={form.control}
                        name="selectedVendor"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Selected Vendor/Partner <span className="text-gray-500">(min 2 chars)</span></FormLabel>
                            <FormControl>
                              <Input 
                                placeholder="e.g., VisionTech Systems"
                                {...field} 
                              />
                            </FormControl>
                            <FormDescription>
                              Name of the technology vendor or implementation partner
                            </FormDescription>
                            <div className="text-xs text-gray-500 mt-1">{field.value?.length || 0}/2 characters</div>
                            <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                          </FormItem>
                        )}
                      />

                      {/* Vendor Evaluation (Optional) */}
                      <div className="space-y-3">
                        <FormLabel className="text-base font-semibold">Vendor Evaluation Process (Optional)</FormLabel>
                        <Textarea
                          placeholder="Describe your evaluation/PoC process..."
                          value={vendorProcess}
                          onChange={(e) => setVendorProcess(e.target.value)}
                          className="min-h-[80px]"
                        />
                        <FormLabel className="text-sm font-medium">Vendor Selection Reasons (Optional)</FormLabel>
                        <div className="space-y-2">
                          {vendorSelectionReasons.map((reason, idx) => (
                            <div key={idx} className="flex items-center space-x-3">
                              <Input
                                placeholder={`Reason ${idx + 1}`}
                                value={reason}
                                onChange={(e) => {
                                  const arr = [...vendorSelectionReasons]
                                  arr[idx] = e.target.value
                                  setVendorSelectionReasons(arr)
                                }}
                              />
                              <Button type="button" variant="outline" size="sm" onClick={() => setVendorSelectionReasons(vendorSelectionReasons.filter((_, i) => i !== idx))} className="text-red-600 hover:text-red-700">
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                          ))}
                          <Button type="button" variant="outline" onClick={() => setVendorSelectionReasons([...vendorSelectionReasons, ""]) } className="flex items-center space-x-2">
                            <Plus className="h-4 w-4" />
                            <span>Add Selection Reason</span>
                          </Button>
                        </div>
                      </div>

                      <div>
                        <FormLabel className="text-base font-semibold">Technology Components</FormLabel>
                        <FormDescription className="mb-4">
                          Describe the key technology components of your solution
                        </FormDescription>
                        <div className="space-y-3">
                          {technologyComponents.map((component, index) => (
                            <div key={index} className="space-y-2">
                              <div className="flex items-center space-x-3">
                                <Textarea
                                  placeholder={`Component ${index + 1} (e.g., 4x 4K industrial cameras with specialized LED lighting systems and conveyor integration)`}
                                  value={component}
                                  onChange={(e) => updateTechnologyComponent(index, e.target.value)}
                                  className="flex-1 min-h-[60px]"
                                />
                                {technologyComponents.length > 1 && (
                                  <Button
                                    type="button"
                                    variant="outline"
                                    size="sm"
                                    onClick={() => removeTechnologyComponent(index)}
                                    className="text-red-600 hover:text-red-700 self-start mt-2"
                                  >
                                    <X className="h-4 w-4" />
                                  </Button>
                                )}
                              </div>
                              <div className="text-xs text-gray-500 ml-1">{component.length}/20 characters minimum</div>
                            </div>
                          ))}
                          
                          {technologyComponents.length < 4 && (
                            <Button
                              type="button"
                              variant="outline"
                              onClick={addTechnologyComponent}
                              className="flex items-center space-x-2"
                            >
                              <Plus className="h-4 w-4" />
                              <span>Add Another Component</span>
                            </Button>
                          )}
                        </div>
                        {/* Show validation error for technology components */}
                        {form.formState.errors.technologyComponents && (
                          <div className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2">
                            {form.formState.errors.technologyComponents.message || "Please add at least 1 technology component (minimum 20 characters)"}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Implementation Details */}
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                    <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
                      <Wrench className="h-6 w-6 mr-3 text-purple-600" />
                      Implementation Details
                    </h2>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <FormField
                        control={form.control}
                        name="implementationTime"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Implementation Duration <span className="text-gray-500">(min 3 chars)</span></FormLabel>
                            <FormControl>
                              <Input placeholder="e.g., 6 months implementation" {...field} />
                            </FormControl>
                            <div className="text-xs text-gray-500 mt-1">{field.value?.length || 0}/3 characters</div>
                            <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="totalBudget"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Total Budget <span className="text-gray-500">(min 3 chars)</span></FormLabel>
                            <FormControl>
                              <Input placeholder="e.g., 285,000" {...field} />
                            </FormControl>
                            <FormDescription>
                              Total project budget (amount only, currency symbol will be added automatically)
                            </FormDescription>
                            <div className="text-xs text-gray-500 mt-1">{field.value?.length || 0}/3 characters</div>
                            <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="methodology"
                        render={({ field }) => (
                          <FormItem className="md:col-span-2">
                            <FormLabel>Implementation Methodology <span className="text-gray-500">(min 20 chars)</span></FormLabel>
                            <FormControl>
                              <Textarea 
                                placeholder="e.g., Agile implementation with weekly sprints and continuous stakeholder feedback"
                                className="min-h-[80px]"
                                {...field} 
                              />
                            </FormControl>
                            <FormDescription>
                              Describe the project management approach and methodology used
                            </FormDescription>
                            <div className="text-xs text-gray-500 mt-1">{field.value?.length || 0}/20 characters</div>
                            <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                          </FormItem>
                        )}
                      />
                    </div>

                    {/* Project Team (Optional) */}
                    <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h3 className="font-semibold text-slate-900 mb-2 flex items-center"><Users className="h-4 w-4 mr-2" />Internal Team</h3>
                        <div className="space-y-3">
                          {projectTeamInternal.map((m, idx) => (
                            <div key={idx} className="grid grid-cols-1 md:grid-cols-3 gap-2">
                              <Input placeholder="Role" value={m.role} onChange={(e) => { const arr = [...projectTeamInternal]; arr[idx].role = e.target.value; setProjectTeamInternal(arr) }} />
                              <Input placeholder="Name" value={m.name} onChange={(e) => { const arr = [...projectTeamInternal]; arr[idx].name = e.target.value; setProjectTeamInternal(arr) }} />
                              <div className="flex items-center space-x-2">
                                <Input placeholder="Title" value={m.title} onChange={(e) => { const arr = [...projectTeamInternal]; arr[idx].title = e.target.value; setProjectTeamInternal(arr) }} />
                                <Button type="button" variant="outline" size="sm" onClick={() => setProjectTeamInternal(projectTeamInternal.filter((_, i) => i !== idx))} className="text-red-600 hover:text-red-700">
                                  <X className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                          ))}
                          <Button type="button" variant="outline" onClick={() => setProjectTeamInternal([...projectTeamInternal, { role: "", name: "", title: "" }])} className="flex items-center space-x-2">
                            <Plus className="h-4 w-4" />
                            <span>Add Internal Member</span>
                          </Button>
                        </div>
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-900 mb-2 flex items-center"><Users className="h-4 w-4 mr-2" />Vendor Team</h3>
                        <div className="space-y-3">
                          {projectTeamVendor.map((m, idx) => (
                            <div key={idx} className="grid grid-cols-1 md:grid-cols-3 gap-2">
                              <Input placeholder="Role" value={m.role} onChange={(e) => { const arr = [...projectTeamVendor]; arr[idx].role = e.target.value; setProjectTeamVendor(arr) }} />
                              <Input placeholder="Name" value={m.name} onChange={(e) => { const arr = [...projectTeamVendor]; arr[idx].name = e.target.value; setProjectTeamVendor(arr) }} />
                              <div className="flex items-center space-x-2">
                                <Input placeholder="Title" value={m.title} onChange={(e) => { const arr = [...projectTeamVendor]; arr[idx].title = e.target.value; setProjectTeamVendor(arr) }} />
                                <Button type="button" variant="outline" size="sm" onClick={() => setProjectTeamVendor(projectTeamVendor.filter((_, i) => i !== idx))} className="text-red-600 hover:text-red-700">
                                  <X className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                          ))}
                          <Button type="button" variant="outline" onClick={() => setProjectTeamVendor([...projectTeamVendor, { role: "", name: "", title: "" }])} className="flex items-center space-x-2">
                            <Plus className="h-4 w-4" />
                            <span>Add Vendor Member</span>
                          </Button>
                        </div>
                      </div>
                    </div>

                    {/* Implementation Phases (Optional) */}
                    <div className="mt-8">
                      <h3 className="font-semibold text-slate-900 mb-3">Implementation Phases</h3>
                      <div className="space-y-4">
                        {phases.map((p, idx) => (
                          <div key={idx} className="border border-gray-200 rounded-lg p-4">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
                              <Input placeholder="Phase Name" value={p.phase} onChange={(e) => { const arr = [...phases]; arr[idx].phase = e.target.value; setPhases(arr) }} />
                              <Input placeholder="Duration (e.g., 4 weeks)" value={p.duration} onChange={(e) => { const arr = [...phases]; arr[idx].duration = e.target.value; setPhases(arr) }} />
                              <div className="flex items-center space-x-2">
                                <Input placeholder="Budget (e.g., 25,000)" value={p.budget} onChange={(e) => { const arr = [...phases]; arr[idx].budget = e.target.value; setPhases(arr) }} />
                                <Button type="button" variant="outline" size="sm" onClick={() => setPhases(phases.filter((_, i) => i !== idx))} className="text-red-600 hover:text-red-700">
                                  <X className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                              <Textarea placeholder="Objectives (comma-separated)" value={p.objectives.join(", ")} onChange={(e) => { const arr = [...phases]; arr[idx].objectives = e.target.value.split(",").map(s => s.trim()).filter(Boolean); setPhases(arr) }} />
                              <Textarea placeholder="Key Activities (comma-separated)" value={p.keyActivities.join(", ")} onChange={(e) => { const arr = [...phases]; arr[idx].keyActivities = e.target.value.split(",").map(s => s.trim()).filter(Boolean); setPhases(arr) }} />
                            </div>
                          </div>
                        ))}
                        <Button type="button" variant="outline" onClick={() => setPhases([...phases, { phase: "", duration: "", objectives: [""], keyActivities: [""], budget: "" }])} className="flex items-center space-x-2">
                          <Plus className="h-4 w-4" />
                          <span>Add Phase</span>
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 4: Technical Architecture */}
              {currentStep === 4 && (
                <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                  <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
                    <Wrench className="h-6 w-6 mr-3 text-purple-600" />
                    Technical Architecture (Optional)
                  </h2>
                  <p className="text-slate-600 mb-6">
                    Provide details about your system architecture, components, and technical specifications.
                  </p>
                  
                  <div className="space-y-6">
                    {/* System Overview */}
                    <div>
                      <label className="text-base font-semibold text-slate-900 mb-3 block">System Overview</label>
                      <Textarea
                        placeholder="Describe the overall system architecture and design principles..."
                        value={systemOverview}
                        onChange={(e) => setSystemOverview(e.target.value)}
                        className="min-h-[100px]"
                      />
                      <p className="text-sm text-slate-500 mt-2">High-level description of your technical solution architecture</p>
                    </div>

                    {/* Architecture Components */}
                    <div>
                      <label className="text-base font-semibold text-slate-900 mb-3 block">Architecture Components</label>
                      <div className="space-y-4">
                        {architectureComponents.map((component, index) => (
                          <div key={index} className="border border-slate-200 rounded-lg p-4 bg-slate-50">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                              <div>
                                <label className="text-sm font-medium text-slate-700">Layer Name</label>
                                <Input
                                  placeholder="e.g., Data Layer, Processing Layer"
                                  value={component.layer}
                                  onChange={(e) => {
                                    const updated = [...architectureComponents]
                                    updated[index].layer = e.target.value
                                    setArchitectureComponents(updated)
                                  }}
                                />
                              </div>
                              <div>
                                <label className="text-sm font-medium text-slate-700">Specifications</label>
                                <Input
                                  placeholder="Technical specifications..."
                                  value={component.specifications}
                                  onChange={(e) => {
                                    const updated = [...architectureComponents]
                                    updated[index].specifications = e.target.value
                                    setArchitectureComponents(updated)
                                  }}
                                />
                              </div>
                            </div>
                            <div className="mb-3">
                              <label className="text-sm font-medium text-slate-700">Components (comma-separated)</label>
                              <Textarea
                                placeholder="List the components in this layer..."
                                value={component.components.join(", ")}
                                onChange={(e) => {
                                  const updated = [...architectureComponents]
                                  updated[index].components = e.target.value.split(",").map(c => c.trim()).filter(Boolean)
                                  setArchitectureComponents(updated)
                                }}
                                className="min-h-[60px]"
                              />
                            </div>
                            {architectureComponents.length > 1 && (
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => setArchitectureComponents(architectureComponents.filter((_, i) => i !== index))}
                                className="text-red-600 hover:text-red-700"
                              >
                                <X className="h-4 w-4 mr-1" />
                                Remove Component
                              </Button>
                            )}
                          </div>
                        ))}
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => setArchitectureComponents([...architectureComponents, { layer: "", components: [""], specifications: "" }])}
                          className="flex items-center space-x-2"
                        >
                          <Plus className="h-4 w-4" />
                          <span>Add Architecture Component</span>
                        </Button>
                      </div>
                    </div>

                    {/* Security Measures */}
                    <div>
                      <label className="text-base font-semibold text-slate-900 mb-3 block">Security Measures</label>
                      <div className="space-y-3">
                        {securityMeasures.map((measure, index) => (
                          <div key={index} className="flex items-center space-x-3">
                            <Input
                              placeholder={`Security measure ${index + 1} (e.g., End-to-end encryption, Role-based access control)`}
                              value={measure}
                              onChange={(e) => {
                                const updated = [...securityMeasures]
                                updated[index] = e.target.value
                                setSecurityMeasures(updated)
                              }}
                            />
                            {securityMeasures.length > 1 && (
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => setSecurityMeasures(securityMeasures.filter((_, i) => i !== index))}
                                className="text-red-600 hover:text-red-700"
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        ))}
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => setSecurityMeasures([...securityMeasures, ""])}
                          className="flex items-center space-x-2"
                        >
                          <Plus className="h-4 w-4" />
                          <span>Add Security Measure</span>
                        </Button>
                      </div>
                    </div>

                    {/* Scalability Design */}
                    <div>
                      <label className="text-base font-semibold text-slate-900 mb-3 block">Scalability Design</label>
                      <div className="space-y-3">
                        {scalabilityDesign.map((design, index) => (
                          <div key={index} className="flex items-center space-x-3">
                            <Input
                              placeholder={`Scalability feature ${index + 1} (e.g., Horizontal scaling, Load balancing)`}
                              value={design}
                              onChange={(e) => {
                                const updated = [...scalabilityDesign]
                                updated[index] = e.target.value
                                setScalabilityDesign(updated)
                              }}
                            />
                            {scalabilityDesign.length > 1 && (
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => setScalabilityDesign(scalabilityDesign.filter((_, i) => i !== index))}
                                className="text-red-600 hover:text-red-700"
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        ))}
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => setScalabilityDesign([...scalabilityDesign, ""])}
                          className="flex items-center space-x-2"
                        >
                          <Plus className="h-4 w-4" />
                          <span>Add Scalability Feature</span>
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 5: Results & Challenges */}
              {currentStep === 5 && (
                <div className="space-y-8">
                  {/* Quantitative Results */}
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                    <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
                      <BarChart3 className="h-6 w-6 mr-3 text-green-600" />
                      Results & Impact
                    </h2>
                    
                    <div className="space-y-6">
                      <div>
                        <FormLabel className="text-base font-semibold">Quantitative Results</FormLabel>
                        <FormDescription className="mb-4">
                          Provide specific metrics showing the impact of your implementation (minimum 2)
                        </FormDescription>
                        <div className="space-y-4">
                          {quantitativeResults.map((result, index) => (
                            <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-3 p-4 border border-gray-200 rounded-lg">
                              <Input
                                placeholder="Metric Name (e.g., Defect Rate Reduction)"
                                value={result.metric}
                                onChange={(e) => {
                                  const updated = [...quantitativeResults]
                                  updated[index].metric = e.target.value
                                  setQuantitativeResults(updated)
                                  form.setValue('quantitativeResults', updated)
                                }}
                              />
                              <Input
                                placeholder="Baseline (e.g., 15.0%)"
                                value={result.baseline}
                                onChange={(e) => {
                                  const updated = [...quantitativeResults]
                                  updated[index].baseline = e.target.value
                                  setQuantitativeResults(updated)
                                  form.setValue('quantitativeResults', updated)
                                }}
                              />
                              <Input
                                placeholder="Current (e.g., 2.25%)"
                                value={result.current}
                                onChange={(e) => {
                                  const updated = [...quantitativeResults]
                                  updated[index].current = e.target.value
                                  setQuantitativeResults(updated)
                                  form.setValue('quantitativeResults', updated)
                                }}
                              />
                              <div className="flex items-center space-x-2">
                                <Input
                                  placeholder="Improvement (e.g., 85% reduction)"
                                  value={result.improvement}
                                  onChange={(e) => {
                                    const updated = [...quantitativeResults]
                                    updated[index].improvement = e.target.value
                                    setQuantitativeResults(updated)
                                    form.setValue('quantitativeResults', updated)
                                  }}
                                />
                                {quantitativeResults.length > 2 && (
                                  <Button
                                    type="button"
                                    variant="outline"
                                    size="sm"
                                    onClick={() => {
                                      const updated = quantitativeResults.filter((_, i) => i !== index)
                                      setQuantitativeResults(updated)
                                      form.setValue('quantitativeResults', updated)
                                    }}
                                    className="text-red-600 hover:text-red-700"
                                  >
                                    <X className="h-4 w-4" />
                                  </Button>
                                )}
                              </div>
                            </div>
                          ))}
                          
                          {quantitativeResults.length < 4 && (
                            <Button
                              type="button"
                              variant="outline"
                              onClick={() => {
                                const updated = [...quantitativeResults, { metric: "", baseline: "", current: "", improvement: "" }]
                                setQuantitativeResults(updated)
                                form.setValue('quantitativeResults', updated)
                              }}
                              className="flex items-center space-x-2"
                            >
                              <Plus className="h-4 w-4" />
                              <span>Add Another Result</span>
                            </Button>
                          )}
                        </div>
                        {/* Show validation error for quantitative results */}
                        {form.formState.errors.quantitativeResults && (
                          <div className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2">
                            {form.formState.errors.quantitativeResults.message || 
                             "Please add at least 2 quantitative results with all fields filled"}
                          </div>
                        )}
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <FormField
                          control={form.control}
                          name="roiPercentage"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>ROI Percentage (Optional)</FormLabel>
                              <FormControl>
                                <Input placeholder="e.g., 250% ROI in first year" {...field} />
                              </FormControl>
                              <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                            </FormItem>
                          )}
                        />

                        <FormField
                          control={form.control}
                          name="annualSavings"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>Annual Savings (Optional)</FormLabel>
                              <FormControl>
                                <Input placeholder="e.g., 2,300,000" {...field} />
                              </FormControl>
                              <FormDescription>
                                Annual cost savings amount (number only)
                              </FormDescription>
                              <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                            </FormItem>
                          )}
                        />
                      </div>

                      {/* ROI extras & Qualitative impacts */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <FormLabel className="text-sm font-medium">Total Investment (Optional)</FormLabel>
                          <Input placeholder="e.g., 285,000" value={roiTotalInvestment} onChange={(e) => setRoiTotalInvestment(e.target.value)} />
                        </div>
                        <div>
                          <FormLabel className="text-sm font-medium">3-Year ROI (Optional)</FormLabel>
                          <Input placeholder="e.g., 2,315%" value={roiThreeYearRoi} onChange={(e) => setRoiThreeYearRoi(e.target.value)} />
                        </div>
                      </div>

                      <div>
                        <FormLabel className="text-base font-semibold">Qualitative Impacts (Optional)</FormLabel>
                        <div className="space-y-2 mt-2">
                          {qualitativeImpacts.map((imp, idx) => (
                            <div key={idx} className="flex items-center space-x-3">
                              <Input placeholder={`Impact ${idx + 1}`} value={imp} onChange={(e) => { const arr = [...qualitativeImpacts]; arr[idx] = e.target.value; setQualitativeImpacts(arr) }} />
                              <Button type="button" variant="outline" size="sm" onClick={() => setQualitativeImpacts(qualitativeImpacts.filter((_, i) => i !== idx))} className="text-red-600 hover:text-red-700">
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                          ))}
                          <Button type="button" variant="outline" onClick={() => setQualitativeImpacts([...qualitativeImpacts, ""]) } className="flex items-center space-x-2">
                            <Plus className="h-4 w-4" />
                            <span>Add Impact</span>
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Challenges & Solutions */}
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                    <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
                      <Shield className="h-6 w-6 mr-3 text-orange-600" />
                      Challenges & Solutions
                    </h2>
                    
                    <div className="space-y-6">
                      <FormDescription>
                        Describe the key challenges encountered during implementation and how they were resolved (minimum 1)
                      </FormDescription>
                      
                      <div className="space-y-6">
                        {challengesSolutions.map((item, index) => (
                          <div key={index} className="p-6 border border-orange-200 rounded-lg bg-orange-50">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                              <div>
                                <FormLabel className="text-sm font-medium">Challenge Name <span className="text-gray-500">(min 10 chars)</span></FormLabel>
                                <Input
                                  placeholder="e.g., Data Quality and Labeling"
                                  value={item.challenge}
                                  onChange={(e) => {
                                    const updated = [...challengesSolutions]
                                    updated[index].challenge = e.target.value
                                    setChallengesSolutions(updated)
                                    form.setValue('challengesSolutions', updated)
                                  }}
                                  className="mt-1"
                                />
                                <div className="text-xs text-gray-500 mt-1">{item.challenge.length}/10 characters</div>
                              </div>
                              {challengesSolutions.length > 1 && (
                                <div className="flex justify-end">
                                  <Button
                                    type="button"
                                    variant="outline"
                                    size="sm"
                                    onClick={() => {
                                      const updated = challengesSolutions.filter((_, i) => i !== index)
                                      setChallengesSolutions(updated)
                                      form.setValue('challengesSolutions', updated)
                                    }}
                                    className="text-red-600 hover:text-red-700"
                                  >
                                    <X className="h-4 w-4" />
                                    <span className="ml-1">Remove</span>
                                  </Button>
                                </div>
                              )}
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <FormLabel className="text-sm font-medium">Challenge Description <span className="text-gray-500">(min 20 chars)</span></FormLabel>
                                <Textarea
                                  placeholder="Describe the challenge in detail..."
                                  value={item.description}
                                  onChange={(e) => {
                                    const updated = [...challengesSolutions]
                                    updated[index].description = e.target.value
                                    setChallengesSolutions(updated)
                                    form.setValue('challengesSolutions', updated)
                                  }}
                                  className="mt-1 min-h-[80px]"
                                />
                                <div className="text-xs text-gray-500 mt-1">{item.description.length}/20 characters</div>
                              </div>
                              <div>
                                <FormLabel className="text-sm font-medium">Solution <span className="text-gray-500">(min 20 chars)</span></FormLabel>
                                <Textarea
                                  placeholder="How was it solved..."
                                  value={item.solution}
                                  onChange={(e) => {
                                    const updated = [...challengesSolutions]
                                    updated[index].solution = e.target.value
                                    setChallengesSolutions(updated)
                                    form.setValue('challengesSolutions', updated)
                                  }}
                                  className="mt-1 min-h-[80px]"
                                />
                                <div className="text-xs text-gray-500 mt-1">{item.solution.length}/20 characters</div>
                              </div>
                            </div>
                            <div className="mt-3">
                              <FormLabel className="text-sm font-medium">Outcome <span className="text-gray-500">(min 10 chars)</span></FormLabel>
                              <Textarea
                                placeholder="What was the result..."
                                value={item.outcome}
                                onChange={(e) => {
                                  const updated = [...challengesSolutions]
                                  updated[index].outcome = e.target.value
                                  setChallengesSolutions(updated)
                                  form.setValue('challengesSolutions', updated)
                                }}
                                className="mt-1 min-h-[80px]"
                              />
                              <div className="text-xs text-gray-500 mt-1">{item.outcome.length}/10 characters</div>
                            </div>
                          </div>
                        ))}
                        
                        {challengesSolutions.length < 4 && (
                          <Button
                            type="button"
                            variant="outline"
                            onClick={() => {
                              const updated = [...challengesSolutions, { challenge: "", description: "", solution: "", outcome: "" }]
                              setChallengesSolutions(updated)
                              form.setValue('challengesSolutions', updated)
                            }}
                            className="flex items-center space-x-2"
                          >
                            <Plus className="h-4 w-4" />
                            <span>Add Another Challenge</span>
                          </Button>
                        )}
                      </div>
                      {/* Show validation error for challenges & solutions */}
                      {form.formState.errors.challengesSolutions && (
                        <div className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2">
                          {form.formState.errors.challengesSolutions.message || "Please add at least 1 challenge with all fields filled"}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Step 6: Location & Contact */}
              {currentStep === 6 && (
                <div className="space-y-8">
                  {/* Location */}
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                    <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
                      <MapPin className="h-6 w-6 mr-3 text-blue-600" />
                      Factory Location
                    </h2>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                      <FormField
                        control={form.control}
                        name="city"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>City <span className="text-gray-500">(2-50 chars)</span></FormLabel>
                            <FormControl>
                              <Input placeholder="e.g., Riyadh" {...field} />
                            </FormControl>
                            <div className="text-xs text-gray-500 mt-1">{field.value?.length || 0}/50 characters</div>
                            <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                          </FormItem>
                        )}
                      />
                    </div>

                    <div className="mb-6">
                      <h3 className="text-lg font-semibold text-slate-900 mb-3">Pin Your Factory Location</h3>
                      <p className="text-slate-600 mb-4">Click on the map to set your factory's location</p>
                      <LocationPicker 
                        onLocationSelect={handleLocationSelect}
                        defaultLat={form.watch('latitude')}
                        defaultLng={form.watch('longitude')}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm text-slate-600">
                      <div>
                        <span className="font-medium">Latitude:</span> {form.watch('latitude').toFixed(6)}
                      </div>
                      <div>
                        <span className="font-medium">Longitude:</span> {form.watch('longitude').toFixed(6)}
                      </div>
                    </div>
                  </div>

                  {/* Images */}
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                    <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
                      <Upload className="h-6 w-6 mr-3 text-blue-600" />
                      Images
                    </h2>
                    
                    <ImageUpload 
                      onImagesUpdate={handleImagesUpdate}
                      maxImages={5}
                    />
                    {/* Show validation error for images */}
                    {form.formState.errors.images && (
                      <div className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2">
                        {form.formState.errors.images.message || "Please upload at least 1 image"}
                      </div>
                    )}
                  </div>

                  {/* Contact Information */}
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                    <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
                      <Users className="h-6 w-6 mr-3 text-purple-600" />
                      Contact Information (Optional)
                    </h2>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <FormField
                        control={form.control}
                        name="contactPerson"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Contact Person</FormLabel>
                            <FormControl>
                              <Input placeholder="e.g., Ahmed Al-Faisal" {...field} />
                            </FormControl>
                            <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="contactTitle"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Title/Position</FormLabel>
                            <FormControl>
                              <Input placeholder="e.g., Operations Manager" {...field} />
                            </FormControl>
                            <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>

                  {/* Tags (Optional) */}
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                    <h2 className="text-2xl font-bold text-slate-900 mb-6">Tags (Optional)</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <FormLabel className="text-sm font-medium">Industry Tags</FormLabel>
                        <div className="space-y-2 mt-2">
                          {industryTags.map((tag, idx) => (
                            <div key={idx} className="flex items-center space-x-3">
                              <Input value={tag} placeholder="e.g., Electronics" onChange={(e) => { const arr = [...industryTags]; arr[idx] = e.target.value; setIndustryTags(arr) }} />
                              <Button type="button" variant="outline" size="sm" onClick={() => setIndustryTags(industryTags.filter((_, i) => i !== idx))} className="text-red-600 hover:text-red-700">
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                          ))}
                          <Button type="button" variant="outline" onClick={() => setIndustryTags([...industryTags, ""]) } className="flex items-center space-x-2">
                            <Plus className="h-4 w-4" />
                            <span>Add Industry Tag</span>
                          </Button>
                        </div>
                      </div>
                      <div>
                        <FormLabel className="text-sm font-medium">Technology Tags</FormLabel>
                        <div className="space-y-2 mt-2">
                          {technologyTags.map((tag, idx) => (
                            <div key={idx} className="flex items-center space-x-3">
                              <Input value={tag} placeholder="e.g., Computer Vision" onChange={(e) => { const arr = [...technologyTags]; arr[idx] = e.target.value; setTechnologyTags(arr) }} />
                              <Button type="button" variant="outline" size="sm" onClick={() => setTechnologyTags(technologyTags.filter((_, i) => i !== idx))} className="text-red-600 hover:text-red-700">
                                <X className="h-4 w-4" />
                              </Button>
                            </div>
                          ))}
                          <Button type="button" variant="outline" onClick={() => setTechnologyTags([...technologyTags, ""]) } className="flex items-center space-x-2">
                            <Plus className="h-4 w-4" />
                            <span>Add Technology Tag</span>
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 7: Review & Submit */}
              {currentStep === 7 && (
                <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                  <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
                    <CheckCircle className="h-6 w-6 mr-3 text-blue-600" />
                    Review & Submit
                  </h2>
                  
                  <div className="space-y-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h3 className="font-semibold text-slate-900 mb-2">Title</h3>
                        <p className="text-slate-600">{form.watch('title')}</p>
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-900 mb-2">Category</h3>
                        <p className="text-slate-600">{form.watch('category')}</p>
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-900 mb-2">Factory</h3>
                        <p className="text-slate-600">{form.watch('factoryName')}</p>
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-900 mb-2">Location</h3>
                        <p className="text-slate-600">{form.watch('city')}</p>
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-slate-900 mb-2">Executive Summary</h3>
                      <p className="text-slate-600">{form.watch('description')}</p>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-slate-900 mb-2">Financial Impact</h3>
                      <p className="text-slate-600">{form.watch('financialLoss')}</p>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-slate-900 mb-2">Selected Vendor</h3>
                      <p className="text-slate-600">{form.watch('selectedVendor')}</p>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-slate-900 mb-2">Implementation</h3>
                      <p className="text-slate-600">{form.watch('implementationTime')} • Budget: {form.watch('totalBudget')}</p>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-slate-900 mb-2">Images</h3>
                      <p className="text-slate-600">{uploadedImages.length} image(s) uploaded</p>
                    </div>
                  </div>
                </div>
              )}


              {/* Navigation Buttons */}
              <div className="flex justify-between items-center pt-8">
                <Button
                  type="button"
                  variant="outline"
                  onClick={prevStep}
                  disabled={currentStep === 1}
                  className="flex items-center space-x-2"
                >
                  <span>Previous</span>
                </Button>

                <div className="flex space-x-4">
                  {currentStep < 7 ? (
                    <Button
                      type="button"
                      onClick={handleNext}
                      className="bg-blue-600 hover:bg-blue-700 text-white flex items-center space-x-2"
                    >
                      <span>Next</span>
                    </Button>
                  ) : (
                    <Button
                      type="submit"
                      disabled={isSubmitting}
                      className="bg-green-600 hover:bg-green-700 text-white flex items-center space-x-2"
                    >
                      {isSubmitting ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          <span>Submitting...</span>
                        </>
                      ) : (
                        <>
                          <Save className="h-4 w-4" />
                          <span>{isEditMode ? 'Update Use Case' : 'Submit Use Case'}</span>
                        </>
                      )}
                    </Button>
                  )}
                </div>
              </div>
            </form>
          </Form>
        </div>
      </div>
    </div>
  )
}