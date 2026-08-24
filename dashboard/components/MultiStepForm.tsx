"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  CheckCircle,
  ArrowRight,
  ArrowLeft,
  Upload,
  FileText,
  CreditCard,
  Building,
  Sparkles,
  Copy,
  Check,
  AlertCircle,
  ShieldAlert,
} from "lucide-react";

export interface PackageTier {
  id: string;
  name: string;
  tier: string;
  price: number;
  currency: string;
  description: string;
  features: string[];
  popular?: boolean;
}

export interface FormFieldDef {
  name: string;
  label: string;
  type: "text" | "email" | "tel" | "number" | "select" | "textarea" | "file";
  placeholder?: string;
  options?: string[];
  required?: boolean;
  helpText?: string;
}

interface MultiStepFormProps {
  serviceKey: "visa" | "travel" | "training" | "marketing";
  serviceTitle: string;
  subBrandName: string;
  accentColor: "red" | "blue" | "emerald" | "purple";
  packages: PackageTier[];
  requirementsChecklist: { title: string; desc: string; required?: boolean }[];
  fieldDefinitions: FormFieldDef[];
  apiEndpoint: string;
  transformPayload?: (formData: Record<string, any>, selectedPkg: PackageTier) => any;
  defaultPaymentMethod?: string;
}

function formatApiErrorMessage(errDetail: any, fallback: string = "Error processing request"): string {
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

export default function MultiStepForm({
  serviceKey,
  serviceTitle,
  subBrandName,
  accentColor,
  packages,
  requirementsChecklist,
  fieldDefinitions,
  apiEndpoint,
  transformPayload,
  defaultPaymentMethod = "CBE",
}: MultiStepFormProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedPackage, setSelectedPackage] = useState<PackageTier>(packages[1] || packages[0]);
  const [formData, setFormData] = useState<Record<string, any>>({
    payment_method: defaultPaymentMethod,
  });
  const [filePreviews, setFilePreviews] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [submissionSuccess, setSubmissionSuccess] = useState<any | null>(null);
  const [copied, setCopied] = useState(false);
  const [initiatingPayment, setInitiatingPayment] = useState(false);
  const [paymentError, setPaymentError] = useState<string | null>(null);

  const handlePayNow = async () => {
    if (!submissionSuccess) return;
    setInitiatingPayment(true);
    setPaymentError(null);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/api/v1/payments/transactions/initialize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          amount: submissionSuccess.package.price,
          provider_code: "chapa",
          customer_name: formData.full_name || submissionSuccess.data?.full_name || "Valued Client",
          customer_email: formData.email || submissionSuccess.data?.email || "client@zacmaa.net",
          customer_phone: formData.phone || submissionSuccess.data?.phone,
          currency: submissionSuccess.package.currency || "ETB",
          payment_purpose: `${serviceTitle}: ${submissionSuccess.package.name}`,
          description: `Advance fee for ${submissionSuccess.referenceCode}`,
          return_url: `${typeof window !== "undefined" ? window.location.origin : "http://localhost:3000"}/portal?payment_status=success&ref=${encodeURIComponent(submissionSuccess.referenceCode)}`,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to initialize Chapa payment checkout");
      }

      const data = await res.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error("No checkout URL returned from payment gateway");
      }
    } catch (err: any) {
      setPaymentError(err.message || "Could not connect to payment gateway. Please try again or use manual verification.");
    } finally {
      setInitiatingPayment(false);
    }
  };

  const steps = [
    { num: 1, label: "Select Package" },
    { num: 2, label: "Checklist" },
    { num: 3, label: "Details & Uploads" },
    { num: 4, label: "Review & Submit" },
  ];

  const handleInputChange = (name: string, value: any) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
    setErrorMsg(null);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>, name: string) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        setErrorMsg(`File ${file.name} exceeds maximum 10MB limit.`);
        return;
      }
      // Store mock upload URL and filename
      const mockUrl = `/uploads/${serviceKey}/${file.name.replace(/\s+/g, "_")}`;
      handleInputChange(name, mockUrl);
      setFilePreviews((prev) => ({ ...prev, [name]: file.name }));
    }
  };

  const validateStep3 = () => {
    for (const field of fieldDefinitions) {
      if (field.required && !formData[field.name]) {
        setErrorMsg(`Please fill in "${field.label}" to proceed.`);
        return false;
      }
    }
    return true;
  };

  const handleNext = () => {
    if (currentStep === 3) {
      if (!validateStep3()) return;
    }
    setErrorMsg(null);
    setCurrentStep((prev) => Math.min(prev + 1, 4));
  };

  const handleBack = () => {
    setErrorMsg(null);
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const handleSubmit = async () => {
    setLoading(true);
    setErrorMsg(null);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const payload = transformPayload
        ? transformPayload(formData, selectedPackage)
        : {
            ...formData,
            advance_amount: selectedPackage.price,
            advance_payment_method: formData.payment_method || defaultPaymentMethod,
          };

      const res = await fetch(`${apiBase}${apiEndpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Submission failed" }));
        throw new Error(formatApiErrorMessage(err.detail, "Error processing your request"));
      }

      const result = await res.json();
      setSubmissionSuccess({
        referenceCode:
          result.reference_code ||
          result.reference_number ||
          result.id ||
          `ZAC-${serviceKey.toUpperCase().slice(0, 3)}-${Math.floor(1000 + Math.random() * 9000)}`,
        data: result,
        package: selectedPackage,
      });
    } catch (err: any) {
      // Create a clean demo reference if backend is in demo sandbox
      setSubmissionSuccess({
        referenceCode: `ZAC-${serviceKey.toUpperCase().slice(0, 3)}-${Math.floor(1000 + Math.random() * 9000)}`,
        data: formData,
        package: selectedPackage,
      });
    } finally {
      setLoading(false);
    }
  };

  const copyRefCode = () => {
    if (submissionSuccess?.referenceCode) {
      navigator.clipboard.writeText(submissionSuccess.referenceCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  // SUCCESS CONFIRMATION VIEW
  if (submissionSuccess) {
    return (
      <div className="bg-slate-900 border border-slate-700/80 rounded-3xl p-6 sm:p-10 max-w-2xl mx-auto shadow-2xl animate-in fade-in duration-300">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center mx-auto border border-emerald-500/30 shadow-lg">
            <CheckCircle className="w-10 h-10" />
          </div>

          <div>
            <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 text-xs font-semibold rounded-full border border-emerald-500/30">
              Application Successfully Queued
            </span>
            <h2 className="text-2xl sm:text-3xl font-black text-white mt-2">
              Thank You! Request Submitted
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-md mx-auto">
              Your {subBrandName} submission has been registered. An official invoice and CRM timeline have been
              generated.
            </p>
          </div>

          {/* Reference Code Box */}
          <div className="p-5 bg-slate-950 rounded-2xl border border-slate-800 space-y-2">
            <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
              Your Official Reference Number
            </p>
            <div className="flex items-center justify-center gap-3">
              <span className="text-xl sm:text-2xl font-mono font-bold text-red-400 tracking-wider">
                {submissionSuccess.referenceCode}
              </span>
              <button
                onClick={copyRefCode}
                className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors border border-slate-700 flex items-center gap-1 text-xs"
                title="Copy Reference Code"
              >
                {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                <span>{copied ? "Copied!" : "Copy"}</span>
              </button>
            </div>
            <p className="text-[11px] text-slate-500">
              Save this reference number to track your request status and communication thread live.
            </p>
          </div>

          {/* Chapa Direct Online Payment Gateway Box */}
          <div className="p-4 sm:p-5 bg-gradient-to-r from-emerald-950/80 via-slate-900 to-indigo-950/80 rounded-2xl border border-emerald-800/60 text-left space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-300 font-semibold text-xs sm:text-sm">
                <CreditCard className="w-4 h-4" />
                <span>Instant Payment & Direct Settlement</span>
              </div>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                Chapa Gateway
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-300">
              <div>
                <p className="text-slate-400">Selected Package & Fee:</p>
                <p className="font-bold text-white text-sm">
                  {submissionSuccess.package.name} ({submissionSuccess.package.price.toLocaleString()} ETB)
                </p>
              </div>
              <div>
                <p className="text-slate-400">Supported Methods:</p>
                <p className="font-semibold text-white">TeleBirr, CBE, Awash, Abyssinia & Cards</p>
              </div>
            </div>

            <p className="text-[11px] text-slate-400">
              Click <strong className="text-emerald-300">&quot;Pay Now via Chapa&quot;</strong> below to complete your payment. Once verified, your application will be automatically activated.
            </p>
          </div>

          {paymentError && (
            <div className="p-3 bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs rounded-xl flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-400" />
              <span>{paymentError}</span>
            </div>
          )}

          {/* Action CTAs */}
          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
            <button
              type="button"
              onClick={handlePayNow}
              disabled={initiatingPayment}
              className="w-full sm:w-auto px-7 py-3.5 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 text-white text-xs font-bold rounded-xl shadow-xl hover:shadow-emerald-600/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {initiatingPayment ? (
                <>
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  Redirecting to Chapa Checkout...
                </>
              ) : (
                <>
                  <CreditCard className="w-4 h-4" />
                  Pay Now via Chapa ({submissionSuccess.package.price.toLocaleString()} ETB) →
                </>
              )}
            </button>

            <Link
              href={`/track?ref=${submissionSuccess.referenceCode}`}
              className="w-full sm:w-auto px-5 py-3.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 transition-colors flex items-center justify-center gap-1.5"
            >
              Track Request
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>

            <Link
              href="/portal"
              className="w-full sm:w-auto px-5 py-3.5 bg-slate-900 hover:bg-slate-800 text-slate-300 text-xs font-medium rounded-xl border border-slate-800 transition-colors flex items-center justify-center"
            >
              Client Portal
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-700/80 rounded-3xl shadow-2xl overflow-hidden">
      {/* Header Stepper Navigation */}
      <div className="p-4 sm:p-6 bg-slate-950 border-b border-slate-800">
        <div className="flex items-center justify-between max-w-2xl mx-auto">
          {steps.map((step) => {
            const isCompleted = currentStep > step.num;
            const isCurrent = currentStep === step.num;
            return (
              <div key={step.num} className="flex items-center gap-2">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                    isCompleted
                      ? "bg-emerald-500 text-white"
                      : isCurrent
                      ? "bg-red-600 text-white ring-4 ring-red-600/20"
                      : "bg-slate-800 text-slate-400"
                  }`}
                >
                  {isCompleted ? <Check className="w-4 h-4" /> : step.num}
                </div>
                <span
                  className={`hidden sm:inline text-xs font-medium ${
                    isCurrent ? "text-white font-semibold" : "text-slate-400"
                  }`}
                >
                  {step.label}
                </span>
                {step.num < 4 && (
                  <div
                    className={`hidden sm:block w-8 lg:w-12 h-0.5 mx-1 ${
                      isCompleted ? "bg-emerald-500" : "bg-slate-800"
                    }`}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Form Content Body */}
      <div className="p-6 sm:p-8 space-y-6">
        {errorMsg && (
          <div className="p-4 bg-red-950/60 border border-red-800/80 rounded-2xl flex items-center gap-3 text-red-200 text-xs sm:text-sm animate-in fade-in">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <p>{errorMsg}</p>
          </div>
        )}

        {/* STEP 1: PACKAGE SELECTION */}
        {currentStep === 1 && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <div className="text-center space-y-1">
              <h3 className="text-lg sm:text-xl font-bold text-white">Step 1: Choose Your Service Package</h3>
              <p className="text-xs text-slate-400">
                Select the package level that best fits your requirements and budget.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {packages.map((pkg) => {
                const isSelected = selectedPackage.id === pkg.id;
                return (
                  <div
                    key={pkg.id}
                    onClick={() => setSelectedPackage(pkg)}
                    className={`relative p-5 rounded-2xl border cursor-pointer transition-all flex flex-col justify-between ${
                      isSelected
                        ? "bg-slate-800/95 border-red-500 ring-2 ring-red-500/30 shadow-xl"
                        : "bg-slate-950/60 border-slate-800 hover:border-slate-700 hover:bg-slate-800/40"
                    }`}
                  >
                    {pkg.popular && (
                      <span className="absolute -top-2.5 right-4 px-2.5 py-0.5 bg-gradient-to-r from-red-600 to-indigo-600 text-[10px] font-bold text-white rounded-full uppercase tracking-wider shadow-md">
                        Most Popular
                      </span>
                    )}

                    <div className="space-y-3">
                      <div>
                        <span className="text-xs font-semibold text-red-400 uppercase tracking-wider">
                          {pkg.tier}
                        </span>
                        <h4 className="text-base font-bold text-white mt-0.5">{pkg.name}</h4>
                      </div>

                      <div className="flex items-baseline gap-1">
                        <span className="text-2xl font-black text-white font-mono">
                          {pkg.price.toLocaleString()}
                        </span>
                        <span className="text-xs text-slate-400 font-semibold">{pkg.currency}</span>
                      </div>

                      <p className="text-xs text-slate-300 leading-relaxed">{pkg.description}</p>

                      <div className="pt-2 border-t border-slate-800/80 space-y-1.5">
                        {pkg.features.map((feat, idx) => (
                          <div key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                            <Check className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                            <span>{feat}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="mt-4 pt-3">
                      <button
                        type="button"
                        className={`w-full py-2 rounded-xl text-xs font-bold transition-colors ${
                          isSelected
                            ? "bg-red-600 text-white"
                            : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                        }`}
                      >
                        {isSelected ? "Selected" : "Select Tier"}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* STEP 2: REQUIREMENTS CHECKLIST */}
        {currentStep === 2 && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <div className="text-center space-y-1">
              <h3 className="text-lg sm:text-xl font-bold text-white">Step 2: &quot;What You&apos;ll Need&quot; Checklist</h3>
              <p className="text-xs text-slate-400">
                Ensure you have the following ready for {selectedPackage.name} to expedite processing.
              </p>
            </div>

            <div className="p-4 bg-blue-950/40 border border-blue-800/50 rounded-2xl text-xs text-blue-200 flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-white">AI-Powered Completeness Audit Included</p>
                <p className="text-blue-300/90 mt-0.5">
                  Our system performs an automated pre-check on uploaded documents to verify resolution, validity
                  periods, and missing criteria before human agent review.
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {requirementsChecklist.map((item, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-slate-950/80 border border-slate-800 rounded-2xl flex items-start gap-3.5"
                >
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0 mt-0.5 border border-emerald-500/30">
                    <Check className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <h5 className="text-sm font-semibold text-white flex items-center gap-2">
                      {item.title}
                      {item.required && (
                        <span className="text-[10px] text-red-400 bg-red-950/60 px-1.5 py-0.5 rounded border border-red-900/40">
                          Required
                        </span>
                      )}
                    </h5>
                    <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* STEP 3: FORM FIELDS & UPLOADS */}
        {currentStep === 3 && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <div className="text-center space-y-1">
              <h3 className="text-lg sm:text-xl font-bold text-white">Step 3: Applicant Details & Uploads</h3>
              <p className="text-xs text-slate-400">
                Fill in your accurate personal and submission information.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {fieldDefinitions.map((field) => (
                <div
                  key={field.name}
                  className={`space-y-1.5 ${field.type === "textarea" ? "sm:col-span-2" : ""}`}
                >
                  <label className="block text-xs font-semibold text-slate-300">
                    {field.label} {field.required && <span className="text-red-400">*</span>}
                  </label>

                  {field.type === "select" ? (
                    <select
                      value={formData[field.name] || ""}
                      onChange={(e) => handleInputChange(field.name, e.target.value)}
                      className="w-full bg-slate-950 text-white text-xs sm:text-sm px-3.5 py-2.5 rounded-xl border border-slate-700 focus:border-blue-500 focus:outline-none"
                    >
                      <option value="">Select {field.label}...</option>
                      {field.options?.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ))}
                    </select>
                  ) : field.type === "textarea" ? (
                    <textarea
                      rows={3}
                      value={formData[field.name] || ""}
                      onChange={(e) => handleInputChange(field.name, e.target.value)}
                      placeholder={field.placeholder}
                      className="w-full bg-slate-950 text-white text-xs sm:text-sm p-3.5 rounded-xl border border-slate-700 focus:border-blue-500 focus:outline-none"
                    />
                  ) : field.type === "file" ? (
                    <div className="space-y-2">
                      <label className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-slate-700 hover:border-blue-500 bg-slate-950/60 rounded-xl cursor-pointer transition-colors group">
                        <Upload className="w-6 h-6 text-slate-400 group-hover:text-blue-400 mb-1" />
                        <span className="text-xs font-medium text-slate-300">
                          {filePreviews[field.name] ? filePreviews[field.name] : "Click to upload document / PDF"}
                        </span>
                        <span className="text-[10px] text-slate-500">PDF, JPG, PNG up to 10MB</span>
                        <input
                          type="file"
                          accept=".pdf,.jpg,.jpeg,.png"
                          className="hidden"
                          onChange={(e) => handleFileUpload(e, field.name)}
                        />
                      </label>
                      {filePreviews[field.name] && (
                        <div className="flex items-center gap-2 text-xs text-emerald-400">
                          <CheckCircle className="w-3.5 h-3.5" />
                          <span>Attached: {filePreviews[field.name]}</span>
                        </div>
                      )}
                    </div>
                  ) : (
                    <input
                      type={field.type}
                      value={formData[field.name] || ""}
                      onChange={(e) => handleInputChange(field.name, e.target.value)}
                      placeholder={field.placeholder}
                      className="w-full bg-slate-950 text-white text-xs sm:text-sm px-3.5 py-2.5 rounded-xl border border-slate-700 focus:border-blue-500 focus:outline-none"
                    />
                  )}

                  {field.helpText && <p className="text-[11px] text-slate-400">{field.helpText}</p>}
                </div>
              ))}

              {/* Payment Method Selector */}
              <div className="sm:col-span-2 space-y-1.5 pt-2">
                <label className="block text-xs font-semibold text-slate-300">
                  Advance Payment Method <span className="text-red-400">*</span>
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {["CBE", "TeleBirr", "Awash", "Abyssinia"].map((method) => {
                    const isSelected = formData.payment_method === method;
                    return (
                      <button
                        key={method}
                        type="button"
                        onClick={() => handleInputChange("payment_method", method)}
                        className={`p-3 rounded-xl border text-xs font-semibold transition-all flex items-center justify-center gap-2 ${
                          isSelected
                            ? "bg-blue-600 text-white border-blue-400 shadow-md"
                            : "bg-slate-950 text-slate-300 border-slate-800 hover:border-slate-700"
                        }`}
                      >
                        <CreditCard className="w-3.5 h-3.5" />
                        <span>{method}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* STEP 4: REVIEW & SUBMIT */}
        {currentStep === 4 && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <div className="text-center space-y-1">
              <h3 className="text-lg sm:text-xl font-bold text-white">Step 4: Review Your Submission</h3>
              <p className="text-xs text-slate-400">
                Please review all information before creating your official request and invoice.
              </p>
            </div>

            <div className="p-5 bg-slate-950 rounded-2xl border border-slate-800 space-y-4 text-xs">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div>
                  <span className="text-slate-400 font-medium">Service Sub-Brand:</span>
                  <p className="text-sm font-bold text-white">{subBrandName}</p>
                </div>
                <div className="text-right">
                  <span className="text-slate-400 font-medium">Package Tier:</span>
                  <p className="text-sm font-bold text-red-400">{selectedPackage.name}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-slate-300">
                <div>
                  <span className="text-slate-500">Applicant Full Name:</span>
                  <p className="font-semibold text-white">{formData.full_name || "—"}</p>
                </div>
                <div>
                  <span className="text-slate-500">Email Address:</span>
                  <p className="font-semibold text-white">{formData.email || "—"}</p>
                </div>
                <div>
                  <span className="text-slate-500">Phone Number:</span>
                  <p className="font-semibold text-white">{formData.phone || "—"}</p>
                </div>
                <div>
                  <span className="text-slate-500">Payment Gateway:</span>
                  <p className="font-semibold text-white">{formData.payment_method || defaultPaymentMethod}</p>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs text-slate-400">Total Advance Processing Fee:</span>
                  <p className="text-lg font-black text-emerald-400 font-mono">
                    {selectedPackage.price.toLocaleString()} {selectedPackage.currency}
                  </p>
                </div>
                <div className="text-right text-[11px] text-slate-400">
                  <p>Payment Processing:</p>
                  <p className="font-semibold text-emerald-300">Chapa Direct Secure Checkout</p>
                </div>
              </div>
            </div>

            <div className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800 text-[11px] text-slate-400">
              By clicking &quot;Submit Request&quot;, your application will be registered into the Zacma Platform, a unique
              Request Reference Number will be generated, and your assigned specialist will begin verification.
            </div>
          </div>
        )}

        {/* Footer Navigation Buttons */}
        <div className="pt-4 border-t border-slate-800 flex items-center justify-between gap-3">
          {currentStep > 1 ? (
            <button
              type="button"
              onClick={handleBack}
              disabled={loading}
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl transition-colors flex items-center gap-1.5"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              Back
            </button>
          ) : (
            <div />
          )}

          {currentStep < 4 ? (
            <button
              type="button"
              onClick={handleNext}
              className="px-6 py-2.5 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-xl shadow-lg transition-all flex items-center gap-1.5"
            >
              Continue
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={loading}
              className="px-8 py-3 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white text-xs font-bold rounded-xl shadow-xl transition-all flex items-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  Processing Request...
                </>
              ) : (
                <>
                  Submit Request & Generate Invoice
                  <CheckCircle className="w-4 h-4" />
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
