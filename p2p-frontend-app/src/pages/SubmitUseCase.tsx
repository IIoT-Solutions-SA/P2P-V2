import React, { useState } from 'react'
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
  TrendingUp, 
  Calendar,
  Plus,
  X,
  Save,
  Target,
  Zap,
  Wrench,
  Shield,
  BarChart3,
  Lightbulb,
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
    .min(5, "Financial loss description is required"),
  
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
  { value: "Sustainability", label: "Sustainability" },
  { value: "Process Optimization", label: "Process Optimization" },
  { value: "Supply Chain", label: "Supply Chain" },
  { value: "Innovation & R&D", label: "Innovation & R&D" },
  { value: "Training & Safety", label: "Training & Safety" },
  { value: "Energy Efficiency", label: "Energy Efficiency" }
]

export default function SubmitUseCase() {
  const [currentStep, setCurrentStep] = useState(1)
  const [uploadedImages, setUploadedImages] = useState<File[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  
  // State for dynamic arrays
  const [specificProblems, setSpecificProblems] = useState<string[]>(["", ""])
  const [selectionCriteria, setSelectionCriteria] = useState<string[]>(["", ""])
  const [technologyComponents, setTechnologyComponents] = useState<string[]>([""])
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

  const steps = [
    { number: 1, title: "Basic Information", icon: Factory },
    { number: 2, title: "Business Challenge", icon: Target },
    { number: 3, title: "Solution & Implementation", icon: Zap },
    { number: 4, title: "Results & Challenges", icon: BarChart3 },
    { number: 5, title: "Location & Contact", icon: MapPin },
    { number: 6, title: "Review & Submit", icon: CheckCircle }
  ]

  // Helper functions for dynamic arrays
  const addBenefit = () => {
    // Legacy function - kept for compatibility
  }

  const removeBenefit = (index: number) => {
    // Legacy function - kept for compatibility
  }

  const updateBenefit = (index: number, value: string) => {
    // Legacy function - kept for compatibility
  }

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
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      console.log('Submitted use case:', {
        ...data,
        images: data.images.map(file => ({
          name: file.name,
          size: file.size,
          type: file.type
        }))
      })
      
      setIsSubmitted(true)
    } catch (error) {
      console.error('Error submitting use case:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const nextStep = () => {
    if (currentStep < 6) setCurrentStep(currentStep + 1)
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
          <h1 className="text-2xl font-bold text-slate-900 mb-4">Use Case Submitted Successfully!</h1>
          <p className="text-slate-600 mb-6">
            Thank you for sharing your factory success story. Our team will review your submission and it will be published on the platform soon.
          </p>
          <Button 
            onClick={() => window.location.reload()} 
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            Submit Another Use Case
          </Button>
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
            <h1 className="text-4xl font-bold text-slate-900 mb-4">Submit Your Success Story</h1>
            <p className="text-xl text-slate-600">Share your factory's transformation with the community</p>
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
                          <FormLabel>Use Case Title</FormLabel>
                          <FormControl>
                            <Input 
                              placeholder="e.g., AI Quality Inspection System Reduces Defects by 85%" 
                              {...field} 
                            />
                          </FormControl>
                          <FormDescription>
                            A clear, compelling title that describes your success story
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="subtitle"
                      render={({ field }) => (
                        <FormItem className="md:col-span-2">
                          <FormLabel>Subtitle</FormLabel>
                          <FormControl>
                            <Input 
                              placeholder="e.g., Transforming PCB Manufacturing Through Computer Vision and Machine Learning" 
                              {...field} 
                            />
                          </FormControl>
                          <FormDescription>
                            A descriptive subtitle explaining the technology or approach used
                          </FormDescription>
                          <FormMessage />
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
                            <SelectContent>
                              {categories.map((category) => (
                                <SelectItem key={category.value} value={category.value}>
                                  {category.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="factoryName"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Factory Name</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g., Advanced Electronics Co." {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="description"
                      render={({ field }) => (
                        <FormItem className="md:col-span-2">
                          <FormLabel>Executive Summary</FormLabel>
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
                          <FormMessage />
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
                          <FormLabel>Industry Context</FormLabel>
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
                          <FormMessage />
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
                          <div key={index} className="flex items-center space-x-3">
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
                    </div>

                    <FormField
                      control={form.control}
                      name="financialLoss"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Financial Impact</FormLabel>
                          <FormControl>
                            <Input 
                              placeholder="e.g., 450K annually in waste, rework, and returns"
                              {...field} 
                            />
                          </FormControl>
                          <FormDescription>
                            Quantify the financial impact of the problems (losses, inefficiencies, opportunity costs)
                          </FormDescription>
                          <FormMessage />
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
                            <div key={index} className="flex items-center space-x-3">
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
                      </div>

                      <FormField
                        control={form.control}
                        name="selectedVendor"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Selected Vendor/Partner</FormLabel>
                            <FormControl>
                              <Input 
                                placeholder="e.g., VisionTech Systems"
                                {...field} 
                              />
                            </FormControl>
                            <FormDescription>
                              Name of the technology vendor or implementation partner
                            </FormDescription>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <div>
                        <FormLabel className="text-base font-semibold">Technology Components</FormLabel>
                        <FormDescription className="mb-4">
                          Describe the key technology components of your solution
                        </FormDescription>
                        <div className="space-y-3">
                          {technologyComponents.map((component, index) => (
                            <div key={index} className="flex items-center space-x-3">
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
                            <FormLabel>Implementation Duration</FormLabel>
                            <FormControl>
                              <Input placeholder="e.g., 6 months implementation" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="totalBudget"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Total Budget</FormLabel>
                            <FormControl>
                              <Input placeholder="e.g., 285,000" {...field} />
                            </FormControl>
                            <FormDescription>
                              Total project budget (amount only, currency symbol will be added automatically)
                            </FormDescription>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="methodology"
                        render={({ field }) => (
                          <FormItem className="md:col-span-2">
                            <FormLabel>Implementation Methodology</FormLabel>
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
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Step 4: Results & Challenges */}
              {currentStep === 4 && (
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
                              <FormMessage />
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
                              <FormMessage />
                            </FormItem>
                          )}
                        />
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
                                <FormLabel className="text-sm font-medium">Challenge Name</FormLabel>
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
                                <FormLabel className="text-sm font-medium">Challenge Description</FormLabel>
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
                              </div>
                              <div>
                                <FormLabel className="text-sm font-medium">Solution & Outcome</FormLabel>
                                <Textarea
                                  placeholder="How was it solved and what was the result..."
                                  value={item.solution}
                                  onChange={(e) => {
                                    const updated = [...challengesSolutions]
                                    updated[index].solution = e.target.value
                                    setChallengesSolutions(updated)
                                    form.setValue('challengesSolutions', updated)
                                  }}
                                  className="mt-1 min-h-[80px]"
                                />
                              </div>
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
                    </div>
                  </div>
                </div>
              )}

              {/* Step 5: Location & Contact */}
              {currentStep === 5 && (
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
                            <FormLabel>City</FormLabel>
                            <FormControl>
                              <Input placeholder="e.g., Riyadh" {...field} />
                            </FormControl>
                            <FormMessage />
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
                            <FormMessage />
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
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Step 6: Review & Submit */}
              {currentStep === 6 && (
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
                  {currentStep < 6 ? (
                    <Button
                      type="button"
                      onClick={nextStep}
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
                          <span>Submit Use Case</span>
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