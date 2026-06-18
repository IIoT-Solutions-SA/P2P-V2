import { useState, useEffect } from "react";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Loader2, Send, MessageSquare, Tag, FileText, Sparkles, X, Save, Upload } from "lucide-react";
import { buildApiUrl } from '@/config/environment';
import { FileDropZone } from '@/components/ui/FileDropZone';

interface Category {
  id: string;
  name: string;
  count: number;
}

interface CreatePostModalProps {
  isOpen: boolean;
  onClose: () => void;
  categories: Category[];
  onPostSuccess: () => void;
  initialTitle?: string;
  initialContent?: string;
  initialCategoryId?: string;
  draftId?: string;
}

export function CreatePostModal({ isOpen, onClose, categories, onPostSuccess, initialTitle, initialContent, initialCategoryId, draftId }: CreatePostModalProps) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [savingDraft, setSavingDraft] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [titleError, setTitleError] = useState<string | null>(null);
  const [contentError, setContentError] = useState<string | null>(null);

  const DANGEROUS_RE = [
    /<\s*script/i,
    /javascript\s*:/i,
    /on(error|load|click|mouseover|keydown|submit|focus|blur|change)\s*=/i,
    /\.\.\//, /\/etc\/passwd/, /oastify\.com/i, /<!--#\w+/i, /[\x00]/
  ]
  const hasDanger = (val: string) => DANGEROUS_RE.some(re => re.test(val))

  // Additional predefined categories for comprehensive manufacturing coverage
  const predefinedCategories = [
    { id: "automation", name: "Automation", count: 0 },
    { id: "quality-management", name: "Quality Management", count: 0 },
    { id: "artificial-intelligence", name: "Artificial Intelligence", count: 0 },
    { id: "maintenance", name: "Maintenance", count: 0 },
    { id: "lean-manufacturing", name: "Lean Manufacturing", count: 0 },
    { id: "supply-chain", name: "Supply Chain Management", count: 0 },
    { id: "digital-transformation", name: "Digital Transformation", count: 0 },
    { id: "iot-sensors", name: "IoT & Sensors", count: 0 },
    { id: "robotics", name: "Robotics", count: 0 },
    { id: "cybersecurity", name: "Cybersecurity", count: 0 },
    { id: "energy-efficiency", name: "Energy Efficiency", count: 0 },
    { id: "sustainability", name: "Sustainability", count: 0 },
    { id: "safety", name: "Safety & Compliance", count: 0 },
    { id: "training-development", name: "Training & Development", count: 0 },
    { id: "cost-optimization", name: "Cost Optimization", count: 0 },
    { id: "inventory-management", name: "Inventory Management", count: 0 },
    { id: "production-planning", name: "Production Planning", count: 0 },
    { id: "machine-learning", name: "Machine Learning", count: 0 },
    { id: "data-analytics", name: "Data Analytics", count: 0 },
    { id: "erp-systems", name: "ERP Systems", count: 0 },
    { id: "cloud-computing", name: "Cloud Computing", count: 0 },
    { id: "3d-printing", name: "3D Printing", count: 0 },
    { id: "packaging", name: "Packaging", count: 0 },
    { id: "logistics", name: "Logistics", count: 0 },
    { id: "procurement", name: "Procurement", count: 0 },
    { id: "vendor-management", name: "Vendor Management", count: 0 },
    { id: "regulatory-compliance", name: "Regulatory Compliance", count: 0 },
    { id: "continuous-improvement", name: "Continuous Improvement", count: 0 },
    { id: "workflow-optimization", name: "Workflow Optimization", count: 0 },
    { id: "equipment-management", name: "Equipment Management", count: 0 },
    { id: "facility-management", name: "Facility Management", count: 0 },
    { id: "human-resources", name: "Human Resources", count: 0 },
    { id: "financial-management", name: "Financial Management", count: 0 },
    { id: "research-development", name: "Research & Development", count: 0 },
    { id: "customer-service", name: "Customer Service", count: 0 }
  ];

  // Merge API categories with predefined ones, avoiding duplicates
  const allCategories = [...categories];
  predefinedCategories.forEach(predefined => {
    if (!categories.find(cat => cat.name.toLowerCase() === predefined.name.toLowerCase())) {
      allCategories.push(predefined);
    }
  });

  // Sort categories alphabetically
  allCategories.sort((a, b) => a.name.localeCompare(b.name));

  // Seed initial values when opening (for drafts)
  useEffect(() => {
    if (!isOpen) return;
    setTitle(initialTitle || "");
    setContent(initialContent || "");
    setCategoryId(initialCategoryId || "");
    setTitleError(null);
    setContentError(null);
    setError(null);
  }, [isOpen, initialTitle, initialContent, initialCategoryId]);

  /** Parse a FastAPI 422 validation error body into a human-readable string */
  const parseApiError = async (response: Response): Promise<string> => {
    try {
      const data = await response.json()
      if (Array.isArray(data?.detail)) {
        return data.detail
          .map((e: any) => e.msg?.replace('Value error, ', '') ?? 'Invalid value')
          .join('\n')
      }
      if (data?.message) return data.message
      if (data?.detail && typeof data.detail === 'string') return data.detail
    } catch {}
    return `Request failed (${response.status})`
  }

  const handleSubmit = async () => {
    // Clear previous errors
    setTitleError(null)
    setContentError(null)
    setError(null)

    let hasFieldError = false

    // Title validation
    const titleSpecialChars = title.match(/[^\w\s\.\-,\u0600-\u06FF]/g) || [];
    const titleLetters = title.match(/[a-zA-Z\u0600-\u06FF]/g) || [];
    const hasRepeatedChars = (val: string) => /(.)\1{4,}/.test(val);
    const hasConsecutiveConsonants = (val: string) => /[bcdfghjklmnpqrstvwxz]{6,}/i.test(val);
    
    if (!title.trim()) {
      setTitleError('Title is required')
      hasFieldError = true
    } else if (hasDanger(title)) {
      setTitleError('Input contains disallowed characters or patterns (e.g. script tags)')
      hasFieldError = true
    } else if (title.trim().length < 8) {
      setTitleError(`Title should have at least 8 characters (${title.trim().length}/8)`)
      hasFieldError = true
    } else if (titleLetters.length < 2) {
      setTitleError('Title must contain at least 2 letters (cannot be only numbers)')
      hasFieldError = true
    } else if (/\d{6,}/.test(title)) {
      setTitleError('Title cannot contain 6 or more consecutive numbers')
      hasFieldError = true
    } else if (titleSpecialChars.length > 3) {
      setTitleError('Too many special characters are not allowed in titles')
      hasFieldError = true
    } else if (hasRepeatedChars(title)) {
      setTitleError('Too many repeated characters are not allowed')
      hasFieldError = true
    } else if (hasConsecutiveConsonants(title)) {
      setTitleError('Too many consecutive consonants are not allowed')
      hasFieldError = true
    }

    // Content validation — always checked, independent of title
    if (!content.trim()) {
      setContentError('Content is required')
      hasFieldError = true
    } else if (hasDanger(content)) {
      setContentError('Input contains disallowed characters or patterns (e.g. script tags)')
      hasFieldError = true
    } else if (content.trim().length < 20) {
      setContentError(`Content should have at least 20 characters (${content.trim().length}/20)`)
      hasFieldError = true
    } else if (hasRepeatedChars(content)) {
      setContentError('Too many repeated characters are not allowed')
      hasFieldError = true
    } else if (hasConsecutiveConsonants(content)) {
      setContentError('Too many consecutive consonants are not allowed')
      hasFieldError = true
    } else if (content.length > 10) {
      const symbolChars = content.match(/[^\w\s\u0600-\u06FF]/g) || [];
      if (symbolChars.length / content.length > 0.5) {
        setContentError('Input contains too many symbols')
        hasFieldError = true
      }
    }

    if (!categoryId) { setError('Please select a category.'); hasFieldError = true }

    if (hasFieldError) return

    setIsLoading(true);
    try {
      // First create the post without attachments
      const response = await fetch(buildApiUrl("/api/v1/forum/posts"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          title,
          content,
          category_id: categoryId
        })
      });

      if (!response.ok) {
        // Map per-field errors from 422 back to the correct field
        try {
          const data = await response.json()
          if (Array.isArray(data?.detail)) {
            data.detail.forEach((e: any) => {
              const loc: string[] = e.loc ?? []
              const raw = e.msg?.replace('Value error, ', '') ?? 'Invalid value'
              // Replace generic Pydantic messages with field-specific ones
              const msg = raw
                .replace(/String should have at least (\d+)/i, 'Should have at least $1')
                .replace(/String should have at most (\d+)/i, 'Should have at most $1')
              if (loc.includes('title')) setTitleError(msg)
              else if (loc.includes('content')) setContentError(msg)
              else setError(msg)
            })
            return
          }
          setError(data?.message || data?.detail || `Request failed (${response.status})`)
        } catch {
          setError(`Request failed (${response.status})`)
        }
        return
      }

      const postResult = await response.json()
      const postId = postResult.id

      // Then upload any attachments with the post ID
      const attachmentUrls = []
      if (attachments.length > 0) {
        for (const file of attachments) {
          const formData = new FormData()
          formData.append('file', file)
          formData.append('post_id', postId)

          const uploadResponse = await fetch(buildApiUrl('/api/v1/media/forum-attachment'), {
            method: 'POST',
            body: formData,
            credentials: 'include'
          })

          if (uploadResponse.ok) {
            const result = await uploadResponse.json()
            attachmentUrls.push({
              url: result.attachment.url,
              filename: result.attachment.filename,
              type: result.attachment.type,
              size: result.attachment.size
            })
          } else {
            const message = await parseApiError(uploadResponse)
            setError(message)
            return
          }
        }

        // NOTE: Attachments are already linked to the post via post_id in the media table
        // No need to update the post document since the association is handled at the database level
      }

      onPostSuccess();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveDraft = async () => {
    if (!title.trim() && !content.trim()) {
      setError("Add a title or content before saving a draft.");
      return;
    }
    setError(null);
    setSavingDraft(true);
    try {
      const url = draftId 
        ? buildApiUrl(`/api/v1/dashboard/drafts/${draftId}`)
        : buildApiUrl("/api/v1/dashboard/drafts");
      const method = draftId ? "PUT" : "POST";
      
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ 
          title: title || 'Untitled', 
          content: content || '', 
          post_type: 'forum_post',
          category: categoryId || 'General'
        })
      });
      if (res.ok) {
        // Close modal and trigger refresh (onPostSuccess refreshes dashboard stats)
        onPostSuccess();
      } else {
        setError("Failed to save draft.");
      }
    } catch (e: any) {
      setError(e.message || "Failed to save draft.");
    } finally {
      setSavingDraft(false);
    }
  };

  const handleOpenChange = (open: boolean) => {
    if (!open) onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[80vh] bg-white rounded-2xl border-0 shadow-2xl p-0 overflow-hidden">
        <div className="relative">
          {/* Beautiful header with gradient */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-5 text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
            <div className="absolute bottom-0 left-0 w-20 h-20 bg-white/10 rounded-full -ml-10 -mb-10"></div>
            <div className="relative flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                  <Sparkles className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Create New Post</h2>
                  <p className="text-blue-100">Share your knowledge with the community</p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="text-white hover:bg-white/20 h-9 w-9 p-0 rounded-full"
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
          </div>

          {/* Form content */}
          <div className="p-8 max-h-[60vh] overflow-y-auto">
            <div className="space-y-4">
              {/* Title field */}
              <div className="space-y-3">
                <Label htmlFor="title" className="text-base font-semibold text-slate-800 flex items-center space-x-2">
                  <MessageSquare className="h-4 w-4 text-blue-600" />
                  <span>Post Title</span>
                </Label>
                <Input 
                  id="title" 
                  placeholder="e.g., How to improve manufacturing efficiency?" 
                  value={title} 
                  onChange={(e) => { setTitle(e.target.value); setTitleError(null) }}
                  className={`h-12 text-base border-2 rounded-xl focus:ring-2 transition-all ${
                    titleError ? 'border-red-400 focus:border-red-400 focus:ring-red-100' : 'border-slate-200 focus:border-blue-500 focus:ring-blue-200'
                  }`}
                />
                {titleError && (
                  <p className="text-red-500 text-sm mt-1">
                    {titleError}
                  </p>
                )}
              </div>

              {/* Category field */}
              <div className="space-y-3">
                <Label htmlFor="category" className="text-base font-semibold text-slate-800 flex items-center space-x-2">
                  <Tag className="h-4 w-4 text-green-600" />
                  <span>Category</span>
                </Label>
                <Select value={categoryId} onValueChange={setCategoryId}>
                  <SelectTrigger className="h-12 text-base border-2 border-slate-200 rounded-xl focus:border-blue-500 transition-all">
                    <SelectValue placeholder="Choose the best category for your post" />
                  </SelectTrigger>
                  <SelectContent className="rounded-xl bg-white border-2 border-slate-200 shadow-xl z-50 max-h-80 overflow-y-auto">
                    {allCategories.map((cat) => (
                      <SelectItem key={cat.id} value={cat.name} className="text-base py-3 hover:bg-blue-50 cursor-pointer">
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${cat.count > 0 ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
                          <span className="font-medium">{cat.name}</span>
                          <span className="text-xs text-slate-500">({cat.count} posts)</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Content field */}
              <div className="space-y-3">
                <Label htmlFor="content" className="text-base font-semibold text-slate-800 flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-purple-600" />
                  <span>Content</span>
                </Label>
                <Textarea 
                  id="content" 
                  placeholder="Share your detailed question, problem, solution, or insight here. The more specific you are, the better help you'll receive from the community..."
                  value={content} 
                  onChange={(e) => { setContent(e.target.value); setContentError(null) }}
                  className={`min-h-[180px] text-base border-2 rounded-xl focus:ring-2 transition-all resize-none ${
                    contentError ? 'border-red-400 focus:border-red-400 focus:ring-red-100' : 'border-slate-200 focus:border-blue-500 focus:ring-blue-200'
                  }`}
                />
                {contentError && (
                  <p className="text-red-500 text-sm mt-1">
                    {contentError}
                  </p>
                )}
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-4 text-slate-500">
                    <span>💡 Tip: Be specific and clear</span>
                    <span>🏷️ Use relevant keywords</span>
                  </div>
                  <span className="text-slate-400">{content.length}/2000</span>
                </div>
              </div>

              {/* Media Attachments */}
              <div className="space-y-3">
                <Label className="text-base font-semibold text-slate-800 flex items-center space-x-2">
                  <Upload className="h-4 w-4 text-green-600" />
                  <span>Attachments (Optional)</span>
                </Label>
                <FileDropZone
                  onFilesSelect={setAttachments}
                  maxFiles={5}
                  acceptedTypes={['image/*', 'video/*']}
                  maxSize={50 * 1024 * 1024}
                />
              </div>

              {/* Error message */}
              {error && (
                <div className="bg-red-50 border-2 border-red-200 rounded-xl p-4">
                  <p className="text-red-700 text-sm font-medium whitespace-pre-line">⚠️ {error}</p>
                </div>
              )}
            </div>

            {/* Action buttons */}
            <div className="flex items-center justify-end space-x-3 pt-8 border-t border-slate-100 mt-8">
              <Button 
                variant="outline" 
                onClick={onClose}
                className="px-6 py-2.5 text-base font-semibold border-2 border-slate-300 hover:border-slate-400 transition-all rounded-xl"
              >
                Cancel
              </Button>
              <Button
                type="button"
                onClick={handleSaveDraft}
                disabled={savingDraft}
                className="px-6 py-2.5 text-base font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-xl"
              >
                {savingDraft ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Saving…
                  </>
                ) : (
                  <>
                    <Save className="h-5 w-5 mr-2" />
                    Save Draft
                  </>
                )}
              </Button>
              <Button 
                onClick={handleSubmit} 
                disabled={isLoading || !title.trim() || !content.trim() || !categoryId}
                className="px-8 py-2.5 text-base font-semibold bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white shadow-lg hover:shadow-xl transition-all transform hover:scale-105 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Publishing...
                  </>
                ) : (
                  <>
                    <Send className="h-5 w-5 mr-2" />
                    Publish Post
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}


