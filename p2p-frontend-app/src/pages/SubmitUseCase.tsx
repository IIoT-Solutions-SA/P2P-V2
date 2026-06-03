import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
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
  Users,
  Lightbulb,
  Calendar,
  AlertCircle,
  Cloud,
  Loader2,
  FileText
} from "lucide-react"
import LocationPicker from '@/components/LocationPicker'
import { FileDropZone } from '@/components/ui/FileDropZone'

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
    .max(15, "Maximum 15 components allowed"),
    
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
    baseline: z.string().min(1, "Baseline value required"),
    current: z.string().min(1, "Current value required"),
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
    .max(5, "Maximum 5 images allowed")
    .optional()
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
  const navigate = useNavigate()
  const editUseCaseId = searchParams.get('edit')
  const isEditMode = !!editUseCaseId

  // Auto-save form data to localStorage
  const FORM_STORAGE_KEY = `usecase_form_${editUseCaseId || 'new'}`

  const [currentStep, setCurrentStep] = useState(1)
  const [uploadedImages, setUploadedImages] = useState<File[]>([])
  const [existingImages, setExistingImages] = useState<string[]>([])  // Store existing image URLs
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [isLoadingExistingData, setIsLoadingExistingData] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  // Autosave status tracking
  const [autosaveStatus, setAutosaveStatus] = useState<'idle' | 'saving' | 'saved' | 'failed'>('idle')
  const [lastSavedAt, setLastSavedAt] = useState<number | null>(null)

  // Server draft tracking (GROUP C)
  const [draftId, setDraftId] = useState<string | null>(null)
  const [savingDraft, setSavingDraft] = useState(false)
  const [serverDraftSaved, setServerDraftSaved] = useState(false)

  // Start New Use Case dialog
  const [showNewUseCaseDialog, setShowNewUseCaseDialog] = useState(false)

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

  // Lessons Learned (optional) - Start with one empty item
  const [lessonsLearned, setLessonsLearned] = useState<Array<{
    category: string
    lesson: string
    description: string
    recommendation: string
  }>>([{ category: "", lesson: "", description: "", recommendation: "" }])

  // Future Roadmap (optional) - Start with one empty item
  const [futureRoadmap, setFutureRoadmap] = useState<Array<{
    timeline: string
    initiative: string
    description: string
    expected_benefit: string
  }>>([{ timeline: "", initiative: "", description: "", expected_benefit: "" }])

  // ROI extras (optional)
  const [roiTotalInvestment, setRoiTotalInvestment] = useState<string>("")
  const [roiThreeYearRoi, setRoiThreeYearRoi] = useState<string>("")
  const [quantitativeResults, setQuantitativeResults] = useState<Array<{
    metric: string
    baseline: string
    current: string
    improvement: string
  }>>(isEditMode ? [] : [
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
    mode: 'onBlur', // Only validate on blur to prevent issues while typing
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
      quantitativeResults: isEditMode ? [] : [
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
  // Auto-save form data to localStorage on form value changes
  useEffect(() => {
    // Subscribe to form changes
    const subscription = form.watch((_value, { name: _name, type: _type }) => {
      // Trigger save whenever form values change
      setAutosaveStatus('saving')

      const saveToLocalStorage = () => {
        try {
          // Get fresh form values
          const formValues = form.getValues()

          // Capture all form state including dynamic arrays
          const completeFormState = {
            formData: formValues,
            currentStep,
            timestamp: Date.now(),
            // Include dynamic states
            specificProblems,
            selectionCriteria,
            technologyComponents,
            vendorProcess,
            vendorSelectionReasons,
            projectTeamInternal,
            projectTeamVendor,
            phases,
            // Include existing images in edit mode
            existingImages: isEditMode ? existingImages : [],
            // Note: uploaded File objects can't be serialized, users will need to re-upload
            uploadedImagesCount: uploadedImages.length
          }

          localStorage.setItem(FORM_STORAGE_KEY, JSON.stringify(completeFormState))
          setAutosaveStatus('saved')
          setLastSavedAt(Date.now())
          console.log('Form auto-saved successfully at step', currentStep)
        } catch (error) {
          console.error('Failed to save form data:', error)
          setAutosaveStatus('failed')
          // Show user-friendly error notification
          if (error instanceof Error && error.name === 'QuotaExceededError') {
            console.error('localStorage quota exceeded. Please clear some browser data.')
          }
        }
      }

      // Debounce save by 1 second
      const timeoutId = setTimeout(saveToLocalStorage, 1000)
      return () => clearTimeout(timeoutId)
    })

    return () => subscription.unsubscribe()
  }, [
    form,
    currentStep,
    FORM_STORAGE_KEY,
    specificProblems,
    selectionCriteria,
    technologyComponents,
    vendorProcess,
    vendorSelectionReasons,
    projectTeamInternal,
    projectTeamVendor,
    phases,
    existingImages,
    uploadedImages.length,
    isEditMode
  ])

  // Additional autosave trigger for step changes and dynamic array updates
  useEffect(() => {
    // Skip on initial mount
    if (currentStep === 1 && !lastSavedAt) return

    const saveOnChanges = () => {
      try {
        const formValues = form.getValues()
        const completeFormState = {
          formData: formValues,
          currentStep,
          timestamp: Date.now(),
          specificProblems,
          selectionCriteria,
          technologyComponents,
          vendorProcess,
          vendorSelectionReasons,
          projectTeamInternal,
          projectTeamVendor,
          phases,
          existingImages: isEditMode ? existingImages : [],
          uploadedImagesCount: uploadedImages.length
        }

        localStorage.setItem(FORM_STORAGE_KEY, JSON.stringify(completeFormState))
        setAutosaveStatus('saved')
        setLastSavedAt(Date.now())
        console.log('Form auto-saved on state change at step', currentStep)
      } catch (error) {
        console.error('Failed to save on state change:', error)
        setAutosaveStatus('failed')
      }
    }

    // Debounce to avoid too frequent saves
    const timeoutId = setTimeout(saveOnChanges, 500)
    return () => clearTimeout(timeoutId)
  }, [
    currentStep,
    specificProblems,
    selectionCriteria,
    technologyComponents,
    vendorProcess,
    vendorSelectionReasons,
    projectTeamInternal,
    projectTeamVendor,
    phases,
    existingImages,
    uploadedImages.length,
    isEditMode,
    FORM_STORAGE_KEY,
    form
  ])

  // Update timestamp display every minute
  useEffect(() => {
    if (autosaveStatus === 'saved' && lastSavedAt) {
      const interval = setInterval(() => {
        // Force re-render to update the "X minutes ago" text
        setLastSavedAt(lastSavedAt)
      }, 60000) // Update every minute

      return () => clearInterval(interval)
    }
  }, [autosaveStatus, lastSavedAt])

  // Load saved form data on mount and reset submission state
  useEffect(() => {
    // Always reset the submission state when component mounts
    // This handles browser back navigation and direct navigation to the page
    setIsSubmitted(false)

    // Load autosaved data for both new and edit modes
    // In edit mode, localStorage takes precedence over server data if it's newer
    try {
      const saved = localStorage.getItem(FORM_STORAGE_KEY)
      if (saved) {
        const savedData = JSON.parse(saved)
        const {
          formData,
          currentStep: savedStep,
          timestamp,
          wasSubmitted,
          specificProblems: savedProblems,
          selectionCriteria: savedCriteria,
          technologyComponents: savedTech,
          vendorProcess: savedVendorProcess,
          vendorSelectionReasons: savedVendorReasons,
          projectTeamInternal: savedTeamInternal,
          projectTeamVendor: savedTeamVendor,
          phases: savedPhases,
          existingImages: savedExistingImages
        } = savedData

        // If form was previously submitted successfully, clear localStorage and don't restore
        if (wasSubmitted) {
          console.log('Previous submission detected - clearing saved data')
          localStorage.removeItem(FORM_STORAGE_KEY)
          return
        }

        // Only restore if saved within last 24 hours
        if (Date.now() - timestamp < 24 * 60 * 60 * 1000) {
          // Automatically restore saved form data without asking
          Object.keys(formData).forEach(key => {
            form.setValue(key as any, formData[key])
          })
          setCurrentStep(savedStep)

          // Restore dynamic arrays and states
          if (savedProblems) setSpecificProblems(savedProblems)
          if (savedCriteria) setSelectionCriteria(savedCriteria)
          if (savedTech) setTechnologyComponents(savedTech)
          if (savedVendorProcess) setVendorProcess(savedVendorProcess)
          if (savedVendorReasons) setVendorSelectionReasons(savedVendorReasons)
          if (savedTeamInternal) setProjectTeamInternal(savedTeamInternal)
          if (savedTeamVendor) setProjectTeamVendor(savedTeamVendor)
          if (savedPhases) setPhases(savedPhases)
          if (savedExistingImages) setExistingImages(savedExistingImages)

          console.log('Auto-saved form data restored', isEditMode ? '(edit mode)' : '(new form)')
        } else {
          // Data is too old, clear it
          localStorage.removeItem(FORM_STORAGE_KEY)
        }
      }
    } catch (error) {
      console.error('Failed to load saved form data:', error)
      // Don't crash the app if restoration fails, just log the error
    }
  }, [])

  // ===== DRAFT MAPPING FUNCTIONS (GROUP C) =====

  // Map form data to backend draft format (camelCase → backend format)
  const mapFormDataToDraft = () => {
    const formValues = form.getValues()
    return {
      draftId: draftId || undefined, // Include draftId if updating existing draft
      currentStep,
      title: formValues.title,
      subtitle: formValues.subtitle,
      description: formValues.description,
      category: formValues.category,
      factoryName: formValues.factoryName,
      city: formValues.city,
      latitude: formValues.latitude,
      longitude: formValues.longitude,
      industryContext: formValues.industryContext,
      specificProblems,
      financialLoss: formValues.financialLoss,
      selectionCriteria,
      selectedVendor: form.getValues('selectedVendor'),
      technologyComponents,
      implementationTime: formValues.implementationTime,
      totalBudget: formValues.totalBudget,
      methodology: formValues.methodology,
      quantitativeResults,
      roiPercentage: formValues.roiPercentage,
      annualSavings: formValues.annualSavings,
      challengesSolutions,
      contactPerson: formValues.contactPerson,
      contactTitle: formValues.contactTitle,
      images: existingImages,
      industryTags,
      technologyTags,
      vendorProcess,
      vendorSelectionReasons,
      projectTeamInternal,
      projectTeamVendor,
      phases,
      qualitativeImpacts,
      roiTotalInvestment,
      roiThreeYearRoi
    }
  }

  // Restore draft data to form (backend format → frontend state)
  const restoreDraftToForm = (draft: any) => {
    try {
      // Restore form fields
      if (draft.title) form.setValue('title', draft.title)
      if (draft.subtitle) form.setValue('subtitle', draft.subtitle)
      if (draft.description) form.setValue('description', draft.description)
      if (draft.category) form.setValue('category', draft.category)
      if (draft.factoryName) form.setValue('factoryName', draft.factoryName)
      if (draft.city) form.setValue('city', draft.city)
      if (draft.latitude) form.setValue('latitude', draft.latitude)
      if (draft.longitude) form.setValue('longitude', draft.longitude)
      if (draft.industryContext) form.setValue('industryContext', draft.industryContext)
      if (draft.financialLoss) form.setValue('financialLoss', draft.financialLoss)
      if (draft.selectedVendor) form.setValue('selectedVendor', draft.selectedVendor)
      if (draft.implementationTime) form.setValue('implementationTime', draft.implementationTime)
      if (draft.totalBudget) form.setValue('totalBudget', draft.totalBudget)
      if (draft.methodology) form.setValue('methodology', draft.methodology)
      if (draft.roiPercentage) form.setValue('roiPercentage', draft.roiPercentage)
      if (draft.annualSavings) form.setValue('annualSavings', draft.annualSavings)
      if (draft.contactPerson) form.setValue('contactPerson', draft.contactPerson)
      if (draft.contactTitle) form.setValue('contactTitle', draft.contactTitle)

      // Restore dynamic arrays
      if (draft.specificProblems) setSpecificProblems(draft.specificProblems)
      if (draft.selectionCriteria) setSelectionCriteria(draft.selectionCriteria)
      if (draft.technologyComponents) setTechnologyComponents(draft.technologyComponents)
      if (draft.quantitativeResults) setQuantitativeResults(draft.quantitativeResults)
      if (draft.challengesSolutions) setChallengesSolutions(draft.challengesSolutions)
      if (draft.vendorProcess) setVendorProcess(draft.vendorProcess)
      if (draft.vendorSelectionReasons) setVendorSelectionReasons(draft.vendorSelectionReasons)
      if (draft.projectTeamInternal) setProjectTeamInternal(draft.projectTeamInternal)
      if (draft.projectTeamVendor) setProjectTeamVendor(draft.projectTeamVendor)
      if (draft.phases) setPhases(draft.phases)
      if (draft.images) setExistingImages(draft.images)

      // Restore current step
      if (draft.currentStep) setCurrentStep(draft.currentStep)

      console.log('Draft data restored to form successfully')
    } catch (error) {
      console.error('Error restoring draft to form:', error)
    }
  }

  useEffect(() => {
    if (isEditMode && editUseCaseId) {
      const fetchExistingUseCase = async () => {
        // Check if we have newer localStorage data first
        const saved = localStorage.getItem(FORM_STORAGE_KEY)

        if (saved) {
          try {
            const savedData = JSON.parse(saved)
            const timestamp = savedData.timestamp || 0
            // If localStorage data is less than 5 minutes old, prioritize it
            if (Date.now() - timestamp < 5 * 60 * 1000) {
              console.log('Edit Mode: Found recent localStorage data (< 5 min), skipping server fetch')
              setIsLoadingExistingData(false)
              return // Don't overwrite with server data
            }
          } catch (e) {
            console.error('Error checking localStorage:', e)
          }
        }

        setIsLoadingExistingData(true)
        try {
          const response = await fetch(buildApiUrl(`/api/v1/use-cases/by-id/${editUseCaseId}`), {
            credentials: 'include'
          })
          if (!response.ok) {
            throw new Error('Failed to fetch use case data')
          }
          const data = await response.json()

          console.log('Edit Mode - Loaded use case data:', data)

          // Pre-populate form fields with existing data
          form.setValue('title', data.title || '')
          form.setValue('subtitle', data.subtitle || '')
          form.setValue('description', data.executive_summary || data.description || '')
          form.setValue('category', data.category || '')
          form.setValue('factoryName', data.factory_name || data.factoryName || '')
          // Set city - backend stores city as "region"
          const cityValue = data.region || data.city || data.location?.city || ''
          console.log('City Debug:', {
            'data.region': data.region,
            'data.city': data.city,
            'data.location': data.location,
            'cityValue set to': cityValue
          })
          form.setValue('city', cityValue)

          // Force the Select to update by setting it after a small delay
          if (cityValue) {
            setTimeout(() => {
              console.log('Setting city again after delay to:', cityValue)
              form.setValue('city', cityValue)
            }, 100)
          }
          // Load location coordinates - check multiple possible fields
          const lat = data.location?.lat || data.latitude || 24.7136
          const lng = data.location?.lng || data.longitude || 46.6753
          form.setValue('latitude', lat)
          form.setValue('longitude', lng)
          console.log('Location loaded for edit:', { lat, lng })
          
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
          
          // Results - Load quantitative metrics/results
          if (data.results?.quantitative_results?.length > 0) {
            const results = data.results.quantitative_results
            setQuantitativeResults(results)
            form.setValue('quantitativeResults', results)
          } else if (data.results?.quantitative_metrics?.length > 0) {
            const metrics = data.results.quantitative_metrics
            setQuantitativeResults(metrics)
            form.setValue('quantitativeResults', metrics)
          }
          
          form.setValue('roiPercentage', data.roi_percentage || '')
          // Check multiple possible locations for annual savings
          form.setValue('annualSavings', data.results?.annual_savings || data.annualSavings || data.results?.roi_analysis?.annual_savings || '')
          
          // Challenges & Solutions
          if (data.results?.challenges_solutions?.length > 0) {
            const challenges = data.results.challenges_solutions
            setChallengesSolutions(challenges)
            form.setValue('challengesSolutions', challenges)
          } else if (data.challenges_and_solutions?.length > 0) {
            // Alternative field name
            setChallengesSolutions(data.challenges_and_solutions)
            form.setValue('challengesSolutions', data.challenges_and_solutions)
          } else {
            // If no challenges exist, set to empty array (not the default with one empty item)
            setChallengesSolutions([{ challenge: "", description: "", solution: "", outcome: "" }])
            form.setValue('challengesSolutions', [{ challenge: "", description: "", solution: "", outcome: "" }])
          }

          // Contact
          form.setValue('contactPerson', data.contact_person || '')
          form.setValue('contactTitle', data.contact_title || '')

          // Load ALL optional fields that might exist
          // Vendor evaluation details
          if (data.solution_details?.vendor_evaluation) {
            const vendorEval = data.solution_details.vendor_evaluation
            if (vendorEval.process) setVendorProcess(vendorEval.process)
            if (vendorEval.selection_reasons) setVendorSelectionReasons(vendorEval.selection_reasons)
          }

          // Implementation phases
          if (data.implementation_details?.phases?.length > 0) {
            setPhases(data.implementation_details.phases)
          }

          // Project team
          if (data.implementation_details?.project_team) {
            const team = data.implementation_details.project_team
            if (team.internal) setProjectTeamInternal(team.internal)
            if (team.vendor) setProjectTeamVendor(team.vendor)
          }

          // Qualitative impacts
          if (data.results?.qualitative_impacts?.length > 0) {
            setQualitativeImpacts(data.results.qualitative_impacts)
          }

          // ROI details (check multiple possible field locations)
          if (data.results?.roi_details || data.results?.roi_analysis) {
            const roi = data.results.roi_details || data.results.roi_analysis
            if (roi.total_investment) setRoiTotalInvestment(roi.total_investment)
            if (roi.three_year_roi) setRoiThreeYearRoi(roi.three_year_roi)
          }
          // Also check if ROI fields are at the root level
          if (data.roiTotalInvestment) setRoiTotalInvestment(data.roiTotalInvestment)
          if (data.roiThreeYearRoi) setRoiThreeYearRoi(data.roiThreeYearRoi)

          // Tags
          if (data.industry_tags?.length > 0) {
            setIndustryTags(data.industry_tags)
          }
          if (data.technology_tags?.length > 0) {
            setTechnologyTags(data.technology_tags)
          }

          // Images - store existing images separately
          if (data.images?.length > 0) {
            console.log('Existing images found:', data.images)
            console.log('Image URLs:', JSON.stringify(data.images, null, 2))
            // Validate and clean up image URLs
            const validImages = data.images.filter((img: any) => {
              if (typeof img === 'string' && img.length > 0) {
                console.log('Valid image URL:', img)
                return true
              }
              console.warn('Invalid image:', img)
              return false
            })
            setExistingImages(validImages)  // Store existing image URLs
          }

          // Technical Architecture (if it exists)
          if (data.technical_architecture) {
            console.log('Technical architecture found:', data.technical_architecture)
            const techArch = data.technical_architecture

            if (techArch.system_overview) {
              setSystemOverview(techArch.system_overview)
            }

            if (techArch.architecture_components?.length > 0) {
              // Ensure components is always an array
              const formattedComponents = techArch.architecture_components.map((comp: any) => ({
                layer: comp.layer || "",
                components: Array.isArray(comp.components) ? comp.components :
                            (typeof comp.components === 'string' ? [comp.components] : []),
                specifications: comp.specifications || ""
              }))
              setArchitectureComponents(formattedComponents)
            }

            if (techArch.security_measures?.length > 0) {
              setSecurityMeasures(techArch.security_measures)
            }

            if (techArch.scalability_design?.length > 0) {
              setScalabilityDesign(techArch.scalability_design)
            }
          }

          // Lessons Learned (if exists, otherwise keep default)
          if (data.lessons_learned?.length > 0) {
            setLessonsLearned(data.lessons_learned)
          }

          // Future Roadmap (if exists, otherwise keep default)
          if (data.future_roadmap?.length > 0) {
            setFutureRoadmap(data.future_roadmap)
          }

          // NOTE: Removed duplicate check for quantitative_metrics - already handled above

          console.log('All form data loaded successfully for edit mode')
          
        } catch (error) {
          console.error('Error fetching existing use case:', error)
        } finally {
          setIsLoadingExistingData(false)
        }
      }
      
      fetchExistingUseCase()
    }
  }, [isEditMode, editUseCaseId])

  // ===== DRAFT RESUME ON MOUNT (GROUP C Phase 1.3) =====
  useEffect(() => {
    const draftIdParam = searchParams.get('draft')
    if (draftIdParam && !isEditMode) {
      fetchServerDraft(draftIdParam)
    }
  }, [searchParams, isEditMode])

  // ===== DRAFT FETCH AND SAVE HANDLERS (GROUP C Phases 1.3 & 1.4) =====

  const fetchServerDraft = async (id: string) => {
    try {
      console.log('Fetching server draft:', id)
      const res = await fetch(buildApiUrl(`/api/v1/use-cases/drafts/${id}`), {
        credentials: 'include'
      })

      console.log('Draft fetch response status:', res.status)

      if (res.ok) {
        const draft = await res.json()
        console.log('Draft data received:', draft)
        restoreDraftToForm(draft)
        setDraftId(id)
        console.log('Draft restored successfully')
      } else {
        const errorData = await res.json().catch(() => ({}))
        console.error('Failed to fetch draft:', res.status, errorData)
        alert(`Failed to load draft (${res.status}). ${errorData.detail || 'It may have been deleted.'}`)
      }
    } catch (error) {
      console.error('Error fetching draft:', error)
      alert('Error loading draft. Please check console for details.')
    }
  }

  const handleSaveDraft = async () => {
    setSavingDraft(true)
    setServerDraftSaved(false)

    try {
      const payload = mapFormDataToDraft()

      console.log('Saving draft to server...')
      const res = await fetch(buildApiUrl('/api/v1/use-cases/drafts'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
      })

      if (res.ok) {
        const data = await res.json()
        const savedDraftId = data.draft_id

        setDraftId(savedDraftId)
        setServerDraftSaved(true)

        // Update URL with draft ID (without reload)
        if (!searchParams.get('draft')) {
          window.history.replaceState({}, '', `/submit?draft=${savedDraftId}`)
        }

        // Hide success message after 3 seconds
        setTimeout(() => setServerDraftSaved(false), 3000)

        console.log('Draft saved to server:', savedDraftId)
      } else {
        const error = await res.json().catch(() => ({}))
        throw new Error(error.detail || 'Failed to save draft')
      }
    } catch (error) {
      console.error('Error saving draft:', error)
      alert('Failed to save draft to server. Please try again.')
    } finally {
      setSavingDraft(false)
    }
  }

  // Clear all form data to start a new use case
  const clearAllFormData = () => {
    form.reset()
    setCurrentStep(1)
    setDraftId(null)
    setSpecificProblems([])
    setSelectionCriteria([])
    setTechnologyComponents([])
    setVendorSelectionReasons([])
    setProjectTeamInternal([])
    setProjectTeamVendor([])
    setPhases([])
    setQuantitativeResults([])
    setQualitativeImpacts([])
    setChallengesSolutions([])
    setUploadedImages([])
    setExistingImages([])
    localStorage.removeItem(FORM_STORAGE_KEY)
    setAutosaveStatus('idle')
    setLastSavedAt(null)
    setServerDraftSaved(false)
  }

  // Handle "Start New Use Case" with confirmation dialog
  const handleStartNew = async (action: 'save' | 'discard' | 'cancel') => {
    setShowNewUseCaseDialog(false)

    if (action === 'cancel') return

    if (action === 'save') {
      await handleSaveDraft()
    } else if (action === 'discard' && draftId) {
      // Delete draft from server
      try {
        await fetch(buildApiUrl(`/api/v1/use-cases/drafts/${draftId}`), {
          method: 'DELETE',
          credentials: 'include'
        })
        console.log('Draft deleted from server')
      } catch (error) {
        console.error('Error deleting draft:', error)
      }
    }

    // Clear everything and start fresh
    clearAllFormData()
    navigate('/submit') // Remove ?draft param from URL
  }

  // Predefined cities for dropdown
  const SAUDI_CITIES = [
    "Riyadh", "Jeddah", "Makkah", "Madinah", "Dammam", "Khobar",
    "Dhahran", "Jubail", "Yanbu", "Tabuk", "Taif", "Buraydah",
    "Khamis Mushait", "Abha", "Najran", "Jizan", "Hail", "Al-Kharj",
    "Hofuf", "Qatif", "Unaizah", "Arar", "Sakaka", "Al-Bahah"
  ].sort()

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
    if (technologyComponents.length < 15) {
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

  /** Parse a FastAPI 422 validation error body into a human-readable string */
  const parseApiError = async (response: Response): Promise<string> => {
    try {
      const data = await response.json()
      if (Array.isArray(data?.detail)) {
        return data.detail
          .map((e: any) => {
            const field = e.loc?.filter((l: any) => l !== 'body').join(' → ') || 'field'
            return `${field}: ${e.msg?.replace('Value error, ', '') ?? 'Invalid value'}`
          })
          .join('\n')
      }
      if (data?.message) return data.message
      if (data?.detail && typeof data.detail === 'string') return data.detail
    } catch {}
    return `Request failed (${response.status})`
  }

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true)
    setSubmitError(null)
    try {
      // First, create the use case WITHOUT images to get the ID
      // Debug: Log lessons learned and roadmap
      console.log('Lessons Learned:', lessonsLearned)
      console.log('Future Roadmap:', futureRoadmap)

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
        images: isEditMode ? existingImages : [], // In edit mode, keep existing images by default
        // Tags
        industryTags,
        technologyTags,
        // Technical Architecture (optional)
        ...(systemOverview || architectureComponents.some(c => c.layer) || securityMeasures.some(s => s) || scalabilityDesign.some(s => s) ? {
          technical_architecture: {
            system_overview: systemOverview || undefined,
            architecture_components: architectureComponents.filter(c => c.layer).length > 0 ? architectureComponents.filter(c => c.layer) : undefined,
            security_measures: securityMeasures.filter(s => s).length > 0 ? securityMeasures.filter(s => s) : undefined,
            scalability_design: scalabilityDesign.filter(s => s).length > 0 ? scalabilityDesign.filter(s => s) : undefined
          }
        } : {}),
        // Lessons Learned (optional)
        ...(lessonsLearned.length > 0 && lessonsLearned.some(l => l.lesson) ? {
          lessons_learned: lessonsLearned.filter(l => l.lesson)
        } : {}),
        // Future Roadmap (optional)
        ...(futureRoadmap.length > 0 && futureRoadmap.some(r => r.initiative) ? {
          future_roadmap: futureRoadmap.filter(r => r.initiative)
        } : {}),
      }

      // Use PUT for edit mode, POST for create mode
      // Debug: Log the full payload
      console.log('Full Payload being sent:', JSON.stringify(payload, null, 2))

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
        const message = await parseApiError(res)
        setSubmitError(message)
        return
      }

      const useCaseResult = await res.json()
      const useCaseId = useCaseResult.id || useCaseResult._id || editUseCaseId

      // Now upload NEW media files with the use case ID
      const newMediaUrls = []
      if (uploadedImages.length > 0 && useCaseId) {
        const uploadFormData = new FormData()

        // Add all files to the form data
        for (const file of uploadedImages) {
          uploadFormData.append('files', file)
        }

        // Add the use case ID
        uploadFormData.append('usecase_id', useCaseId)

        const uploadResponse = await fetch(buildApiUrl('/api/v1/media/usecase-media'), {
          method: 'POST',
          body: uploadFormData,
          credentials: 'include'
        })

        if (uploadResponse.ok) {
          const uploadResult = await uploadResponse.json()
          // Extract URLs from the response
          if (uploadResult.files) {
            for (const file of uploadResult.files) {
              newMediaUrls.push(file.url)
            }
          }
          console.log(`Successfully uploaded ${uploadResult.files?.length || 0} new media files`)

          // If in edit mode, we need to update the use case with ALL images (existing + new)
          if (isEditMode) {
            const allImages = [...existingImages, ...newMediaUrls]
            const updatePayload = { ...payload, images: allImages }

            await fetch(buildApiUrl(`/api/v1/use-cases/${useCaseId}`), {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              credentials: 'include',
              body: JSON.stringify(updatePayload)
            })
            console.log('Updated use case with all images:', allImages)
          }
        } else {
          console.error('Failed to upload media files, but use case was created successfully')
          const errorData = await uploadResponse.json().catch(() => ({}))
          console.error('Upload error:', errorData.detail || 'Unknown error')
        }
      }

      setIsSubmitted(true)

      // Delete server draft after successful submission
      if (draftId) {
        try {
          await fetch(buildApiUrl(`/api/v1/use-cases/drafts/${draftId}`), {
            method: 'DELETE',
            credentials: 'include'
          })
          console.log('Deleted server draft after successful submission')
        } catch (error) {
          console.error('Failed to delete server draft:', error)
          // Non-critical error, don't block the success flow
        }
      }

      // Mark in localStorage that submission was successful so we don't restore this data
      try {
        localStorage.setItem(FORM_STORAGE_KEY, JSON.stringify({
          wasSubmitted: true,
          timestamp: Date.now()
        }))
      } catch (error) {
        console.error('Failed to mark submission in localStorage:', error)
      }
    } catch (error) {
      console.error(`Error ${isEditMode ? 'updating' : 'submitting'} use case:`, error)
      setSubmitError('An unexpected error occurred. Please try again.')
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

    // --- Security: check all string fields for injection patterns ---
    const DANGEROUS_RE = [
      /<\s*script/i,
      /javascript\s*:/i,
      /on(error|load|click|mouseover|keydown|submit|focus|blur|change)\s*=/i,
      /\.\.\//,
      /\/etc\/passwd/,
      /oastify\.com/i,
      /<!--#\w+/i,
      /[\x00]/
    ]
    const hasDangerousPattern = (val: string) => DANGEROUS_RE.some(re => re.test(val))

    const currentValues = form.getValues()
    const stepStringFields: Record<number, string[]> = {
      1: ['title', 'subtitle', 'description', 'factoryName'],
      2: ['industryContext', 'financialLoss'],
      3: ['selectedVendor', 'implementationTime', 'totalBudget', 'methodology'],
      4: [],
      5: [],
      6: [],
      7: []
    }

    for (const fieldName of (stepStringFields[currentStep] || [])) {
      const val = (currentValues as any)[fieldName]
      if (typeof val === 'string' && hasDangerousPattern(val)) {
        form.setError(fieldName as keyof FormData, {
          type: 'manual',
          message: 'Input contains disallowed characters or patterns (e.g. script tags)'
        })
        hasValidationErrors = true
      }
    }

    // Check dynamic array fields for current step
    if (currentStep === 2) {
      specificProblems.forEach((p, i) => {
        if (hasDangerousPattern(p)) {
          form.setError('specificProblems', { type: 'manual', message: `Problem ${i + 1} contains disallowed characters` })
          hasValidationErrors = true
        }
      })
    }
    if (currentStep === 3) {
      selectionCriteria.forEach((c, i) => {
        if (hasDangerousPattern(c)) {
          form.setError('selectionCriteria', { type: 'manual', message: `Criteria ${i + 1} contains disallowed characters` })
          hasValidationErrors = true
        }
      })
      technologyComponents.forEach((c, i) => {
        if (hasDangerousPattern(c)) {
          form.setError('technologyComponents', { type: 'manual', message: `Component ${i + 1} contains disallowed characters` })
          hasValidationErrors = true
        }
      })
    }

    if (hasValidationErrors) return
    // --- End security check ---
    
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
        r.baseline.trim().length >= 1 &&
        r.current.trim().length >= 1 &&
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
      // Validate images - check for either existing or new images
      const hasExistingImages = isEditMode && existingImages.length > 0
      const hasNewImages = uploadedImages.length > 0

      if (!hasExistingImages && !hasNewImages) {
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
    if (currentStep < 7) {
      setCurrentStep(currentStep + 1)
      // Don't auto-scroll on mobile - let user stay where they are
      if (window.innerWidth > 768) {
        // Only scroll to top on larger screens
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
      // Don't auto-scroll on mobile - let user stay where they are
      if (window.innerWidth > 768) {
        // Only scroll to top on larger screens
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }
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
          <div className="flex gap-4">
            <Button
              onClick={() => {
                // Reset everything completely
                setIsSubmitted(false)
                setCurrentStep(1)
                form.reset()

                // Reset all image states
                setUploadedImages([])
                setExistingImages([])

                // Reset required arrays
                setSpecificProblems(["", ""])
                setSelectionCriteria(["", ""])
                setTechnologyComponents([""])

                // Reset optional vendor fields
                setVendorProcess("")
                setVendorSelectionReasons([])

                // Reset team fields
                setProjectTeamInternal([{ role: "", name: "", title: "" }])
                setProjectTeamVendor([{ role: "", name: "", title: "" }])
                setPhases([{ phase: "", duration: "", objectives: [""], keyActivities: [""], budget: "" }])

                // Reset ROI fields
                setRoiTotalInvestment("")
                setRoiThreeYearRoi("")

                // Reset results and challenges
                setQuantitativeResults([
                  { metric: "", baseline: "", current: "", improvement: "" },
                  { metric: "", baseline: "", current: "", improvement: "" }
                ])
                setChallengesSolutions([{ challenge: "", description: "", solution: "", outcome: "" }])
                setQualitativeImpacts([])

                // Reset tags
                setIndustryTags([])
                setTechnologyTags([])

                // Reset technical architecture fields
                setSystemOverview("")
                setArchitectureComponents([{ layer: "", components: [""], specifications: "" }])
                setSecurityMeasures([""])
                setScalabilityDesign([""])

                // Reset lessons learned and future roadmap
                setLessonsLearned([{ category: "", lesson: "", description: "", recommendation: "" }])
                setFutureRoadmap([{ timeline: "", initiative: "", description: "", expected_benefit: "" }])

                // Clear localStorage
                localStorage.removeItem(FORM_STORAGE_KEY)

                // Scroll to top
                window.scrollTo({ top: 0, behavior: 'smooth' })
              }}
              className="bg-green-600 hover:bg-green-700 text-white"
            >
              Submit Another
            </Button>
            <Button
              onClick={() => {
                // Clear everything immediately
                localStorage.removeItem(FORM_STORAGE_KEY)
                window.location.href = '/usecases'
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isEditMode ? 'View Use Cases' : 'Browse Use Cases'}
            </Button>
          </div>
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 pb-20 md:pb-0">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="w-full px-4 sm:px-6 lg:max-w-7xl lg:mx-auto py-6 sm:py-8">
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

            {/* Autosave Status Indicator - Top Header */}
            <div className="mt-4 flex items-center justify-center gap-2 text-sm min-h-[24px]">
              {autosaveStatus === 'saving' && (
                <div className="flex items-center gap-2 text-blue-600">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span>Saving draft...</span>
                </div>
              )}
              {autosaveStatus === 'saved' && lastSavedAt && (
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircle className="h-4 w-4" />
                  <span>
                    Draft saved {(() => {
                      const seconds = Math.floor((Date.now() - lastSavedAt) / 1000)
                      if (seconds < 60) return 'just now'
                      const minutes = Math.floor(seconds / 60)
                      if (minutes === 1) return '1 minute ago'
                      if (minutes < 60) return `${minutes} minutes ago`
                      const hours = Math.floor(minutes / 60)
                      if (hours === 1) return '1 hour ago'
                      return `${hours} hours ago`
                    })()}
                  </span>
                </div>
              )}
              {autosaveStatus === 'failed' && (
                <div className="flex items-center gap-2 text-red-600">
                  <AlertCircle className="h-4 w-4" />
                  <span>Failed to save draft</span>
                </div>
              )}
            </div>
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
      <div className="w-full px-4 sm:px-6 lg:max-w-7xl lg:mx-auto py-8 sm:py-12">
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
                          
                          {technologyComponents.length < 15 && (
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
                                value={Array.isArray(component.components) ? component.components.join(", ") : ""}
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
                                value={result.metric || ''}
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
                                  value={result.improvement || ''}
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

                  {/* Lessons Learned (Optional) */}
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                    <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
                      <Lightbulb className="h-6 w-6 mr-3 text-yellow-600" />
                      Lessons Learned (Optional)
                    </h2>
                    <p className="text-slate-600 mb-6">
                      Share key insights and recommendations from your implementation experience.
                    </p>

                    <div className="space-y-4">
                      {lessonsLearned.map((lesson, index) => (
                        <div key={index} className="border border-slate-200 rounded-lg p-4 bg-slate-50">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                            <div>
                              <label className="text-sm font-medium text-slate-700">Category</label>
                              <select
                                value={lesson.category}
                                onChange={(e) => {
                                  const updated = [...lessonsLearned]
                                  updated[index].category = e.target.value
                                  setLessonsLearned(updated)
                                }}
                                className="w-full mt-1 px-3 py-2 border border-slate-200 rounded-md"
                              >
                                <option value="">Select category</option>
                                <option value="Technical">Technical</option>
                                <option value="Process">Process</option>
                                <option value="People">People</option>
                                <option value="Budget">Budget</option>
                                <option value="Timeline">Timeline</option>
                                <option value="Vendor">Vendor</option>
                              </select>
                            </div>
                            <div>
                              <label className="text-sm font-medium text-slate-700">Lesson Title</label>
                              <Input
                                placeholder="Key lesson learned"
                                value={lesson.lesson}
                                onChange={(e) => {
                                  const updated = [...lessonsLearned]
                                  updated[index].lesson = e.target.value
                                  setLessonsLearned(updated)
                                }}
                              />
                            </div>
                          </div>
                          <div className="mb-3">
                            <label className="text-sm font-medium text-slate-700">Description</label>
                            <Textarea
                              placeholder="Detailed description of the lesson..."
                              value={lesson.description}
                              onChange={(e) => {
                                const updated = [...lessonsLearned]
                                updated[index].description = e.target.value
                                setLessonsLearned(updated)
                              }}
                              className="min-h-[80px]"
                            />
                          </div>
                          <div>
                            <label className="text-sm font-medium text-slate-700">Recommendation</label>
                            <Textarea
                              placeholder="What would you recommend to others..."
                              value={lesson.recommendation}
                              onChange={(e) => {
                                const updated = [...lessonsLearned]
                                updated[index].recommendation = e.target.value
                                setLessonsLearned(updated)
                              }}
                              className="min-h-[60px]"
                            />
                          </div>
                          {lessonsLearned.length > 0 && (
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => setLessonsLearned(lessonsLearned.filter((_, i) => i !== index))}
                              className="mt-3 text-red-600 hover:text-red-700"
                            >
                              <X className="h-4 w-4 mr-1" />
                              Remove Lesson
                            </Button>
                          )}
                        </div>
                      ))}

                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setLessonsLearned([...lessonsLearned, { category: "", lesson: "", description: "", recommendation: "" }])}
                        className="flex items-center space-x-2"
                      >
                        <Plus className="h-4 w-4" />
                        <span>Add Lesson Learned</span>
                      </Button>
                    </div>
                  </div>

                  {/* Future Roadmap (Optional) */}
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                    <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
                      <Calendar className="h-6 w-6 mr-3 text-purple-600" />
                      Future Roadmap (Optional)
                    </h2>
                    <p className="text-slate-600 mb-6">
                      Outline planned improvements and future initiatives.
                    </p>

                    <div className="space-y-4">
                      {futureRoadmap.map((item, index) => (
                        <div key={index} className="border border-slate-200 rounded-lg p-4 bg-slate-50">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                            <div>
                              <label className="text-sm font-medium text-slate-700">Timeline</label>
                              <Input
                                placeholder="e.g., Q2 2025, Next 6 months"
                                value={item.timeline}
                                onChange={(e) => {
                                  const updated = [...futureRoadmap]
                                  updated[index].timeline = e.target.value
                                  setFutureRoadmap(updated)
                                }}
                              />
                            </div>
                            <div>
                              <label className="text-sm font-medium text-slate-700">Initiative</label>
                              <Input
                                placeholder="Name of the initiative"
                                value={item.initiative}
                                onChange={(e) => {
                                  const updated = [...futureRoadmap]
                                  updated[index].initiative = e.target.value
                                  setFutureRoadmap(updated)
                                }}
                              />
                            </div>
                          </div>
                          <div className="mb-3">
                            <label className="text-sm font-medium text-slate-700">Description</label>
                            <Textarea
                              placeholder="Detailed description of the initiative..."
                              value={item.description}
                              onChange={(e) => {
                                const updated = [...futureRoadmap]
                                updated[index].description = e.target.value
                                setFutureRoadmap(updated)
                              }}
                              className="min-h-[80px]"
                            />
                          </div>
                          <div>
                            <label className="text-sm font-medium text-slate-700">Expected Benefit</label>
                            <Textarea
                              placeholder="What benefits are expected..."
                              value={item.expected_benefit}
                              onChange={(e) => {
                                const updated = [...futureRoadmap]
                                updated[index].expected_benefit = e.target.value
                                setFutureRoadmap(updated)
                              }}
                              className="min-h-[60px]"
                            />
                          </div>
                          {futureRoadmap.length > 0 && (
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => setFutureRoadmap(futureRoadmap.filter((_, i) => i !== index))}
                              className="mt-3 text-red-600 hover:text-red-700"
                            >
                              <X className="h-4 w-4 mr-1" />
                              Remove Item
                            </Button>
                          )}
                        </div>
                      ))}

                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setFutureRoadmap([...futureRoadmap, { timeline: "", initiative: "", description: "", expected_benefit: "" }])}
                        className="flex items-center space-x-2"
                      >
                        <Plus className="h-4 w-4" />
                        <span>Add Roadmap Item</span>
                      </Button>
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
                        render={({ field }) => {
                          console.log('City Select field value:', field.value)
                          return (
                          <FormItem>
                            <FormLabel>City</FormLabel>
                            <Select onValueChange={field.onChange} value={field.value || ""} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Select a city" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent className="z-[9999] bg-white">
                                {SAUDI_CITIES.map((city) => (
                                  <SelectItem key={city} value={city}>
                                    {city}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            <FormMessage className="text-red-600 font-semibold text-sm bg-red-50 px-3 py-1 rounded-lg border-l-4 border-red-500 mt-2" />
                          </FormItem>
                        )}}
                      />
                    </div>

                    <div className="mb-6">
                      <h3 className="text-lg font-semibold text-slate-900 mb-3">Pin Your Factory Location</h3>
                      <p className="text-slate-600 mb-4">Click on the map or enter coordinates manually</p>

                      {/* Manual coordinate inputs */}
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-1">Latitude</label>
                          <Input
                            type="number"
                            step="0.000001"
                            value={form.watch('latitude')}
                            onChange={(e) => {
                              const value = parseFloat(e.target.value)
                              if (!isNaN(value) && value >= -90 && value <= 90) {
                                form.setValue('latitude', value)
                              }
                            }}
                            placeholder="e.g., 24.713552"
                            className="w-full"
                          />
                          <span className="text-xs text-gray-500">Range: -90 to 90</span>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-slate-700 mb-1">Longitude</label>
                          <Input
                            type="number"
                            step="0.000001"
                            value={form.watch('longitude')}
                            onChange={(e) => {
                              const value = parseFloat(e.target.value)
                              if (!isNaN(value) && value >= -180 && value <= 180) {
                                form.setValue('longitude', value)
                              }
                            }}
                            placeholder="e.g., 46.675267"
                            className="w-full"
                          />
                          <span className="text-xs text-gray-500">Range: -180 to 180</span>
                        </div>
                      </div>

                      {/* Show loading state in edit mode until coordinates are loaded */}
                      {isEditMode && isLoadingExistingData ? (
                        <div className="h-[400px] bg-gray-100 rounded-xl flex items-center justify-center border border-slate-200">
                          <div className="text-center">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-3"></div>
                            <p className="text-gray-600">Loading location data...</p>
                          </div>
                        </div>
                      ) : (
                        <LocationPicker
                          onLocationSelect={handleLocationSelect}
                          defaultLat={form.watch('latitude')}
                          defaultLng={form.watch('longitude')}
                          key={`map-${form.watch('latitude')}-${form.watch('longitude')}`} // Force re-render when coords change
                        />
                      )}
                    </div>

                    <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                      <div className="grid grid-cols-2 gap-4 text-sm text-slate-700">
                        <div className="flex items-center">
                          <MapPin className="h-4 w-4 mr-2 text-blue-600" />
                          <span className="font-medium">Current Latitude:</span>
                          <span className="ml-2 font-mono">{form.watch('latitude').toFixed(6)}</span>
                        </div>
                        <div className="flex items-center">
                          <MapPin className="h-4 w-4 mr-2 text-blue-600" />
                          <span className="font-medium">Current Longitude:</span>
                          <span className="ml-2 font-mono">{form.watch('longitude').toFixed(6)}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Images */}
                  <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm">
                    <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
                      <Upload className="h-6 w-6 mr-3 text-blue-600" />
                      Images
                    </h2>

                    {/* Display existing images in edit mode */}
                    {isEditMode && existingImages.length > 0 && (
                      <div className="mb-6">
                        <h3 className="text-lg font-semibold text-gray-700 mb-3">Current Images</h3>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-4">
                          {existingImages.map((imageUrl, index) => {
                            // Ensure the URL is properly formatted
                            const fullImageUrl = imageUrl.startsWith('http')
                              ? imageUrl
                              : `${imageUrl}`;

                            console.log(`Image ${index + 1} URL:`, fullImageUrl);

                            return (
                              <div key={index} className="relative group">
                                <img
                                  src={fullImageUrl}
                                  alt={`Existing image ${index + 1}`}
                                  className="w-full h-32 object-cover rounded-lg border-2 border-gray-200"
                                  onError={(e) => {
                                    console.error(`Failed to load image ${index + 1}:`, fullImageUrl);
                                    console.error('Error event:', e);
                                  }}
                                  onLoad={(e) => {
                                    console.log(`Successfully loaded image ${index + 1}`);
                                    const img = e.target as HTMLImageElement;
                                    console.log('Image loaded with dimensions:', img.naturalWidth, 'x', img.naturalHeight);
                                    console.log('Display dimensions:', img.clientWidth, 'x', img.clientHeight);
                                  }}
                                />
                                {/* Delete button for existing images */}
                                <button
                                  type="button"
                                  onClick={() => {
                                    const updatedImages = existingImages.filter((_, i) => i !== index)
                                    setExistingImages(updatedImages)
                                    console.log(`Removed image ${index + 1}, remaining images:`, updatedImages)
                                  }}
                                  className="absolute top-2 right-2 bg-red-600 hover:bg-red-700 text-white rounded-full p-1.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                                  title="Remove this image"
                                >
                                  <X className="h-4 w-4" />
                                </button>
                                <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
                                  Image {index + 1}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                        <p className="text-sm text-gray-500 mb-4">
                          These images are already uploaded. Click the X button to remove any image. You can add more images below.
                        </p>
                      </div>
                    )}

                    <FileDropZone
                      onFilesSelect={handleImagesUpdate}
                      maxFiles={10}
                      acceptedTypes={['image/*', 'video/*']}
                      maxSize={50 * 1024 * 1024}
                    />
                    <p className="text-sm text-gray-500 mt-2">
                      {isEditMode ? 'Add new images (existing images will be kept unless you upload new ones)' : 'Upload images for your use case'}
                    </p>
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

                    {/* Show Future Roadmap if it has items */}
                    {futureRoadmap.length > 0 && futureRoadmap.some(r => r.initiative) && (
                      <div>
                        <h3 className="font-semibold text-slate-900 mb-2">Future Roadmap</h3>
                        <div className="space-y-3">
                          {futureRoadmap.filter(r => r.initiative).map((item, index) => (
                            <div key={index} className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                              <p className="font-medium text-slate-800">{item.timeline}: {item.initiative}</p>
                              {item.description && (
                                <p className="text-sm text-slate-600 mt-1">{item.description}</p>
                              )}
                              {item.expected_benefit && (
                                <p className="text-sm text-slate-500 mt-1">Expected: {item.expected_benefit}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}


              {/* Navigation Buttons */}
              <div className="flex flex-col gap-4 pt-8">
                {/* Autosave Status Indicator - Always Visible */}
                <div className="flex flex-col items-center justify-center gap-2 text-sm min-h-[24px]">
                  {/* localStorage autosave status */}
                  <div className="flex items-center gap-2">
                    {autosaveStatus === 'saving' && (
                      <div className="flex items-center gap-2 text-blue-600">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                        <span>Saving draft locally...</span>
                      </div>
                    )}
                    {autosaveStatus === 'saved' && lastSavedAt && (
                      <div className="flex items-center gap-2 text-green-600">
                        <CheckCircle className="h-4 w-4" />
                        <span>
                          Draft saved locally {(() => {
                            const seconds = Math.floor((Date.now() - lastSavedAt) / 1000)
                            if (seconds < 60) return 'just now'
                            const minutes = Math.floor(seconds / 60)
                            if (minutes === 1) return '1 minute ago'
                            if (minutes < 60) return `${minutes} minutes ago`
                            const hours = Math.floor(minutes / 60)
                            if (hours === 1) return '1 hour ago'
                            return `${hours} hours ago`
                          })()}
                        </span>
                      </div>
                    )}
                    {autosaveStatus === 'failed' && (
                      <div className="flex items-center gap-2 text-red-600">
                        <AlertCircle className="h-4 w-4" />
                        <span>Failed to save draft locally</span>
                      </div>
                    )}
                  </div>

                  {/* Server save status indicator */}
                  {serverDraftSaved && (
                    <div className="flex items-center gap-2 text-blue-600">
                      <Cloud className="h-4 w-4" />
                      <span>Saved to server</span>
                    </div>
                  )}
                </div>

                {/* Navigation Buttons Row */}
                <div className="flex justify-between items-center">
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
                  {/* Save as Draft Button */}
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleSaveDraft}
                    disabled={savingDraft}
                    className="flex items-center gap-2"
                  >
                    {savingDraft ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4" />
                        Save as Draft
                      </>
                    )}
                  </Button>

                  {/* Start New Use Case Button */}
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowNewUseCaseDialog(true)}
                    className="flex items-center gap-2"
                  >
                    <FileText className="h-4 w-4" />
                    Start New Use Case
                  </Button>

                  {/* Submit validation error */}
                  {submitError && (
                    <div className="flex items-start gap-3 px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 mb-2">
                      <span className="text-red-500 mt-0.5 flex-shrink-0">⚠️</span>
                      <div className="whitespace-pre-line">{submitError}</div>
                    </div>
                  )}
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
              </div>
            </form>
          </Form>
        </div>
      </div>

      {/* Start New Use Case Confirmation Dialog */}
      {showNewUseCaseDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setShowNewUseCaseDialog(false)}
          />
          <div className="relative bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-2">Start New Use Case?</h3>
            <p className="text-slate-600 mb-6">
              You are currently {draftId ? 'working on a draft' : 'creating a use case'}.
              What would you like to do?
            </p>
            <div className="space-y-3">
              <button
                onClick={() => handleStartNew('save')}
                className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-left transition-colors"
              >
                <div className="font-medium">Save & Start New</div>
                <div className="text-sm text-blue-100">Save current work as draft, then start fresh</div>
              </button>
              <button
                onClick={() => handleStartNew('discard')}
                className="w-full px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg text-left transition-colors"
              >
                <div className="font-medium">Discard & Start New</div>
                <div className="text-sm text-red-100">Delete this draft and start fresh (cannot be undone)</div>
              </button>
              <button
                onClick={() => handleStartNew('cancel')}
                className="w-full px-4 py-3 bg-slate-200 hover:bg-slate-300 text-slate-900 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}