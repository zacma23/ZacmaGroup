"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ShieldCheck,
  Plane,
  GraduationCap,
  Megaphone,
  Search,
  ArrowRight,
  CheckCircle2,
  CreditCard,
  Building,
  Sparkles,
  Users,
  Award,
  Globe2,
  Clock,
  ChevronRight,
  Bot,
  Send,
  Code,
  Layers,
  ExternalLink,
} from "lucide-react";

export default function HomePage() {
  const router = useRouter();
  const [trackRef, setTrackRef] = useState("");
  const [activeTab, setActiveTab] = useState<"software" | "visa" | "travel" | "training" | "marketing">("software");

  const handleTrackSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (trackRef.trim()) {
      router.push(`/track?ref=${encodeURIComponent(trackRef.trim())}`);
    }
  };

  const services = [
    {
      key: "software",
      title: "Software Development",
      tagline: "Custom Web, Mobile (Android/iOS), ERP & AI Agents",
      desc: "Full-cycle software engineering. Enterprise web applications, native mobile apps, custom ERP/CRM systems, MySchool, E-Commerce, and AI agents.",
      icon: Code,
      color: "from-blue-600 to-amber-600",
      badge: "Software & SaaS",
      href: "/software",
      stats: "50+ Enterprise Deployments",
      packages: [
        { name: "MVP Prototype", price: "25,000 ETB", desc: "Core workflow, UI prototype & database" },
        { name: "Production System", price: "50,000 ETB", desc: "Full-stack web & mobile app + API", popular: true },
        { name: "Enterprise Architecture", price: "100,000+ ETB", desc: "Multi-tenant cloud ERP/SaaS + AI agents" },
      ],
    },
    {
      key: "visa",
      title: "Zacma Visa Assistant",
      tagline: "Tourist, Work, Study & Business Visa Processing",
      desc: "Fast-track your global journey. Full embassy liaison, AI document audits, and personalized appointment assistance with higher visa approval rates.",
      icon: ShieldCheck,
      color: "from-red-600 to-rose-700",
      badge: "Visa & Immigration",
      href: "/visa",
      stats: "98.4% Visa Success Rate",
      packages: [
        { name: "Basic Guidance", price: "2,500 ETB", desc: "Checklist verification & form template" },
        { name: "Standard Review", price: "5,000 ETB", desc: "AI document audit & itinerary support", popular: true },
        { name: "Premium Concierge", price: "10,000 ETB", desc: "Full embassy liaison & 1-on-1 interview coach" },
      ],
    },
    {
      key: "travel",
      title: "Zacma Travel Agent",
      tagline: "Flights, 5-Day Holiday Packages & Hotel Reservations",
      desc: "Personal & corporate travel coordination. Exclusive flight deals with major international airlines, curated 5-day holiday itineraries, and verified hotel stays.",
      icon: Plane,
      color: "from-blue-600 to-indigo-700",
      badge: "Travel & Tours",
      href: "/travel",
      stats: "12,000+ Flights Booked",
      packages: [
        { name: "Standard Booking", price: "3,500 ETB", desc: "Direct flight & hotel reservation" },
        { name: "Full 5-Day Itinerary", price: "8,000 ETB", desc: "Daily itinerary, transfers & tour passes", popular: true },
        { name: "VIP Concierge", price: "15,000 ETB", desc: "5-Star suites, chauffeur & VIP lounge" },
      ],
    },
    {
      key: "training",
      title: "Zacma Training Institute",
      tagline: "Career Programs in IT, AI, Design, Media & Hardware",
      desc: "Industry-accredited practical courses in Programming (Python/Web), Artificial Intelligence, Graphics, Video Editing, Accounting, and Hardware Maintenance.",
      icon: GraduationCap,
      color: "from-emerald-600 to-teal-700",
      badge: "Career Institute",
      href: "/training",
      stats: "4,500+ Certified Graduates",
      packages: [
        { name: "Single Course", price: "4,500 ETB", desc: "40+ hours hands-on lab & certificate" },
        { name: "Professional Bundle", price: "8,000 ETB", desc: "Dual courses (e.g. AI + Programming)", popular: true },
        { name: "Full Career Track", price: "14,000 ETB", desc: "Mastery track, mentorship & job referral" },
      ],
    },
    {
      key: "marketing",
      title: "Zacma Marketing Service",
      tagline: "Social Media, Brand Identity & Performance Advertising",
      desc: "High-impact digital marketing campaigns. Social media growth, brand identity design, targeted Facebook/Google ad funnels, and enterprise lead generation.",
      icon: Megaphone,
      color: "from-purple-600 to-pink-700",
      badge: "Digital Growth",
      href: "/marketing",
      stats: "350+ Brands Scaled",
      packages: [
        { name: "Social Media Starter", price: "6,000 ETB", desc: "12 custom branded posts & management" },
        { name: "Full Digital Marketing", price: "15,000 ETB", desc: "Multi-channel paid ads & lead funnels", popular: true },
        { name: "Branding & Growth", price: "25,000 ETB", desc: "Complete visual identity & digital PR" },
      ],
    },
  ];

  const activeService = services.find((s) => s.key === activeTab) || services[0];

  return (
    <div className="space-y-16 sm:space-y-24 pb-16">
      {/* HERO SECTION */}
      <section className="relative pt-12 sm:pt-20 pb-12 overflow-hidden bg-gradient-to-b from-slate-900 via-slate-950 to-slate-950">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(200,16,46,0.15),rgba(255,255,255,0))] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center space-y-6 max-w-4xl mx-auto">
            {/* Top Tag */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-red-950/70 border border-red-800/60 text-red-300 text-xs font-semibold shadow-inner">
              <Sparkles className="w-3.5 h-3.5 text-red-400" />
              <span>ZACMA TECHNOLOGY GROUP · ONE UNIFIED CLIENT PORTAL</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight leading-tight">
              Global Visa, Travel, Training & <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-rose-400 to-blue-400">Business Solutions</span>
            </h1>

            <p className="text-sm sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
              Experience seamless, AI-assisted services across international visa applications, curated travel
              itineraries, accredited technical courses, and digital marketing growth.
            </p>

            {/* Quick Track Your Request Search Box */}
            <div className="pt-2 max-w-xl mx-auto">
              <form
                onSubmit={handleTrackSubmit}
                className="p-2 bg-slate-900/90 backdrop-blur-md rounded-2xl border border-slate-700/80 shadow-2xl flex flex-col sm:flex-row items-center gap-2"
              >
                <div className="flex-1 flex items-center gap-2.5 px-3 w-full">
                  <Search className="w-4 h-4 text-red-400 flex-shrink-0" />
                  <input
                    type="text"
                    value={trackRef}
                    onChange={(e) => setTrackRef(e.target.value)}
                    placeholder="Enter Reference Number (e.g. ZAC-VIS-4419, visa-001)..."
                    className="w-full bg-transparent text-white placeholder-slate-500 text-xs sm:text-sm focus:outline-none py-2"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full sm:w-auto px-6 py-2.5 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded-xl shadow-lg transition-all flex items-center justify-center gap-1.5 flex-shrink-0"
                >
                  <span>Track Request</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </form>
              <p className="text-[11px] text-slate-400 text-center mt-2">
                Already submitted an application? Look up your status, download invoices, and chat with AI/human agents.
              </p>
            </div>

            {/* Official Payment Account Highlights */}
            <div className="pt-4 max-w-2xl mx-auto">
              <div className="p-3.5 bg-slate-900/80 rounded-2xl border border-blue-900/50 flex flex-wrap items-center justify-center gap-x-4 gap-y-2 text-xs text-slate-300">
                <span className="font-semibold text-white flex items-center gap-1.5">
                  <CreditCard className="w-4 h-4 text-blue-400" />
                  Payment Platform:
                </span>
                <span className="font-semibold text-emerald-400 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
                  Instant SantimPay Checkout & Multi-Bank Transfers
                </span>
                <span className="text-slate-400">CBE · TeleBirr · Awash</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FOUR CORE SERVICE LINES CARDS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-2 mb-10">
          <span className="text-xs font-bold uppercase tracking-wider text-red-400">Our Premier Divisions</span>
          <h2 className="text-2xl sm:text-4xl font-black text-white tracking-tight">
            Choose a Zacma Service to Begin
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
            Each service features a simple 4-step intake form, automated invoice generation, and real-time timeline
            tracking.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5">
          {services.map((svc) => (
            <div
              key={svc.key}
              className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-3xl p-6 shadow-xl hover:shadow-2xl transition-all flex flex-col justify-between group hover:-translate-y-1"
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div
                    className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${svc.color} flex items-center justify-center text-white shadow-lg`}
                  >
                    <svc.icon className="w-6 h-6" />
                  </div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 bg-slate-950 px-2.5 py-1 rounded-full border border-slate-800">
                    {svc.badge}
                  </span>
                </div>

                <div>
                  <h3 className="text-base font-bold text-white group-hover:text-red-400 transition-colors">
                    {svc.title}
                  </h3>
                  <p className="text-[11px] font-medium text-slate-400 mt-0.5">{svc.tagline}</p>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed line-clamp-3">{svc.desc}</p>

                <div className="pt-3 border-t border-slate-800/80">
                  <p className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    {svc.stats}
                  </p>
                </div>
              </div>

              <div className="pt-6">
                <Link
                  href={svc.href}
                  className="w-full py-2.5 px-3 bg-slate-800 hover:bg-red-600 text-slate-200 hover:text-white rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 border border-slate-700 hover:border-red-500 shadow-md"
                >
                  <span>Apply / Request</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* OUR ENTERPRISE PLATFORMS SECTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="rounded-3xl bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950/60 border border-slate-800 p-8 sm:p-12 space-y-8 shadow-2xl">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" />
                Live Cloud Ecosystem
              </span>
              <h2 className="text-2xl sm:text-4xl font-black text-white tracking-tight mt-1">
                Our Official Enterprise Platforms
              </h2>
              <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-xl">
                Explore Zacma Group&apos;s live cloud platforms for enterprise management, school digitization, multi-vendor e-commerce, and tech talent.
              </p>
            </div>
            <Link
              href="/platforms"
              className="px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition shadow-lg shadow-amber-500/10 flex items-center gap-1.5 self-start md:self-auto"
            >
              <span>Explore All Platforms</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              {
                name: "Zacma ERP",
                tag: "https://erp.zacmaa.net/",
                desc: "Multi-branch cloud ERP for inventory, accounting & payroll.",
                badge: "Enterprise Suite",
                badgeColor: "text-blue-400 border-blue-500/20 bg-blue-500/10",
                btnClass: "bg-blue-600 hover:bg-blue-500 text-white",
              },
              {
                name: "MySchool",
                tag: "https://myschool.zacmaa.net/",
                desc: "Cloud school management for admissions, gradebooks & fees.",
                badge: "EdTech Cloud",
                badgeColor: "text-emerald-400 border-emerald-500/20 bg-emerald-500/10",
                btnClass: "bg-emerald-600 hover:bg-emerald-500 text-white",
              },
              {
                name: "Zacma E-Commerce",
                tag: "https://ecommerce.zacmaa.net/",
                desc: "Multi-vendor digital storefronts with TeleBirr & CBE checkout.",
                badge: "Digital Commerce",
                badgeColor: "text-amber-400 border-amber-500/20 bg-amber-500/10",
                btnClass: "bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold",
              },
              {
                name: "Zacma Freelancer",
                tag: "https://freelancer.zacmaa.net/",
                desc: "Vetted software engineers, UI/UX designers & marketers.",
                badge: "Talent Marketplace",
                badgeColor: "text-purple-400 border-purple-500/20 bg-purple-500/10",
                btnClass: "bg-purple-600 hover:bg-purple-500 text-white",
              },
            ].map((p, i) => (
              <div
                key={i}
                className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800/80 flex flex-col justify-between space-y-4 hover:border-slate-700 transition shadow-md"
              >
                <div className="space-y-2">
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${p.badgeColor}`}>
                    {p.badge}
                  </span>
                  <h4 className="text-base font-bold text-white mt-1">{p.name}</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">{p.desc}</p>
                </div>
                <div className="pt-2 border-t border-slate-900 flex items-center justify-between">
                  <a
                    href={p.tag}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`w-full py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition shadow-sm ${p.btnClass}`}
                  >
                    <span>Visit Platform</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* INTERACTIVE SERVICE PACKAGES EXPLORER */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-10 shadow-2xl space-y-8">
          <div className="text-center space-y-2 max-w-2xl mx-auto">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-400">Data-Driven Tiers</span>
            <h3 className="text-2xl sm:text-3xl font-black text-white">Transparent Package Pricing</h3>
            <p className="text-xs sm:text-sm text-slate-400">
              Select a service tab below to review available package tiers, included features, and instant fee
              schedules.
            </p>
          </div>

          {/* Tabs Switcher */}
          <div className="flex flex-wrap items-center justify-center gap-2">
            {services.map((s) => (
              <button
                key={s.key}
                onClick={() => setActiveTab(s.key as any)}
                className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                  activeTab === s.key
                    ? "bg-red-600 text-white shadow-lg ring-2 ring-red-600/30"
                    : "bg-slate-950 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800"
                }`}
              >
                <s.icon className="w-4 h-4" />
                <span>{s.title}</span>
              </button>
            ))}
          </div>

          {/* Package Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            {activeService.packages.map((pkg, idx) => (
              <div
                key={idx}
                className={`p-5 rounded-2xl border flex flex-col justify-between space-y-4 ${
                  pkg.popular
                    ? "bg-slate-800/90 border-red-500/80 shadow-xl relative"
                    : "bg-slate-950/70 border-slate-800"
                }`}
              >
                {pkg.popular && (
                  <span className="absolute -top-2.5 right-4 px-2.5 py-0.5 bg-red-600 text-[10px] font-bold text-white rounded-full uppercase tracking-wider shadow">
                    Recommended
                  </span>
                )}

                <div className="space-y-2">
                  <h4 className="text-base font-bold text-white">{pkg.name}</h4>
                  <div className="text-2xl font-black text-white font-mono">{pkg.price}</div>
                  <p className="text-xs text-slate-300 leading-relaxed">{pkg.desc}</p>
                </div>

                <Link
                  href={activeService.href}
                  className={`w-full py-2 rounded-xl text-xs font-bold text-center transition-colors ${
                    pkg.popular
                      ? "bg-red-600 hover:bg-red-500 text-white shadow-md"
                      : "bg-slate-800 hover:bg-slate-700 text-slate-200"
                  }`}
                >
                  Select This Tier →
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* WHY ZACMA TECHNOLOGY GROUP */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-center">
          <div className="space-y-4 lg:col-span-1">
            <span className="text-xs font-bold uppercase tracking-wider text-red-400">Enterprise Standard</span>
            <h3 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Why Individuals & Organizations Choose Zacma
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              We combine specialized human expertise with cutting-edge AI verification to deliver rapid, dependable
              results across all operational domains.
            </p>
            <div className="pt-2">
              <Link
                href="/contact"
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold rounded-xl border border-slate-700 transition-colors"
              >
                <span>Talk to a Specialist</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 lg:col-span-2">
            <div className="p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-2">
              <div className="w-9 h-9 rounded-xl bg-blue-600/20 text-blue-400 flex items-center justify-center">
                <Globe2 className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-bold text-white">Unified Multi-Service Portal</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Manage visa, travel, training, and marketing under a single account without repeating paperwork.
              </p>
            </div>

            <div className="p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-2">
              <div className="w-9 h-9 rounded-xl bg-red-600/20 text-red-400 flex items-center justify-center">
                <Sparkles className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-bold text-white">AI-Powered Pre-Audit</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Automated document validity checks and itinerary drafting reduce waiting times and prevent rejections.
              </p>
            </div>

            <div className="p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-2">
              <div className="w-9 h-9 rounded-xl bg-emerald-600/20 text-emerald-400 flex items-center justify-center">
                <CreditCard className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-bold text-white">Transparent Multi-Provider Payments</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Direct integration with SantimPay online checkout, Commercial Bank of Ethiopia (CBE), TeleBirr, Awash, and Abyssinia.
              </p>
            </div>

            <div className="p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-2">
              <div className="w-9 h-9 rounded-xl bg-purple-600/20 text-purple-400 flex items-center justify-center">
                <Users className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-bold text-white">Dedicated Case Supervisors</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Full human oversight with instant live chat and Telegram bot status synchronization.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FINAL CALL TO ACTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-r from-red-950 via-slate-900 to-indigo-950 border border-red-900/50 rounded-3xl p-8 sm:p-12 text-center space-y-6 shadow-2xl relative overflow-hidden">
          <div className="space-y-2 max-w-2xl mx-auto">
            <h3 className="text-2xl sm:text-4xl font-black text-white tracking-tight">
              Ready to Start Your Request?
            </h3>
            <p className="text-xs sm:text-sm text-slate-300">
              Submit your inquiry online in under 3 minutes or track an existing application in real time.
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/visa"
              className="px-6 py-3 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded-xl shadow-lg transition-all flex items-center gap-2"
            >
              <span>Apply for Visa</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/travel"
              className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow-lg transition-all flex items-center gap-2"
            >
              <span>Book Travel</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/training"
              className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl shadow-lg transition-all flex items-center gap-2"
            >
              <span>Enroll in Courses</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/track"
              className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs rounded-xl border border-slate-700 transition-colors"
            >
              Track Request Status
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
