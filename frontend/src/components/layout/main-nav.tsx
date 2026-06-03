"use client"

import Link from "next/link"
import { cn } from "@/lib/utils"
import { usePathname } from "next/navigation"

export function MainNav({
  className,
  ...props
}: React.HTMLAttributes<HTMLElement>) {
  const pathname = usePathname();

  const links = [
    { href: "/dashboard", label: "Overview" },
    { href: "/meal-generator", label: "Meal Generator" },
    { href: "/ingredient-scanner", label: "Ingredient Scanner" },
    { href: "/analyzer", label: "Food Analyzer" },
    { href: "/analytics", label: "Analytics" },
  ];

  return (
    <nav
      className={cn("flex items-center space-x-4 lg:space-x-6 hidden md:flex", className)}
      {...props}
    >
      {links.map((link) => (
        <Link
          key={link.href}
          href={link.href}
          className={cn(
            "text-sm font-medium transition-colors hover:text-primary",
            pathname === link.href ? "text-primary" : "text-muted-foreground"
          )}
        >
          {link.label}
        </Link>
      ))}
    </nav>
  )
}
