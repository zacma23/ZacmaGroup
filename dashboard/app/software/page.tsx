"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Code,
  Smartphone,
  Layers,
  Database,
  Bot,
  Cloud,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  FileText,
  CreditCard,
  Building,
} from "lucide-react";

function formatApiErrorMessage(errDetail: any, fallback: string = "Failed to submit project request"): string {
  if (!errDetail) return fallback;
  if (typeof errDetail === "string") return errDetail;
  if (Array.isArray(errDetail)) {
    const formatted = errDetail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object") {
          const loc = Array.isArray(item.loc) ? item.loc.filter((x: any) => x !== "body").join(" -> ") : "";
          const msg = item.msg || item.message || "Invalid input";
          return loc ? `${loc}: ${msg}` : msg;
        }
        return String(item);
      })
      .join("; ");
    return formatted || fallback;
  }
  if (typeof errDetail === "object") {
    if (errDetail.message && typeof errDetail.message === "string") return errDetail.message;
    if (errDetail.msg && typeof errDetail.msg === "string") return errDetail.msg;
    if (errDetail.detail) return formatApiErrorMessage(errDetail.detail, fallback);
    return JSON.stringify(errDetail);
  }
  return String(errDetail);
}

export default function SoftwareDevelopmentPage() {
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [submittedProject, setSubmittedProject] = useState<any | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form State
  const [projectName, setProjectName] = useState("");
  const [clientName, setClientName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("+2519");
  const [industry, setIndustry] = useState("Technology");
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(["Web", "Android"]);
  const [projectDescription, setProjectDescription] = useState("");
  const [problemToSolve, setProblemToSolve] = useState("");
  const [requiredFeatures, setRequiredFeatures] = useState("");
  const [targetUsers, setTargetUsers] = useState("");
  const [aiRequirements, setAiRequirements] = useState("");
  const [integrationRequirements, setIntegrationRequirements] = useState("");
  const [expectedTimeline, setExpectedTimeline] = useState("8-12 Weeks");
  const [budget, setBudget] = useState(50000);
  const [paymentMethod, setPaymentMethod] = useState("CBE");
  const [docUrl, setDocUrl] = useState("");

  const togglePlatform = (p: string) => {
    if (selectedPlatforms.includes(p)) {
      setSelectedPlatforms(selectedPlatforms.filter((item) => item !== p));
    } else {
      setSelectedPlatforms([...selectedPlatforms, p]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setErrorMsg(null);

    const featuresList = requiredFeatures
      .split("\n")
      .map((f) => f.trim())
      .filter((f) => f.length > 0);

    const payload = {
      project_name: projectName.trim(),
      client_name: clientName.trim(),
      email: email.trim(),
      phone: phone.trim(),
      industry,
      platforms: selectedPlatforms,
      project_description: projectDescription.trim(),
      problem_to_solve: problemToSolve.trim() || undefined,
      required_features: featuresList,
      target_users: targetUsers.trim() || undefined,
      ai_requirements: aiRequirements.trim() || undefined,
      integration_requirements: integrationRequirements.trim() || undefined,
      expected_timeline: expectedTimeline,
      budget: Number(budget),
      currency: "ETB",
      advance_payment_method: paymentMethod,
      advance_amount: Math.round(Number(budget) * 0.25),
      supporting_document_urls: docUrl ? [docUrl] : [],
    };

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/api/v1/software/projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(formatApiErrorMessage(data.detail, "Failed to submit project request"));
      }

      setSubmittedProject(data);
      setStep(5);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to submit request");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-10">
        {/* Header */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-blue-400">
            <Code className="w-3.5 h-3.5" />
            <span>Zacma Software Engineering Division</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-white">
            Software Development & <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-amber-400 bg-clip-text text-transparent">Custom Solutions</span>
          </h1>
          <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto">
            From modern web apps and mobile apps to custom ERP, School Management (MySchool), E-Commerce, and AI agents.
          </p>
        </div>

        {/* Step Progression Bar (1-4) */}
        {step < 5 && (
          <div className="bg-slate-900/80 p-4 rounded-2xl border border-slate-800 flex items-center justify-between gap-2 max-w-2xl mx-auto text-xs">
            {[
              { num: 1, label: "Scope & Platforms" },
              { num: 2, label: "Requirements" },
              { num: 3, label: "Budget & Plan" },
              { num: 4, label: "Client Details" },
            ].map((s) => (
              <div
                key={s.num}
                className={`flex items-center gap-2 cursor-pointer transition ${
                  step === s.num
                    ? "text-amber-400 font-bold"
                    : step > s.num
                    ? "text-emerald-400 font-medium"
                    : "text-slate-500"
                }`}
                onClick={() => step > s.num && setStep(s.num)}
              >
                <span
                  className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    step === s.num
                      ? "bg-amber-400 text-slate-950"
                      : step > s.num
                      ? "bg-emerald-500 text-slate-950"
                      : "bg-slate-800 text-slate-400"
                  }`}
                >
                  {step > s.num ? "✓" : s.num}
                </span>
                <span className="hidden sm:inline">{s.label}</span>
              </div>
            ))}
          </div>
        )}

        {errorMsg && (
          <div className="p-4 rounded-2xl bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs max-w-2xl mx-auto">
            {errorMsg}
          </div>
        )}

        {/* Form Container */}
        {step < 5 ? (
          <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 sm:p-10 shadow-2xl max-w-2xl mx-auto">
            <form onSubmit={step === 4 ? handleSubmit : (e) => { e.preventDefault(); setStep(step + 1); }}>
              {/* Step 1: Scope & Platform */}
              {step === 1 && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-xl font-bold text-white">Project Scope & Platforms</h2>
                    <p className="text-xs text-slate-400 mt-1">Specify your project name and target operating platforms.</p>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300">Project / Application Name *</label>
                    <input
                      type="text"
                      required
                      value={projectName}
                      onChange={(e) => setProjectName(e.target.value)}
                      placeholder="e.g. Telehealth Patient Portal & Delivery App"
                      className="mt-1.5 block w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-amber-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300">Industry / Domain</label>
                    <select
                      value={industry}
                      onChange={(e) => setIndustry(e.target.value)}
                      className="mt-1.5 block w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-amber-500"
                    >
                      <option>Technology & SaaS</option>
                      <option>Healthcare & Telemedicine</option>
                      <option>School & Education (MySchool)</option>
                      <option>Retail & E-Commerce</option>
                      <option>Enterprise ERP & Supply Chain</option>
                      <option>Finance & Fintech</option>
                      <option>Real Estate & Hospitality</option>
                      <option>Other Custom Industry</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-2">Target Platforms (Select all that apply)</label>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                      {[
                        { key: "Web", icon: Layers, desc: "Next.js / Cloud Web App" },
                        { key: "Android", icon: Smartphone, desc: "Google Play Store" },
                        { key: "iOS", icon: Smartphone, desc: "Apple App Store" },
                        { key: "Desktop", icon: Code, desc: "Windows / Mac" },
                        { key: "Cloud", icon: Cloud, desc: "REST APIs / Backend" },
                        { key: "AI Agent", icon: Bot, desc: "LLM / Autonomous Agent" },
                      ].map((p) => {
                        const isSelected = selectedPlatforms.includes(p.key);
                        const Icon = p.icon;
                        return (
                          <div
                            key={p.key}
                            onClick={() => togglePlatform(p.key)}
                            className={`p-3 rounded-2xl border cursor-pointer transition ${
                              isSelected
                                ? "bg-amber-500/10 border-amber-500 text-amber-300"
                                : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                            }`}
                          >
                            <Icon className="w-5 h-5 mb-1.5" />
                            <strong className="block text-xs text-white">{p.key}</strong>
                            <span className="text-[10px] text-slate-400">{p.desc}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={!projectName.trim() || selectedPlatforms.length === 0}
                    className="w-full py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-sm transition disabled:opacity-50"
                  >
                    Continue to Requirements →
                  </button>
                </div>
              )}

              {/* Step 2: Requirements */}
              {step === 2 && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-xl font-bold text-white">Technical & Feature Requirements</h2>
                    <p className="text-xs text-slate-400 mt-1">Describe the problem your project solves and core functional features.</p>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300">Project Description *</label>
                    <textarea
                      rows={3}
                      required
                      value={projectDescription}
                      onChange={(e) => setProjectDescription(e.target.value)}
                      placeholder="Explain what the system should do, who uses it, and the high-level workflow..."
                      className="mt-1.5 block w-full p-3.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300">Core Required Features (One per line)</label>
                    <textarea
                      rows={4}
                      value={requiredFeatures}
                      onChange={(e) => setRequiredFeatures(e.target.value)}
                      placeholder={"- User registration & KYC\n- TeleBirr/CBE payment integration\n- Real-time notifications\n- Admin management dashboard"}
                      className="mt-1.5 block w-full p-3.5 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-white focus:outline-none focus:border-amber-500"
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300">Target User Groups</label>
                      <input
                        type="text"
                        value={targetUsers}
                        onChange={(e) => setTargetUsers(e.target.value)}
                        placeholder="e.g. Customers, Admin, Cashiers"
                        className="mt-1.5 block w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-300">AI / Automation Needs</label>
                      <input
                        type="text"
                        value={aiRequirements}
                        onChange={(e) => setAiRequirements(e.target.value)}
                        placeholder="e.g. Chatbot, auto-categorization"
                        className="mt-1.5 block w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500"
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => setStep(1)}
                      className="w-1/3 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-xl text-xs transition"
                    >
                      ← Back
                    </button>
                    <button
                      type="submit"
                      disabled={!projectDescription.trim()}
                      className="w-2/3 py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-sm transition disabled:opacity-50"
                    >
                      Continue to Budget →
                    </button>
                  </div>
                </div>
              )}

              {/* Step 3: Budget & Timeline */}
              {step === 3 && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-xl font-bold text-white">Timeline & Payment Preference</h2>
                    <p className="text-xs text-slate-400 mt-1">Set your estimated budget and milestone schedule.</p>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300">Expected Timeline</label>
                    <select
                      value={expectedTimeline}
                      onChange={(e) => setExpectedTimeline(e.target.value)}
                      className="mt-1.5 block w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-amber-500"
                    >
                      <option>4-6 Weeks (Rapid Prototype / MVP)</option>
                      <option>8-12 Weeks (Production Release)</option>
                      <option>3-6 Months (Large-Scale Enterprise)</option>
                      <option>Ongoing Dedicated Engineering Team</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300">Estimated Project Budget (ETB) *</label>
                    <input
                      type="number"
                      min={10000}
                      step={5000}
                      value={budget}
                      onChange={(e) => setBudget(Number(e.target.value))}
                      className="mt-1.5 block w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm font-mono text-amber-300 focus:outline-none focus:border-amber-500"
                    />
                    <span className="text-[11px] text-slate-500 mt-1 block">
                      Advance architecture deposit (25%): <strong className="text-slate-300 font-mono">{Math.round(budget * 0.25).toLocaleString()} ETB</strong>
                    </span>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300">Advance Payment Method</label>
                    <select
                      value={paymentMethod}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                      className="mt-1.5 block w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-amber-500"
                    >
                      <option value="Chapa">Chapa Online Checkout (Cards / Wallets)</option>
                      <option value="CBE">Commercial Bank of Ethiopia (CBE)</option>
                      <option value="TeleBirr">TeleBirr Mobile Money</option>
                      <option value="Awash">Awash Bank Transfer</option>
                      <option value="Abyssinia">Bank of Abyssinia</option>
                    </select>
                  </div>

                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => setStep(2)}
                      className="w-1/3 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-xl text-xs transition"
                    >
                      ← Back
                    </button>
                    <button
                      type="submit"
                      className="w-2/3 py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-sm transition"
                    >
                      Continue to Contact Details →
                    </button>
                  </div>
                </div>
              )}

              {/* Step 4: Contact & Submit */}
              {step === 4 && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-xl font-bold text-white">Client / Organization Details</h2>
                    <p className="text-xs text-slate-400 mt-1">Provide your official contact information to receive project updates.</p>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300">Client / Company Name *</label>
                      <input
                        type="text"
                        required
                        value={clientName}
                        onChange={(e) => setClientName(e.target.value)}
                        placeholder="e.g. Abebe Kebede / TechCorp"
                        className="mt-1.5 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-amber-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-300">Email Address *</label>
                      <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="client@example.com"
                        className="mt-1.5 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-amber-500"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300">Phone Number *</label>
                      <input
                        type="tel"
                        required
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        placeholder="+251911..."
                        className="mt-1.5 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-amber-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-300">Supporting PRD / Spec Doc URL</label>
                      <input
                        type="text"
                        value={docUrl}
                        onChange={(e) => setDocUrl(e.target.value)}
                        placeholder="/uploads/specs/project_spec.pdf"
                        className="mt-1.5 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500"
                      />
                    </div>
                  </div>

                  <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 space-y-1">
                    <strong className="text-white block font-semibold">Advance Payment Notice:</strong>
                    <span>
                      An advance invoice for <strong>{Math.round(budget * 0.25).toLocaleString()} ETB</strong> will be generated. You can complete payment via online gateway or bank transfer and upload the receipt in your Client Portal.
                    </span>
                  </div>

                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => setStep(3)}
                      className="w-1/3 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-xl text-xs transition"
                    >
                      ← Back
                    </button>
                    <button
                      type="submit"
                      disabled={submitting || !clientName.trim() || !email.trim() || !phone.trim()}
                      className="w-2/3 py-3.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-sm transition shadow-lg shadow-amber-500/10 disabled:opacity-50"
                    >
                      {submitting ? "Submitting Project..." : "🚀 Submit Software Request"}
                    </button>
                  </div>
                </div>
              )}
            </form>
          </div>
        ) : (
          /* Step 5: Success & Confirmation */
          <div className="bg-slate-900 rounded-3xl border border-slate-800 p-8 sm:p-12 text-center max-w-2xl mx-auto space-y-6 shadow-2xl">
            <div className="w-16 h-16 rounded-3xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mx-auto text-2xl">
              ✓
            </div>
            <div>
              <span className="text-xs font-mono font-bold text-amber-400 bg-amber-400/10 px-3 py-1 rounded-full">
                {submittedProject?.reference_code}
              </span>
              <h2 className="text-2xl font-bold text-white mt-3">Software Project Request Submitted!</h2>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                Thank you, <strong>{submittedProject?.client_name}</strong>. Your project &quot;{submittedProject?.project_name}&quot; has been received and routed to our engineering solutions architects.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-left text-xs space-y-2">
              <div className="flex justify-between text-slate-400">
                <span>Advance Architecture Deposit:</span>
                <strong className="text-white font-mono">{submittedProject?.advance_amount?.toLocaleString()} ETB</strong>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Payment Reference:</span>
                <strong className="text-amber-300 font-mono">{submittedProject?.reference_code}</strong>
              </div>
            </div>

            <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
              <Link
                href="/portal"
                className="px-6 py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-xl transition shadow-lg shadow-amber-500/10"
              >
                Upload Payment Receipt in Portal →
              </Link>
              <Link
                href={`/track?ref=${submittedProject?.reference_code}`}
                className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs rounded-xl transition border border-slate-700"
              >
                Track Live Status
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
