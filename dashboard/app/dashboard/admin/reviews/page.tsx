"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "../../../../components/AuthProvider";

interface ReviewItem {
  id: string;
  reference_code: string;
  service_type: string;
  title: string;
  client_name: string;
  client_email: string;
  client_phone: string;
  status: string;
  payment_status: string;
  amount: number;
  currency: string;
  payment_receipt?: {
    payment_method: string;
    transaction_reference: string;
    receipt_file_url: string;
    amount: number;
    currency: string;
    submitted_at: string;
    status: string;
    comment?: string;
  };
  has_receipt: boolean;
  passport_upload_url?: string;
  supporting_document_urls?: string[];
  ai_generated_result?: any;
  admin_response?: {
    status: string;
    message: string;
    decided_by: string;
    decided_at: string;
  };
  created_at: string;
}

export default function AdminReviewsPage() {
  const { role, token } = useAuth();
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState("");
  const [actionLoading, setActionLoading] = useState(false);
  const [successBanner, setSuccessBanner] = useState<string | null>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

  const fetchQueue = async () => {
    setLoading(true);
    try {
      const url = statusFilter === "all"
        ? `${apiBase}/api/v1/admin/reviews/queue`
        : `${apiBase}/api/v1/admin/reviews/queue?status_filter=${statusFilter}`;
      const res = await fetch(url, {
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
        },
      });
      if (res.ok) {
        const data = await res.json();
        setItems(data);
        if (selectedItem) {
          const updated = data.find((d: ReviewItem) => d.reference_code === selectedItem.reference_code);
          if (updated) setSelectedItem(updated);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, [statusFilter, token]);

  const handleVerifyPayment = async (verified: boolean) => {
    if (!selectedItem) return;
    setActionLoading(true);
    try {
      const res = await fetch(
        `${apiBase}/api/v1/admin/reviews/${selectedItem.reference_code}/verify-payment`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : "",
          },
          body: JSON.stringify({
            verified,
            comment: verified
              ? "Payment verified by finance admin."
              : "Payment receipt rejected. Invalid reference.",
          }),
        }
      );
      if (res.ok) {
        setSuccessBanner(
          `Payment for ${selectedItem.reference_code} has been ${verified ? "APPROVED" : "REJECTED"}.`
        );
        fetchQueue();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleTriggerAi = async () => {
    if (!selectedItem) return;
    setActionLoading(true);
    try {
      const res = await fetch(
        `${apiBase}/api/v1/admin/reviews/${selectedItem.reference_code}/trigger-ai`,
        {
          method: "POST",
          headers: {
            Authorization: token ? `Bearer ${token}` : "",
          },
        }
      );
      if (res.ok) {
        setSuccessBanner(`AI Service Deliverable generated for ${selectedItem.reference_code}.`);
        fetchQueue();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleApproveService = async (newStatus: "Approved" | "ServiceDelivered" | "NeedsCorrection" | "Rejected") => {
    if (!selectedItem) return;
    setActionLoading(true);
    try {
      const res = await fetch(
        `${apiBase}/api/v1/admin/reviews/${selectedItem.reference_code}/approve-service`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : "",
          },
          body: JSON.stringify({
            status: newStatus,
            admin_response_message:
              feedbackMessage.trim() ||
              (newStatus === "ServiceDelivered"
                ? "Your official service package and deliverables are ready."
                : `Service status updated to ${newStatus}.`),
          }),
        }
      );
      if (res.ok) {
        setSuccessBanner(`Request ${selectedItem.reference_code} updated to ${newStatus}.`);
        setFeedbackMessage("");
        fetchQueue();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
          <div>
            <div className="flex items-center gap-3">
              <span className="px-2.5 py-1 bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-semibold rounded-full">
                Operations & Finance
              </span>
              <h1 className="text-2xl font-bold text-white tracking-tight">Client Case Reviews & Approvals</h1>
            </div>
            <p className="text-slate-400 text-sm mt-1">
              Verify client payment receipts (SantimPay / CBE / TeleBirr / Awash), inspect AI deliverables, and issue final service approvals.
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-2 bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs">
            {["all", "PaymentUnderReview", "PaymentApproved", "ServiceDelivered"].map((f) => (
              <button
                key={f}
                onClick={() => setStatusFilter(f)}
                className={`px-3 py-1.5 rounded-lg transition font-medium ${
                  statusFilter === f
                    ? "bg-amber-500 text-slate-950 shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {f === "all" ? "All Queue" : f}
              </button>
            ))}
          </div>
        </div>

        {successBanner && (
          <div className="p-4 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-sm flex items-center justify-between">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>{successBanner}</span>
            </div>
            <button onClick={() => setSuccessBanner(null)} className="text-emerald-400 hover:text-emerald-200">
              ✕
            </button>
          </div>
        )}

        {/* Master-Detail Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Queue List */}
          <div className="lg:col-span-5 space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400 px-1 font-semibold uppercase tracking-wider">
              <span>Incoming Cases ({items.length})</span>
              <button onClick={fetchQueue} className="text-amber-400 hover:underline">
                Refresh
              </button>
            </div>

            {loading ? (
              <div className="p-8 bg-slate-900/50 rounded-2xl border border-slate-800 text-center text-slate-400 text-sm">
                Loading review queue...
              </div>
            ) : items.length === 0 ? (
              <div className="p-8 bg-slate-900/50 rounded-2xl border border-slate-800 text-center text-slate-500 text-sm">
                No cases currently in this filter view.
              </div>
            ) : (
              <div className="space-y-2.5 max-h-[750px] overflow-y-auto pr-1">
                {items.map((item) => {
                  const isSelected = selectedItem?.reference_code === item.reference_code;
                  return (
                    <div
                      key={item.id}
                      onClick={() => setSelectedItem(item)}
                      className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                        isSelected
                          ? "bg-slate-900 border-amber-500 shadow-md shadow-amber-500/5"
                          : "bg-slate-900/50 border-slate-800 hover:border-slate-700"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-mono font-bold text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded">
                              {item.reference_code}
                            </span>
                            <span className="text-xs text-slate-400">{item.service_type}</span>
                          </div>
                          <h4 className="font-semibold text-white text-sm mt-1">{item.title}</h4>
                          <p className="text-xs text-slate-400 mt-0.5">{item.client_name} ({item.client_email})</p>
                        </div>
                        <span
                          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                            item.status === "PaymentApproved" || item.status === "ServiceDelivered"
                              ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                              : item.status === "PaymentUnderReview"
                              ? "bg-amber-500/20 text-amber-300 border-amber-500/30 animate-pulse"
                              : "bg-slate-800 text-slate-300 border-slate-700"
                          }`}
                        >
                          {item.status}
                        </span>
                      </div>

                      <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                        <span className="font-medium text-slate-200">
                          {item.amount.toLocaleString()} {item.currency}
                        </span>
                        <span>
                          {item.has_receipt ? (
                            <span className="text-amber-300 font-medium">📄 Receipt Attached</span>
                          ) : (
                            <span className="text-slate-500">No receipt yet</span>
                          )}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Right: Inspection & Approval Console */}
          <div className="lg:col-span-7">
            {selectedItem ? (
              <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 space-y-6">
                {/* Header detail */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-5">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold text-amber-400 bg-amber-400/10 px-2.5 py-1 rounded-md">
                        {selectedItem.reference_code}
                      </span>
                      <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded-md">
                        {selectedItem.service_type}
                      </span>
                    </div>
                    <h2 className="text-xl font-bold text-white mt-2">{selectedItem.title}</h2>
                    <p className="text-xs text-slate-400 mt-1">
                      Submitted by <strong className="text-slate-200">{selectedItem.client_name}</strong> •{" "}
                      {selectedItem.client_email} • {selectedItem.client_phone || "No phone"}
                    </p>
                  </div>

                  <div className="text-right">
                    <div className="text-xs text-slate-400">Total Fee</div>
                    <div className="text-lg font-bold text-amber-300">
                      {selectedItem.amount.toLocaleString()} {selectedItem.currency}
                    </div>
                  </div>
                </div>

                {/* Section 1: Payment Receipt Verification */}
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                      <span>💳 Payment Receipt Audit</span>
                      <span className="text-xs font-normal text-slate-400">(Multi-Provider Platform)</span>
                    </h3>
                    <span
                      className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${
                        selectedItem.payment_status === "Paid"
                          ? "bg-emerald-500/20 text-emerald-300"
                          : "bg-amber-500/20 text-amber-300"
                      }`}
                    >
                      {selectedItem.payment_status}
                    </span>
                  </div>

                  {selectedItem.payment_receipt ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                      <div>
                        <span className="text-slate-400 block">Bank / Gateway:</span>
                        <strong className="text-white text-sm">{selectedItem.payment_receipt.payment_method}</strong>
                      </div>
                      <div>
                        <span className="text-slate-400 block">Transaction Reference:</span>
                        <strong className="text-amber-300 font-mono text-sm">
                          {selectedItem.payment_receipt.transaction_reference}
                        </strong>
                      </div>
                      <div>
                        <span className="text-slate-400 block">Uploaded Amount:</span>
                        <span className="text-slate-200">
                          {selectedItem.payment_receipt.amount} {selectedItem.payment_receipt.currency}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block">Proof Document:</span>
                        <a
                          href={selectedItem.payment_receipt.receipt_file_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-amber-400 hover:underline inline-flex items-center gap-1 font-medium"
                        >
                          <span>View Proof Screenshot</span> ↗
                        </a>
                      </div>
                    </div>
                  ) : (
                    <div className="text-xs text-slate-400 italic py-2">
                      No payment receipt uploaded by client yet.
                    </div>
                  )}

                  {/* Payment Verification Buttons */}
                  <div className="flex items-center gap-2 pt-2">
                    <button
                      onClick={() => handleVerifyPayment(true)}
                      disabled={actionLoading}
                      className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition disabled:opacity-50"
                    >
                      ✓ Approve Payment & Trigger AI
                    </button>
                    <button
                      onClick={() => handleVerifyPayment(false)}
                      disabled={actionLoading}
                      className="px-3.5 py-1.5 rounded-xl bg-rose-900/60 hover:bg-rose-800 text-rose-200 text-xs font-semibold transition disabled:opacity-50"
                    >
                      ✕ Reject Payment
                    </button>
                  </div>
                </div>

                {/* Section 2: AI Service Deliverables */}
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                      <span>🤖 AI Generated Service Output</span>
                    </h3>
                    <button
                      onClick={handleTriggerAi}
                      disabled={actionLoading}
                      className="text-xs text-amber-400 hover:text-amber-300 font-semibold"
                    >
                      {selectedItem.ai_generated_result ? "Regenerate AI Output" : "+ Generate Output"}
                    </button>
                  </div>

                  {selectedItem.ai_generated_result ? (
                    <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 text-xs space-y-3 max-h-60 overflow-y-auto">
                      <div className="text-amber-300 font-semibold">
                        {selectedItem.ai_generated_result.deliverable_type}
                      </div>
                      {selectedItem.ai_generated_result.cover_letter && (
                        <div className="p-3 bg-slate-950 rounded-lg text-slate-300 font-mono text-[11px] whitespace-pre-line">
                          {selectedItem.ai_generated_result.cover_letter}
                        </div>
                      )}
                      {selectedItem.ai_generated_result.daily_itinerary && (
                        <div className="space-y-1.5">
                          {selectedItem.ai_generated_result.daily_itinerary.map((d: any, idx: number) => (
                            <div key={idx} className="p-2 bg-slate-950 rounded-lg">
                              <strong className="text-white">{d.day}: {d.title}</strong>
                              <p className="text-slate-400 text-[11px] mt-0.5">{d.morning} | {d.afternoon}</p>
                            </div>
                          ))}
                        </div>
                      )}
                      {selectedItem.ai_generated_result.weekly_syllabus && (
                        <div className="space-y-1.5">
                          {selectedItem.ai_generated_result.weekly_syllabus.map((s: any, idx: number) => (
                            <div key={idx} className="p-2 bg-slate-950 rounded-lg">
                              <strong className="text-white">{s.week}: {s.module}</strong>
                              <p className="text-slate-400 text-[11px] mt-0.5">Lab: {s.lab}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-xs text-slate-400 italic py-2">
                      AI deliverable will be generated automatically once payment is verified, or click &quot;Generate Output&quot; above.
                    </div>
                  )}
                </div>

                {/* Section 3: Admin Decision & Client Response */}
                <div className="space-y-3 pt-2">
                  <label className="text-xs font-semibold text-slate-300 block">
                    Admin Feedback / Instructions to Client
                  </label>
                  <textarea
                    rows={2}
                    value={feedbackMessage}
                    onChange={(e) => setFeedbackMessage(e.target.value)}
                    placeholder="Enter instructions, embassy interview date, certificate details, or corrections needed..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                  />

                  <div className="flex flex-wrap items-center gap-2 pt-1">
                    <button
                      onClick={() => handleApproveService("ServiceDelivered")}
                      disabled={actionLoading}
                      className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition shadow-lg shadow-amber-500/10 disabled:opacity-50"
                    >
                      🚀 Deliver Service to Client
                    </button>
                    <button
                      onClick={() => handleApproveService("Approved")}
                      disabled={actionLoading}
                      className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs transition disabled:opacity-50"
                    >
                      Mark Approved
                    </button>
                    <button
                      onClick={() => handleApproveService("NeedsCorrection")}
                      disabled={actionLoading}
                      className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-300 font-semibold text-xs transition disabled:opacity-50"
                    >
                      Request Correction
                    </button>
                    <button
                      onClick={() => handleApproveService("Rejected")}
                      disabled={actionLoading}
                      className="px-3.5 py-2 rounded-xl bg-rose-950/60 hover:bg-rose-900 text-rose-300 font-semibold text-xs transition disabled:opacity-50"
                    >
                      Reject Application
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/40 rounded-3xl border border-slate-800 p-12 text-center text-slate-500 text-sm">
                Select a client case from the left queue to audit receipts, review AI deliverables, and issue service approvals.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
