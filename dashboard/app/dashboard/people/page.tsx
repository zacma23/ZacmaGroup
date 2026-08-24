"use client";

import { useEffect, useState } from "react";
import {
  Users,
  Building2,
  UserCheck,
  GraduationCap,
  Briefcase,
  Search,
  Plus,
  Filter,
  Eye,
  Mail,
  Phone,
  MapPin,
  Tag,
  DollarSign,
  Clock,
  CheckCircle2,
  Calendar,
  Send,
  X,
  FileText,
  CreditCard,
  Layers,
  ArrowUpRight,
} from "lucide-react";

export default function PeoplePage() {
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

  const [activeTab, setActiveTab] = useState<"people" | "organizations">("people");
  const [people, setPeople] = useState<any[]>([]);
  const [organizations, setOrganizations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  // Detail 360 profile modal state
  const [selectedPersonId, setSelectedPersonId] = useState<string | null>(null);
  const [profileData, setProfileData] = useState<any | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);

  // New Person modal state
  const [showNewPersonModal, setShowNewPersonModal] = useState(false);
  const [newPersonForm, setNewPersonForm] = useState({
    full_name: "",
    email: "",
    phone: "",
    organization_id: "",
    job_title: "",
    person_type: "Individual",
    status: "Active",
    tags: "",
    address: "",
    city: "Addis Ababa",
    country: "Ethiopia",
    notes: "",
  });

  // New Organization modal state
  const [showNewOrgModal, setShowNewOrgModal] = useState(false);
  const [newOrgForm, setNewOrgForm] = useState({
    name: "",
    business_type: "Company",
    email: "",
    phone: "",
    website: "",
    industry: "",
    address: "Addis Ababa",
    notes: "",
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [peopleRes, orgsRes] = await Promise.all([
        fetch(`${apiBase}/api/v1/people`),
        fetch(`${apiBase}/api/v1/people/organizations/list`),
      ]);
      if (peopleRes.ok) setPeople(await peopleRes.json());
      if (orgsRes.ok) setOrganizations(await orgsRes.json());
    } catch (e) {
      console.error("Failed to load People data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const openPersonProfile = async (id: string) => {
    setSelectedPersonId(id);
    setProfileLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/v1/people/${id}/profile`);
      if (res.ok) {
        setProfileData(await res.json());
      }
    } catch (e) {
      console.error("Failed to fetch 360 profile:", e);
    } finally {
      setProfileLoading(false);
    }
  };

  const handleCreatePerson = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...newPersonForm,
        organization_id: newPersonForm.organization_id || undefined,
        tags: newPersonForm.tags ? newPersonForm.tags.split(",").map((t) => t.trim()) : [],
      };
      const res = await fetch(`${apiBase}/api/v1/people`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setShowNewPersonModal(false);
        setNewPersonForm({
          full_name: "",
          email: "",
          phone: "",
          organization_id: "",
          job_title: "",
          person_type: "Individual",
          status: "Active",
          tags: "",
          address: "",
          city: "Addis Ababa",
          country: "Ethiopia",
          notes: "",
        });
        fetchData();
      }
    } catch (e) {
      console.error("Error creating person:", e);
    }
  };

  const handleCreateOrg = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${apiBase}/api/v1/people/organizations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newOrgForm),
      });
      if (res.ok) {
        setShowNewOrgModal(false);
        setNewOrgForm({
          name: "",
          business_type: "Company",
          email: "",
          phone: "",
          website: "",
          industry: "",
          address: "Addis Ababa",
          notes: "",
        });
        fetchData();
      }
    } catch (e) {
      console.error("Error creating organization:", e);
    }
  };

  const filteredPeople = people.filter((p) => {
    const matchesType = typeFilter === "all" || (p.person_type || "").toLowerCase() === typeFilter.toLowerCase();
    const matchesStatus = statusFilter === "all" || (p.status || "").toLowerCase() === statusFilter.toLowerCase();
    const s = search.toLowerCase();
    const matchesSearch =
      !s ||
      p.full_name?.toLowerCase().includes(s) ||
      p.email?.toLowerCase().includes(s) ||
      p.phone?.includes(s) ||
      p.organization_name?.toLowerCase().includes(s) ||
      p.job_title?.toLowerCase().includes(s);
    return matchesType && matchesStatus && matchesSearch;
  });

  const filteredOrgs = organizations.filter((o) => {
    const s = search.toLowerCase();
    return !s || o.name?.toLowerCase().includes(s) || o.industry?.toLowerCase().includes(s) || o.email?.toLowerCase().includes(s);
  });

  const totalPeople = people.length;
  const totalOrgs = organizations.length;
  const customersCount = people.filter((p) => p.person_type === "Customer").length;
  const studentsCount = people.filter((p) => p.person_type === "Student" || p.tags?.includes("Student")).length;

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-blue-600/20 text-blue-400 rounded-xl border border-blue-500/30">
              <Users className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white tracking-tight">People & Organizations</h1>
              <p className="text-xs text-slate-400">Centralized contact directory, identity matching & 360° customer timelines.</p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setShowNewOrgModal(true)}
            className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition"
          >
            <Building2 className="w-3.5 h-3.5 text-blue-400" />
            <span>Add Organization</span>
          </button>
          <button
            onClick={() => setShowNewPersonModal(true)}
            className="px-4 py-2 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white rounded-xl text-xs font-bold shadow-lg shadow-red-600/20 flex items-center gap-1.5 transition"
          >
            <Plus className="w-4 h-4" />
            <span>Add Person</span>
          </button>
        </div>
      </div>

      {/* KPI Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Total Contacts</span>
            <Users className="w-4 h-4 text-blue-400" />
          </div>
          <p className="text-2xl font-black text-white mt-1">{totalPeople}</p>
          <p className="text-[11px] text-slate-400 mt-0.5">Individuals across all modules</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Organizations</span>
            <Building2 className="w-4 h-4 text-purple-400" />
          </div>
          <p className="text-2xl font-black text-white mt-1">{totalOrgs}</p>
          <p className="text-[11px] text-slate-400 mt-0.5">Registered corporate accounts</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Active Customers</span>
            <UserCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-black text-white mt-1">{customersCount}</p>
          <p className="text-[11px] text-emerald-400/80 mt-0.5">Paid & completed services</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Enrolled Students</span>
            <GraduationCap className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-black text-white mt-1">{studentsCount}</p>
          <p className="text-[11px] text-slate-400 mt-0.5">Active academy learners</p>
        </div>
      </div>

      {/* Tabs & Filters */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-1.5 p-1 bg-slate-950 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveTab("people")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                activeTab === "people" ? "bg-red-600 text-white shadow-md" : "text-slate-400 hover:text-white"
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>People Directory ({filteredPeople.length})</span>
            </button>
            <button
              onClick={() => setActiveTab("organizations")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                activeTab === "organizations" ? "bg-red-600 text-white shadow-md" : "text-slate-400 hover:text-white"
              }`}
            >
              <Building2 className="w-3.5 h-3.5" />
              <span>Organizations ({filteredOrgs.length})</span>
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <div className="relative flex-1 sm:w-64">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder={activeTab === "people" ? "Search people, email, tags..." : "Search companies, industry..."}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-slate-950 text-white text-xs pl-8 pr-3 py-2 rounded-xl border border-slate-800 focus:border-blue-500 focus:outline-none"
              />
            </div>

            {activeTab === "people" && (
              <>
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="bg-slate-950 text-slate-300 text-xs px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                >
                  <option value="all">All Types</option>
                  <option value="individual">Individual</option>
                  <option value="customer">Customer</option>
                  <option value="lead">Lead</option>
                  <option value="student">Student</option>
                  <option value="staff">Staff</option>
                  <option value="partner">Partner</option>
                </select>

                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="bg-slate-950 text-slate-300 text-xs px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                >
                  <option value="all">All Statuses</option>
                  <option value="active">Active</option>
                  <option value="lead">Lead</option>
                  <option value="prospect">Prospect</option>
                  <option value="enrolled">Enrolled</option>
                  <option value="customer">Customer</option>
                </select>
              </>
            )}
          </div>
        </div>

        {/* Content Views */}
        {loading ? (
          <div className="py-16 text-center text-slate-400 text-xs animate-pulse">Loading directory...</div>
        ) : activeTab === "people" ? (
          filteredPeople.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-xs">No people matched your search criteria.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-3">Name & Title</th>
                    <th className="py-3 px-3">Organization</th>
                    <th className="py-3 px-3">Contact Info</th>
                    <th className="py-3 px-3">Type</th>
                    <th className="py-3 px-3">Status</th>
                    <th className="py-3 px-3">Tags</th>
                    <th className="py-3 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredPeople.map((p) => (
                    <tr key={p.id} className="hover:bg-slate-800/40 transition group">
                      <td className="py-3.5 px-3">
                        <div className="font-bold text-white text-sm">{p.full_name}</div>
                        <div className="text-[11px] text-slate-400">{p.job_title || "Individual Client"}</div>
                      </td>
                      <td className="py-3.5 px-3">
                        {p.organization_name ? (
                          <span className="inline-flex items-center gap-1 text-slate-300 font-medium bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
                            <Building2 className="w-3 h-3 text-purple-400" />
                            {p.organization_name}
                          </span>
                        ) : (
                          <span className="text-slate-400">—</span>
                        )}
                      </td>
                      <td className="py-3.5 px-3 space-y-0.5">
                        <div className="flex items-center gap-1.5 text-slate-300">
                          <Mail className="w-3 h-3 text-blue-400" />
                          <span>{p.email || "No email"}</span>
                        </div>
                        {p.phone && (
                          <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                            <Phone className="w-3 h-3 text-emerald-400" />
                            <span>{p.phone}</span>
                          </div>
                        )}
                      </td>
                      <td className="py-3.5 px-3">
                        <span className="px-2.5 py-1 rounded-md text-[11px] font-semibold bg-slate-950 border border-slate-800 text-slate-300">
                          {p.person_type}
                        </span>
                      </td>
                      <td className="py-3.5 px-3">
                        <span
                          className={`px-2.5 py-1 rounded-md text-[11px] font-bold ${
                            p.status === "Active" || p.status === "Customer"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : p.status === "Lead" || p.status === "Prospect"
                              ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                              : "bg-slate-800 text-slate-300"
                          }`}
                        >
                          {p.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-3">
                        <div className="flex flex-wrap gap-1 max-w-xs">
                          {p.tags && p.tags.length > 0 ? (
                            p.tags.slice(0, 3).map((t: string, i: number) => (
                              <span key={i} className="px-2 py-0.5 bg-slate-950 rounded text-[10px] text-slate-400 border border-slate-800">
                                {t}
                              </span>
                            ))
                          ) : (
                            <span className="text-slate-400 text-[11px]">—</span>
                          )}
                        </div>
                      </td>
                      <td className="py-3.5 px-3 text-right">
                        <button
                          onClick={() => openPersonProfile(p.id)}
                          className="px-3 py-1.5 bg-blue-600/20 hover:bg-blue-600 text-blue-400 hover:text-white rounded-lg font-semibold transition flex items-center gap-1 ml-auto text-[11px] border border-blue-500/30"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>360° Profile</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : filteredOrgs.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-xs">No organizations found.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredOrgs.map((org) => (
              <div key={org.id} className="bg-slate-950 border border-slate-800 rounded-2xl p-4 space-y-3 hover:border-slate-700 transition">
                <div className="flex items-start justify-between gap-2">
                  <div className="p-2 bg-purple-600/20 text-purple-400 rounded-xl border border-purple-500/30">
                    <Building2 className="w-5 h-5" />
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-900 border border-slate-800 text-emerald-400">
                    {org.status}
                  </span>
                </div>
                <div>
                  <h3 className="font-bold text-white text-base">{org.name}</h3>
                  <p className="text-xs text-slate-400">{org.business_type} · {org.industry || "General"}</p>
                </div>
                <div className="space-y-1.5 text-xs text-slate-300 border-t border-slate-800/80 pt-3">
                  {org.email && (
                    <div className="flex items-center gap-2">
                      <Mail className="w-3.5 h-3.5 text-slate-400" />
                      <span>{org.email}</span>
                    </div>
                  )}
                  {org.phone && (
                    <div className="flex items-center gap-2">
                      <Phone className="w-3.5 h-3.5 text-slate-400" />
                      <span>{org.phone}</span>
                    </div>
                  )}
                  {org.address && (
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" />
                      <span>{org.address}</span>
                    </div>
                  )}
                </div>
                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                  <span>Linked Contacts: <strong className="text-white">{org.people_count || 0}</strong></span>
                  <button
                    onClick={() => {
                      setSearch(org.name);
                      setActiveTab("people");
                    }}
                    className="text-blue-400 hover:underline text-[11px] font-semibold"
                  >
                    View People →
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 360° Profile Inspector Modal */}
      {selectedPersonId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-4xl max-h-[90vh] overflow-y-auto p-6 sm:p-8 space-y-6 shadow-2xl">
            {profileLoading || !profileData ? (
              <div className="py-20 text-center text-slate-400 text-xs animate-pulse">Loading 360° customer profile...</div>
            ) : (
              <>
                {/* Header */}
                <div className="flex items-start justify-between gap-4 border-b border-slate-800 pb-5">
                  <div className="flex items-center gap-3.5">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-red-600 to-blue-600 flex items-center justify-center text-white font-black text-lg shadow-lg">
                      {profileData.person?.full_name?.charAt(0) || "P"}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h2 className="text-xl font-bold text-white">{profileData.person?.full_name}</h2>
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {profileData.person?.status}
                        </span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-950 text-slate-300 border border-slate-800">
                          {profileData.person?.person_type}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {profileData.person?.job_title || "Individual"} {profileData.organization && `· ${profileData.organization.name}`}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setSelectedPersonId(null);
                      setProfileData(null);
                    }}
                    className="p-2 text-slate-400 hover:text-white bg-slate-950 border border-slate-800 rounded-xl"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                {/* Profile Grid Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 space-y-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Direct Contact</span>
                    <div className="space-y-1 text-xs text-slate-300">
                      <div className="flex items-center gap-2">
                        <Mail className="w-3.5 h-3.5 text-blue-400" />
                        <span className="truncate">{profileData.person?.email || "—"}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Phone className="w-3.5 h-3.5 text-emerald-400" />
                        <span>{profileData.person?.phone || "—"}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <MapPin className="w-3.5 h-3.5 text-red-400" />
                        <span>{profileData.person?.address || "Addis Ababa, Ethiopia"}</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 space-y-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Revenue & Transactions</span>
                    <p className="text-xl font-black text-emerald-400">
                      {profileData.total_paid_volume?.toLocaleString() || "0"} ETB
                    </p>
                    <p className="text-[11px] text-slate-400">
                      {profileData.payments?.length || 0} Successful Payments · {profileData.invoices?.length || 0} Invoices
                    </p>
                  </div>

                  <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 space-y-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">CRM Deals & Pipeline</span>
                    <p className="text-xl font-black text-white">{profileData.opportunities?.length || 0} Deals</p>
                    <p className="text-[11px] text-slate-400">
                      {profileData.activities?.length || 0} Interaction touchpoints logged
                    </p>
                  </div>
                </div>

                {/* Sub-sections: Connected Deals, Student Records, and Timeline */}
                <div className="space-y-4">
                  {/* Opportunities */}
                  {profileData.opportunities && profileData.opportunities.length > 0 && (
                    <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 space-y-3">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-1.5">
                        <Briefcase className="w-3.5 h-3.5" />
                        Connected CRM Opportunities / Deals
                      </h4>
                      <div className="space-y-2">
                        {profileData.opportunities.map((opp: any) => (
                          <div key={opp.id} className="p-3 bg-slate-900 rounded-xl border border-slate-800 flex items-center justify-between text-xs">
                            <div>
                              <p className="font-bold text-white">{opp.title}</p>
                              <p className="text-[11px] text-slate-400">Stage: <strong className="text-blue-400">{opp.pipeline_stage}</strong> · Probability: {opp.probability}%</p>
                            </div>
                            <div className="text-right">
                              <p className="font-black text-white">{opp.value?.toLocaleString()} {opp.currency}</p>
                              <span className="text-[10px] font-bold text-emerald-400">{opp.status}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Student Registrations */}
                  {profileData.student_records && profileData.student_records.length > 0 && (
                    <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 space-y-3">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                        <GraduationCap className="w-3.5 h-3.5" />
                        Training Course Enrollments
                      </h4>
                      <div className="space-y-2">
                        {profileData.student_records.map((s: any) => (
                          <div key={s.id} className="p-3 bg-slate-900 rounded-xl border border-slate-800 flex items-center justify-between text-xs">
                            <div>
                              <p className="font-bold text-white">{s.course} {s.specialty && `(${s.specialty})`}</p>
                              <p className="text-[11px] text-slate-400">Schedule: {s.schedule || "Regular"} · Education: {s.education_level}</p>
                            </div>
                            <span className="px-2.5 py-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-md font-semibold text-[10px]">
                              {s.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 360 Chronological Timeline */}
                  <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                      <Clock className="w-4 h-4 text-red-400" />
                      Unified Interaction Timeline (Real Events)
                    </h4>
                    {profileData.timeline && profileData.timeline.length > 0 ? (
                      <div className="relative border-l-2 border-slate-800 ml-3 space-y-5 pl-5 py-2">
                        {profileData.timeline.map((evt: any, i: number) => (
                          <div key={i} className="relative group">
                            <div className="absolute -left-[27px] top-1 w-3.5 h-3.5 rounded-full bg-slate-900 border-2 border-red-500" />
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <span className="text-[10px] font-mono text-slate-400">{evt.date ? new Date(evt.date).toLocaleDateString() : "Recent"}</span>
                                <span className="px-2 py-0.5 bg-slate-900 text-slate-300 border border-slate-800 rounded text-[10px] font-bold uppercase">
                                  {evt.category}
                                </span>
                              </div>
                              <p className="text-xs font-bold text-white">{evt.title}</p>
                              <p className="text-xs text-slate-400">{evt.description}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-slate-400">No timeline events recorded yet.</p>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* New Person Modal */}
      {showNewPersonModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-lg p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">Create New Person</h3>
              <button onClick={() => setShowNewPersonModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>
            <form onSubmit={handleCreatePerson} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Full Name *</label>
                <input
                  type="text"
                  required
                  value={newPersonForm.full_name}
                  onChange={(e) => setNewPersonForm({ ...newPersonForm, full_name: e.target.value })}
                  placeholder="e.g. Solomon Girma"
                  className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Email Address</label>
                  <input
                    type="email"
                    value={newPersonForm.email}
                    onChange={(e) => setNewPersonForm({ ...newPersonForm, email: e.target.value })}
                    placeholder="solomon@example.com"
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Phone Number</label>
                  <input
                    type="tel"
                    value={newPersonForm.phone}
                    onChange={(e) => setNewPersonForm({ ...newPersonForm, phone: e.target.value })}
                    placeholder="+251 91 123 4567"
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Organization</label>
                  <select
                    value={newPersonForm.organization_id}
                    onChange={(e) => setNewPersonForm({ ...newPersonForm, organization_id: e.target.value })}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  >
                    <option value="">None (Individual)</option>
                    {organizations.map((o) => (
                      <option key={o.id} value={o.id}>{o.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Job Title</label>
                  <input
                    type="text"
                    value={newPersonForm.job_title}
                    onChange={(e) => setNewPersonForm({ ...newPersonForm, job_title: e.target.value })}
                    placeholder="e.g. IT Manager"
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Contact Type</label>
                  <select
                    value={newPersonForm.person_type}
                    onChange={(e) => setNewPersonForm({ ...newPersonForm, person_type: e.target.value })}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  >
                    <option value="Individual">Individual</option>
                    <option value="Customer">Customer</option>
                    <option value="Lead">Lead</option>
                    <option value="Student">Student</option>
                    <option value="Staff">Staff</option>
                    <option value="Partner">Partner</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Status</label>
                  <select
                    value={newPersonForm.status}
                    onChange={(e) => setNewPersonForm({ ...newPersonForm, status: e.target.value })}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  >
                    <option value="Active">Active</option>
                    <option value="Lead">Lead</option>
                    <option value="Prospect">Prospect</option>
                    <option value="Enrolled">Enrolled</option>
                    <option value="Customer">Customer</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Tags (Comma-separated)</label>
                <input
                  type="text"
                  value={newPersonForm.tags}
                  onChange={(e) => setNewPersonForm({ ...newPersonForm, tags: e.target.value })}
                  placeholder="VIP, Software, Travel"
                  className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                />
              </div>
              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowNewPersonModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl"
                >
                  Save Person
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* New Organization Modal */}
      {showNewOrgModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-lg p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">Create New Organization</h3>
              <button onClick={() => setShowNewOrgModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>
            <form onSubmit={handleCreateOrg} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Company / Organization Name *</label>
                <input
                  type="text"
                  required
                  value={newOrgForm.name}
                  onChange={(e) => setNewOrgForm({ ...newOrgForm, name: e.target.value })}
                  placeholder="e.g. Nile Logistics PLC"
                  className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Industry</label>
                  <input
                    type="text"
                    value={newOrgForm.industry}
                    onChange={(e) => setNewOrgForm({ ...newOrgForm, industry: e.target.value })}
                    placeholder="Logistics, Healthcare, IT"
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Business Type</label>
                  <input
                    type="text"
                    value={newOrgForm.business_type}
                    onChange={(e) => setNewOrgForm({ ...newOrgForm, business_type: e.target.value })}
                    placeholder="Enterprise, NGO, SME"
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Corporate Email</label>
                  <input
                    type="email"
                    value={newOrgForm.email}
                    onChange={(e) => setNewOrgForm({ ...newOrgForm, email: e.target.value })}
                    placeholder="info@nilelogistics.et"
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Corporate Phone</label>
                  <input
                    type="tel"
                    value={newOrgForm.phone}
                    onChange={(e) => setNewOrgForm({ ...newOrgForm, phone: e.target.value })}
                    placeholder="+251 91 100 2233"
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  />
                </div>
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Website URL</label>
                <input
                  type="url"
                  value={newOrgForm.website}
                  onChange={(e) => setNewOrgForm({ ...newOrgForm, website: e.target.value })}
                  placeholder="https://nilelogistics.et"
                  className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                />
              </div>
              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowNewOrgModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl"
                >
                  Save Organization
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
