import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { Calendar, Image, Users } from "lucide-react"

import { EventsService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import useAuth from "@/hooks/useAuth"
import { canUploadMedia } from "@/lib/roles"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [{ title: "Dashboard - Event Media Platform" }],
  }),
})

function Dashboard() {
  const { user: currentUser } = useAuth()

  const { data: events } = useQuery({
    queryKey: ["events"],
    queryFn: () => EventsService.eventsReadEvents({ limit: 5 }),
  })

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-2xl truncate max-w-sm font-bold tracking-tight">
          Hi, {currentUser?.full_name || currentUser?.email}
        </h1>
        <p className="text-muted-foreground">
          Welcome to the Event & Media Management Platform
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Calendar className="size-4" />
              Events
            </CardTitle>
            <CardDescription>Total events in the platform</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{events?.count ?? "—"}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Users className="size-4" />
              Your Role
            </CardTitle>
            <CardDescription>Access level for media operations</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold capitalize">
              {currentUser?.role?.replace("_", " ") ?? "viewer"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Image className="size-4" />
              Upload Access
            </CardTitle>
            <CardDescription>Can you upload photos and videos?</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              {canUploadMedia(currentUser?.role) ? "Yes" : "No"}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-wrap gap-3">
        <Button asChild>
          <Link to="/events">Browse Events</Link>
        </Button>
        <Button variant="outline" asChild>
          <Link to="/notifications">View Notifications</Link>
        </Button>
      </div>

      {events && events.data.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-3">Recent Events</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {events.data.slice(0, 4).map((event) => (
              <Link
                key={event.id}
                to="/events/$eventId"
                params={{ eventId: event.id }}
                className="rounded-lg border p-4 hover:bg-muted/50 transition-colors"
              >
                <p className="font-medium">{event.name}</p>
                {event.category && (
                  <p className="text-sm text-muted-foreground">{event.category}</p>
                )}
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
