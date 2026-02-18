import type { Metadata } from "next";

import { AppLayout } from "@/components/layout/AppLayout";

import "./globals.css";

export const metadata: Metadata = {
  title: "Submission Ghostwriter",
  description: "AI-native underwriting submission cockpit",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppLayout>{children}</AppLayout>
      </body>
    </html>
  );
}
