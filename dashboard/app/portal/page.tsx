"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "../../components/AuthProvider";

function formatApiErrorMessage(errDetail: any, fallback: string = "Request failed"): string {
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

export default function ClientPortalPage() {
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
  const { role, email, fullName, token, login, logout } = useAuth();

  // Auth form states
  const [authMode, setAuthMode] = useState<"login" | "register" | "forgot">("login");
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authFullName, setAuthFullName] = useState("");
  const [authPhone, setAuthPhone] = useState("");
  const [authAddress, setAuthAddress] = useState("");
  const [authEducation, setAuthEducation] = useState("Bachelor's Degree");
  const [rememberMe, setRememberMe] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [authSuccess, setAuthSuccess] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState(false);

  // Password reset states
  const [resetToken, setResetToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [resetStep, setResetStep] = useState<"request" | "confirm">("request");

  // Portal dashboard states
  const [activeTab, setActiveTab] = useState<"overview" | "requests" | "receipt" | "deliverables" | "profile">("overview");
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loadingDashboard, setLoadingDashboard] = useState(false);

  // Receipt submission state
  const [selectedRef, setSelectedRef] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("CBE");
  const [txRef, setTxRef] = useState("");
  const [receiptFileUrl, setReceiptFileUrl] = useState("/uploads/receipts/proof_screenshot.jpg");
  const [receiptNotes, setReceiptNotes] = useState("");
  const [receiptSubmitting, setReceiptSubmitting] = useState(false);
  const [receiptSuccess, setReceiptSuccess] = useState<string | null>(null);
  const [paymentNotification, setPaymentNotification] = useState<{ type: "success" | "error"; message: string } | null>(null);

  // Profile update state
  const [profilePhone, setProfilePhone] = useState("");
  const [profileAddress, setProfileAddress] = useState("");
  const [profileEducation, setProfileEducation] = useState("Diploma");
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileMsg, setProfileMsg] = useState<string | null>(null);

  // Fetch client dashboard
  const fetchDashboard = async () => {
    if (!email) return;
    setLoadingDashboard(true);
    try {
      const res = await fetch(`${apiBase}/api/v1/client/dashboard`, {
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
        },
      });
      if (res.ok) {
        const data = await res.json();
        setDashboardData(data);
        if (data.recent_requests && data.recent_requests.length > 0 && !selectedRef) {
          setSelectedRef(data.recent_requests[0].reference_code);
        }
      }
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setLoadingDashboard(false);
    }
  };

  useEffect(() => {
    if (email) {
      fetchDashboard();
    }
  }, [email, token]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const urlParams = new URLSearchParams(window.location.search);
    const paymentStatus = urlParams.get("payment_status");
    const refCode = urlParams.get("ref") || urlParams.get("tx_ref");

    if (paymentStatus === "success" && refCode) {
      const verifyPaymentReturn = async () => {
        try {
          const res = await fetch(`${apiBase}/api/v1/payments/transactions/${encodeURIComponent(refCode)}/verify`, {
            method: "POST",
          });
          if (res.ok) {
            setPaymentNotification({
              type: "success",
              message: `Payment verified successfully via SantimPay for Reference #${refCode}! Your service request has been activated.`,
            });
            fetchDashboard();
          }
        } catch (e) {
          console.error("Return payment verification:", e);
        }
      };
      verifyPaymentReturn();
    }
  }, []);

  const handleDirectSantimPay = async (r: any) => {
    try {
      const res = await fetch(`${apiBase}/api/v1/payments/transactions/initialize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          amount: r.advance_amount || r.amount || 2500,
          provider_code: "santimpay",
          customer_name: r.full_name || fullName || "Client",
          customer_email: r.email || email || "client@zacmaa.net",
          customer_phone: r.phone || profilePhone,
          currency: "ETB",
          payment_purpose: `${r.service_type || "Service"}: ${r.title || r.reference_code}`,
          description: `Direct Checkout for Ref #${r.reference_code}`,
          return_url: `${typeof window !== "undefined" ? window.location.origin : "http://localhost:3000"}/portal?payment_status=success&ref=${encodeURIComponent(r.reference_code)}`,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.checkout_url) {
          window.location.href = data.checkout_url;
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Auth Handlers
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    try {
      const res = await fetch(`${apiBase}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: authEmail.trim(),
          password: authPassword,
          remember_me: rememberMe,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(formatApiErrorMessage(data.detail, "Login failed"));
      }
      login(data.role, data.email, data.access_token, data.full_name);
    } catch (err: any) {
      setAuthError(err.message || "Invalid credentials");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    try {
      const res = await fetch(`${apiBase}/api/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: authEmail.trim(),
          password: authPassword,
          full_name: authFullName.trim(),
          phone: authPhone.trim(),
          address: authAddress.trim(),
          education_level: authEducation,
          role: "client",
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(formatApiErrorMessage(data.detail, "Registration failed"));
      }
      login(data.role, data.email, data.access_token, data.full_name, authPhone);
    } catch (err: any) {
      setAuthError(err.message || "Registration failed");
    } finally {
      setAuthLoading(false);
    }
  };

  const handlePasswordResetRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    try {
      const res = await fetch(`${apiBase}/api/v1/auth/password-reset-request`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: authEmail.trim() }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(formatApiErrorMessage(data.detail, "Request failed"));
      setAuthSuccess(data.message);
      if (data.reset_token) {
        setResetToken(data.reset_token);
        setResetStep("confirm");
      }
    } catch (err: any) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handlePasswordResetConfirm = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    try {
      const res = await fetch(`${apiBase}/api/v1/auth/password-reset-confirm`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: resetToken, new_password: newPassword }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(formatApiErrorMessage(data.detail, "Reset failed"));
      setAuthSuccess("Password successfully updated. Please log in with your new password.");
      setAuthMode("login");
      setResetStep("request");
    } catch (err: any) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleSubmitReceipt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRef) return;
    setReceiptSubmitting(true);
    setReceiptSuccess(null);
    try {
      const res = await fetch(`${apiBase}/api/v1/client/requests/${selectedRef}/receipt`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : "",
        },
        body: JSON.stringify({
          reference_code: selectedRef,
          payment_method: paymentMethod,
          transaction_reference: txRef,
          receipt_file_url: receiptFileUrl,
          notes: receiptNotes,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(formatApiErrorMessage(data.detail, "Failed to upload receipt"));
      setReceiptSuccess("Payment receipt uploaded successfully! Finance admin will verify shortly.");
      setTxRef("");
      setReceiptNotes("");
      fetchDashboard();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setReceiptSubmitting(false);
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileSaving(true);
    setProfileMsg(null);
    try {
      const res = await fetch(`${apiBase}/api/v1/auth/me`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : "",
        },
        body: JSON.stringify({
          phone: profilePhone,
          address: profileAddress,
          education_level: profileEducation,
        }),
      });
      if (res.ok) {
        setProfileMsg("Profile details updated successfully.");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setProfileSaving(false);
    }
  };

  // ---------------------------------------------------------------------------
  // View 1: Unauthenticated Login / Register / Forgot Password View
  // ---------------------------------------------------------------------------
  if (!email) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 font-black text-2xl mb-4 shadow-lg shadow-amber-500/5">
            Z
          </div>
          <h2 className="text-3xl font-black tracking-tight text-white">Client Service Portal</h2>
          <p className="mt-2 text-sm text-slate-400">
            Sign in to track your Visa, Travel, Course Training, and Marketing applications.
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-slate-900/90 py-8 px-6 shadow-2xl rounded-3xl border border-slate-800 sm:px-10">
            {/* Tab switchers */}
            <div className="flex border-b border-slate-800 pb-3 mb-6 gap-4 text-sm font-semibold">
              <button
                onClick={() => { setAuthMode("login"); setAuthError(null); setAuthSuccess(null); }}
                className={`pb-2 border-b-2 transition ${
                  authMode === "login"
                    ? "border-amber-400 text-amber-400"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                Sign In
              </button>
              <button
                onClick={() => { setAuthMode("register"); setAuthError(null); setAuthSuccess(null); }}
                className={`pb-2 border-b-2 transition ${
                  authMode === "register"
                    ? "border-amber-400 text-amber-400"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                New Account
              </button>
              <button
                onClick={() => { setAuthMode("forgot"); setAuthError(null); setAuthSuccess(null); }}
                className={`pb-2 border-b-2 transition ${
                  authMode === "forgot"
                    ? "border-amber-400 text-amber-400"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                Reset Password
              </button>
            </div>

            {authError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs">
                {authError}
              </div>
            )}
            {authSuccess && (
              <div className="mb-4 p-3 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-xs">
                {authSuccess}
              </div>
            )}

            {/* Login Form */}
            {authMode === "login" && (
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300">Email or Phone Number</label>
                  <input
                    type="text"
                    required
                    value={authEmail}
                    onChange={(e) => setAuthEmail(e.target.value)}
                    placeholder="e.g. client@example.com or +251911..."
                    className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300">Password</label>
                  <input
                    type="password"
                    required
                    value={authPassword}
                    onChange={(e) => setAuthPassword(e.target.value)}
                    placeholder="••••••••"
                    className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                  />
                </div>

                <div className="flex items-center justify-between text-xs text-slate-400">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="rounded bg-slate-950 border-slate-800 text-amber-500 focus:ring-0"
                    />
                    <span>Remember this device</span>
                  </label>
                  <button
                    type="button"
                    onClick={() => setAuthMode("forgot")}
                    className="text-amber-400 hover:underline"
                  >
                    Forgot password?
                  </button>
                </div>

                <button
                  type="submit"
                  disabled={authLoading}
                  className="w-full mt-2 py-3 px-4 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-sm transition shadow-lg shadow-amber-500/10 disabled:opacity-50"
                >
                  {authLoading ? "Authenticating..." : "Sign In to Portal"}
                </button>

                {/* Demo Quick Access */}
                <div className="mt-4 pt-4 border-t border-slate-800/80">
                  <span className="text-[11px] text-slate-500 block mb-2 font-medium">Quick Demo Sign-In:</span>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        setAuthEmail("client@zacma.com");
                        setAuthPassword("client123");
                      }}
                      className="py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold"
                    >
                      Client Demo
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setAuthEmail("admin@zacma.com");
                        setAuthPassword("admin");
                      }}
                      className="py-1.5 px-3 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 rounded-lg text-xs font-semibold"
                    >
                      Admin Demo
                    </button>
                  </div>
                </div>
              </form>
            )}

            {/* Register Form */}
            {authMode === "register" && (
              <form onSubmit={handleRegister} className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300">Full Name</label>
                  <input
                    type="text"
                    required
                    value={authFullName}
                    onChange={(e) => setAuthFullName(e.target.value)}
                    placeholder="e.g. Bethlehem Tadesse"
                    className="mt-1 block w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300">Email Address</label>
                  <input
                    type="email"
                    required
                    value={authEmail}
                    onChange={(e) => setAuthEmail(e.target.value)}
                    placeholder="e.g. beth@example.com"
                    className="mt-1 block w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs font-medium text-slate-300">Phone Number</label>
                    <input
                      type="tel"
                      value={authPhone}
                      onChange={(e) => setAuthPhone(e.target.value)}
                      placeholder="+251911..."
                      className="mt-1 block w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-300">Education Level</label>
                    <select
                      value={authEducation}
                      onChange={(e) => setAuthEducation(e.target.value)}
                      className="mt-1 block w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500"
                    >
                      <option>High School</option>
                      <option>Diploma</option>
                      <option>Bachelor&apos;s Degree</option>
                      <option>Master&apos;s Degree</option>
                      <option>Other</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300">Address / City</label>
                  <input
                    type="text"
                    value={authAddress}
                    onChange={(e) => setAuthAddress(e.target.value)}
                    placeholder="e.g. Addis Ababa, Ethiopia"
                    className="mt-1 block w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300">Create Password (min. 8 chars)</label>
                  <input
                    type="password"
                    required
                    minLength={8}
                    value={authPassword}
                    onChange={(e) => setAuthPassword(e.target.value)}
                    placeholder="••••••••"
                    className="mt-1 block w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                  />
                </div>

                <button
                  type="submit"
                  disabled={authLoading}
                  className="w-full mt-2 py-3 px-4 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-sm transition shadow-lg shadow-amber-500/10 disabled:opacity-50"
                >
                  {authLoading ? "Creating Account..." : "Create Client Account"}
                </button>
              </form>
            )}

            {/* Forgot Password Form */}
            {authMode === "forgot" && (
              <div>
                {resetStep === "request" ? (
                  <form onSubmit={handlePasswordResetRequest} className="space-y-4">
                    <p className="text-xs text-slate-400">
                      Enter your account email to receive a password reset token.
                    </p>
                    <div>
                      <label className="block text-xs font-medium text-slate-300">Registered Email</label>
                      <input
                        type="email"
                        required
                        value={authEmail}
                        onChange={(e) => setAuthEmail(e.target.value)}
                        placeholder="your.email@example.com"
                        className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={authLoading}
                      className="w-full py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-sm transition"
                    >
                      Send Reset Token
                    </button>
                  </form>
                ) : (
                  <form onSubmit={handlePasswordResetConfirm} className="space-y-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-300">Reset Token</label>
                      <input
                        type="text"
                        required
                        value={resetToken}
                        onChange={(e) => setResetToken(e.target.value)}
                        className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-amber-300"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-300">New Password (min 8 chars)</label>
                      <input
                        type="password"
                        required
                        minLength={8}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="••••••••"
                        className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-amber-500"
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={authLoading}
                      className="w-full py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-sm transition"
                    >
                      Update Password
                    </button>
                  </form>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // View 2: Authenticated Client Portal Dashboard
  // ---------------------------------------------------------------------------
  const summary = dashboardData?.summary || {
    total_requests: 0,
    active_requests: 0,
    receipts_under_review: 0,
    deliverables_ready: 0,
  };
  const requests = dashboardData?.recent_requests || [];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Top bar */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 p-5 rounded-3xl border border-slate-800">
          <div>
            <div className="flex items-center gap-3">
              <span className="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 font-bold flex items-center justify-center">
                {fullName ? fullName.charAt(0).toUpperCase() : "C"}
              </span>
              <div>
                <h1 className="text-xl font-bold text-white">Welcome, {fullName || email}</h1>
                <p className="text-xs text-slate-400">{email} • Role: {role || "Client"}</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Link
              href="/track"
              className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition"
            >
              Public Tracking
            </Link>
            {role === "admin" && (
              <Link
                href="/dashboard/admin/reviews"
                className="px-3.5 py-2 rounded-xl bg-amber-500/20 border border-amber-500/30 hover:bg-amber-500/30 text-amber-300 text-xs font-semibold transition"
              >
                Admin Review Console →
              </Link>
            )}
            <button
              onClick={logout}
              className="px-3.5 py-2 rounded-xl bg-rose-950/60 hover:bg-rose-900 text-rose-200 text-xs font-semibold transition"
            >
              Sign Out
            </button>
          </div>
        </div>

        {paymentNotification && (
          <div className={`p-4 rounded-2xl text-xs font-semibold border flex items-center justify-between ${
            paymentNotification.type === "success"
              ? "bg-emerald-950/80 border-emerald-500/50 text-emerald-200"
              : "bg-rose-950/80 border-rose-500/50 text-rose-200"
          }`}>
            <span>{paymentNotification.message}</span>
            <button
              onClick={() => setPaymentNotification(null)}
              className="px-2 py-0.5 rounded bg-black/30 hover:bg-black/50 text-white text-[11px]"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 overflow-x-auto border-b border-slate-800 pb-3 text-xs font-semibold">
          {[
            { key: "overview", label: "📊 Overview" },
            { key: "requests", label: "📋 My Applications & Requests" },
            { key: "receipt", label: "💳 Upload Payment Receipt" },
            { key: "deliverables", label: "🤖 AI Deliverables" },
            { key: "profile", label: "👤 Profile & Settings" },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`px-4 py-2 rounded-xl transition ${
                activeTab === tab.key
                  ? "bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/10"
                  : "bg-slate-900 text-slate-400 hover:text-slate-200"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content 1: Overview */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
                <span className="text-xs text-slate-400 font-medium">Total Requests</span>
                <div className="text-2xl font-black text-white mt-1">{summary.total_requests}</div>
              </div>
              <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
                <span className="text-xs text-slate-400 font-medium">Active Applications</span>
                <div className="text-2xl font-black text-amber-400 mt-1">{summary.active_requests}</div>
              </div>
              <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
                <span className="text-xs text-slate-400 font-medium">Receipts Under Review</span>
                <div className="text-2xl font-black text-amber-300 mt-1">{summary.receipts_under_review}</div>
              </div>
              <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
                <span className="text-xs text-slate-400 font-medium">Approved Deliverables</span>
                <div className="text-2xl font-black text-emerald-400 mt-1">{summary.deliverables_ready}</div>
              </div>
            </div>

            {/* Official Payment Accounts Notice */}
            <div className="p-5 rounded-3xl bg-amber-500/10 border border-amber-500/20 text-amber-200 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
                  Zacma Multi-Provider Payment Platform
                </span>
                <h3 className="text-base font-bold text-white mt-0.5">
                  Instant Online Checkout & Bank Transfers
                </h3>
                <p className="text-xs text-amber-300/80 mt-1">
                  We accept SantimPay (Debit/Credit Cards, Telebirr, CBE Birr), Commercial Bank of Ethiopia (CBE), TeleBirr, Awash Bank, and Bank of Abyssinia.
                </p>
              </div>
              <button
                onClick={() => setActiveTab("receipt")}
                className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-xl transition whitespace-nowrap"
              >
                Upload Receipt Now →
              </button>
            </div>

            {/* Quick Service Action Launcher */}
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-white">Start a New Service Request:</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <Link
                  href="/visa"
                  className="p-4 rounded-2xl bg-slate-900 border border-slate-800 hover:border-amber-500/50 transition group"
                >
                  <span className="text-2xl">🛂</span>
                  <h4 className="font-bold text-white text-sm mt-2 group-hover:text-amber-400">Visa Assistant</h4>
                  <p className="text-xs text-slate-400 mt-1">Embassy cover letters, document audits & visa processing.</p>
                </Link>
                <Link
                  href="/travel"
                  className="p-4 rounded-2xl bg-slate-900 border border-slate-800 hover:border-amber-500/50 transition group"
                >
                  <span className="text-2xl">✈️</span>
                  <h4 className="font-bold text-white text-sm mt-2 group-hover:text-amber-400">Travel Agent</h4>
                  <p className="text-xs text-slate-400 mt-1">Flight bookings & 5-day curated holiday itineraries.</p>
                </Link>
                <Link
                  href="/training"
                  className="p-4 rounded-2xl bg-slate-900 border border-slate-800 hover:border-amber-500/50 transition group"
                >
                  <span className="text-2xl">💻</span>
                  <h4 className="font-bold text-white text-sm mt-2 group-hover:text-amber-400">Training Institute</h4>
                  <p className="text-xs text-slate-400 mt-1">Practical courses in Programming, AI, Graphics & Hardware.</p>
                </Link>
                <Link
                  href="/marketing"
                  className="p-4 rounded-2xl bg-slate-900 border border-slate-800 hover:border-amber-500/50 transition group"
                >
                  <span className="text-2xl">📈</span>
                  <h4 className="font-bold text-white text-sm mt-2 group-hover:text-amber-400">Marketing Service</h4>
                  <p className="text-xs text-slate-400 mt-1">Digital growth campaigns & 30-day content strategies.</p>
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* Tab Content 2: My Requests */}
        {activeTab === "requests" && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white">Your Submitted Service Applications ({requests.length})</h3>
            {requests.length === 0 ? (
              <div className="p-8 bg-slate-900 rounded-2xl border border-slate-800 text-center text-slate-400 text-sm">
                You have not submitted any service applications yet. Use the buttons in Overview to get started!
              </div>
            ) : (
              <div className="space-y-3">
                {requests.map((r: any) => (
                  <div key={r.id} className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono font-bold text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded">
                            {r.reference_code}
                          </span>
                          <span className="text-xs text-slate-400">{r.service_type}</span>
                        </div>
                        <h4 className="text-base font-bold text-white mt-1">{r.title}</h4>
                        {r.course && (
                          <div className="flex flex-wrap items-center gap-2 text-xs text-slate-300 mt-2 bg-slate-950/60 p-2.5 rounded-xl border border-slate-800">
                            <span>Course: <strong className="text-white">{r.course}</strong></span>
                            {r.specialty && <span>• Specialty: <strong className="text-amber-300">{r.specialty}</strong></span>}
                            {r.schedule && <span>• Schedule: <strong className="text-blue-300">{r.schedule}</strong></span>}
                            {r.time_slot && <span>• Time: <strong className="text-emerald-300">{r.time_slot}</strong></span>}
                          </div>
                        )}
                      </div>

                      <div className="flex items-center gap-2">
                        <span
                          className={`text-xs px-2.5 py-1 rounded-full font-semibold border ${
                            r.status === "Approved" || r.status === "ServiceDelivered"
                              ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                              : r.status === "PaymentUnderReview"
                              ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
                              : "bg-slate-800 text-slate-300 border-slate-700"
                          }`}
                        >
                          Status: {r.status}
                        </span>
                      </div>
                    </div>

                    {/* Admin feedback if present */}
                    {r.admin_response && (
                      <div className="p-3 bg-slate-950 rounded-xl border border-slate-800/80 text-xs">
                        <strong className="text-amber-400">Case Manager Response:</strong>
                        <p className="text-slate-300 mt-1">{r.admin_response.message}</p>
                      </div>
                    )}

                    <div className="flex flex-wrap items-center justify-between pt-2 border-t border-slate-800/60 text-xs text-slate-400 gap-2">
                      <span>Payment Status: <strong className="text-slate-200">{r.payment_status}</strong></span>
                      <div className="flex items-center gap-2">
                        {r.payment_status !== "Paid" && r.payment_status !== "Verified" && (
                          <button
                            onClick={() => handleDirectSantimPay(r)}
                            className="px-3 py-1 bg-emerald-600/90 hover:bg-emerald-600 text-white rounded-lg font-bold text-xs shadow transition flex items-center gap-1"
                          >
                            Pay via SantimPay →
                          </button>
                        )}
                        {!r.has_receipt && (
                          <button
                            onClick={() => {
                              setSelectedRef(r.reference_code);
                              setActiveTab("receipt");
                            }}
                            className="text-amber-400 hover:underline font-semibold"
                          >
                            + Upload Receipt
                          </button>
                        )}
                        {r.has_ai_output && (
                          <button
                            onClick={() => setActiveTab("deliverables")}
                            className="text-emerald-400 hover:underline font-semibold"
                          >
                            View Deliverable →
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab Content 3: Upload Receipt */}
        {activeTab === "receipt" && (
          <div className="max-w-2xl bg-slate-900 p-6 rounded-3xl border border-slate-800 space-y-5">
            <div>
              <h3 className="text-lg font-bold text-white">Upload Payment Receipt</h3>
              <p className="text-xs text-slate-400 mt-1">
                Attach your transfer confirmation screenshot or transaction number for admin verification.
              </p>
            </div>

            {receiptSuccess && (
              <div className="p-3 bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-xs rounded-xl">
                {receiptSuccess}
              </div>
            )}

            <form onSubmit={handleSubmitReceipt} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300">Select Service Request Reference</label>
                <select
                  value={selectedRef}
                  onChange={(e) => setSelectedRef(e.target.value)}
                  className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-amber-500"
                >
                  {requests.map((r: any) => (
                    <option key={r.id} value={r.reference_code}>
                      {r.reference_code} — {r.title} ({r.service_type})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300">Payment Gateway / Bank</label>
                  <select
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="mt-1 block w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500"
                  >
                    <option value="SantimPay">SantimPay Online Gateway</option>
                    <option value="CBE">Commercial Bank of Ethiopia (CBE)</option>
                    <option value="TeleBirr">TeleBirr Mobile Money</option>
                    <option value="Awash">Awash Bank</option>
                    <option value="Abyssinia">Bank of Abyssinia</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300">Transaction Reference Code</label>
                  <input
                    type="text"
                    required
                    value={txRef}
                    onChange={(e) => setTxRef(e.target.value)}
                    placeholder="e.g. FT260823CBE991"
                    className="mt-1 block w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono placeholder-slate-500 focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Receipt Proof File URL / Path</label>
                <input
                  type="text"
                  required
                  value={receiptFileUrl}
                  onChange={(e) => setReceiptFileUrl(e.target.value)}
                  placeholder="/uploads/receipts/proof.jpg"
                  className="mt-1 block w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Optional Notes</label>
                <textarea
                  rows={2}
                  value={receiptNotes}
                  onChange={(e) => setReceiptNotes(e.target.value)}
                  placeholder="e.g. Paid via CBE Birr app at 2:30 PM."
                  className="mt-1 block w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
                />
              </div>

              <button
                type="submit"
                disabled={receiptSubmitting || !selectedRef}
                className="w-full py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-sm transition shadow-lg shadow-amber-500/10 disabled:opacity-50"
              >
                {receiptSubmitting ? "Submitting Receipt..." : "Submit Receipt for Review"}
              </button>
            </form>
          </div>
        )}

        {/* Tab Content 4: AI Deliverables */}
        {activeTab === "deliverables" && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white">Your Generated AI Deliverables</h3>
            <div className="space-y-4">
              {requests.filter((r: any) => r.has_ai_output).length === 0 ? (
                <div className="p-8 bg-slate-900 rounded-2xl border border-slate-800 text-center text-slate-400 text-sm">
                  No deliverables ready yet. Once your payment receipt is verified, AI outputs will appear here.
                </div>
              ) : (
                requests
                  .filter((r: any) => r.has_ai_output)
                  .map((r: any) => (
                    <div key={r.id} className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                        <div>
                          <span className="text-xs font-mono font-bold text-amber-400">{r.reference_code}</span>
                          <h4 className="text-lg font-bold text-white mt-1">{r.title}</h4>
                        </div>
                        <span className="text-xs px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full font-semibold border border-emerald-500/30">
                          Ready for Download
                        </span>
                      </div>

                      <div className="p-4 bg-slate-950 rounded-2xl text-xs font-mono text-slate-300 whitespace-pre-line border border-slate-800/80">
                        {r.ai_generated_result?.cover_letter ||
                          JSON.stringify(r.ai_generated_result, null, 2)}
                      </div>
                    </div>
                  ))
              )}
            </div>
          </div>
        )}

        {/* Tab Content 5: Profile & Settings */}
        {activeTab === "profile" && (
          <div className="max-w-2xl bg-slate-900 p-6 rounded-3xl border border-slate-800 space-y-5">
            <div>
              <h3 className="text-lg font-bold text-white">Profile & Security Settings</h3>
              <p className="text-xs text-slate-400 mt-1">Manage your account information and contact preferences.</p>
            </div>

            {profileMsg && (
              <div className="p-3 bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 text-xs rounded-xl">
                {profileMsg}
              </div>
            )}

            <form onSubmit={handleSaveProfile} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300">Email Address (Fixed)</label>
                <input
                  type="text"
                  disabled
                  value={email}
                  className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950/50 border border-slate-800 rounded-xl text-sm text-slate-400"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Phone Number</label>
                <input
                  type="text"
                  value={profilePhone}
                  onChange={(e) => setProfilePhone(e.target.value)}
                  placeholder="+251911..."
                  className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Residential Address</label>
                <input
                  type="text"
                  value={profileAddress}
                  onChange={(e) => setProfileAddress(e.target.value)}
                  placeholder="e.g. Bole Sub-City, Addis Ababa"
                  className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300">Education Level</label>
                <select
                  value={profileEducation}
                  onChange={(e) => setProfileEducation(e.target.value)}
                  className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:border-amber-500"
                >
                  <option>High School</option>
                  <option>Diploma</option>
                  <option>Bachelor&apos;s Degree</option>
                  <option>Master&apos;s Degree</option>
                  <option>Other</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={profileSaving}
                className="py-3 px-6 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-sm transition shadow-lg shadow-amber-500/10 disabled:opacity-50"
              >
                {profileSaving ? "Saving..." : "Save Profile Details"}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
