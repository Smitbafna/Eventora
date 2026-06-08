import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Calendar, Search } from "lucide-react"
import { Suspense, useMemo, useState } from "react"

import { EventsService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddEvent from "@/components/Events/AddEvent"
import { columns } from "@/components/Events/columns"
import PendingEvents from "@/components/Pending/PendingEvents"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

function getEventsQueryOptions() {
  return {
    queryFn: () => EventsService.eventsReadEvents({ skip: 0, limit: 100 }),
    queryKey: ["events"],
  }
}

export const Route = createFileRoute("/_layout/events")({
  component: Events,
  head: () => ({
    meta: [{ title: "Events - Event Media Platform" }],
  }),
})

type SortOption = "name" | "date" | "category"

function EventsTableContent() {
  const { data: events } = useSuspenseQuery(getEventsQueryOptions())
  const [search, setSearch] = useState("")
  const [sortBy, setSortBy] = useState<SortOption>("date")

  const filtered = useMemo(() => {
    let list = [...events.data]
    if (search) {
      const q = search.toLowerCase()
      list = list.filter(
        (e) =>
          e.name.toLowerCase().includes(q) ||
          e.category?.toLowerCase().includes(q) ||
          e.description?.toLowerCase().includes(q),
      )
    }
    list.sort((a, b) => {
      if (sortBy === "name") return a.name.localeCompare(b.name)
      if (sortBy === "category")
        return (a.category ?? "").localeCompare(b.category ?? "")
      const da = a.event_date ? new Date(a.event_date).getTime() : 0
      const db = b.event_date ? new Date(b.event_date).getTime() : 0
      return db - da
    })
    return list
  }, [events.data, search, sortBy])

  if (events.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Calendar className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No events yet</h3>
        <p className="text-muted-foreground">
          Create your first event to start organizing media
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder="Search events..."
            className="pl-9"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Select value={sortBy} onValueChange={(v) => setSortBy(v as SortOption)}>
          <SelectTrigger className="w-full sm:w-40">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="name">Name</SelectItem>
            <SelectItem value="date">Date</SelectItem>
            <SelectItem value="category">Category</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <DataTable columns={columns} data={filtered} />
    </div>
  )
}

function EventsTable() {
  return (
    <Suspense fallback={<PendingEvents />}>
      <EventsTableContent />
    </Suspense>
  )
}

function Events() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Events</h1>
          <p className="text-muted-foreground">
            Create and manage club events, albums, and media
          </p>
        </div>
        <AddEvent />
      </div>
      <EventsTable />
    </div>
  )
}
