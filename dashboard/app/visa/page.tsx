"use client";

import React, { useEffect, useState } from "react";
import MultiStepForm, { FormFieldDef, PackageTier } from "../../components/MultiStepForm";
import { ShieldCheck, Globe, FileCheck, CheckCircle2, Clock, Users, ArrowRight } from "lucide-react";

const DEFAULT_VISA_PACKAGES: PackageTier[] = [
  {
    id: "pkg-vis-basic",
    name: "Basic Guidance",
    tier: "Basic",
    price: 2500,
    currency: "ETB",
    description: "Standard visa document guidance and application self-submission kit.",
    features: [
      "Embassy checklist verification",
      "Form completion template",
      "Email support within 48h",
    ],
    popular: false,
  },
  {
    id: "pkg-vis-std",
    name: "Standard Review",
    tier: "Standard",
    price: 5000,
    currency: "ETB",
    description: "Comprehensive document review, AI completeness audit, and flight itinerary assistance.",
    features: [
      "AI document verification & audit",
      "Hotel booking & flight reservation assistance",
      "Financial document review",
      "Dedicated visa case manager",
    ],
    popular: true,
  },
  {
    id: "pkg-vis-prem",
    name: "Premium Concierge",
    tier: "Premium",
    price: 10000,
    currency: "ETB",
    description: "End-to-end embassy liaison, appointment booking, expedited review, and mock interview prep.",
    features: [
      "Full embassy appointment liaison",
      "Priority expedited processing",
      "1-on-1 Visa Interview coaching session",
      "24/7 priority support on WhatsApp & Telegram",
    ],
    popular: false,
  },
];

const VISA_CHECKLIST = [
  {
    title: "Valid Passport Scan",
    desc: "Clear scan of passport photo page with at least 6 months validity remaining from intended travel date.",
    required: true,
  },
  {
    title: "Passport-sized Digital Photo",
    desc: "Recent colored passport photo with white background (35mm x 45mm standard).",
    required: true,
  },
  {
    title: "Proof of Financial Funds / Bank Statement",
    desc: "Recent 3 to 6 months stamped official bank statement or proof of financial sponsorship.",
    required: true,
  },
  {
    title: "Purpose of Travel Documents",
    desc: "Invitation letter, university admission letter, conference pass, or hotel booking confirmation.",
    required: false,
  },
];

const VISA_FIELDS: FormFieldDef[] = [
  { name: "full_name", label: "Applicant Full Name", type: "text", placeholder: "e.g. Abebe Bikila", required: true },
  { name: "email", label: "Email Address", type: "email", placeholder: "abebe@example.com", required: true },
  { name: "phone", label: "Phone Number", type: "tel", placeholder: "+251 91 123 4567", required: true },
  { name: "address", label: "Current City / Address", type: "text", placeholder: "Addis Ababa, Ethiopia", required: true },
  {
    name: "destination_country",
    label: "Destination Country",
    type: "select",
    options: ["Germany", "Canada", "United Kingdom", "United States", "UAE (Dubai)", "Italy", "France", "Japan", "Australia", "Turkey", "Other Schengen"],
    required: true,
  },
  {
    name: "visa_type",
    label: "Visa Category",
    type: "select",
    options: ["Tourist", "Study", "Work", "Business", "Medical"],
    required: true,
  },
  {
    name: "passport_upload_url",
    label: "Upload Passport Scan (PDF/Image)",
    type: "file",
    required: false,
    helpText: "Clear colored scan of passport information page.",
  },
  {
    name: "notes",
    label: "Additional Context / Travel Dates",
    type: "textarea",
    placeholder: "Intended travel dates, previous visa history, or special requests...",
  },
];

export default function VisaPage() {
  const [packages, setPackages] = useState<PackageTier[]>(DEFAULT_VISA_PACKAGES);

  useEffect(() => {
    const fetchPackages = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
        const res = await fetch(`${apiBase}/api/v1/support/packages?service=visa`);
        if (res.ok) {
          const data = await res.json();
          if (data.visa && Array.isArray(data.visa)) {
            setPackages(data.visa);
          }
        }
      } catch (e) {
        // Fallback to DEFAULT_VISA_PACKAGES
      }
    };
    fetchPackages();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Header Banner */}
      <div className="text-center space-y-4 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-950/70 border border-red-800/60 text-red-300 text-xs font-semibold">
          <ShieldCheck className="w-3.5 h-3.5 text-red-400" />
          <span>ZACMA VISA ASSISTANT · OFFICIAL EMBASSY & DOCUMENT LIAISON</span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
          Global Visa Application & Document Consultation
        </h1>

        <p className="text-xs sm:text-base text-slate-300 leading-relaxed">
          Embark on your journey with complete confidence. We process Tourist, Study, Work, and Business visas for
          Germany, Canada, UK, Schengen Area, UAE, and beyond with AI-assisted document accuracy.
        </p>

        {/* Feature badges */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2 text-xs text-slate-300">
          <span className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" /> 98.4% Success Rate
          </span>
          <span className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
            <Clock className="w-4 h-4 text-blue-400" /> Fast 48h Turnaround
          </span>
          <span className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
            <Users className="w-4 h-4 text-purple-400" /> 1-on-1 Case Officer
          </span>
        </div>
      </div>

      {/* Multi-Step Application Form */}
      <div className="max-w-4xl mx-auto">
        <MultiStepForm
          serviceKey="visa"
          serviceTitle="Visa Assistant"
          subBrandName="Zacma Visa Assistant"
          accentColor="red"
          packages={packages}
          requirementsChecklist={VISA_CHECKLIST}
          fieldDefinitions={VISA_FIELDS}
          apiEndpoint="/api/v1/visa/applications"
          transformPayload={(formData, selectedPkg) => ({
            full_name: formData.full_name,
            email: formData.email,
            phone: formData.phone,
            address: formData.address,
            country: "Ethiopia",
            destination_country: formData.destination_country || "Germany",
            visa_type: formData.visa_type || "Tourist",
            passport_upload_url: formData.passport_upload_url || "/uploads/passports/sample_passport.pdf",
            supporting_document_urls: ["/uploads/docs/bank_statement.pdf"],
            advance_payment_method: formData.payment_method || "CBE",
            advance_amount: selectedPkg.price,
            notes: `${selectedPkg.name} tier selected. ${formData.notes || ""}`,
          })}
        />
      </div>
    </div>
  );
}
