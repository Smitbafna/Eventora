import { useMutation, useSuspenseQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Bell } from "lucide-react"
import { Suspense } from "react"

import { NotificationsService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

function getNotificationsQueryOptions() {
  return {
    queryFn: () => NotificationsService.notificationsReadNotifications({ limit: 100 }),
    queryKey: ["notifications"],
  }
}

export const Route = createFileRoute("/_layout/notifications")({
  component: Notifications,
  head: () => ({
    meta: [{ title: "Notifications - Event Media Platform" }],
  }),
})

function NotificationsContent() {
  const { data: notifications } = useSuspenseQuery(
    getNotificationsQueryOptions(),
  )
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()

  const markReadMutation = useMutation({
    mutationFn: (notificationId: string) =>
      NotificationsService.notificationsMarkNotificationRead({ notificationId }),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  if (notifications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Bell className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No notifications</h3>
        <p className="text-muted-foreground">
          Likes, comments, and tags will appear here
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {notifications.map((n) => (
        <div
          key={n.id}
          className={`flex items-start justify-between gap-4 rounded-lg border p-4 ${
            n.is_read ? "opacity-70" : "bg-muted/30"
          }`}
        >
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Badge variant="outline">{n.type}</Badge>
              {!n.is_read && <Badge>New</Badge>}
            </div>
            <p className="text-sm">{n.message}</p>
            {n.created_at && (
              <p className="text-xs text-muted-foreground">
                {new Date(n.created_at).toLocaleString()}
              </p>
            )}
          </div>
          {!n.is_read && (
            <Button
              variant="outline"
              size="sm"
              disabled={markReadMutation.isPending}
              onClick={() => markReadMutation.mutate(n.id)}
            >
              Mark read
            </Button>
          )}
        </div>
      ))}
    </div>
  )
}

function NotificationsSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 4 }).map((_, i) => (
        <Skeleton key={i} className="h-20 w-full rounded-lg" />
      ))}
    </div>
  )
}

function Notifications() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Notifications</h1>
        <p className="text-muted-foreground">
          Stay updated on likes, comments, and tags
        </p>
      </div>
      <Suspense fallback={<NotificationsSkeleton />}>
        <NotificationsContent />
      </Suspense>
    </div>
  )
}
