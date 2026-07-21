"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  MessageSquare,
  FileText,
  Sprout,
  LogOut,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const isAdmin = user?.role === "admin";

  const navItems = [
    ...(isAdmin ? [{ href: "/", label: "Dashboard", icon: LayoutDashboard }] : []),
    { href: "/chat", label: "Chat", icon: MessageSquare },
    ...(isAdmin ? [{ href: "/report", label: "Report", icon: FileText }] : []),
  ];

  return (
    <aside className="w-16 shrink-0 bg-card border-r border-border p-2 sm:w-64 sm:p-4 flex flex-col gap-6">
      <div className="flex items-center gap-2 text-primary font-bold text-xl">
        <Sprout className="w-6 h-6" />
        <span className="hidden sm:inline">AgriGuard AI</span>
      </div>

      <nav className="flex flex-col gap-1 flex-1">
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

      <div className="mt-auto flex flex-col gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={logout}
          aria-label="Logout"
          className="self-center sm:self-stretch"
        >
          <LogOut className="w-4 h-4 sm:mr-2" />
          <span className="hidden sm:inline text-xs">Logout</span>
        </Button>
      </div>
    </aside>
  );
}