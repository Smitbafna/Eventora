import type { ColumnDef } from "@tanstack/react-table"
import { Link } from "@tanstack/react-router"
import { ExternalLink } from "lucide-react"

import type { EventPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { EventActionsMenu } from "./EventActionsMenu"

function formatDate(value?: string | null) {
  if (!value) return null
  return new Date(value).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

export const columns: ColumnDef<EventPublic>[] = [
  {
    accessorKey: "name",
    header: "Name",
    cell: ({ row }) => (
      <Link
        to="/events/$eventId"
        params={{ eventId: row.original.id }}
        className="font-medium hover:underline"
      >
        {row.original.name}
      </Link>
    ),
  },
  {
    accessorKey: "category",
    header: "Category",
    cell: ({ row }) =>
      row.original.category ? (
        <Badge variant="secondary">{row.original.category}</Badge>
      ) : (
        <span className="text-muted-foreground italic">Uncategorized</span>
      ),
  },
  {
    accessorKey: "event_date",
    header: "Date",
    cell: ({ row }) => {
      const formatted = formatDate(row.original.event_date)
      return (
        <span className={cn(!formatted && "text-muted-foreground italic")}>
          {formatted || "No date"}
        </span>
      )
    },
  },
  {
    accessorKey: "description",
    header: "Description",
    cell: ({ row }) => (
      <span
        className={cn(
          "max-w-xs truncate block text-muted-foreground",
          !row.original.description && "italic",
        )}
      >
        {row.original.description || "No description"}
      </span>
    ),
  },
  {
    id: "view",
    header: "",
    cell: ({ row }) => (
      <Button variant="ghost" size="sm" asChild>
        <Link to="/events/$eventId" params={{ eventId: row.original.id }}>
          <ExternalLink className="size-4" />
          Open
        </Link>
      </Button>
    ),
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <EventActionsMenu event={row.original} />
      </div>
    ),
  },
]
