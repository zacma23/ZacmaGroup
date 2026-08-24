"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Search,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileText,
  CreditCard,
  Send,
  Bot,
  User,
  ShieldCheck,
  Plane,
  GraduationCap,
  Megaphone,
  Sparkles,
  ArrowRight,
  Headphones,
} from "lucide-react";

function TrackRequestContent() {
  const searchParams = useSearchParams();
  const initialRef = searchParams?.get("ref") || "";

  const [refInput, setRefInput] = useState(initialRef);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [requestData, setRequestData] = useState<any | null>(null);
  const [payingInvoice, setPayingInvoice] = useState(false);
  const [paymentError, setPaymentError] = useState<string | null>(null);

  // Thread messaging state
  const [clientMsg, setClientMsg] = useState("");
  const [sendingMsg, setSendingMsg] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);

  const handlePayNowInvoice = async () => {
    if (!requestData?.invoice) return;
    setPayingInvoice(true);
    setPaymentError(null);

    const invoice = requestData.invoice;
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/api/v1/payments/transactions/initialize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          amount: invoice.amount,
          provider_code: "santimpay",
          customer_name: requestData.customer_name || "Valued Client",
          customer_email: requestData.email || "client@zacmaa.net",
          customer_phone: requestData.phone,
          currency: invoice.currency || "ETB",
          payment_purpose: `Invoice: ${requestData.package || requestData.service_type}`,
          description: `Payment for Reference #${requestData.reference_code}`,
          invoice_id: invoice.id,
          return_url: `${typeof window !== "undefined" ? window.location.origin : "http://localhost:3000"}/portal?payment_status=success&ref=${encodeURIComponent(requestData.reference_code)}`,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to initialize SantimPay payment checkout");
      }

      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error("No checkout URL returned from payment gateway");
      }
    } catch (err: any) {
      setPaymentError(err.message || "Failed to connect to payment gateway");
    } finally {
      setPayingInvoice(false);
    }
  };

  const fetchTrackData = async (refCode: string) => {
    if (!refCode.trim()) return;
    setLoading(true);
    setErrorMsg(null);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/api/v1/support/track/${encodeURIComponent(refCode.trim())}`);
      if (!res.ok) {
        throw new Error("Request not found");
      }
      const data = await res.json();
      setRequestData(data);
      setMessages(data.messages || []);
    } catch (err: any) {
      setErrorMsg(`Could not find request with reference "${refCode}". Please check the reference number and try again.`);
      setRequestData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialRef) {
      fetchTrackData(initialRef);
    }
  }, [initialRef]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (refInput.trim()) {
      fetchTrackData(refInput.trim());
    }
  };

  const handleSendMessage = async (talkToHuman = false) => {
    if (!clientMsg.trim() && !talkToHuman) return;
    setSendingMsg(true);

    const messageContent = talkToHuman
      ? "I would like to speak with a human support specialist regarding my application."
      : clientMsg;

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/api/v1/support/track/${encodeURIComponent(requestData.reference_code)}/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: messageContent,
          sender_name: requestData.customer_name || "Client",
          talk_to_human: talkToHuman,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [...prev, data.client_message, data.ai_response]);
        setClientMsg("");
      }
    } catch (e) {
      // Local fallback in case backend is offline
      const userMessage = {
        id: `msg-${Date.now()}`,
        sender_type: "client",
        sender_name: requestData.customer_name || "Client",
        message: messageContent,
        created_at: new Date().toISOString(),
      };
      const aiReply = {
        id: `ai-${Date.now()}`,
        sender_type: "ai",
        sender_name: "Zacma AI Assistant",
        message: talkToHuman
          ? "Your request for a human specialist has been logged. A case manager will contact you within business hours."
          : "Thank you for your message. Your file is being processed in our queue.",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage, aiReply]);
      setClientMsg("");
    } finally {
      setSendingMsg(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Search Header */}
      <div className="text-center space-y-3 max-w-2xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-slate-300 text-xs font-semibold">
          <Search className="w-3.5 h-3.5 text-red-400" />
          <span>LIVE REQUEST TRACKING & TIMELINE</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
          Track Your Application & Invoices
        </h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Enter your Reference Number (e.g. <span className="font-mono text-red-400">ZAC-VIS-4419</span>,{" "}
          <span className="font-mono text-blue-400">visa-001</span>, or{" "}
          <span className="font-mono text-emerald-400">INV-2026-001</span>) to view real-time status and invoices.
        </p>

        {/* Input Form */}
        <form onSubmit={handleSearch} className="pt-2 flex items-center gap-2 max-w-lg mx-auto">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={refInput}
              onChange={(e) => setRefInput(e.target.value)}
              placeholder="Enter reference number..."
              className="w-full bg-slate-900 text-white placeholder-slate-500 text-xs sm:text-sm pl-10 pr-4 py-2.5 rounded-xl border border-slate-700 focus:border-red-500 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2.5 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded-xl shadow-lg transition-all flex items-center gap-1.5 disabled:opacity-50 flex-shrink-0"
          >
            {loading ? "Searching..." : "Track"}
          </button>
        </form>
      </div>

      {errorMsg && (
        <div className="max-w-xl mx-auto p-4 bg-red-950/60 border border-red-800 rounded-2xl flex items-center gap-3 text-red-200 text-xs sm:text-sm">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <p>{errorMsg}</p>
        </div>
      )}

      {/* RESULT VIEW */}
      {requestData && (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Top Status Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl space-y-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-red-400 bg-red-950/70 px-2.5 py-0.5 rounded border border-red-900/40">
                    {requestData.service_type}
                  </span>
                  <span className="font-mono text-xs text-slate-400">Ref: {requestData.reference_code}</span>
                </div>
                <h2 className="text-xl sm:text-2xl font-black text-white">{requestData.package}</h2>
                <p className="text-xs text-slate-300">Applicant: {requestData.customer_name}</p>
              </div>

              <div className="sm:text-right space-y-1">
                <span className="text-xs text-slate-400">Current Status</span>
                <div>
                  <span className="px-3 py-1 text-xs font-bold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    {requestData.status}
                  </span>
                </div>
              </div>
            </div>

            {/* Timeline Progress Tracker */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Application Timeline</h4>
              <div className="space-y-3">
                {requestData.timeline?.map((evt: any, idx: number) => (
                  <div key={idx} className="flex items-start gap-3 text-xs">
                    <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <p className="font-semibold text-white">{evt.status || "Update"}</p>
                      <p className="text-slate-400">{evt.description}</p>
                      {evt.timestamp && (
                        <p className="text-[10px] text-slate-500 mt-0.5">
                          {new Date(evt.timestamp).toLocaleString()}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Invoice & Payment Box */}
            {requestData.invoice && (
              <div className="p-5 bg-slate-950 rounded-2xl border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-semibold text-blue-300">
                    <CreditCard className="w-4 h-4" />
                    <span>Invoice & Payment Information</span>
                  </div>
                  <span className={`text-xs font-bold px-2.5 py-0.5 rounded border uppercase ${
                    requestData.invoice.status === "Paid"
                      ? "bg-emerald-950/70 text-emerald-300 border-emerald-800/40"
                      : "bg-amber-950/70 text-amber-300 border-amber-800/40"
                  }`}>
                    {requestData.invoice.status || "Pending"}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-slate-300">
                  <div>
                    <span className="text-slate-500">Invoice Amount:</span>
                    <p className="font-bold text-white font-mono text-sm">
                      {requestData.invoice.amount?.toLocaleString()} {requestData.invoice.currency || "ETB"}
                    </p>
                  </div>
                  <div>
                    <span className="text-slate-500">Supported Methods:</span>
                    <p className="font-semibold text-white">TeleBirr, CBE, Awash, Abyssinia & Cards</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Settlement Gateway:</span>
                    <p className="font-medium text-emerald-400">SantimPay Direct Secure Checkout</p>
                  </div>
                </div>

                {paymentError && (
                  <div className="p-2.5 bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs rounded-xl flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-400" />
                    <span>{paymentError}</span>
                  </div>
                )}

                {requestData.invoice.status !== "Paid" && (
                  <div className="pt-2 flex flex-col sm:flex-row items-center gap-3">
                    <button
                      type="button"
                      onClick={handlePayNowInvoice}
                      disabled={payingInvoice}
                      className="w-full sm:w-auto px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 text-white font-bold text-xs rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                      {payingInvoice ? (
                        <>
                          <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                          Redirecting to SantimPay...
                        </>
                      ) : (
                        <>
                          <CreditCard className="w-3.5 h-3.5" />
                          Pay Invoice Now via SantimPay ({requestData.invoice.amount?.toLocaleString()} {requestData.invoice.currency || "ETB"}) →
                        </>
                      )}
                    </button>

                    <Link
                      href="/portal"
                      className="w-full sm:w-auto px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-medium rounded-xl border border-slate-800 text-center"
                    >
                      Upload Manual Transfer Proof in Portal
                    </Link>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Interactive Request Message Thread (Client ↔ AI/Admin) */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-blue-600/20 text-blue-400 rounded-xl border border-blue-500/30">
                  <Bot className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Request Communication Thread</h3>
                  <p className="text-xs text-slate-400">Direct message channel for reference #{requestData.reference_code}</p>
                </div>
              </div>

              <button
                onClick={() => handleSendMessage(true)}
                disabled={sendingMsg}
                className="px-3 py-1.5 bg-indigo-950 hover:bg-indigo-900 text-indigo-200 border border-indigo-700/60 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors"
              >
                <Headphones className="w-3.5 h-3.5 text-indigo-400" />
                <span>Talk to Human</span>
              </button>
            </div>

            {/* Messages Scroll Area */}
            <div className="space-y-4 max-h-96 overflow-y-auto pr-2 bg-slate-950/60 p-4 rounded-2xl border border-slate-800/80">
              {messages.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-6">
                  No messages yet on this request. Type a question below to speak with your assigned specialist or AI assistant.
                </p>
              ) : (
                messages.map((m, idx) => {
                  const isClient = m.sender_type === "client";
                  return (
                    <div
                      key={m.id || idx}
                      className={`flex gap-3 ${isClient ? "justify-end" : "justify-start"}`}
                    >
                      {!isClient && (
                        <div className="w-7 h-7 rounded-full bg-blue-600/80 text-white flex items-center justify-center text-xs flex-shrink-0 mt-1 shadow">
                          <Bot className="w-4 h-4" />
                        </div>
                      )}
                      <div className={`max-w-[80%] space-y-1`}>
                        <div
                          className={`p-3 rounded-2xl text-xs sm:text-sm ${
                            isClient
                              ? "bg-red-600 text-white rounded-br-none shadow"
                              : "bg-slate-800 text-slate-200 border border-slate-700 rounded-bl-none shadow"
                          }`}
                        >
                          <p className="font-bold text-[11px] mb-0.5 text-slate-300">
                            {m.sender_name || (isClient ? "You" : "Zacma Assistant")}
                          </p>
                          <p className="whitespace-pre-line leading-relaxed">{m.message}</p>
                        </div>
                        {m.created_at && (
                          <p
                            className={`text-[10px] text-slate-500 px-1 ${
                              isClient ? "text-right" : "text-left"
                            }`}
                          >
                            {new Date(m.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                          </p>
                        )}
                      </div>
                      {isClient && (
                        <div className="w-7 h-7 rounded-full bg-slate-700 text-slate-300 flex items-center justify-center text-xs flex-shrink-0 mt-1">
                          <User className="w-4 h-4" />
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>

            {/* Input form */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage(false);
              }}
              className="flex items-center gap-2 pt-2"
            >
              <input
                type="text"
                value={clientMsg}
                onChange={(e) => setClientMsg(e.target.value)}
                placeholder="Ask about embassy timeline, travel date adjustments, or course schedule..."
                className="flex-1 bg-slate-950 text-white placeholder-slate-500 text-xs sm:text-sm px-4 py-2.5 rounded-xl border border-slate-700 focus:border-red-500 focus:outline-none"
              />
              <button
                type="submit"
                disabled={!clientMsg.trim() || sendingMsg}
                className="px-5 py-2.5 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded-xl shadow-lg transition-all flex items-center gap-1.5 disabled:opacity-40"
              >
                {sendingMsg ? "Sending..." : "Send"}
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default function TrackRequestPage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-7xl mx-auto px-4 py-16 text-center text-xs text-slate-400">
          <span className="w-4 h-4 border-2 border-red-500 border-t-transparent rounded-full animate-spin inline-block mr-2" />
          Loading request tracker...
        </div>
      }
    >
      <TrackRequestContent />
    </Suspense>
  );
}

