"use client"

// import { UserButton } from "@clerk/nextjs"
import { Button } from "@/components/ui/button"

export function UserNav() {
  return (
    <div className="flex items-center gap-4">
      {/* <UserButton afterSignOutUrl="/" /> */}
      <Button variant="ghost" className="relative h-8 w-8 rounded-full bg-muted">
        U
      </Button>
    </div>
  )
}
