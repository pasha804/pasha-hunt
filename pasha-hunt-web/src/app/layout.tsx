import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PASHA HUNT 2.0 — AI Career Intelligence Platform | Midnight × Amber Edition",
  description: "Your Career. Your Intelligence. Your Next Opportunity. Autonomous career intelligence workstation: sweep 18 job feeds, test ATS resumes with the Google XYZ formula, verify recruiter mailboxes, and organize applications with zero spam.",
  openGraph: {
    title: "PASHA HUNT 2.0 — Midnight × Amber Edition",
    description: "Your Career. Your Intelligence. Your Next Opportunity. A commercial AI career command center by Pasha Dev.",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "PASHA HUNT 2.0 — AI Career Intelligence",
    description: "Your Career. Your Intelligence. Your Next Opportunity.",
  },
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark scroll-smooth" suppressHydrationWarning>
      <head>
        <meta name="theme-color" content="#101820" />
      </head>
      <body
        suppressHydrationWarning
        className="min-h-screen flex flex-col bg-[#101820] text-[#F7F3EA] selection:bg-[#F2AA4C]/25 selection:text-white"
      >
        {children}
      </body>
    </html>
  );
}
