"use client";

import React, { useEffect, useState } from "react";
import {
  GraduationCap,
  Wrench,
  CheckCircle2,
  XCircle,
  Clock,
  Calendar,
  Layers,
  Search,
  Filter,
  Eye,
  Edit3,
  UserCheck,
  Building,
  RefreshCw,
  Plus,
} from "lucide-react";

interface StudentReg {
  id: string;
  reference_code?: string;
  full_name: string;
  email: string;
  phone?: string;
  education_level?: string;
  course: string;
  specialty?: string;
  maintenance_sub_type?: string;
  schedule?: string;
  time_slot?: string;
  time?: string;
  payment_method?: string;
  status: string;
  created_at?: string;
}

export default function AdminTrainingPage() {
  const [registrations, setRegistrations] = useState<StudentReg[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [courseFilter, setCourseFilter] = useState<string>("all");
  const [activeTab, setActiveTab] = useState<"registrations" | "courses">("registrations");

  // Edit schedule modal state
  const [editingStudent, setEditingStudent] = useState<StudentReg | null>(null);
  const [editSchedule, setEditSchedule] = useState<string>("");
  const [editTime, setEditTime] = useState<string>("");
  const [editStatus, setEditStatus] = useState<string>("");
  const [savingEdit, setSavingEdit] = useState<boolean>(false);

  const fetchRegistrations = async () => {
    setLoading(true);
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/api/v1/students/registrations`);
      if (res.ok) {
        const data = await res.json();
        setRegistrations(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRegistrations();
  }, []);

  const handleUpdateStatus = async (id: string, newStatus: string) => {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/api/v1/students/registrations/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) {
        fetchRegistrations();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingStudent) return;
    setSavingEdit(true);
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/api/v1/students/registrations/${editingStudent.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          schedule: editSchedule,
          time_slot: editTime,
          time: editTime,
          status: editStatus,
        }),
      });
      if (res.ok) {
        setEditingStudent(null);
        fetchRegistrations();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSavingEdit(false);
    }
  };

  const filteredRegistrations = registrations.filter((r) => {
    const matchesSearch =
      r.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.course?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.reference_code?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === "all" || r.status?.toLowerCase() === statusFilter.toLowerCase();
    const matchesCourse = courseFilter === "all" || r.course?.toLowerCase() === courseFilter.toLowerCase();

    return matchesSearch && matchesStatus && matchesCourse;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 p-6 rounded-3xl border border-slate-800 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <GraduationCap className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Training & Student Management</h1>
            <p className="text-xs text-slate-400">
              Manage student registrations, Maintenance Hardware Specialties, and batch timetables.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab("registrations")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
              activeTab === "registrations"
                ? "bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20"
                : "bg-slate-800 text-slate-300 hover:text-white"
            }`}
          >
            Student Registrations ({registrations.length})
          </button>
          <button
            onClick={() => setActiveTab("courses")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
              activeTab === "courses"
                ? "bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20"
                : "bg-slate-800 text-slate-300 hover:text-white"
            }`}
          >
            Course Structure (15)
          </button>
          <button
            onClick={fetchRegistrations}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs transition"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {activeTab === "registrations" ? (
        <div className="space-y-4">
          {/* Filter Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
              <input
                type="text"
                placeholder="Search student, email, code..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="all">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>

            <select
              value={courseFilter}
              onChange={(e) => setCourseFilter(e.target.value)}
              className="px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="all">All Courses</option>
              <option value="maintenance">Maintenance</option>
              <option value="web design">Web Design</option>
              <option value="ai">AI</option>
              <option value="graphics">Graphics</option>
              <option value="programming">Programming</option>
            </select>
          </div>

          {/* Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 font-bold uppercase tracking-wider border-b border-slate-800">
                  <tr>
                    <th className="p-4">Student</th>
                    <th className="p-4">Course & Specialty</th>
                    <th className="p-4">Selected Schedule</th>
                    <th className="p-4">Selected Time</th>
                    <th className="p-4">Status</th>
                    <th className="p-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredRegistrations.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="p-8 text-center text-slate-500">
                        {loading ? "Loading registrations..." : "No matching student registrations found."}
                      </td>
                    </tr>
                  ) : (
                    filteredRegistrations.map((r) => {
                      const specialty = r.specialty || r.maintenance_sub_type;
                      return (
                        <tr key={r.id} className="hover:bg-slate-800/40 transition">
                          <td className="p-4">
                            <div className="font-bold text-white text-sm">{r.full_name}</div>
                            <div className="text-slate-400">{r.email}</div>
                            {r.phone && <div className="text-[11px] text-slate-500">{r.phone}</div>}
                            <div className="font-mono text-[10px] text-amber-400 mt-0.5">
                              {r.reference_code || r.id}
                            </div>
                          </td>

                          <td className="p-4">
                            <div className="inline-flex items-center gap-1 font-bold text-emerald-400">
                              <span>{r.course}</span>
                            </div>
                            {specialty ? (
                              <div className="text-amber-300 font-semibold text-[11px] flex items-center gap-1 mt-0.5">
                                <Wrench className="w-3 h-3" />
                                <span>{specialty}</span>
                              </div>
                            ) : (
                              <div className="text-slate-500 text-[11px]">General Track</div>
                            )}
                          </td>

                          <td className="p-4">
                            <div className="text-slate-200 font-medium flex items-center gap-1.5">
                              <Calendar className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
                              <span>{r.schedule || "Monday + Wednesday + Thursday"}</span>
                            </div>
                          </td>

                          <td className="p-4">
                            <div className="font-mono text-emerald-300 font-semibold flex items-center gap-1.5">
                              <Clock className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                              <span>{r.time_slot || r.time || "03:00 – 05:00"}</span>
                            </div>
                          </td>

                          <td className="p-4">
                            <span
                              className={`px-2.5 py-1 rounded-full text-xs font-bold border ${
                                r.status === "Approved"
                                  ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                                  : r.status === "Rejected"
                                  ? "bg-rose-500/20 text-rose-300 border-rose-500/30"
                                  : "bg-amber-500/20 text-amber-300 border-amber-500/30"
                              }`}
                            >
                              {r.status}
                            </span>
                          </td>

                          <td className="p-4 text-right">
                            <div className="flex items-center justify-end gap-1.5">
                              <button
                                onClick={() => {
                                  setEditingStudent(r);
                                  setEditSchedule(r.schedule || "Monday + Wednesday + Thursday");
                                  setEditTime(r.time_slot || r.time || "03:00 – 05:00");
                                  setEditStatus(r.status || "Pending");
                                }}
                                className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs transition"
                                title="Edit Schedule / Status"
                              >
                                <Edit3 className="w-3.5 h-3.5" />
                              </button>

                              {r.status !== "Approved" && (
                                <button
                                  onClick={() => handleUpdateStatus(r.id, "Approved")}
                                  className="p-1.5 bg-emerald-950/80 border border-emerald-700 hover:bg-emerald-900 text-emerald-300 rounded-lg text-xs transition"
                                  title="Approve Registration"
                                >
                                  <CheckCircle2 className="w-3.5 h-3.5" />
                                </button>
                              )}

                              {r.status !== "Rejected" && (
                                <button
                                  onClick={() => handleUpdateStatus(r.id, "Rejected")}
                                  className="p-1.5 bg-rose-950/80 border border-rose-800 hover:bg-rose-900 text-rose-300 rounded-lg text-xs transition"
                                  title="Reject Registration"
                                >
                                  <XCircle className="w-3.5 h-3.5" />
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        /* Courses Tab */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-5 rounded-2xl bg-slate-900 border border-emerald-500/50 shadow-xl space-y-3 md:col-span-2">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Wrench className="w-4 h-4 text-amber-400" /> Maintenance Course & Hardware Specialty
              </h3>
              <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 text-[10px] font-bold rounded-full border border-emerald-500/30">
                Core Program
              </span>
            </div>
            <p className="text-xs text-slate-300">
              Component diagnostics, motherboard repair, PCB soldering, hardware assembly & firmware flashing.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs">
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 space-y-1">
                <span className="font-bold text-blue-300">Available Schedules:</span>
                <p className="text-[11px] text-slate-400">1. Monday + Wednesday + Thursday</p>
                <p className="text-[11px] text-slate-400">2. Tuesday + Thursday + Saturday</p>
                <p className="text-[11px] text-slate-400">3. Saturday + Sunday</p>
              </div>
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 space-y-1">
                <span className="font-bold text-emerald-300">Available Time Slots:</span>
                <p className="text-[11px] text-slate-400">03:00–05:00 • 05:00–07:00 • 07:00–09:00</p>
                <p className="text-[11px] text-slate-400">09:00–11:00 • 11:00–01:00 • 12:00–02:00</p>
              </div>
            </div>
          </div>

          {[
            { name: "Basic Computer", cat: "General IT", desc: "OS fundamentals & Office Suite." },
            { name: "Graphics", cat: "Design", desc: "Photoshop, Illustrator & vector branding." },
            { name: "Video Editing", cat: "Media", desc: "Premiere Pro, DaVinci Resolve & motion." },
            { name: "Videography", cat: "Media", desc: "Camera lighting & studio video shoots." },
            { name: "Photography", cat: "Media", desc: "DSLR photo & studio portraiture." },
            { name: "AI", cat: "Emerging Tech", desc: "Applied AI, Machine Learning & prompts." },
            { name: "Cloud Computing", cat: "Cloud & Infra", desc: "AWS, Azure, Docker & DevOps." },
            { name: "Spoken English", cat: "Languages", desc: "Workplace fluency & communication." },
            { name: "Accounting", cat: "Business", desc: "Financial accounting & QuickBooks." },
            { name: "IT Support", cat: "Technical", desc: "Helpdesk diagnostics & client PC support." },
            { name: "AutoCAD", cat: "Engineering", desc: "2D drafting & 3D architectural CAD." },
            { name: "ETABS", cat: "Engineering", desc: "Structural analysis & building modeling." },
            { name: "Web Design", cat: "Software", desc: "HTML5, Tailwind, React & JavaScript." },
            { name: "Networking", cat: "Technical", desc: "Cisco routing, switching & CCNA." },
          ].map((c, i) => (
            <div key={i} className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-white">{c.name}</h4>
                <span className="text-[10px] text-slate-400 font-mono">{c.cat}</span>
              </div>
              <p className="text-[11px] text-slate-400">{c.desc}</p>
            </div>
          ))}
        </div>
      )}

      {/* Edit Schedule Modal */}
      {editingStudent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-white">Edit Schedule & Status</h3>
              <button onClick={() => setEditingStudent(null)} className="text-slate-400 hover:text-white">
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveEdit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Student</label>
                <p className="font-bold text-white text-sm">{editingStudent.full_name}</p>
                <p className="text-slate-400">{editingStudent.course} {editingStudent.specialty ? `(${editingStudent.specialty})` : ""}</p>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Schedule</label>
                <select
                  value={editSchedule}
                  onChange={(e) => setEditSchedule(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="Monday + Wednesday + Thursday">Monday + Wednesday + Thursday</option>
                  <option value="Tuesday + Thursday + Saturday">Tuesday + Thursday + Saturday</option>
                  <option value="Saturday + Sunday">Saturday + Sunday</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Time Slot</label>
                <select
                  value={editTime}
                  onChange={(e) => setEditTime(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="03:00 – 05:00">03:00 – 05:00</option>
                  <option value="05:00 – 07:00">05:00 – 07:00</option>
                  <option value="07:00 – 09:00">07:00 – 09:00</option>
                  <option value="09:00 – 11:00">09:00 – 11:00</option>
                  <option value="11:00 – 01:00">11:00 – 01:00</option>
                  <option value="12:00 – 02:00">12:00 – 02:00</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Status</label>
                <select
                  value={editStatus}
                  onChange={(e) => setEditStatus(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="Pending">Pending</option>
                  <option value="Approved">Approved</option>
                  <option value="Rejected">Rejected</option>
                </select>
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="submit"
                  disabled={savingEdit}
                  className="flex-1 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl transition"
                >
                  {savingEdit ? "Saving..." : "Save Changes"}
                </button>
                <button
                  type="button"
                  onClick={() => setEditingStudent(null)}
                  className="py-2.5 px-4 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-xl transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

