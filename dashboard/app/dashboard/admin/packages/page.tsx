"use client";

import React, { useState, useEffect } from "react";
import { Package, Plus, Edit2, Check, ShieldCheck, Plane, GraduationCap, Megaphone, Save, Trash2 } from "lucide-react";

export default function AdminPackagesPage() {
  const [packages, setPackages] = useState<any>({
    visa: [
      { id: "pkg-vis-basic", name: "Basic Guidance", tier: "Basic", price: 2500, currency: "ETB", description: "Standard visa guidance kit", features: ["Checklist", "Template"] },
      { id: "pkg-vis-std", name: "Standard Review", tier: "Standard", price: 5000, currency: "ETB", description: "AI document review & itinerary", features: ["AI audit", "Itinerary", "Case manager"] },
      { id: "pkg-vis-prem", name: "Premium Concierge", tier: "Premium", price: 10000, currency: "ETB", description: "Full embassy liaison & interview prep", features: ["Embassy liaison", "1-on-1 coach", "Priority support"] },
    ],
    travel: [
      { id: "pkg-trv-std", name: "Standard Booking", tier: "Standard", price: 3500, currency: "ETB", description: "Direct flight & hotel reservation", features: ["Flight ticketing", "Hotel booking"] },
      { id: "pkg-trv-itinerary", name: "Full 5-Day Itinerary", tier: "Full Itinerary", price: 8000, currency: "ETB", description: "Daily itinerary & tour passes", features: ["5-Day plan", "Airport transfers", "Tours"] },
      { id: "pkg-trv-vip", name: "VIP Concierge", tier: "VIP", price: 15000, currency: "ETB", description: "5-Star hotel suites & chauffeur", features: ["5-Star suites", "VIP lounge", "Chauffeur"] },
    ],
    training: [
      { id: "pkg-trn-single", name: "Single Course", tier: "Single", price: 4500, currency: "ETB", description: "Accredited course with practical lab", features: ["40+ hours", "Lab equipment", "Certificate"] },
      { id: "pkg-trn-bundle", name: "Professional Bundle", tier: "Bundle", price: 8000, currency: "ETB", description: "Dual-course bundle", features: ["2 courses", "Portfolio review", "Discount"] },
      { id: "pkg-trn-track", name: "Full Career Track", tier: "Career Track", price: 14000, currency: "ETB", description: "Mastery program with job referral", features: ["3-4 courses", "Mentorship", "Job referral"] },
    ],
    marketing: [
      { id: "pkg-mkt-starter", name: "Social Media Starter", tier: "Starter", price: 6000, currency: "ETB", description: "12 branded posts & community management", features: ["12 posts", "Facebook & Telegram"] },
      { id: "pkg-mkt-full", name: "Full Digital Marketing", tier: "Growth", price: 15000, currency: "ETB", description: "Paid ad campaigns & lead funnels", features: ["Meta/Google ads", "Landing pages", "Weekly ROI"] },
      { id: "pkg-mkt-combo", name: "Branding & Growth", tier: "Enterprise", price: 25000, currency: "ETB", description: "Complete brand book & digital PR", features: ["Brand identity", "Video reels", "Full campaigns"] },
    ],
  });

  const [activeTab, setActiveTab] = useState<"visa" | "travel" | "training" | "marketing">("visa");
  const [savedStatus, setSavedStatus] = useState<string | null>(null);

  const handlePriceChange = (pkgId: string, newPrice: number) => {
    setPackages((prev: any) => ({
      ...prev,
      [activeTab]: prev[activeTab].map((p: any) => (p.id === pkgId ? { ...p, price: newPrice } : p)),
    }));
  };

  const handleSave = () => {
    setSavedStatus("Package tiers updated successfully!");
    setTimeout(() => setSavedStatus(null), 3000);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
            <Package className="w-6 h-6 text-red-500" />
            Service Package & Pricing Manager
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Configure dynamic package tiers, fees, and feature descriptions across all four service lines.
          </p>
        </div>

        <button
          onClick={handleSave}
          className="px-5 py-2.5 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-xl shadow-lg transition-all flex items-center gap-1.5"
        >
          <Save className="w-4 h-4" />
          <span>Save Changes</span>
        </button>
      </div>

      {savedStatus && (
        <div className="p-3 bg-emerald-950/70 border border-emerald-800 rounded-xl text-xs text-emerald-300 flex items-center gap-2">
          <Check className="w-4 h-4 text-emerald-400" />
          <span>{savedStatus}</span>
        </div>
      )}

      {/* Service Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-3">
        {[
          { key: "visa", label: "Visa Assistant", icon: ShieldCheck },
          { key: "travel", label: "Travel Agent", icon: Plane },
          { key: "training", label: "Training Institute", icon: GraduationCap },
          { key: "marketing", label: "Marketing Service", icon: Megaphone },
        ].map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key as any)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-colors ${
              activeTab === t.key
                ? "bg-red-600 text-white shadow-md"
                : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
            }`}
          >
            <t.icon className="w-4 h-4" />
            <span>{t.label}</span>
          </button>
        ))}
      </div>

      {/* Packages Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {packages[activeTab]?.map((pkg: any) => (
          <div
            key={pkg.id}
            className="bg-slate-950/80 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-xl flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider text-red-400 bg-red-950/70 px-2 py-0.5 rounded border border-red-900/40">
                  {pkg.tier}
                </span>
                <span className="text-xs text-slate-500 font-mono">ID: {pkg.id}</span>
              </div>

              <div>
                <h3 className="text-base font-bold text-white">{pkg.name}</h3>
                <p className="text-xs text-slate-400 mt-1">{pkg.description}</p>
              </div>

              <div className="space-y-1.5 pt-2">
                <label className="block text-[11px] font-semibold text-slate-300">
                  Package Fee ({pkg.currency || "ETB"}):
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    value={pkg.price}
                    onChange={(e) => handlePriceChange(pkg.id, Number(e.target.value))}
                    className="w-full bg-slate-900 text-white font-mono font-bold text-sm px-3 py-2 rounded-xl border border-slate-700 focus:border-red-500 focus:outline-none"
                  />
                  <span className="text-xs font-semibold text-slate-400 font-mono">ETB</span>
                </div>
              </div>

              <div className="space-y-1.5 pt-2 border-t border-slate-800">
                <span className="text-[11px] font-semibold text-slate-400">Included Features:</span>
                <ul className="space-y-1 text-xs text-slate-300">
                  {pkg.features?.map((f: string, i: number) => (
                    <li key={i} className="flex items-center gap-1.5">
                      <Check className="w-3 h-3 text-emerald-400 flex-shrink-0" />
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800">
              <button
                type="button"
                onClick={handleSave}
                className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 transition-colors"
              >
                Update Tier Settings
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
