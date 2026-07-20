"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  MessageSquare,
  FileText,
  User,
  Sprout,
  Sun,
  Moon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "next-themes";
import { useState } from "react";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/chat", label: "Chat", icon: MessageSquare },
  { href: "/report", label: "Report", icon: FileText },
  { href: "/profile", label: "Profile", icon: User },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const [mounted] = useState(() => typeof window !== "undefined");

  return (
    <aside className="w-16 shrink-0 bg-card border-r border-border p-2 sm:w-64 sm:p-4 flex flex-col gap-6">
      <div className="flex items-center gap-2 text-primary font-bold text-xl">
        <Sprout className="w-6 h-6" />
        <span className="hidden sm:inline">AgriGuard AI</span>
      </div>

      <nav className="flex flex-col gap-1">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center justify-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors sm:justify-start",
              pathname === href
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            )}
          >
            <Icon className="w-4 h-4" />
            <span className="hidden sm:inline">{label}</span>
          </Link>
        ))}
      </nav>

      <div className="mt-auto">
        {mounted && (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </Button>
        )}
      </div>
    </aside>
  );
}
