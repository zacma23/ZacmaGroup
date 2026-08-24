"use client";

import React, { useEffect, useState } from "react";
import MultiStepForm, { FormFieldDef, PackageTier } from "../../components/MultiStepForm";
import { Megaphone, Target, TrendingUp, Sparkles, CheckCircle2, Share2, BarChart3 } from "lucide-react";

const DEFAULT_MARKETING_PACKAGES: PackageTier[] = [
  {
    id: "pkg-mkt-starter",
    name: "Social Media Starter",
    tier: "Starter",
    price: 6000,
    currency: "ETB",
    description: "Essential social media setup, brand positioning, and monthly content calendar.",
    features: [
      "12 custom branded social media posts/month",
      "Facebook, Instagram & Telegram management",
      "Audience targeting & community engagement",
    ],
    popular: false,
  },
  {
    id: "pkg-mkt-full",
    name: "Full Digital Marketing",
    tier: "Growth",
    price: 15000,
    currency: "ETB",
    description: "Multi-channel advertising, lead generation funnels, and performance reporting.",
    features: [
      "Paid ad campaign management (Meta & Google Ads)",
      "High-converting landing page copywriting",
      "Weekly analytics & ROI reporting",
      "Dedicated marketing strategist",
    ],
    popular: true,
  },
  {
    id: "pkg-mkt-combo",
    name: "Branding & Growth Combo",
    tier: "Enterprise",
    price: 25000,
    currency: "ETB",
    description: "Complete corporate visual identity, logo package, digital PR, and full-funnel marketing.",
    features: [
      "Full Brand Identity (Logo, Typography, Brand Book)",
      "Complete multi-channel marketing campaigns",
      "Video production and commercial reels",
      "Continuous conversion optimization",
    ],
    popular: false,
  },
];

const MARKETING_CHECKLIST = [
  {
    title: "Brand Name & Business Overview",
    desc: "Business legal or trade name, industry sector, and core products or services offered.",
    required: true,
  },
  {
    title: "Target Customer Audience",
    desc: "Primary customer demographic (age, location, business vs individual consumer).",
    required: true,
  },
  {
    title: "Existing Social Links / Assets",
    desc: "Current website URL, Facebook/Instagram links, or brand logo files if already created.",
    required: false,
  },
  {
    title: "Monthly Growth Goals & Budget",
    desc: "Lead targets, brand awareness benchmarks, or planned monthly ad spend.",
    required: true,
  },
];

const MARKETING_FIELDS: FormFieldDef[] = [
  { name: "full_name", label: "Contact Person / Client Name", type: "text", placeholder: "e.g. Yonas Mulugeta", required: true },
  { name: "company_name", label: "Business / Brand Name", type: "text", placeholder: "e.g. Acme Trading Plc", required: true },
  { name: "email", label: "Business Email", type: "email", placeholder: "info@acme.com", required: true },
  { name: "phone", label: "Phone Number", type: "tel", placeholder: "+251 91 123 4567", required: true },
  {
    name: "service_scope",
    label: "Primary Marketing Scope",
    type: "select",
    options: [
      "Social Media Management & Content Creation",
      "Meta (Facebook/Instagram) Paid Ads & Lead Generation",
      "Brand Identity, Logo & Corporate Design",
      "Video Commercials & Product Photography",
      "Complete Full-Funnel Digital Growth Strategy",
    ],
    required: true,
  },
  {
    name: "target_market",
    label: "Target Geographic Market",
    type: "select",
    options: ["Ethiopia (Addis Ababa & Regional)", "East Africa Region", "Middle East & GCC", "Global / International"],
    required: true,
  },
  {
    name: "monthly_budget",
    label: "Estimated Monthly Ad Spend (Optional)",
    type: "text",
    placeholder: "e.g. 10,000 - 30,000 ETB",
    required: false,
  },
  {
    name: "brand_notes",
    label: "Key Goals & Current Challenges",
    type: "textarea",
    placeholder: "Tell us about your brand vision, target leads, or specific campaigns you want to launch...",
  },
];

export default function MarketingPage() {
  const [packages, setPackages] = useState<PackageTier[]>(DEFAULT_MARKETING_PACKAGES);

  useEffect(() => {
    const fetchPackages = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
        const res = await fetch(`${apiBase}/api/v1/support/packages?service=marketing`);
        if (res.ok) {
          const data = await res.json();
          if (data.marketing && Array.isArray(data.marketing)) {
            setPackages(data.marketing);
          }
        }
      } catch (e) {
        // Fallback to DEFAULT_MARKETING_PACKAGES
      }
    };
    fetchPackages();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Header Banner */}
      <div className="text-center space-y-4 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-950/70 border border-purple-800/60 text-purple-300 text-xs font-semibold">
          <Megaphone className="w-3.5 h-3.5 text-purple-400" />
          <span>ZACMA MARKETING SERVICE · DIGITAL GROWTH, BRANDING & LEAD GENERATION</span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
          Strategic Digital Marketing & Brand Scaling
        </h1>

        <p className="text-xs sm:text-base text-slate-300 leading-relaxed">
          Scale your enterprise with data-driven social media management, high-converting Meta and Google ad campaigns,
          and unforgettable visual brand identities.
        </p>

        {/* Feature badges */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2 text-xs text-slate-300">
          <span className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
            <TrendingUp className="w-4 h-4 text-emerald-400" /> High ROI Performance
          </span>
          <span className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
            <Share2 className="w-4 h-4 text-blue-400" /> Multi-Channel Social Reach
          </span>
          <span className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
            <BarChart3 className="w-4 h-4 text-purple-400" /> Transparent Weekly Analytics
          </span>
        </div>
      </div>

      {/* Multi-Step Application Form */}
      <div className="max-w-4xl mx-auto">
        <MultiStepForm
          serviceKey="marketing"
          serviceTitle="Marketing Service"
          subBrandName="Zacma Marketing Service"
          accentColor="purple"
          packages={packages}
          requirementsChecklist={MARKETING_CHECKLIST}
          fieldDefinitions={MARKETING_FIELDS}
          apiEndpoint="/api/v1/marketing/campaigns"
          transformPayload={(formData, selectedPkg) => ({
            name: `${formData.company_name || formData.full_name} - ${selectedPkg.name}`,
            channel: "Social & Search Ads",
            budget: selectedPkg.price,
            description: `Brand: ${formData.company_name}. Scope: ${formData.service_scope}. Client: ${formData.full_name} (${formData.phone}). ${formData.brand_notes || ""}`,
          })}
        />
      </div>
    </div>
  );
}
