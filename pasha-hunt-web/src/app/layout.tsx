import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PASHA HUNT 2.0 — AI Career Intelligence & Job Automation Platform",
  description: "Next-generation career automation workstation. Sweep 18 job boards, test ATS resumes against the Google XYZ formula, verify recruiter emails, and apply with AI precision.",
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
    <html lang="en" className="dark scroll-smooth">
      <head>
        <meta name="theme-color" content="#080E19" />
      </head>
      <body className="min-h-screen flex flex-col bg-[#080E19] text-[#F3F7FC] selection:bg-[#168BFF]/30 selection:text-[#00D6C9]">
        {children}
      </body>
    </html>
  );
}
