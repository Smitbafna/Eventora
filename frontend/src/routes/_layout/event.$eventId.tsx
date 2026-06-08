import { useQuery, useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { ArrowLeft } from "lucide-react"
import { Suspense } from "react"

import { AlbumsService, EventsService, MediaService } from "@/client"
import AddAlbum from "@/components/Albums/AddAlbum"
import MediaCard from "@/components/Media/MediaCard"
import UploadMedia from "@/components/Media/UploadMedia"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useAuth from "@/hooks/useAuth"
import { canUploadMedia } from "@/lib/roles"

export const Route = createFileRoute("/_layout/event/$eventId")({
  component: EventDetail,
  head: () => ({
    meta: [{ title: "Event Details - Event Media Platform" }],
  }),
})

function EventDetailContent() {
  const { eventId } = Route.useParams()
  const { user } = useAuth()

  const { data: event } = useSuspenseQuery({
    queryKey: ["event", eventId],
    queryFn: () => EventsService.eventsReadEvent({ eventId }),
  })

  const { data: albums } = useSuspenseQuery({
    queryKey: ["albums", eventId],
    queryFn: () => AlbumsService.albumsReadAlbumsByEvent({ eventId }),
  })

  const { data: media } = useSuspenseQuery({
    queryKey: ["media", eventId],
    queryFn: () => MediaService.mediaReadMediaByEvent({ eventId, limit: 100 }),
  })

  const showUpload = canUploadMedia(user?.role)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/events">
            <ArrowLeft />
          </Link>
        </Button>
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <h1 className="text-2xl font-bold tracking-tight">{event.name}</h1>
            {event.category && (
              <Badge variant="secondary">{event.category}</Badge>
            )}
          </div>
          {event.description && (
            <p className="text-muted-foreground">{event.description}</p>
          )}
          {event.event_date && (
            <p className="text-sm text-muted-foreground mt-1">
              {new Date(event.event_date).toLocaleString()}
            </p>
          )}
        </div>
        {showUpload && (
          <div className="flex gap-2">
            <AddAlbum eventId={eventId} />
            <UploadMedia eventId={eventId} albums={albums.data} />
          </div>
        )}
      </div>

      <Tabs defaultValue="media">
        <TabsList>
          <TabsTrigger value="media">
            Media ({media.count})
          </TabsTrigger>
          <TabsTrigger value="albums">
            Albums ({albums.count})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="media" className="mt-4">
        {media.data.length === 0 ? (
  <div className="text-center py-12 text-muted-foreground">
    <p className="mb-4">No media uploaded yet.</p>
    <UploadMedia eventId={eventId} albums={albums.data} />
  </div>
) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {media.data.map((item) => (
                <MediaCard key={item.id} media={item} />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="albums" className="mt-4">
  {albums.data.length === 0 ? (
    <div className="text-center py-12 text-muted-foreground">
      <p className="mb-4">No albums yet. Create an album to organize media.</p>
      <AddAlbum eventId={eventId} />
    </div>
  ) : (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {albums.data.map((album) => (
        <div key={album.id} className="rounded-lg border p-4">
          <h3 className="font-semibold">{album.name}</h3>
          <p className="text-sm text-muted-foreground mt-1">
            {album.description || "No description"}
          </p>
          <AlbumMediaCount albumId={album.id} />
        </div>
      ))}
    </div>
  )}
</TabsContent>
      </Tabs>
    </div>
  )
}

function AlbumMediaCount({ albumId }: { albumId: string }) {
  const { data } = useQuery({
    queryKey: ["media-album", albumId],
    queryFn: () => MediaService.mediaReadMediaByAlbum({ albumId }),
  })
  return (
    <p className="text-xs text-muted-foreground mt-2">
      {data?.count ?? 0} media item{(data?.count ?? 0) !== 1 ? "s" : ""}
    </p>
  )
}

function EventDetailSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-4 w-96" />
      <div className="grid grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="aspect-video rounded-lg" />
        ))}
      </div>
    </div>
  )
}

function EventDetail() {
  return (
    <Suspense fallback={<EventDetailSkeleton />}>
      <EventDetailContent />
    </Suspense>
  )
}
