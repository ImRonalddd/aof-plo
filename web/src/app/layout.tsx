import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AOF PLO Range Viewer",
  description: "4-max 5BB All-In-Or-Fold PLO preflop GTO ranges",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-mono bg-gray-900 text-white min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
