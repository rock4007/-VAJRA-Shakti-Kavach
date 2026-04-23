import "./globals.css";

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "PFID Dashboard",
  description: "Personal Freelance Intelligence Dashboard"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
