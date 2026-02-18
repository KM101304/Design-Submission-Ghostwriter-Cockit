import { ReactNode } from "react";

import { NavBar } from "@/components/layout/NavBar";

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#071019] via-[#0b1624] to-[#0d1b2a] text-white">
      <div className="pointer-events-none fixed inset-0 bg-cockpit-noise opacity-20" />
      <NavBar />
      <main className="relative z-10 mx-auto w-full max-w-7xl px-8 py-10">{children}</main>
    </div>
  );
}
