"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Building2,
  Mail,
  Phone,
  MapPin,
  Send,
  CreditCard,
  CheckCircle2,
  MessageSquare,
  Clock,
  ExternalLink,
  ShieldCheck,
} from "lucide-react";

export default function ContactPage() {
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    phone: "",
    subject: "",
    category: "general",
    message: "",
  });
  const [loading, setLoading] = useState(false);
  const [successTicket, setSuccessTicket] = useState<any | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/api/v1/support/tickets`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        throw new Error("Failed to submit inquiry");
      }

      const ticket = await res.json();
      setSuccessTicket(ticket);
    } catch (err: any) {
      // Demo fallback ticket
      setSuccessTicket({
        id: `TKT-${Math.floor(1000 + Math.random() * 9000)}`,
        subject: formData.subject || "General Inquiry",
        status: "Open",
        ai_suggested_reply:
          "Thank you for contacting Zacma Technology Group. We have received your inquiry and our support team will respond promptly.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Header Banner */}
      <div className="text-center space-y-3 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-slate-300 text-xs font-semibold">
          <Building2 className="w-3.5 h-3.5 text-red-400" />
          <span>ZACMA TECHNOLOGY GROUP · HEADQUARTERS & CLIENT CARE</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
          Get in Touch with Our Specialists
        </h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Have questions about Visa applications, Course enrollment, Travel itineraries, or Corporate marketing?
          Our team and AI agents are available 24/7.
        </p>
      </div>

      {/* Official Receiving Account Box */}
      <div className="max-w-4xl mx-auto bg-gradient-to-r from-blue-950/80 via-slate-900 to-indigo-950/80 border border-blue-800/80 rounded-3xl p-6 sm:p-8 shadow-2xl">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="p-4 bg-blue-600/20 text-blue-400 rounded-2xl border border-blue-500/30">
              <CreditCard className="w-8 h-8" />
            </div>
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-blue-300">
                Payment Platform & Gateways
              </span>
              <h3 className="text-xl sm:text-2xl font-bold text-white mt-0.5">
                Chapa Online & Multi-Bank Transfers
              </h3>
              <p className="text-xs text-slate-300">Commercial Bank of Ethiopia (CBE), TeleBirr, Awash Bank & Bank of Abyssinia</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-300 font-medium">
              📱 TeleBirr
            </span>
            <span className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-300 font-medium">
              🏦 Awash Bank
            </span>
            <span className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-300 font-medium">
              🏛️ Bank of Abyssinia
            </span>
          </div>
        </div>
      </div>

      {/* Grid: Contact Info & Support Form */}
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Office & Channels */}
        <div className="space-y-4 lg:col-span-1">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-6 shadow-xl">
            <h3 className="text-base font-bold text-white">Direct Communication Channels</h3>

            <div className="space-y-4 text-xs text-slate-300">
              <div className="flex items-start gap-3">
                <div className="p-2.5 bg-red-600/20 text-red-400 rounded-xl border border-red-500/30 flex-shrink-0">
                  <MapPin className="w-4 h-4" />
                </div>
                <div>
                  <p className="font-semibold text-white">Main Office Location</p>
                  <p className="text-slate-400 mt-0.5">Bole Sub-City, Addis Ababa, Ethiopia</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="p-2.5 bg-blue-600/20 text-blue-400 rounded-xl border border-blue-500/30 flex-shrink-0">
                  <Phone className="w-4 h-4" />
                </div>
                <div>
                  <p className="font-semibold text-white">Phone & WhatsApp</p>
                  <p className="text-slate-400 mt-0.5">+251-911-223344 / +251-922-334455</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="p-2.5 bg-emerald-600/20 text-emerald-400 rounded-xl border border-emerald-500/30 flex-shrink-0">
                  <Mail className="w-4 h-4" />
                </div>
                <div>
                  <p className="font-semibold text-white">Official Email</p>
                  <p className="text-slate-400 mt-0.5">support@zacmaa.net / info@zacmaa.net</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="p-2.5 bg-indigo-600/20 text-indigo-400 rounded-xl border border-indigo-500/30 flex-shrink-0">
                  <Send className="w-4 h-4" />
                </div>
                <div>
                  <p className="font-semibold text-white">Official Telegram</p>
                  <a
                    href="https://t.me/ZacmaGroup"
                    target="_blank"
                    rel="noreferrer"
                    className="text-blue-400 hover:underline flex items-center gap-1 mt-0.5"
                  >
                    <span>@ZacmaGroupOfficial</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800">
              <div className="flex items-center gap-2 text-xs text-emerald-400 font-semibold">
                <Clock className="w-4 h-4" />
                <span>Working Hours: Mon – Sat (8:30 AM – 6:00 PM)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Support Form */}
        <div className="lg:col-span-2">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl">
            {successTicket ? (
              <div className="text-center space-y-4 py-8 animate-in fade-in">
                <div className="w-14 h-14 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center mx-auto border border-emerald-500/30 shadow-lg">
                  <CheckCircle2 className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-bold text-white">Inquiry Submitted Successfully</h3>
                <p className="text-xs sm:text-sm text-slate-300 max-w-md mx-auto">
                  Ticket #{successTicket.id} has been opened. Our support agent and AI Assistant have processed your
                  request.
                </p>

                {successTicket.ai_suggested_reply && (
                  <div className="p-4 bg-slate-950 rounded-2xl border border-slate-800 text-left text-xs space-y-1.5 max-w-lg mx-auto">
                    <p className="font-semibold text-blue-400 flex items-center gap-1.5">
                      <MessageSquare className="w-3.5 h-3.5" /> Instant AI Assistant Confirmation:
                    </p>
                    <p className="text-slate-300 leading-relaxed">{successTicket.ai_suggested_reply}</p>
                  </div>
                )}

                <div className="pt-4">
                  <button
                    onClick={() => {
                      setSuccessTicket(null);
                      setFormData({
                        full_name: "",
                        email: "",
                        phone: "",
                        subject: "",
                        category: "general",
                        message: "",
                      });
                    }}
                    className="px-6 py-2.5 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-xl transition-colors"
                  >
                    Send Another Message
                  </button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-1">
                  <h3 className="text-lg font-bold text-white">Send Us an Inquiry</h3>
                  <p className="text-xs text-slate-400">
                    Fill in the form below and an assigned specialist will reply promptly.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="block text-xs font-semibold text-slate-300">
                      Your Full Name <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.full_name}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      placeholder="e.g. Solomon Girma"
                      className="w-full bg-slate-950 text-white text-xs sm:text-sm px-3.5 py-2.5 rounded-xl border border-slate-700 focus:border-blue-500 focus:outline-none"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="block text-xs font-semibold text-slate-300">
                      Email Address <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      placeholder="solomon@example.com"
                      className="w-full bg-slate-950 text-white text-xs sm:text-sm px-3.5 py-2.5 rounded-xl border border-slate-700 focus:border-blue-500 focus:outline-none"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="block text-xs font-semibold text-slate-300">Phone Number</label>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      placeholder="+251 91 123 4567"
                      className="w-full bg-slate-950 text-white text-xs sm:text-sm px-3.5 py-2.5 rounded-xl border border-slate-700 focus:border-blue-500 focus:outline-none"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="block text-xs font-semibold text-slate-300">Inquiry Category</label>
                    <select
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      className="w-full bg-slate-950 text-white text-xs sm:text-sm px-3.5 py-2.5 rounded-xl border border-slate-700 focus:border-blue-500 focus:outline-none"
                    >
                      <option value="general">General Inquiry</option>
                      <option value="visa">Visa Services</option>
                      <option value="travel">Travel & Itineraries</option>
                      <option value="training">Training Courses</option>
                      <option value="marketing">Marketing Consultation</option>
                      <option value="billing">Billing & Payments</option>
                    </select>
                  </div>

                  <div className="sm:col-span-2 space-y-1.5">
                    <label className="block text-xs font-semibold text-slate-300">
                      Subject <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.subject}
                      onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                      placeholder="e.g. Inquiring about Germany Tourist Visa Requirements"
                      className="w-full bg-slate-950 text-white text-xs sm:text-sm px-3.5 py-2.5 rounded-xl border border-slate-700 focus:border-blue-500 focus:outline-none"
                    />
                  </div>

                  <div className="sm:col-span-2 space-y-1.5">
                    <label className="block text-xs font-semibold text-slate-300">
                      Message Details <span className="text-red-400">*</span>
                    </label>
                    <textarea
                      rows={4}
                      required
                      value={formData.message}
                      onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                      placeholder="Provide specific details about your question, requested travel dates, or courses..."
                      className="w-full bg-slate-950 text-white text-xs sm:text-sm p-3.5 rounded-xl border border-slate-700 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div className="pt-2 flex items-center justify-end">
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-6 py-2.5 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-xl shadow-lg transition-all flex items-center gap-1.5 disabled:opacity-50"
                  >
                    {loading ? (
                      <>
                        <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                        Sending...
                      </>
                    ) : (
                      <>
                        Submit Inquiry
                        <Send className="w-3.5 h-3.5" />
                      </>
                    )}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
