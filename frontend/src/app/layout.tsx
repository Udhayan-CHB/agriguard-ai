import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/ui/theme-provider";
import Sidebar from "@/components/ui/sidebar";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AgriGuard AI",
  description: "Multi-Agent System for Sustainable Farming",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
            <div className="flex min-h-screen bg-background">
              <Sidebar />
              <main className="flex-1 p-6 overflow-auto">{children}</main>
            </div>
          </ThemeProvider>
        </Providers>
      </body>
    </html>
  );
}