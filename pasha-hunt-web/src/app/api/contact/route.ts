import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { name, email, organization, inquiryType, message, honeypot } = body;

    // Spam honeypot detection
    if (honeypot && String(honeypot).trim().length > 0) {
      return NextResponse.json({ success: true, referenceId: "SPAM-TRAP" });
    }

    // Validation
    if (!name || String(name).trim().length < 2) {
      return NextResponse.json({ error: "Please enter your full name (minimum 2 characters)." }, { status: 400 });
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(String(email).trim())) {
      return NextResponse.json({ error: "Please provide a valid corporate or personal email address." }, { status: 400 });
    }

    if (!message || String(message).trim().length < 10) {
      return NextResponse.json({ error: "Message must be at least 10 characters detailing your inquiry." }, { status: 400 });
    }

    const referenceId = `PSH-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).substring(2, 6).toUpperCase()}`;
    const submission = {
      referenceId,
      timestamp: new Date().toISOString(),
      name: String(name).trim(),
      email: String(email).trim().toLowerCase(),
      organization: organization ? String(organization).trim() : "Individual / Stealth",
      inquiryType: inquiryType || "General Inquiry",
      message: String(message).trim()
    };

    // Safely persist to local submissions log
    try {
      const dataDir = path.join(process.cwd(), "data");
      if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
      }
      const logFile = path.join(dataDir, "inquiries.json");
      let existing: any[] = [];
      if (fs.existsSync(logFile)) {
        try {
          existing = JSON.parse(fs.readFileSync(logFile, "utf-8"));
        } catch {
          existing = [];
        }
      }
      existing.unshift(submission);
      fs.writeFileSync(logFile, JSON.stringify(existing, null, 2), "utf-8");
    } catch (fsErr) {
      console.warn("Could not save to disk, logging to console:", fsErr);
    }

    return NextResponse.json({
      success: true,
      referenceId,
      message: "Your message has been securely delivered to Pasha Dev engineering.",
      details: { name: submission.name, email: submission.email }
    });

  } catch (err: any) {
    return NextResponse.json({ error: "Internal server processing error. Please try again." }, { status: 500 });
  }
}
