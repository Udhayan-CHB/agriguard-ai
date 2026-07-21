"use client";

import { useAuth } from "@/context/AuthContext";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import Sidebar from "@/components/ui/sidebar";

const PUBLIC_PATHS = ["/login", "/signup"];

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  // 1. Show a simple spinner while AuthProvider is still loading
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        Loading...
      </div>
    );
  }

  // 2. Public paths – render without sidebar
  if (PUBLIC_PATHS.includes(pathname)) {
    return <>{children}</>;
  }

  // 3. Protected paths – if not logged in, redirect to /login
  if (!user) {
    useEffect(() => {
      router.replace("/login");
    }, [router]);
    return null;
  }

  // 4. Authenticated user on a protected route – show full layout
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 p-6 overflow-auto">{children}</main>
    </div>
  );
}