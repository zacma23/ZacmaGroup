"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  GraduationCap,
  Wrench,
  CheckCircle2,
  Calendar,
  Clock,
  Building,
  CreditCard,
  ArrowRight,
  ShieldCheck,
  Award,
  BookOpen,
  Sparkles,
  Layers,
  AlertCircle,
} from "lucide-react";

interface CourseDef {
  id: string;
  name: string;
  category: string;
  description: string;
  specialties?: {
    id: string;
    name: string;
    description: string;
    schedules: { id: string; label: string; days: string[] }[];
    time_slots: string[];
  }[];
}

const OFFICIAL_COURSES: CourseDef[] = [
  { id: "basic_computer", name: "Basic Computer", category: "General IT", description: "Fundamentals of computing, Windows OS, Office Suite & Internet productivity." },
  { id: "graphics", name: "Graphics", category: "Design", description: "Photoshop, Illustrator, vector branding & visual communication." },
  { id: "video_editing", name: "Video Editing", category: "Media", description: "Premiere Pro, DaVinci Resolve, motion graphics & color grading." },
  { id: "videography", name: "Videography", category: "Media", description: "Studio camera setups, lighting, composition & audio recording." },
  { id: "photography", name: "Photography", category: "Media", description: "DSLR photography, studio lighting & professional portraiture." },
  { id: "ai", name: "AI", category: "Emerging Tech", description: "Applied Artificial Intelligence, prompt engineering & automation workflows." },
  { id: "cloud_computing", name: "Cloud Computing", category: "Cloud & Infra", description: "AWS, Docker containers, Azure & modern DevOps fundamentals." },
  { id: "spoken_english", name: "Spoken English", category: "Languages", description: "Workplace English communication, presentation skills & fluency." },
  { id: "accounting", name: "Accounting", category: "Business", description: "Financial accounting principles, computerized accounting & payroll." },
  { id: "it_support", name: "IT Support", category: "Technical", description: "Helpdesk diagnostics, OS troubleshooting & hardware support." },
  { id: "autocad", name: "AutoCAD", category: "Engineering", description: "2D Drafting, architectural layouts & 3D CAD modeling." },
  { id: "etabs", name: "ETABS", category: "Engineering", description: "Structural analysis, reinforced concrete & steel building design." },
  { id: "web_design", name: "Web Design", category: "Software", description: "HTML5, Tailwind CSS, JavaScript & responsive UI/UX." },
  { id: "networking", name: "Networking", category: "Technical", description: "Cisco routing, switching, IP subnetting & network security." },
  {
    id: "maintenance",
    name: "Maintenance",
    category: "Hardware & Repair",
    description: "Component-level hardware diagnostics, device repair & maintenance.",
    specialties: [
      {
        id: "hardware_specialty",
        name: "Hardware Specialty",
        description: "Component diagnostics, motherboard repair, PCB soldering, hardware assembly & firmware flashing.",
        schedules: [
          {
            id: "sch_1",
            label: "Monday + Wednesday + Thursday",
            days: ["Monday", "Wednesday", "Thursday"],
          },
          {
            id: "sch_2",
            label: "Tuesday + Thursday + Saturday",
            days: ["Tuesday", "Thursday", "Saturday"],
          },
          {
            id: "sch_3",
            label: "Saturday + Sunday",
            days: ["Saturday", "Sunday"],
          },
        ],
        time_slots: [
          "03:00 – 05:00",
          "05:00 – 07:00",
          "07:00 – 09:00",
          "09:00 – 11:00",
          "11:00 – 01:00",
          "12:00 – 02:00",
        ],
      },
    ],
  },
];

const STANDARD_SCHEDULES = [
  "Monday, Wednesday & Friday (Weekday Morning)",
  "Tuesday, Thursday & Saturday (Weekday Afternoon)",
  "Saturday & Sunday (Weekend Intensive)",
];

const STANDARD_TIME_SLOTS = [
  "08:30 AM – 11:30 AM",
  "02:00 PM – 05:00 PM",
  "05:30 PM – 08:00 PM (Evening)",
];

const TUITION_PACKAGES = [
  { id: "single", name: "Single Course", price: 4500, desc: "Standard 6-week accredited training with practical lab sessions." },
  { id: "bundle", name: "Professional Bundle", price: 8000, desc: "Dual-course package with 15% discount and career guidance." },
  { id: "career_track", name: "Full Career Track", price: 14000, desc: "Complete certification track with 1-on-1 mentorship and job referrals." },
];

function formatApiErrorMessage(errDetail: any, fallback: string = "Registration failed. Please check your details and try again."): string {
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

export default function TrainingPage() {
  const [selectedCourse, setSelectedCourse] = useState<string>("Maintenance");
  const [selectedSpecialty, setSelectedSpecialty] = useState<string>("Hardware Specialty");
  const [selectedSchedule, setSelectedSchedule] = useState<string>("Monday + Wednesday + Thursday");
  const [selectedTimeSlot, setSelectedTimeSlot] = useState<string>("03:00 – 05:00");
  const [selectedPackage, setSelectedPackage] = useState<string>("single");
  const [paymentMethod, setPaymentMethod] = useState<string>("CBE");

  // Student profile form state
  const [fullName, setFullName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [phone, setPhone] = useState<string>("");
  const [address, setAddress] = useState<string>("Addis Ababa");
  const [educationLevel, setEducationLevel] = useState<string>("Diploma / TVET");

  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successResult, setSuccessResult] = useState<any | null>(null);
  const [initiatingPayment, setInitiatingPayment] = useState<boolean>(false);
  const [paymentError, setPaymentError] = useState<string | null>(null);

  const currentCourseObj = OFFICIAL_COURSES.find((c) => c.name.toLowerCase() === selectedCourse.toLowerCase()) || OFFICIAL_COURSES[14];
  const isMaintenance = selectedCourse.toLowerCase() === "maintenance";

  const handlePayNowTraining = async () => {
    if (!successResult) return;
    setInitiatingPayment(true);
    setPaymentError(null);

    const activePkg = TUITION_PACKAGES.find((p) => p.id === selectedPackage) || TUITION_PACKAGES[0];
    const refCode = successResult.reference_code || successResult.id;

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/api/v1/payments/transactions/initialize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          amount: activePkg.price,
          provider_code: "chapa",
          customer_name: successResult.full_name || fullName || "Student",
          customer_email: successResult.email || email || "student@zacmaa.net",
          customer_phone: successResult.phone || phone,
          currency: "ETB",
          payment_purpose: `Academy Course: ${successResult.course}`,
          description: `Tuition Fee for ${refCode}`,
          return_url: `${typeof window !== "undefined" ? window.location.origin : "http://localhost:3000"}/portal?payment_status=success&ref=${encodeURIComponent(refCode)}`,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(formatApiErrorMessage(data?.detail, "Failed to initialize Chapa payment checkout"));
      }

      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error("No checkout URL returned from payment gateway");
      }
    } catch (err: any) {
      setPaymentError(err.message || "Could not connect to Chapa payment gateway. Please try again.");
    } finally {
      setInitiatingPayment(false);
    }
  };

  const handleCourseChange = (courseName: string) => {
    setSelectedCourse(courseName);
    if (courseName.toLowerCase() === "maintenance") {
      setSelectedSpecialty("Hardware Specialty");
      setSelectedSchedule("Monday + Wednesday + Thursday");
      setSelectedTimeSlot("03:00 – 05:00");
    } else {
      setSelectedSpecialty("");
      setSelectedSchedule(STANDARD_SCHEDULES[0]);
      setSelectedTimeSlot(STANDARD_TIME_SLOTS[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName || !email || !phone) {
      setErrorMsg("Please fill in your name, email, and phone number.");
      return;
    }
    if (!selectedSchedule || !selectedTimeSlot) {
      setErrorMsg("Please select an available schedule and time slot.");
      return;
    }

    setLoading(true);
    setErrorMsg(null);

    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    const payload = {
      full_name: fullName.trim(),
      email: email.trim(),
      phone: phone.trim(),
      address: address.trim() || "Addis Ababa",
      education_level: educationLevel,
      course: selectedCourse,
      specialty: isMaintenance ? selectedSpecialty : null,
      maintenance_sub_type: isMaintenance ? selectedSpecialty : null,
      schedule: selectedSchedule,
      time_slot: selectedTimeSlot,
      time: selectedTimeSlot,
      payment_method: paymentMethod,
      interests: `${selectedCourse} - ${selectedSpecialty || ""} (Schedule: ${selectedSchedule}, Time: ${selectedTimeSlot})`,
    };

    try {
      const res = await fetch(`${apiBase}/api/v1/students/registrations`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(formatApiErrorMessage(data?.detail, "Registration failed. Please verify your form entries."));
      }

      setSuccessResult(data);
    } catch (err: any) {
      setErrorMsg(err.message || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (successResult) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16">
        <div className="bg-slate-900 border border-emerald-500/40 rounded-3xl p-8 sm:p-10 shadow-2xl space-y-6">
          <div className="flex items-center gap-3 text-emerald-400">
            <CheckCircle2 className="w-8 h-8 flex-shrink-0" />
            <div>
              <h2 className="text-2xl font-bold text-white">Student Registration Submitted!</h2>
              <p className="text-xs text-slate-400">Your enrollment is in Pending status awaiting fee verification.</p>
            </div>
          </div>

          <div className="p-4 bg-slate-950 rounded-2xl border border-slate-800 space-y-3 text-sm">
            <div className="flex justify-between items-center border-b border-slate-800/80 pb-2">
              <span className="text-slate-400">Registration Code:</span>
              <span className="font-mono font-bold text-amber-400 text-base">{successResult.reference_code || successResult.id}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Student Name:</span>
              <span className="text-white font-medium">{successResult.full_name}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Course:</span>
              <span className="text-emerald-300 font-bold">{successResult.course}</span>
            </div>
            {successResult.specialty && (
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Specialty:</span>
                <span className="text-amber-300 font-semibold">{successResult.specialty}</span>
              </div>
            )}
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Selected Schedule:</span>
              <span className="text-blue-300 font-medium">{successResult.schedule || selectedSchedule}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Selected Time:</span>
              <span className="text-emerald-400 font-medium">{successResult.time_slot || successResult.time || selectedTimeSlot}</span>
            </div>
            <div className="flex justify-between items-center pt-2 border-t border-slate-800/80">
              <span className="text-slate-400">Status:</span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                {successResult.status || "Pending"}
              </span>
            </div>
          </div>

          {/* Chapa Direct Online Payment Gateway Box */}
          <div className="p-5 rounded-2xl bg-gradient-to-r from-emerald-950/80 via-slate-900 to-indigo-950/80 border border-emerald-800/60 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-300 font-semibold text-xs sm:text-sm">
                <CreditCard className="w-4 h-4" />
                <span>Tuition Payment & Instant Enrollment</span>
              </div>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                Chapa Gateway
              </span>
            </div>

            <p className="text-xs text-slate-300">
              Complete your tuition via <strong className="text-white">TeleBirr, CBE, Awash Bank, Bank of Abyssinia, or Cards</strong>. Your student seat is reserved immediately upon payment verification.
            </p>

            {paymentError && (
              <div className="p-3 bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs rounded-xl flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-400" />
                <span>{paymentError}</span>
              </div>
            )}
          </div>

          <div className="flex flex-col sm:flex-row gap-3 pt-2">
            <button
              type="button"
              onClick={handlePayNowTraining}
              disabled={initiatingPayment}
              className="flex-1 py-3.5 px-6 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 text-white font-bold text-center rounded-xl text-xs sm:text-sm transition shadow-xl hover:shadow-emerald-600/30 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {initiatingPayment ? (
                <>
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  Redirecting to Chapa Checkout...
                </>
              ) : (
                <>
                  <CreditCard className="w-4 h-4" />
                  Pay Tuition Now via Chapa →
                </>
              )}
            </button>

            <Link
              href="/portal"
              className="py-3.5 px-4 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-center rounded-xl text-xs sm:text-sm transition"
            >
              Client Portal
            </Link>

            <Link
              href="/track"
              className="py-3.5 px-4 bg-slate-900 hover:bg-slate-800 text-slate-400 font-medium text-center rounded-xl text-xs sm:text-sm border border-slate-800 transition"
            >
              Track Status
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Header Banner */}
      <div className="text-center space-y-4 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/70 border border-emerald-800/60 text-emerald-300 text-xs font-semibold">
          <GraduationCap className="w-3.5 h-3.5 text-emerald-400" />
          <span>ZACMA TRAINING INSTITUTE · ACCREDITED PRACTICAL CAREER PROGRAMS</span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
          Practical Technology & Career Training
        </h1>

        <p className="text-xs sm:text-base text-slate-300 leading-relaxed">
          Master hands-on industry skills across 15 accredited training programs — from Software, AI, and Media to
          our specialized <strong className="text-emerald-300">Maintenance: Hardware Specialty</strong>.
        </p>

        {/* Feature badges */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2 text-xs text-slate-300">
          <span className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
            <Award className="w-4 h-4 text-emerald-400" /> Accredited Certificates
          </span>
          <span className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
            <BookOpen className="w-4 h-4 text-blue-400" /> 80% Practical Lab Work
          </span>
          <span className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
            <CheckCircle2 className="w-4 h-4 text-purple-400" /> Structured Timetables
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Course Selector & Syllabus */}
        <div className="lg:col-span-5 space-y-6">
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-emerald-400" /> 1. Select Training Course
            </h3>

            <div className="grid grid-cols-2 gap-2 max-h-[380px] overflow-y-auto pr-1">
              {OFFICIAL_COURSES.map((c) => {
                const isSelected = selectedCourse.toLowerCase() === c.name.toLowerCase();
                return (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => handleCourseChange(c.name)}
                    className={`p-3 rounded-2xl text-left border transition ${
                      isSelected
                        ? "bg-emerald-950/60 border-emerald-500 text-white shadow-md shadow-emerald-500/10"
                        : "bg-slate-950/80 border-slate-800 text-slate-300 hover:border-slate-700"
                    }`}
                  >
                    <p className="text-xs font-bold">{c.name}</p>
                    <p className="text-[10px] text-slate-400 truncate mt-0.5">{c.category}</p>
                  </button>
                );
              })}
            </div>

            {/* Selected Course Details Card */}
            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Course Selected:</span>
                <span className="font-bold text-white text-sm">{currentCourseObj.name}</span>
              </div>
              <p className="text-slate-300 leading-relaxed">{currentCourseObj.description}</p>

              {isMaintenance && (
                <div className="mt-3 p-3 rounded-xl bg-amber-950/30 border border-amber-900/50 space-y-1">
                  <div className="flex items-center gap-1.5 text-amber-400 font-bold">
                    <Wrench className="w-3.5 h-3.5" />
                    <span>Specialty: Hardware Specialty</span>
                  </div>
                  <p className="text-[11px] text-slate-300">
                    Component-level hardware diagnostics, PCB soldering, logic board troubleshooting, hardware assembly & firmware flashing.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Pricing & Tuition Packages */}
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 space-y-3 shadow-xl">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-amber-400" /> Tuition Tier
            </h3>
            <div className="space-y-2">
              {TUITION_PACKAGES.map((pkg) => (
                <label
                  key={pkg.id}
                  className={`flex items-center justify-between p-3 rounded-2xl border cursor-pointer transition ${
                    selectedPackage === pkg.id
                      ? "bg-amber-950/40 border-amber-500 text-white"
                      : "bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <input
                      type="radio"
                      name="tuition_pkg"
                      checked={selectedPackage === pkg.id}
                      onChange={() => setSelectedPackage(pkg.id)}
                      className="text-amber-500 focus:ring-amber-500"
                    />
                    <div>
                      <p className="text-xs font-bold text-white">{pkg.name}</p>
                      <p className="text-[11px] text-slate-400">{pkg.desc}</p>
                    </div>
                  </div>
                  <span className="font-mono font-bold text-amber-400 text-sm ml-2">{pkg.price.toLocaleString()} ETB</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Registration Form with Schedule & Time Slots */}
        <div className="lg:col-span-7">
          <form onSubmit={handleSubmit} className="p-6 sm:p-8 rounded-3xl bg-slate-900 border border-slate-800 shadow-2xl space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white">Student Registration & Timetable</h2>
              <p className="text-xs text-slate-400 mt-1">
                Select your required course specialty, schedule, and time slot.
              </p>
            </div>

            {errorMsg && (
              <div className="p-3.5 bg-rose-950/80 border border-rose-800 text-rose-200 text-xs rounded-2xl">
                {errorMsg}
              </div>
            )}

            {/* Section A: Course & Specialty Confirmation */}
            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400">Course</label>
                  <input
                    type="text"
                    readOnly
                    value={selectedCourse}
                    className="mt-1 block w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs font-bold text-emerald-400 cursor-not-allowed"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400">Specialty / Track</label>
                  <input
                    type="text"
                    readOnly
                    value={isMaintenance ? "Hardware Specialty" : "General Curriculum"}
                    className="mt-1 block w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs font-bold text-amber-400 cursor-not-allowed"
                  />
                </div>
              </div>
            </div>

            {/* Section B: Schedules Selection */}
            <div className="space-y-3">
              <label className="block text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <Calendar className="w-4 h-4 text-blue-400" /> Available Schedules
              </label>

              {isMaintenance ? (
                <div className="space-y-2">
                  {[
                    "Monday + Wednesday + Thursday",
                    "Tuesday + Thursday + Saturday",
                    "Saturday + Sunday",
                  ].map((sch) => (
                    <label
                      key={sch}
                      className={`flex items-center gap-3 p-3.5 rounded-2xl border cursor-pointer transition ${
                        selectedSchedule === sch
                          ? "bg-blue-950/50 border-blue-500 text-white shadow-md shadow-blue-500/10"
                          : "bg-slate-950/80 border-slate-800 text-slate-300 hover:border-slate-700"
                      }`}
                    >
                      <input
                        type="radio"
                        name="maintenance_schedule"
                        checked={selectedSchedule === sch}
                        onChange={() => setSelectedSchedule(sch)}
                        className="text-blue-500 focus:ring-blue-500"
                      />
                      <div>
                        <p className="text-xs font-bold text-white">{sch}</p>
                        <p className="text-[11px] text-slate-400">Fixed days schedule (No arbitrary combinations)</p>
                      </div>
                    </label>
                  ))}
                </div>
              ) : (
                <div className="space-y-2">
                  {STANDARD_SCHEDULES.map((sch) => (
                    <label
                      key={sch}
                      className={`flex items-center gap-3 p-3 rounded-2xl border cursor-pointer transition ${
                        selectedSchedule === sch
                          ? "bg-blue-950/50 border-blue-500 text-white"
                          : "bg-slate-950/80 border-slate-800 text-slate-300 hover:border-slate-700"
                      }`}
                    >
                      <input
                        type="radio"
                        name="std_schedule"
                        checked={selectedSchedule === sch}
                        onChange={() => setSelectedSchedule(sch)}
                        className="text-blue-500 focus:ring-blue-500"
                      />
                      <span className="text-xs font-medium text-slate-200">{sch}</span>
                    </label>
                  ))}
                </div>
              )}
            </div>

            {/* Section C: Time Slots Selection */}
            <div className="space-y-3">
              <label className="block text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <Clock className="w-4 h-4 text-emerald-400" /> Available Time Slots
              </label>

              {isMaintenance ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {[
                    "03:00 – 05:00",
                    "05:00 – 07:00",
                    "07:00 – 09:00",
                    "09:00 – 11:00",
                    "11:00 – 01:00",
                    "12:00 – 02:00",
                  ].map((time) => {
                    const isChosen = selectedTimeSlot === time;
                    return (
                      <button
                        key={time}
                        type="button"
                        onClick={() => setSelectedTimeSlot(time)}
                        className={`p-3 rounded-2xl text-center border font-mono transition ${
                          isChosen
                            ? "bg-emerald-950/70 border-emerald-500 text-emerald-300 font-bold shadow-md shadow-emerald-500/10"
                            : "bg-slate-950/80 border-slate-800 text-slate-300 hover:border-slate-700"
                        }`}
                      >
                        <p className="text-xs">{time}</p>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  {STANDARD_TIME_SLOTS.map((time) => {
                    const isChosen = selectedTimeSlot === time;
                    return (
                      <button
                        key={time}
                        type="button"
                        onClick={() => setSelectedTimeSlot(time)}
                        className={`p-3 rounded-2xl text-center border text-xs transition ${
                          isChosen
                            ? "bg-emerald-950/70 border-emerald-500 text-emerald-300 font-bold"
                            : "bg-slate-950/80 border-slate-800 text-slate-300 hover:border-slate-700"
                        }`}
                      >
                        {time}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Section D: Student Profile Details */}
            <div className="space-y-4 pt-2 border-t border-slate-800">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Student Personal Information
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300">Full Name *</label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Marta Gebre"
                    className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300">Email Address *</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="marta@example.com"
                    className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300">Phone Number *</label>
                  <input
                    type="tel"
                    required
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+251 92 233 4455"
                    className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300">Education Level</label>
                  <select
                    value={educationLevel}
                    onChange={(e) => setEducationLevel(e.target.value)}
                    className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="High School Complete">High School Complete</option>
                    <option value="Diploma / TVET">Diploma / TVET</option>
                    <option value="Bachelor's Degree">{"Bachelor's Degree"}</option>
                    <option value="Master's Degree">{"Master's Degree"}</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300">Payment Gateway</label>
                <select
                  value={paymentMethod}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  className="mt-1 block w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="CBE">Commercial Bank of Ethiopia (CBE)</option>
                  <option value="Chapa">Chapa Online Checkout (Cards / Wallets)</option>
                  <option value="TeleBirr">TeleBirr Mobile Money</option>
                  <option value="Awash">Awash Bank Transfer</option>
                  <option value="Abyssinia">Bank of Abyssinia</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-2xl text-sm transition flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20"
            >
              {loading ? (
                <span>Submitting Registration...</span>
              ) : (
                <>
                  <span>Submit Training Registration</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

