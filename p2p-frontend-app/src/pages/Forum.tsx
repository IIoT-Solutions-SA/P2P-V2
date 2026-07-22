import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import type { FormEvent } from "react"
import { useSearchParams } from "react-router-dom"
import { ArrowLeft, BadgeCheck, Bookmark, Bot, CheckCircle2, CircleHelp, Clock3, DatabaseZap, Eye, Film, Flame, Gauge, ImageIcon, MessageSquare, Paperclip, Plus, ScanEye, Search, Send, ThumbsUp, Trash2, X } from "lucide-react"
import { Avatar } from "@/components/ui/Avatar"
import { Button } from "@/components/ui/button"
import { EmptyState, ErrorState, LoadingState } from "@/components/shared/AppState"
import { forumApi, type ForumAttachment, type ForumCategory, type ForumContributor, type ForumPost, type ForumReply, type ForumStats } from "@/lib/api/forum"
import { dashboardApi, type ForumDraft } from "@/lib/api/dashboard"
import { buildApiUrl } from "@/config/environment"
import { useAuth } from "@/contexts/AuthContext"
import { cn } from "@/lib/utils"

const displayName = (value?: string) => value || "Community member"
const acceptedMediaTypes = ["image/jpeg", "image/png", "image/webp", "image/gif", "video/mp4", "video/webm"]
const maxImageBytes = 5 * 1024 * 1024
const maxVideoBytes = 50 * 1024 * 1024

const attachmentType = (attachment: ForumAttachment) => attachment.type || attachment.mime_type || ""
const readableSize = (bytes?: number) => bytes ? `${(bytes / (1024 * 1024)).toFixed(bytes > 10 * 1024 * 1024 ? 0 : 1)} MB` : ""

function AttachmentGallery({ attachments }: { attachments?: ForumAttachment[] }) {
  if (!attachments?.length) return null
  return (
    <div className={cn("mt-4 grid gap-3", attachments.length > 1 && "sm:grid-cols-2")}>
      {attachments.map((attachment, index) => {
        const type = attachmentType(attachment)
        const mediaUrl = attachment.url.startsWith("/") ? buildApiUrl(attachment.url) : attachment.url
        return (
          <figure key={`${attachment.url}-${index}`} className="overflow-hidden border border-[var(--peer-line)] bg-[#f2f4f0]">
            {type.startsWith("video/") ? (
              <video controls preload="metadata" className="max-h-[460px] w-full bg-black object-contain" src={mediaUrl}>
                Your browser does not support this video.
              </video>
            ) : (
              <a href={mediaUrl} target="_blank" rel="noreferrer" aria-label={`Open ${attachment.filename}`}>
                <img src={mediaUrl} alt={attachment.filename} loading="lazy" className="max-h-[460px] w-full object-contain" />
              </a>
            )}
            <figcaption className="flex items-center gap-2 border-t border-[var(--peer-line)] bg-white px-3 py-2 text-[11px] text-[var(--peer-muted)]">
              {type.startsWith("video/") ? <Film className="size-3.5 shrink-0" /> : <ImageIcon className="size-3.5 shrink-0" />}
              <span className="min-w-0 flex-1 truncate">{attachment.filename}</span><span>{readableSize(attachment.size)}</span>
            </figcaption>
          </figure>
        )
      })}
    </div>
  )
}

function SelectedFileCard({ file, onRemove }: { file: File; onRemove: () => void }) {
  const [previewUrl, setPreviewUrl] = useState("")
  useEffect(() => {
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [file])
  return (
    <div className="relative overflow-hidden border border-[var(--peer-line)] bg-[#f2f4f0]">
      {file.type.startsWith("video/") ? <video src={previewUrl} muted className="h-28 w-full bg-black object-contain" /> : <img src={previewUrl} alt="" className="h-28 w-full object-contain" />}
      <div className="flex items-center gap-2 bg-white px-2 py-2 text-[10px]"><span className="min-w-0 flex-1 truncate">{file.name}</span><span className="text-[var(--peer-muted)]">{readableSize(file.size)}</span></div>
      <button type="button" onClick={onRemove} aria-label={`Remove ${file.name}`} className="absolute right-1.5 top-1.5 grid size-7 place-items-center bg-black/75 text-white"><X className="size-3.5" /></button>
    </div>
  )
}

function MediaPicker({ id, files, onChange, onError }: { id: string; files: File[]; onChange: (files: File[]) => void; onError: (message: string | null) => void }) {
  const addFiles = (incoming: File[]) => {
    onError(null)
    const next = [...files]
    for (const file of incoming) {
      if (!acceptedMediaTypes.includes(file.type)) { onError(`${file.name}: use JPEG, PNG, WebP, GIF, MP4, or WebM.`); continue }
      const limit = file.type.startsWith("video/") ? maxVideoBytes : maxImageBytes
      if (file.size > limit) { onError(`${file.name}: ${file.type.startsWith("video/") ? "videos" : "images"} must be under ${limit / 1024 / 1024} MB.`); continue }
      if (next.length >= 5) { onError("You can attach up to 5 images or videos."); break }
      next.push(file)
    }
    onChange(next)
  }
  return (
    <div>
      {files.length ? <div className="mb-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{files.map((file, index) => <SelectedFileCard key={`${file.name}-${file.lastModified}-${index}`} file={file} onRemove={() => onChange(files.filter((_, itemIndex) => itemIndex !== index))} />)}</div> : null}
      <label htmlFor={id} className="inline-flex h-10 cursor-pointer items-center gap-2 border border-[var(--peer-line)] bg-white px-3 text-xs font-bold text-[var(--peer-blue)] hover:bg-[#f2f5f1]"><Paperclip className="size-4" />Add photos or videos</label>
      <input id={id} type="file" multiple accept="image/jpeg,image/png,image/webp,image/gif,video/mp4,video/webm" className="sr-only" onChange={(event) => { addFiles(Array.from(event.target.files || [])); event.target.value = "" }} />
      <p className="mt-2 text-[10px] text-[var(--peer-muted)]">Up to 5 files · images 5 MB each · videos 50 MB each</p>
    </div>
  )
}

function ReplyNode({
  reply,
  onReply,
  onLike,
}: {
  reply: ForumReply
  onReply: (replyId: string) => void
  onLike: (replyId: string) => void
}) {
  return (
    <div className="border-l border-[var(--peer-line)] pl-4">
      <div className={reply.isBestAnswer ? "bg-[var(--peer-teal-soft)] p-4" : "p-4"}>
        <div className="mb-3 flex items-center justify-between gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <Avatar name={reply.author} src={reply.authorProfilePicture} size="sm" />
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold">{reply.author}</p>
              <p className="text-xs text-[var(--peer-muted)]">{reply.timeAgo}</p>
            </div>
          </div>
          {reply.isBestAnswer ? <span className="flex items-center gap-1 text-xs font-bold text-[var(--peer-teal)]"><CheckCircle2 className="size-4" />Best answer</span> : null}
        </div>
        <p className="whitespace-pre-wrap text-sm leading-6 text-[var(--peer-ink)]">{reply.content}</p>
        <AttachmentGallery attachments={reply.attachments} />
        <div className="mt-3 flex gap-2">
          <Button variant="ghost" size="sm" onClick={() => onLike(reply.id)}><ThumbsUp className="size-4" />{reply.likes}</Button>
          <Button variant="ghost" size="sm" onClick={() => onReply(reply.id)}><MessageSquare className="size-4" />Reply</Button>
        </div>
      </div>
      {(reply.replies || []).map((child) => (
        <ReplyNode key={child.id} reply={child} onReply={onReply} onLike={onLike} />
      ))}
    </div>
  )
}

export default function Forum() {
  const { user } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()
  const [categories, setCategories] = useState<ForumCategory[]>([])
  const [posts, setPosts] = useState<ForumPost[]>([])
  const [stats, setStats] = useState<ForumStats>({ total_topics: 0, active_members: 0, helpful_answers: 0 })
  const [contributors, setContributors] = useState<ForumContributor[]>([])
  const [drafts, setDrafts] = useState<ForumDraft[]>([])
  const [selectedPost, setSelectedPost] = useState<ForumPost | null>(null)
  const [bookmarks, setBookmarks] = useState<Set<string>>(new Set())
  const [category, setCategory] = useState("all")
  const [query, setQuery] = useState("")
  const [viewFilter, setViewFilter] = useState<"recent" | "unanswered" | "solved" | "saved">("recent")
  const [loading, setLoading] = useState(true)
  const [threadLoading, setThreadLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [composerOpen, setComposerOpen] = useState(false)
  const [composer, setComposer] = useState({ title: "", category: "General Discussion", content: "", tags: "" })
  const [reply, setReply] = useState("")
  const [replyTo, setReplyTo] = useState<string | null>(null)
  const [postFiles, setPostFiles] = useState<File[]>([])
  const [replyFiles, setReplyFiles] = useState<File[]>([])
  const [mediaError, setMediaError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const closingThreadRef = useRef(false)
  const postParam = searchParams.get("post")

  const loadForum = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [categoryData, postData, bookmarkData, statsData, contributorData, draftData] = await Promise.all([
        forumApi.categories(),
        forumApi.posts(category, 100),
        forumApi.bookmarks().catch(() => []),
        forumApi.stats().catch(() => ({ total_topics: 0, active_members: 0, helpful_answers: 0 })),
        forumApi.contributors(4).catch(() => ({ contributors: [] })),
        dashboardApi.forumDrafts().catch(() => ({ drafts: [], total: 0 })),
      ])
      setCategories(categoryData.categories || [])
      setPosts(postData.posts || [])
      setBookmarks(new Set((bookmarkData || []).map((item) => String(item.target_id))))
      setStats(statsData)
      setContributors(contributorData.contributors || [])
      setDrafts(draftData.drafts || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load forum")
    } finally {
      setLoading(false)
    }
  }, [category])

  const openThread = useCallback(async (postId: string) => {
    setThreadLoading(true)
    try {
      const post = await forumApi.post(postId)
      setSelectedPost(post)
      setSearchParams({ post: postId })
    } finally {
      setThreadLoading(false)
    }
  }, [setSearchParams])

  useEffect(() => {
    void loadForum()
  }, [loadForum])

  useEffect(() => {
    if (!postParam) {
      closingThreadRef.current = false
      return
    }
    if (!closingThreadRef.current && selectedPost?.id !== postParam) void openThread(postParam)
  }, [openThread, postParam, selectedPost?.id])

  const filteredPosts = useMemo(() => {
    const needle = query.toLowerCase().trim()
    return posts.filter((post) => {
      const matchesQuery = !needle || [post.title, post.excerpt, post.content, post.author, post.category, ...(post.tags || [])].join(" ").toLowerCase().includes(needle)
      const matchesView = viewFilter === "recent"
        || (viewFilter === "unanswered" && post.replies === 0)
        || (viewFilter === "solved" && post.hasBestAnswer)
        || (viewFilter === "saved" && bookmarks.has(post.id))
      return matchesQuery && matchesView
    })
  }, [bookmarks, posts, query, viewFilter])

  const closeThread = () => {
    closingThreadRef.current = true
    setSelectedPost(null)
    setReply("")
    setReplyTo(null)
    setReplyFiles([])
    setMediaError(null)
    setSearchParams({}, { replace: true })
  }

  const submitPost = async (event: FormEvent) => {
    event.preventDefault()
    setMediaError(null)
    setSaving(true)
    try {
      const created = await forumApi.createPost({
        title: composer.title,
        category_id: composer.category,
        content: composer.content,
        tags: composer.tags.split(",").map((tag) => tag.trim()).filter(Boolean).slice(0, 5),
      })
      try {
        for (const file of postFiles) await forumApi.uploadAttachment(file, { postId: created.id })
      } catch (err) {
        setMediaError(err instanceof Error ? `The discussion was posted, but media upload failed: ${err.message}` : "The discussion was posted, but media upload failed.")
      }
      setComposer({ title: "", category: composer.category, content: "", tags: "" })
      setPostFiles([])
      setComposerOpen(false)
      await loadForum()
      await openThread(created.id)
    } catch (err) {
      setMediaError(err instanceof Error ? err.message : "Unable to publish the discussion.")
    } finally {
      setSaving(false)
    }
  }

  const submitReply = async (event: FormEvent) => {
    event.preventDefault()
    if (!selectedPost || !reply.trim()) return
    setMediaError(null)
    setSaving(true)
    try {
      const created = await forumApi.reply(selectedPost.id, reply, replyTo)
      try {
        for (const file of replyFiles) await forumApi.uploadAttachment(file, { replyId: created.reply_id })
      } catch (err) {
        setMediaError(err instanceof Error ? `The reply was posted, but media upload failed: ${err.message}` : "The reply was posted, but media upload failed.")
      }
      setReply("")
      setReplyTo(null)
      setReplyFiles([])
      await openThread(selectedPost.id)
    } catch (err) {
      setMediaError(err instanceof Error ? err.message : "Unable to publish the reply.")
    } finally {
      setSaving(false)
    }
  }

  const togglePostLike = async (post: ForumPost) => {
    const result = await forumApi.likePost(post.id)
    setPosts((prev) => prev.map((item) => item.id === post.id ? { ...item, likes: result.likes, isLikedByUser: result.liked } : item))
    setSelectedPost((prev) => prev && prev.id === post.id ? { ...prev, likes: result.likes, isLikedByUser: result.liked } : prev)
  }

  const toggleBookmark = async (post: ForumPost) => {
    const result = await forumApi.bookmarkPost(post.id)
    setBookmarks((prev) => {
      const next = new Set(prev)
      if (result.bookmarked) next.add(post.id)
      else next.delete(post.id)
      return next
    })
  }

  const deletePost = async (post: ForumPost) => {
    if (!window.confirm(`Delete "${post.title}"?`)) return
    await forumApi.deletePost(post.id)
    closeThread()
    await loadForum()
  }

  const canManagePost = (post: ForumPost) => {
    const userWithMongoId = user as (typeof user & { mongo_id?: string })
    return Boolean(user && (user.role === "admin" || user.id === post.author_id || userWithMongoId?.mongo_id === post.author_id))
  }

  if (loading) return <div className="px-5 py-10 md:px-8 xl:px-[58px]"><LoadingState title="Loading forum workspace" /></div>
  if (error) return <div className="px-5 py-10 md:px-8 xl:px-[58px]"><ErrorState title="Forum unavailable" description={error} actionLabel="Retry" onAction={() => void loadForum()} /></div>

  const categoryIcons = [Bot, ScanEye, Gauge, DatabaseZap]
  const featuredCategories = categories.filter((item) => item.id !== "all").slice(0, 4)
  const totalTopics = stats.total_topics || posts.length
  const solvedCount = posts.filter((post) => post.hasBestAnswer).length
  const awaitingInput = posts.filter((post) => post.replies === 0).length

  return (
    <div className="min-h-[calc(100vh-var(--peer-topbar-height))] bg-[var(--peer-paper)] [--peer-surface:#ffffff]">
      <div className="mx-auto w-full max-w-[1430px] px-5 pb-16 pt-8 md:px-8 md:pt-11 xl:px-[58px]">
        <header className="mb-8 grid items-end gap-5 md:grid-cols-[minmax(0,1fr)_auto] md:gap-7">
          <div>
            <p className="peer-eyebrow mb-2">Peer troubleshooting</p>
            <h1 className="font-display max-w-[800px] text-[clamp(30px,3.2vw,44px)] font-semibold leading-[1.13] tracking-[-0.045em]">Forum built for practical manufacturing questions.</h1>
            <p className="mt-3 max-w-[760px] text-[15px] leading-6 text-[var(--peer-muted)]">Search active discussions, browse technical categories, and move unresolved shop-floor problems toward tested answers.</p>
          </div>
          <div className="min-w-[220px] border-l-2 border-[var(--peer-teal)] py-1 pl-4">
            <strong className="font-display block text-xl font-semibold">{totalTopics} discussions</strong>
            <span className="text-xs text-[var(--peer-muted)]">{solvedCount} solved · {awaitingInput} awaiting expert input</span>
          </div>
        </header>

        {mediaError ? <div role="alert" className="mb-5 flex items-start justify-between gap-3 border border-[#d7a7a1] bg-[#fff2f0] px-4 py-3 text-sm text-[var(--peer-danger)]"><span>{mediaError}</span><button type="button" onClick={() => setMediaError(null)} aria-label="Dismiss message"><X className="size-4" /></button></div> : null}

        {composerOpen ? (
          <section className="peer-panel mb-[22px]" aria-labelledby="composer-title">
            <div className="flex items-start justify-between border-b border-[var(--peer-line)] px-6 py-5">
              <div><p className="peer-eyebrow mb-1">New discussion</p><h2 id="composer-title" className="font-display text-xl font-semibold">Ask the network</h2></div>
              <button type="button" onClick={() => setComposerOpen(false)} aria-label="Close composer" className="grid size-9 place-items-center border border-[var(--peer-line)]"><X className="size-4" /></button>
            </div>
            <form onSubmit={submitPost} className="grid gap-4 p-6">
              <div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_260px]">
                <label className="grid gap-1.5 text-xs font-semibold">Question title<input required minLength={8} maxLength={150} className="h-11 border border-[var(--peer-line)] bg-white px-3 text-sm font-normal" placeholder="What problem are you trying to solve?" value={composer.title} onChange={(event) => setComposer((prev) => ({ ...prev, title: event.target.value }))} /></label>
                <label className="grid gap-1.5 text-xs font-semibold">Category<select className="h-11 border border-[var(--peer-line)] bg-white px-3 text-sm font-normal" value={composer.category} onChange={(event) => setComposer((prev) => ({ ...prev, category: event.target.value }))}>{categories.filter((item) => item.id !== "all").map((item) => <option key={item.id} value={item.name}>{item.name}</option>)}</select></label>
              </div>
              <label className="grid gap-1.5 text-xs font-semibold">Context, constraints and what you tried<textarea required minLength={20} maxLength={5000} className="min-h-40 border border-[var(--peer-line)] bg-white p-3 text-sm font-normal leading-6" value={composer.content} onChange={(event) => setComposer((prev) => ({ ...prev, content: event.target.value }))} /></label>
              <MediaPicker id="forum-post-media" files={postFiles} onChange={setPostFiles} onError={setMediaError} />
              <label className="grid gap-1.5 text-xs font-semibold">Tags<input className="h-11 border border-[var(--peer-line)] bg-white px-3 text-sm font-normal" placeholder="PLC, compressed air, OEE" value={composer.tags} onChange={(event) => setComposer((prev) => ({ ...prev, tags: event.target.value }))} /></label>
              <div className="flex flex-wrap justify-end gap-2"><Button type="button" variant="outline" className="bg-white" onClick={() => { setComposerOpen(false); setPostFiles([]); setMediaError(null) }}>Cancel</Button><Button disabled={saving} className="bg-[var(--peer-teal)] text-white"><Send className="size-4" />{saving ? "Publishing…" : "Post question"}</Button></div>
            </form>
          </section>
        ) : null}

        {threadLoading ? <LoadingState title="Opening discussion" /> : selectedPost ? (
          <article className="grid items-start gap-[22px] lg:grid-cols-[minmax(0,1fr)_310px]">
            <div className="peer-panel min-w-0">
              <div className="border-b border-[var(--peer-line)] px-6 py-5">
                <button type="button" onClick={closeThread} className="mb-5 inline-flex items-center gap-2 text-xs font-bold text-[var(--peer-blue)]"><ArrowLeft className="size-4" />Back to discussions</button>
                <div className="flex flex-wrap items-center gap-2 text-[11px] text-[var(--peer-muted)]">
                  {selectedPost.hasBestAnswer ? <span className="inline-flex items-center gap-1 bg-[var(--peer-teal-soft)] px-2 py-1 font-bold text-[var(--peer-teal)]"><BadgeCheck className="size-3.5" />Solved</span> : <span className="bg-[#f0e7da] px-2 py-1 font-bold text-[var(--peer-amber)]">Needs input</span>}
                  <span>{selectedPost.category}</span><span>·</span><span>{selectedPost.timeAgo}</span>
                </div>
                <h1 className="font-display mt-3 text-[clamp(25px,3vw,36px)] font-semibold leading-tight tracking-[-0.035em]">{selectedPost.title}</h1>
                <div className="mt-5 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                  <div className="flex items-center gap-3"><Avatar name={selectedPost.author} src={selectedPost.author_profile_picture} size="sm" /><div><strong className="block text-sm">{displayName(selectedPost.author)}</strong><span className="text-xs text-[var(--peer-muted)]">{selectedPost.authorTitle || "PeerLink contributor"}</span></div></div>
                  <div className="flex gap-2"><Button variant="outline" className="bg-white" onClick={() => void togglePostLike(selectedPost)}><ThumbsUp className={selectedPost.isLikedByUser ? "size-4 fill-current" : "size-4"} />{selectedPost.likes}</Button><Button variant="outline" className="bg-white" onClick={() => void toggleBookmark(selectedPost)}><Bookmark className={bookmarks.has(selectedPost.id) ? "size-4 fill-current" : "size-4"} /></Button>{canManagePost(selectedPost) ? <Button variant="outline" className="bg-white text-[var(--peer-danger)]" onClick={() => void deletePost(selectedPost)}><Trash2 className="size-4" /></Button> : null}</div>
                </div>
              </div>
              <div className="border-b border-[var(--peer-line)] px-6 py-7"><p className="whitespace-pre-wrap text-[15px] leading-7">{selectedPost.content}</p><AttachmentGallery attachments={selectedPost.attachments} /><div className="mt-6 flex gap-5 text-xs text-[var(--peer-muted)]"><span className="inline-flex items-center gap-1.5"><Eye className="size-4" />{selectedPost.views} views</span><span className="inline-flex items-center gap-1.5"><MessageSquare className="size-4" />{selectedPost.comments?.length || selectedPost.replies} replies</span></div></div>
              <div className="p-6"><p className="peer-eyebrow mb-1">Peer responses</p><h2 className="font-display mb-5 text-xl font-semibold">Replies</h2><div className="grid gap-4">{(selectedPost.comments || []).length === 0 ? <EmptyState className="min-h-52 shadow-none" title="No replies yet" description="Share the first answer or request clarification." /> : selectedPost.comments?.map((item) => <ReplyNode key={item.id} reply={item} onReply={(id) => setReplyTo(id)} onLike={(id) => void forumApi.likeReply(id).then(() => openThread(selectedPost.id))} />)}</div>
                <form onSubmit={submitReply} className="mt-6 border-t border-[var(--peer-line)] pt-6">{replyTo ? <p className="mb-2 text-xs text-[var(--peer-muted)]">Replying to a response · <button type="button" className="font-bold text-[var(--peer-blue)]" onClick={() => setReplyTo(null)}>Cancel</button></p> : null}<textarea required minLength={3} maxLength={3000} className="mb-3 min-h-32 w-full border border-[var(--peer-line)] bg-white p-3 text-sm" value={reply} onChange={(event) => setReply(event.target.value)} placeholder="Add practical detail, a tested method, or a clarifying question." /><MediaPicker id="forum-reply-media" files={replyFiles} onChange={setReplyFiles} onError={setMediaError} /><Button disabled={saving} className="mt-3 bg-[var(--peer-teal)] text-white"><Send className="size-4" />{saving ? "Publishing…" : "Post reply"}</Button></form>
              </div>
            </div>
            <aside className="grid gap-[22px] lg:sticky lg:top-[calc(var(--peer-topbar-height)+22px)]"><section className="peer-panel p-5"><p className="peer-eyebrow mb-2">Discussion status</p><dl className="grid gap-3 text-sm"><div className="flex justify-between"><dt className="text-[var(--peer-muted)]">Replies</dt><dd className="font-semibold">{selectedPost.replies}</dd></div><div className="flex justify-between"><dt className="text-[var(--peer-muted)]">Views</dt><dd className="font-semibold">{selectedPost.views}</dd></div><div className="flex justify-between"><dt className="text-[var(--peer-muted)]">Category</dt><dd className="max-w-[160px] text-right font-semibold">{selectedPost.category}</dd></div></dl></section><Button onClick={() => setComposerOpen(true)} className="min-h-11 bg-[var(--peer-teal)] text-white"><Plus className="size-4" />Ask another question</Button></aside>
          </article>
        ) : (
          <>
            <section className="peer-panel mb-[22px]" aria-labelledby="forum-tools-title">
              <div className="flex flex-col justify-between gap-4 border-b border-[var(--peer-line)] px-6 py-5 sm:flex-row sm:items-center"><div><p className="peer-eyebrow mb-1">Find a discussion</p><h2 id="forum-tools-title" className="font-display text-xl font-semibold">Search, categories and filters</h2></div><Button onClick={() => setComposerOpen(true)} className="bg-[var(--peer-teal)] text-white"><Plus className="size-4" />Ask a question</Button></div>
              <div className="grid gap-4 border-b border-[var(--peer-line)] p-5 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center"><label className="relative block"><Search className="absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-[var(--peer-muted)]" /><input className="h-11 w-full border border-[var(--peer-line)] bg-white pl-10 pr-3 text-sm" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search active manufacturing discussions" /></label><div className="flex flex-wrap gap-2">{([['recent', Clock3], ['unanswered', CircleHelp], ['solved', BadgeCheck], ['saved', Bookmark]] as const).map(([filter, Icon]) => <button key={filter} type="button" onClick={() => setViewFilter(filter)} className={viewFilter === filter ? "inline-flex h-10 items-center gap-1.5 bg-[var(--peer-teal)] px-3 text-xs font-bold capitalize text-white" : "inline-flex h-10 items-center gap-1.5 border border-[var(--peer-line)] bg-white px-3 text-xs font-semibold capitalize text-[var(--peer-muted)]"}><Icon className="size-3.5" />{filter}</button>)}</div></div>
              <div className="grid sm:grid-cols-2 xl:grid-cols-4">{featuredCategories.map((item, index) => { const Icon = categoryIcons[index] || MessageSquare; return <button key={item.id} type="button" onClick={() => setCategory(item.name)} className={cn("group min-h-[155px] border-b border-[var(--peer-line)] p-5 text-left hover:bg-[#f2f5f1] sm:border-r", index > 1 && "sm:border-b-0", index === 1 && "sm:border-r-0 xl:border-r", index === 3 && "sm:border-r-0")}><span className="mb-5 flex items-start justify-between"><span className="grid size-10 place-items-center border border-[#c4d7d1] bg-[var(--peer-teal-soft)] text-[var(--peer-teal)]"><Icon className="size-5" /></span><span className="font-display text-xl font-semibold text-[var(--peer-teal)]">{item.count}</span></span><strong className="block text-sm">{item.name}</strong><span className="mt-1 block text-xs text-[var(--peer-muted)]">Browse field questions and tested answers.</span></button> })}</div>
            </section>

            <div className="grid items-start gap-[22px] xl:grid-cols-[minmax(0,1fr)_320px]">
              <section className="peer-panel min-w-0" aria-labelledby="threads-title"><div className="flex items-start justify-between border-b border-[var(--peer-line)] px-6 py-5"><div><p className="peer-eyebrow mb-1">Open questions</p><h2 id="threads-title" className="font-display text-xl font-semibold">Latest discussions</h2></div><span className="text-xs text-[var(--peer-muted)]">{filteredPosts.length} shown</span></div>{filteredPosts.length === 0 ? <EmptyState className="m-5 min-h-56 shadow-none" title="No matching discussions" description="Try a broader search or another filter." actionLabel="Clear filters" onAction={() => { setQuery(''); setViewFilter('recent'); setCategory('all') }} /> : <div>{filteredPosts.map((post) => <article key={post.id} className="grid gap-4 border-b border-[var(--peer-line)] px-5 py-5 last:border-b-0 md:grid-cols-[42px_minmax(0,1fr)_210px]"><Avatar name={post.author} src={post.author_profile_picture} size="md" /><button type="button" onClick={() => void openThread(post.id)} className="min-w-0 text-left"><div className="mb-2 flex flex-wrap items-center gap-2 text-[11px] text-[var(--peer-muted)]">{post.hasBestAnswer ? <span className="inline-flex items-center gap-1 bg-[var(--peer-teal-soft)] px-2 py-1 font-bold text-[var(--peer-teal)]"><BadgeCheck className="size-3.5" />Solved</span> : post.replies > 3 ? <span className="inline-flex items-center gap-1 bg-[#f0e7da] px-2 py-1 font-bold text-[var(--peer-amber)]"><Flame className="size-3.5" />Active</span> : <span className="bg-[#eeece5] px-2 py-1 font-bold">Needs input</span>}<span>{post.category}</span><span>·</span><span>{post.timeAgo}</span></div><h3 className="font-display text-[17px] font-semibold leading-snug hover:text-[var(--peer-teal)]">{post.title}</h3><p className="mt-2 line-clamp-2 text-xs leading-5 text-[var(--peer-muted)]">{post.excerpt || post.content}</p><span className="mt-3 block text-[11px] text-[var(--peer-muted)]">{displayName(post.author)}{post.authorTitle ? ` · ${post.authorTitle}` : ''}</span></button><div className="grid grid-cols-3 border border-[var(--peer-line)] self-center"><span className="px-2 py-3 text-center"><strong className="font-display block text-base">{post.replies}</strong><span className="text-[10px] text-[var(--peer-muted)]">Replies</span></span><span className="border-x border-[var(--peer-line)] px-2 py-3 text-center"><strong className="font-display block text-base">{post.likes}</strong><span className="text-[10px] text-[var(--peer-muted)]">Useful</span></span><span className="px-2 py-3 text-center"><strong className="font-display block text-base">{post.views}</strong><span className="text-[10px] text-[var(--peer-muted)]">Views</span></span></div></article>)}</div>}</section>
              <aside className="grid gap-[22px]"><section className="peer-panel"><div className="border-b border-[var(--peer-line)] px-5 py-4"><p className="peer-eyebrow mb-1">Draft access</p><h2 className="font-display text-lg font-semibold">Continue writing</h2></div><div>{drafts.slice(0, 2).map((draft) => <div key={draft.id} className="border-b border-[var(--peer-line)] px-5 py-4"><strong className="block truncate text-xs">{draft.title || 'Untitled forum draft'}</strong><span className="mt-1 block text-[10px] text-[var(--peer-muted)]">Forum draft · saved recently</span></div>)}</div><button type="button" onClick={() => setComposerOpen(true)} className="flex w-full items-center justify-between bg-[#f1f2ed] px-5 py-4 text-left"><span><strong className="block text-xs">Open forum composer</strong><span className="text-[10px] text-[var(--peer-muted)]">Recover or start a question</span></span><span className="font-display text-xl font-bold text-[var(--peer-amber)]">{drafts.length}</span></button></section><section className="peer-panel"><div className="border-b border-[var(--peer-line)] px-5 py-4"><p className="peer-eyebrow mb-1">Available expertise</p><h2 className="font-display text-lg font-semibold">Relevant peers</h2></div>{contributors.length ? contributors.map((person) => <div key={person.name} className="flex items-center gap-3 border-b border-[var(--peer-line)] px-5 py-4 last:border-b-0"><Avatar name={person.name} src={person.avatar} size="sm" /><span className="min-w-0"><strong className="block truncate text-xs">{person.name}</strong><span className="text-[10px] text-[var(--peer-muted)]">{person.points} contribution points</span></span></div>) : <div className="p-5 text-xs text-[var(--peer-muted)]">Peer expertise will appear as the network contributes.</div>}</section></aside>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
