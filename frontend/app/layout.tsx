import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Submission Ghostwriter",
  description: "AI-native underwriting submission cockpit",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
