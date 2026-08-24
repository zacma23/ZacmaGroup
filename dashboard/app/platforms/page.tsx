"use client";

import React from "react";
import Link from "next/link";
import {
  Building2,
  GraduationCap,
  ShoppingBag,
  Users,
  ExternalLink,
  ShieldCheck,
  Zap,
  ArrowRight,
  CheckCircle2,
  Sparkles,
} from "lucide-react";

const PLATFORMS = [
  {
    id: "erp",
    name: "Zacma ERP",
    tagline: "Enterprise Resource Planning & Cloud Operations",
    url: "https://erp.zacmaa.net/",
    badge: "Enterprise Suite",
    badgeColor: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    icon: Building2,
    gradient: "from-blue-600/20 via-indigo-600/10 to-transparent",
    borderColor: "border-blue-500/30 hover:border-blue-500/60",
    buttonClass: "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-500/20",
    description:
      "A complete cloud ERP solution for managing multi-branch operations, multi-warehouse inventory, procurement workflows, double-entry accounting, and human capital payroll.",
    highlights: [
      "Multi-Branch & Warehouse Inventory with real-time barcode tracking",
      "Financial Accounting, General Ledger & Tax Audit reports",
      "Human Capital Management (HRM), Attendance & Payroll automation",
      "Point of Sale (POS) with receipt printing & offline mode",
      "Live Executive Dashboard with profit/loss analytics",
    ],
  },
  {
    id: "myschool",
    name: "MySchool",
    tagline: "Next-Generation School & Campus Management System",
    url: "https://myschool.zacmaa.net/",
    badge: "EdTech Cloud",
    badgeColor: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    icon: GraduationCap,
    gradient: "from-emerald-600/20 via-teal-600/10 to-transparent",
    borderColor: "border-emerald-500/30 hover:border-emerald-500/60",
    buttonClass: "bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-500/20",
    description:
      "Dedicated school management platform designed for K-12 schools, colleges, and academies to automate admissions, academics, tuition fees, and parent engagement.",
    highlights: [
      "Online Student Admissions, Enrollment & Digital Student IDs",
      "Automated Gradebooks, Weighted GPA & Terminal Report Cards",
      "Daily Attendance Tracking with instant SMS notification to parents",
      "Tuition Fee Billing with TeleBirr & CBE Mobile Banking integration",
      "Dedicated Teacher, Student & Parent Web Portals",
    ],
  },
  {
    id: "ecommerce",
    name: "Zacma E-Commerce",
    tagline: "High-Conversion Multi-Vendor & Digital Storefronts",
    url: "https://ecommerce.zacmaa.net/",
    badge: "Digital Commerce",
    badgeColor: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    icon: ShoppingBag,
    gradient: "from-amber-600/20 via-orange-600/10 to-transparent",
    borderColor: "border-amber-500/30 hover:border-amber-500/60",
    buttonClass: "bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-amber-500/20 font-bold",
    description:
      "Modern digital commerce engine supporting single-brand stores and multi-vendor marketplaces with direct local payment gateway checkout and courier logistics.",
    highlights: [
      "Ethiopian Payment Gateways: TeleBirr, CBE Birr & Chapa checkout",
      "Multi-Vendor Merchant Management with automated commission splits",
      "Dynamic Product Catalogs, Stock Alerts & Variant Management",
      "Courier Integration with real-time SMS delivery tracking",
      "Discount Engine, Flash Sales & Promo Coupons",
    ],
  },
  {
    id: "freelancer",
    name: "Zacma Freelancer",
    tagline: "Vetted Tech Talent & Project Marketplace",
    url: "https://freelancer.zacmaa.net/",
    badge: "Talent Marketplace",
    badgeColor: "bg-purple-500/10 text-purple-400 border-purple-500/20",
    icon: Users,
    gradient: "from-purple-600/20 via-pink-600/10 to-transparent",
    borderColor: "border-purple-500/30 hover:border-purple-500/60",
    buttonClass: "bg-purple-600 hover:bg-purple-500 text-white shadow-purple-500/20",
    description:
      "Premier marketplace connecting vetted Ethiopian software engineers, mobile developers, UI/UX designers, and digital specialists with enterprise clients.",
    highlights: [
      "Rigorous Technical Screening & Verified Developer Profiles",
      "Milestone-based Escrow Payments & Transparent Contract Tracking",
      "On-Demand Dedicated Engineering Pods & Individual Contractors",
      "Real-Time Chat, Code Repositories & Work Log Verification",
      "Enterprise Service Level Agreements (SLAs) & IP protection",
    ],
  },
];

export default function PlatformsPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Header */}
        <div className="text-center space-y-4 max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs font-semibold text-amber-400 shadow-inner">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Zacma Technology Group Ecosystem</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-white">
            Our Enterprise <span className="bg-gradient-to-r from-red-500 via-amber-400 to-blue-400 bg-clip-text text-transparent">Platforms</span>
          </h1>
          <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
            Discover Zacma Group&apos;s suite of cloud platforms engineered to digitize schools, streamline enterprise operations, scale e-commerce, and connect top technology talent.
          </p>
        </div>

        {/* Platforms Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {PLATFORMS.map((platform) => {
            const Icon = platform.icon;
            return (
              <div
                key={platform.id}
                className={`relative flex flex-col justify-between rounded-3xl bg-slate-900/90 border p-7 sm:p-8 transition-all duration-300 shadow-xl hover:shadow-2xl ${platform.borderColor} bg-gradient-to-b ${platform.gradient}`}
              >
                <div className="space-y-5">
                  {/* Top Bar */}
                  <div className="flex items-start justify-between gap-4">
                    <div className="p-3.5 rounded-2xl bg-slate-800/90 border border-slate-700/80 shadow-md text-white">
                      <Icon className="w-7 h-7" />
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${platform.badgeColor}`}>
                      {platform.badge}
                    </span>
                  </div>

                  {/* Title & Tagline */}
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">{platform.name}</h2>
                    <p className="text-xs font-medium text-slate-400 mt-1">{platform.tagline}</p>
                  </div>

                  {/* Description */}
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                    {platform.description}
                  </p>

                  {/* Feature Highlights */}
                  <div className="space-y-2 pt-2 border-t border-slate-800/80">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                      Core Platform Capabilities:
                    </span>
                    <ul className="space-y-1.5">
                      {platform.highlights.map((h, i) => (
                        <li key={i} className="flex items-start gap-2 text-xs text-slate-300">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                          <span>{h}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Bottom Action */}
                <div className="pt-6 mt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div className="text-xs text-slate-400 font-mono truncate w-full sm:w-auto">
                    {platform.url}
                  </div>
                  <a
                    href={platform.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`w-full sm:w-auto px-5 py-2.5 rounded-xl text-xs font-bold transition-all shadow-md flex items-center justify-center gap-2 ${platform.buttonClass}`}
                  >
                    <span>Visit Platform</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>

        {/* Custom Solution Call to Action */}
        <div className="rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950/50 to-slate-900 border border-slate-800 p-8 text-center space-y-4">
          <h3 className="text-xl sm:text-2xl font-bold text-white">Need a Custom Software Solution?</h3>
          <p className="text-xs sm:text-sm text-slate-400 max-w-2xl mx-auto">
            Our software engineering division can build custom extensions, tailored modules, or standalone mobile and web applications for your enterprise.
          </p>
          <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/software"
              className="px-6 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition shadow-lg shadow-amber-500/10 flex items-center gap-2"
            >
              <span>Request Software Development</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/portal"
              className="px-6 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs transition border border-slate-700"
            >
              Open Client Portal
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
