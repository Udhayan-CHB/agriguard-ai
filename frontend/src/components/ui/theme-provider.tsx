"use client";

import type { ReactNode } from "react";

/** The application has a deterministic dark default; no runtime theme script is needed. */
export function ThemeProvider({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
