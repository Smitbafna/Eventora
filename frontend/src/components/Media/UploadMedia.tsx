import { useMutation, useQueryClient } from "@tanstack/react-query"
import { ImagePlus, Upload } from "lucide-react"
import { useCallback, useState } from "react"

import type { AccessLevel, AlbumPublic } from "@/client"
import { MediaService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface UploadMediaProps {
  eventId: string
  albums: AlbumPublic[]
}

interface PendingFile {
  file: File
  preview: string
}

const UploadMedia = ({ eventId, albums }: UploadMediaProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const [pendingFiles, setPendingFiles] = useState<PendingFile[]>([])
  const [accessLevel, setAccessLevel] = useState<AccessLevel>("private")
  const [albumId, setAlbumId] = useState<string>("none")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const addFiles = useCallback((files: FileList | File[]) => {
    const next = Array.from(files).map((file) => ({
      file,
      preview: URL.createObjectURL(file),
    }))
    setPendingFiles((prev) => [...prev, ...next])
  }, [])

  const mutation = useMutation({
    mutationFn: async () => {
      for (const { file } of pendingFiles) {
        const mediaType = file.type.startsWith("video/") ? "video" : "photo"
        await MediaService.mediaCreateMedia({
          requestBody: {
            filename: file.name,
            media_type: mediaType,
            access_level: accessLevel,
            file_size: file.size,
            file_path: `/uploads/${eventId}/${file.name}`,
            event_id: eventId,
            album_id: albumId === "none" ? null : albumId,
          },
        })
      }
    },
    onSuccess: () => {
      showSuccessToast(
        `${pendingFiles.length} file(s) uploaded successfully`,
      )
      pendingFiles.forEach(({ preview }) => URL.revokeObjectURL(preview))
      setPendingFiles([])
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["media", eventId] })
    },
  })

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => {
        if (!open) {
          pendingFiles.forEach(({ preview }) => URL.revokeObjectURL(preview))
          setPendingFiles([])
        }
        setIsOpen(open)
      }}
    >
      <DialogTrigger asChild>
        <Button size="sm">
          <Upload className="mr-2 size-4" />
          Upload Media
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Upload Media</DialogTitle>
          <DialogDescription>
            Drag and drop photos or videos, or browse files. Supports bulk
            upload.
          </DialogDescription>
        </DialogHeader>

        <div
          className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:bg-muted/50 transition-colors"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault()
            if (e.dataTransfer.files.length) addFiles(e.dataTransfer.files)
          }}
          onClick={() => {
            const input = document.createElement("input")
            input.type = "file"
            input.multiple = true
            input.accept = "image/*,video/*"
            input.onchange = () => {
              if (input.files?.length) addFiles(input.files)
            }
            input.click()
          }}
        >
          <ImagePlus className="mx-auto size-10 text-muted-foreground mb-2" />
          <p className="text-sm font-medium">Drop files here or click to browse</p>
          <p className="text-xs text-muted-foreground mt-1">
            Photos and videos supported
          </p>
        </div>

        {pendingFiles.length > 0 && (
          <div className="grid grid-cols-3 gap-2 max-h-48 overflow-y-auto">
            {pendingFiles.map(({ file, preview }) => (
              <div key={preview} className="relative rounded-md overflow-hidden border">
                {file.type.startsWith("image/") ? (
                  <img
                    src={preview}
                    alt={file.name}
                    className="aspect-square object-cover w-full"
                  />
                ) : (
                  <div className="aspect-square flex items-center justify-center bg-muted text-xs p-2">
                    {file.name}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label>Access Level</Label>
            <Select
              value={accessLevel}
              onValueChange={(v) => setAccessLevel(v as AccessLevel)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="public">Public</SelectItem>
                <SelectItem value="private">Private</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Album (optional)</Label>
            <Select value={albumId} onValueChange={setAlbumId}>
              <SelectTrigger>
                <SelectValue placeholder="No album" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">No album</SelectItem>
                {albums.map((album) => (
                  <SelectItem key={album.id} value={album.id}>
                    {album.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {pendingFiles.length > 0 && (
          <Badge variant="secondary">{pendingFiles.length} file(s) selected</Badge>
        )}

        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" disabled={mutation.isPending}>
              Cancel
            </Button>
          </DialogClose>
          <LoadingButton
            loading={mutation.isPending}
            disabled={pendingFiles.length === 0}
            onClick={() => mutation.mutate()}
          >
            Upload {pendingFiles.length > 0 ? `(${pendingFiles.length})` : ""}
          </LoadingButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default UploadMedia
