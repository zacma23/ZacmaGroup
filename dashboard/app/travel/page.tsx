"use client";

import React, { useEffect, useState } from "react";
import MultiStepForm, { FormFieldDef, PackageTier } from "../../components/MultiStepForm";
import { Plane, Calendar, Hotel, CheckCircle2, MapPin, Compass, ShieldCheck } from "lucide-react";

const DEFAULT_TRAVEL_PACKAGES: PackageTier[] = [
  {
    id: "pkg-trv-std",
    name: "Standard Booking",
    tier: "Standard",
    price: 3500,
    currency: "ETB",
    description: "Direct flight ticketing and verified hotel accommodation bookings.",
    features: [
      "Best flight fare search & ticketing",
      "Hotel booking with free cancellation options",
      "E-ticket issuance & confirmation",
    ],
    popular: false,
  },
  {
    id: "pkg-trv-itinerary",
    name: "Full 5-Day Itinerary",
    tier: "Full Itinerary",
    price: 8000,
    currency: "ETB",
    description: "Personalized day-by-day travel plan, tours, airport transfers, and activity bookings.",
    features: [
      "Customized 5-day daily travel itinerary",
      "Airport transfers and ground transit planning",
      "Guided tour & landmark ticket reservations",
      "24/7 emergency travel helpline",
    ],
    popular: true,
  },
  {
    id: "pkg-trv-vip",
    name: "VIP Concierge",
    tier: "VIP",
    price: 15000,
    currency: "ETB",
    description: "Luxury travel concierge with premium lounge access, 5-star hotels, and dedicated agent.",
    features: [
      "5-Star hotel suites & business class coordination",
      "VIP airport lounge passes",
      "Private chauffeur & bespoke experiences",
      "Dedicated travel concierge manager",
    ],
    popular: false,
  },
];

const TRAVEL_CHECKLIST = [
  {
    title: "Passport Scan / ID",
    desc: "Valid passport or national identification of all traveling passengers.",
    required: true,
  },
  {
    title: "Target Destination & Dates",
    desc: "Preferred departure dates, return timeline, and target destinations.",
    required: true,
  },
  {
    title: "Budget & Accommodation Preference",
    desc: "Estimated overall budget, hotel star rating (3-star, 4-star, 5-star), and room preferences.",
    required: true,
  },
  {
    title: "Special Needs / Group Size",
    desc: "Dietary restrictions, infant seats, wheelchair assistance, or group tour requirements.",
    required: false,
  },
];

const TRAVEL_FIELDS: FormFieldDef[] = [
  { name: "full_name", label: "Lead Traveler Full Name", type: "text", placeholder: "e.g. Dawit Tesfaye", required: true },
  { name: "email", label: "Email Address", type: "email", placeholder: "dawit@example.com", required: true },
  { name: "phone", label: "Phone Number", type: "tel", placeholder: "+251 91 123 4567", required: true },
  { name: "address", label: "Current Residence / City", type: "text", placeholder: "Bole, Addis Ababa", required: true },
  {
    name: "destination_country",
    label: "Destination & Cities",
    type: "select",
    options: ["UAE (Dubai & Abu Dhabi)", "Turkey (Istanbul & Antalya)", "Zanzibar & Tanzania", "Egypt (Cairo & Red Sea)", "Kenya (Nairobi & Mombasa)", "Thailand (Bangkok & Phuket)", "Europe Multi-City", "Domestic Ethiopia (Lalibela/Gondar/Bale)"],
    required: true,
  },
  {
    name: "travel_date_preference",
    label: "Preferred Travel Dates",
    type: "text",
    placeholder: "e.g. October 15 - October 22, 2026",
    required: true,
  },
  {
    name: "budget",
    label: "Estimated Total Travel Budget (ETB or USD)",
    type: "number",
    placeholder: "e.g. 50000",
    required: true,
  },
  {
    name: "passport_upload_url",
    label: "Upload Passport Copy (PDF / Image)",
    type: "file",
    required: false,
    helpText: "Clear photo page of traveler's passport.",
  },
];

export default function TravelPage() {
  const [packages, setPackages] = useState<PackageTier[]>(DEFAULT_TRAVEL_PACKAGES);

  useEffect(() => {
    const fetchPackages = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
        const res = await fetch(`${apiBase}/api/v1/support/packages?service=travel`);
        if (res.ok) {
          const data = await res.json();
          if (data.travel && Array.isArray(data.travel)) {
            setPackages(data.travel);
          }
        }
      } catch (e) {
        // Fallback to DEFAULT_TRAVEL_PACKAGES
      }
    };
    fetchPackages();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Header Banner */}
      <div className="text-center space-y-4 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-950/70 border border-blue-800/60 text-blue-300 text-xs font-semibold">
          <Plane className="w-3.5 h-3.5 text-blue-400" />
          <span>ZACMA TRAVEL AGENT · FLIGHTS, ITINERARIES & HOTEL PACKAGES</span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
          Personal & Corporate Travel Management
        </h1>

        <p className="text-xs sm:text-base text-slate-300 leading-relaxed">
          From flight bookings with leading international carriers to curated 5-day holiday itineraries and luxury
          hotel reservations in Dubai, Istanbul, Zanzibar, and beyond.
        </p>

        {/* Feature badges */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2 text-xs text-slate-300">
          <span className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Best Price Guarantee
          </span>
          <span className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
            <Calendar className="w-4 h-4 text-blue-400" /> Custom 5-Day Itineraries
          </span>
          <span className="flex items-center gap-1.5 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
            <Hotel className="w-4 h-4 text-purple-400" /> Verified 4 & 5-Star Stays
          </span>
        </div>
      </div>

      {/* Multi-Step Application Form */}
      <div className="max-w-4xl mx-auto">
        <MultiStepForm
          serviceKey="travel"
          serviceTitle="Travel Agent"
          subBrandName="Zacma Travel Agent"
          accentColor="blue"
          packages={packages}
          requirementsChecklist={TRAVEL_CHECKLIST}
          fieldDefinitions={TRAVEL_FIELDS}
          apiEndpoint="/api/v1/travel/requests"
          transformPayload={(formData, selectedPkg) => ({
            full_name: formData.full_name,
            email: formData.email,
            phone: formData.phone,
            address: formData.address,
            destination_country: formData.destination_country || "Dubai, UAE",
            travel_date_preference: formData.travel_date_preference || "Flexible",
            budget: Number(formData.budget) || selectedPkg.price,
            advance_payment_method: formData.payment_method || "Awash",
            advance_amount: selectedPkg.price,
            notes: `${selectedPkg.name} package selected.`,
          })}
        />
      </div>
    </div>
  );
}
