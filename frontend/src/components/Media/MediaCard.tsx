import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  Download,
  Heart,
  Lock,
  MessageCircle,
  Share2,
  Tag,
  Unlock,
} from "lucide-react"
import { useState } from "react"

import type { MediaPublic } from "@/client"
import { MediaService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface MediaCardProps {
  media: MediaPublic
}

const MediaCard = ({ media }: MediaCardProps) => {
  const [commentsOpen, setCommentsOpen] = useState(false)
  const [commentText, setCommentText] = useState("")
  const [tagName, setTagName] = useState("")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data: comments = [] } = useQuery({
    queryKey: ["comments", media.id],
    queryFn: () => MediaService.mediaReadComments({ mediaId: media.id }),
    enabled: commentsOpen,
  })

  const { data: tags = [] } = useQuery({
    queryKey: ["media-tags", media.id],
    queryFn: () => MediaService.mediaReadMediaTags({ mediaId: media.id }),
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["media"] })
  }

  const likeMutation = useMutation({
    mutationFn: () => MediaService.mediaLikeMedia({ mediaId: media.id }),
    onSuccess: () => showSuccessToast("Liked"),
    onError: handleError.bind(showErrorToast),
    onSettled: invalidate,
  })

  const favoriteMutation = useMutation({
    mutationFn: () => MediaService.mediaAddFavorite({ mediaId: media.id }),
    onSuccess: () => showSuccessToast("Added to favorites"),
    onError: handleError.bind(showErrorToast),
    onSettled: invalidate,
  })

  const commentMutation = useMutation({
    mutationFn: () =>
      MediaService.mediaCreateComment({
        mediaId: media.id,
        requestBody: { text: commentText, media_id: media.id },
      }),
    onSuccess: () => {
      showSuccessToast("Comment added")
      setCommentText("")
      queryClient.invalidateQueries({ queryKey: ["comments", media.id] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const tagMutation = useMutation({
    mutationFn: () =>
      MediaService.mediaCreateMediaTag({
        mediaId: media.id,
        requestBody: { tag_name: tagName },
      }),
    onSuccess: () => {
      showSuccessToast("Tag added")
      setTagName("")
      queryClient.invalidateQueries({ queryKey: ["media-tags", media.id] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const toggleAccessMutation = useMutation({
    mutationFn: () =>
      MediaService.mediaUpdateMedia({
        mediaId: media.id,
        requestBody: {
          access_level: media.access_level === "public" ? "private" : "public",
        },
      }),
    onSuccess: () => showSuccessToast("Access level updated"),
    onError: handleError.bind(showErrorToast),
    onSettled: invalidate,
  })

  const handleShare = async () => {
    const url = `${window.location.origin}/events/${media.event_id}?media=${media.id}`
    await navigator.clipboard.writeText(url)
    showSuccessToast("Link copied to clipboard")
  }

  const handleDownload = () => {
    showSuccessToast("Download started (watermark applied)")
    if (media.file_path) {
      const a = document.createElement("a")
      a.href = media.file_path
      a.download = media.filename
      a.click()
    }
  }

  return (
    <>
      <div className="rounded-lg border overflow-hidden bg-card">
        <div className="aspect-video bg-muted flex items-center justify-center relative">
          {media.media_type === "photo" ? (
            <img
              src={media.file_path || undefined}
              alt={media.filename}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.currentTarget.style.display = "none"
              }}
            />
          ) : null}
          <div className="absolute inset-0 flex flex-col items-center justify-center text-muted-foreground p-4 text-center">
            <span className="text-4xl mb-2">
              {media.media_type === "video" ? "🎬" : "📷"}
            </span>
            <span className="text-xs truncate max-w-full">{media.filename}</span>
          </div>
          <Badge
            className="absolute top-2 right-2"
            variant={media.access_level === "public" ? "default" : "secondary"}
          >
            {media.access_level === "public" ? (
              <Unlock className="size-3 mr-1" />
            ) : (
              <Lock className="size-3 mr-1" />
            )}
            {media.access_level}
          </Badge>
        </div>

        <div className="p-3 space-y-3">
          <div className="flex flex-wrap gap-1">
            {tags.map((tag) => (
              <Badge key={tag.id} variant="outline" className="text-xs">
                {tag.tag_name}
              </Badge>
            ))}
          </div>

          <div className="flex flex-wrap gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => likeMutation.mutate()}
              disabled={likeMutation.isPending}
            >
              <Heart className="size-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => favoriteMutation.mutate()}
              disabled={favoriteMutation.isPending}
            >
              <Heart className="size-4 fill-current" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setCommentsOpen(true)}>
              <MessageCircle className="size-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={handleShare}>
              <Share2 className="size-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={handleDownload}>
              <Download className="size-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => toggleAccessMutation.mutate()}
              disabled={toggleAccessMutation.isPending}
            >
              {media.access_level === "public" ? (
                <Lock className="size-4" />
              ) : (
                <Unlock className="size-4" />
              )}
            </Button>
          </div>

          <div className="flex gap-2">
            <Input
              placeholder="Add AI tag..."
              value={tagName}
              onChange={(e) => setTagName(e.target.value)}
              className="h-8 text-xs"
            />
            <Button
              size="sm"
              variant="outline"
              disabled={!tagName || tagMutation.isPending}
              onClick={() => tagMutation.mutate()}
            >
              <Tag className="size-3" />
            </Button>
          </div>
        </div>
      </div>

      <Dialog open={commentsOpen} onOpenChange={setCommentsOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Comments</DialogTitle>
          </DialogHeader>
          <div className="max-h-48 overflow-y-auto space-y-2">
            {comments.length === 0 && (
              <p className="text-sm text-muted-foreground">No comments yet.</p>
            )}
            {comments.map((c) => (
              <div key={c.id} className="text-sm border rounded-md p-2">
                {c.text}
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              placeholder="Write a comment..."
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
            />
            <LoadingButton
              loading={commentMutation.isPending}
              disabled={!commentText}
              onClick={() => commentMutation.mutate()}
            >
              Post
            </LoadingButton>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

export default MediaCard
