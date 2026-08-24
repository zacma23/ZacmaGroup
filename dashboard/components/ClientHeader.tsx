"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Compass,
  GraduationCap,
  Plane,
  Megaphone,
  Search,
  User,
  Menu,
  X,
  ChevronDown,
  LayoutDashboard,
  ShieldCheck,
  PhoneCall,
  Sparkles,
  Code,
  Layers,
} from "lucide-react";

export default function ClientHeader() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [servicesDropdown, setServicesDropdown] = useState(false);

  const navLinks = [
    { label: "Home", href: "/", icon: Compass },
    { label: "Platforms", href: "/platforms", icon: Layers },
    { label: "Visa Assistant", href: "/visa", icon: ShieldCheck },
    { label: "Travel Agent", href: "/travel", icon: Plane },
    { label: "Training", href: "/training", icon: GraduationCap },
    { label: "Marketing", href: "/marketing", icon: Megaphone },
    { label: "Track Request", href: "/track", icon: Search },
    { label: "Contact", href: "/contact", icon: PhoneCall },
  ];

  const subBrands = [
    {
      name: "Software Development",
      desc: "Custom web, mobile apps, ERP, MySchool, E-Commerce & AI",
      href: "/software",
      badge: "Software & SaaS",
      icon: Code,
      color: "text-amber-400",
    },
    {
      name: "Zacma Visa Assistant",
      desc: "Global visa consulting, embassy processing & document audits",
      href: "/visa",
      badge: "Visa & Immigration",
      icon: ShieldCheck,
      color: "text-red-400",
    },
    {
      name: "Zacma Travel Agent",
      desc: "Flight ticketing, 5-day holiday packages & hotel reservations",
      href: "/travel",
      badge: "Travel & Tours",
      icon: Plane,
      color: "text-blue-400",
    },
    {
      name: "Zacma Training",
      desc: "Accredited courses in Programming, AI, Media & Maintenance",
      href: "/training",
      badge: "Career Institute",
      icon: GraduationCap,
      color: "text-emerald-400",
    },
    {
      name: "Zacma Marketing Service",
      desc: "Social media management, brand identity & lead generation",
      href: "/marketing",
      badge: "Digital Growth",
      icon: Megaphone,
      color: "text-purple-400",
    },
  ];

  return (
    <header className="sticky top-0 z-40 w-full bg-slate-950/95 backdrop-blur border-b border-slate-800/80 shadow-lg">
      {/* Top Banner: Group Info & Multi-Channel Payment Indicator */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/70 to-slate-900 py-1.5 px-4 text-xs border-b border-slate-800/50">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2 text-slate-300">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 font-medium text-slate-200">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Zacma Technology Group · Multi-Service Client Platform
            </span>
            <span className="hidden md:inline text-slate-500">|</span>
            <span className="hidden md:inline text-slate-400">
              💳 Secure Instant Checkout via <strong className="text-emerald-300 font-semibold">SantimPay (Telebirr, CBE, Awash, Abyssinia & Cards)</strong>
            </span>
          </div>

          <div className="flex items-center gap-4 text-[11px]">
            <Link
              href="/track"
              className="text-red-400 hover:text-red-300 font-semibold flex items-center gap-1 transition-colors"
            >
              <Search className="w-3 h-3" />
              Track My Request
            </Link>
            <span className="text-slate-700">·</span>
            <Link
              href="/dashboard/crm"
              className="text-slate-400 hover:text-white flex items-center gap-1 transition-colors"
            >
              <LayoutDashboard className="w-3 h-3" />
              Admin Back-Office
            </Link>
          </div>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-600 via-red-700 to-indigo-950 flex items-center justify-center text-white shadow-md border border-red-500/40 group-hover:scale-105 transition-transform">
              <span className="text-2xl font-black tracking-tighter text-white">Z</span>
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-black tracking-tight text-white leading-tight flex items-center gap-1">
                <span className="text-red-500">ZACMA</span>
                <span className="text-blue-400 font-bold">GROUP</span>
              </span>
              <span className="text-[10px] font-semibold text-slate-400 tracking-wider uppercase">
                Technology & Services
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1">
            <Link
              href="/"
              className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === "/"
                  ? "bg-slate-800 text-white font-semibold"
                  : "text-slate-300 hover:text-white hover:bg-slate-900"
              }`}
            >
              Home
            </Link>

            {/* Services Dropdown */}
            <div
              className="relative"
              onMouseEnter={() => setServicesDropdown(true)}
              onMouseLeave={() => setServicesDropdown(false)}
            >
              <button
                className={`px-3.5 py-2 rounded-lg text-sm font-medium flex items-center gap-1.5 transition-colors ${
                  ["/software", "/visa", "/travel", "/training", "/marketing"].includes(pathname)
                    ? "bg-blue-950/60 text-blue-300 border border-blue-800/40"
                    : "text-slate-300 hover:text-white hover:bg-slate-900"
                }`}
              >
                <span>Services</span>
                <ChevronDown className="w-4 h-4 text-slate-400" />
              </button>

              {servicesDropdown && (
                <div className="absolute top-full left-0 w-80 pt-2 shadow-2xl animate-in fade-in slide-in-from-top-2 duration-150">
                  <div className="p-3 bg-slate-900/95 backdrop-blur-md rounded-2xl border border-slate-700/80 shadow-2xl space-y-1">
                    {subBrands.map((b, i) => (
                      <Link
                        key={i}
                        href={b.href}
                        onClick={() => setServicesDropdown(false)}
                        className="flex items-start gap-3 p-2.5 rounded-xl hover:bg-slate-800/80 transition-colors group"
                      >
                        <div className="p-2 rounded-lg bg-slate-800 border border-slate-700/60 group-hover:border-blue-500/40 text-blue-400">
                          <b.icon className="w-4 h-4" />
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-white group-hover:text-blue-300 transition-colors">
                            {b.name}
                          </p>
                          <p className="text-[11px] text-slate-400 leading-tight mt-0.5">{b.desc}</p>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <Link
              href="/platforms"
              className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === "/platforms"
                  ? "text-amber-400 font-semibold bg-amber-950/30 border border-amber-900/40"
                  : "text-slate-300 hover:text-white hover:bg-slate-900"
              }`}
            >
              Platforms
            </Link>

            <Link
              href="/visa"
              className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === "/visa"
                  ? "text-red-400 font-semibold bg-red-950/30 border border-red-900/40"
                  : "text-slate-300 hover:text-white hover:bg-slate-900"
              }`}
            >
              Visa Assistant
            </Link>

            <Link
              href="/travel"
              className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === "/travel"
                  ? "text-blue-400 font-semibold bg-blue-950/30 border border-blue-900/40"
                  : "text-slate-300 hover:text-white hover:bg-slate-900"
              }`}
            >
              Travel Agent
            </Link>

            <Link
              href="/training"
              className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === "/training"
                  ? "text-emerald-400 font-semibold bg-emerald-950/30 border border-emerald-900/40"
                  : "text-slate-300 hover:text-white hover:bg-slate-900"
              }`}
            >
              Training
            </Link>

            <Link
              href="/marketing"
              className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === "/marketing"
                  ? "text-purple-400 font-semibold bg-purple-950/30 border border-purple-900/40"
                  : "text-slate-300 hover:text-white hover:bg-slate-900"
              }`}
            >
              Marketing
            </Link>

            <Link
              href="/contact"
              className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === "/contact"
                  ? "text-white font-semibold bg-slate-800"
                  : "text-slate-300 hover:text-white hover:bg-slate-900"
              }`}
            >
              Contact
            </Link>
          </nav>

          {/* Right CTAs */}
          <div className="hidden lg:flex items-center gap-3">
            <Link
              href="/track"
              className="px-3.5 py-2 text-xs font-semibold text-slate-200 hover:text-white bg-slate-800/80 hover:bg-slate-700 border border-slate-700 rounded-xl transition-colors flex items-center gap-1.5"
            >
              <Search className="w-3.5 h-3.5 text-red-400" />
              Track Request
            </Link>

            <Link
              href="/portal"
              className="px-4 py-2 text-xs font-semibold text-white bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 rounded-xl shadow-md hover:shadow-red-600/30 transition-all flex items-center gap-1.5 border border-red-500/30"
            >
              <User className="w-3.5 h-3.5" />
              Client Portal
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="flex lg:hidden items-center gap-2">
            <Link
              href="/track"
              className="p-2 text-slate-300 hover:text-white bg-slate-900 border border-slate-800 rounded-lg"
              aria-label="Track Request"
            >
              <Search className="w-4 h-4 text-red-400" />
            </Link>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-slate-950 border-b border-slate-800 px-4 pt-2 pb-6 space-y-3">
          <div className="grid grid-cols-1 gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium ${
                    pathname === link.href
                      ? "bg-red-600/20 text-red-400 border border-red-600/30 font-semibold"
                      : "text-slate-300 hover:bg-slate-900"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {link.label}
                </Link>
              );
            })}
          </div>

          <div className="pt-3 border-t border-slate-800 space-y-2">
            <Link
              href="/portal"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-red-600 hover:bg-red-500 text-white text-sm font-semibold shadow-md"
            >
              <User className="w-4 h-4" />
              Client Portal Login
            </Link>
            <Link
              href="/dashboard/crm"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 text-sm font-medium border border-slate-800"
            >
              <LayoutDashboard className="w-4 h-4" />
              Admin Back-Office
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
