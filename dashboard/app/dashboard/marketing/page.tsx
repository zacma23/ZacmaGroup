"use client";

import { useEffect, useState } from "react";
import {
  Send,
  Users,
  MessageSquare,
  Mail,
  Smartphone,
  Plus,
  Play,
  CheckCircle2,
  Clock,
  Filter,
  Search,
  Building2,
  GraduationCap,
  Sparkles,
  BarChart3,
  X,
  Layers,
} from "lucide-react";

export default function MarketingPage() {
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

  const [activeTab, setActiveTab] = useState<"campaigns" | "segments" | "logs">("campaigns");
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [segments, setSegments] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [dispatchingId, setDispatchingId] = useState<string | null>(null);

  // New Campaign Modal
  const [showNewCampaignModal, setShowNewCampaignModal] = useState(false);
  const [campaignForm, setCampaignForm] = useState({
    name: "",
    campaign_type: "Email",
    segment_id: "",
    subject: "",
    message_body: "",
    budget: 0,
  });

  // New Segment Modal
  const [showNewSegmentModal, setShowNewSegmentModal] = useState(false);
  const [segmentForm, setSegmentForm] = useState({
    name: "",
    description: "",
    criteria_type: "students",
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [campsRes, segsRes, logsRes] = await Promise.all([
        fetch(`${apiBase}/api/v1/marketing/campaigns`),
        fetch(`${apiBase}/api/v1/marketing/segments`),
        fetch(`${apiBase}/api/v1/marketing/logs`),
      ]);
      if (campsRes.ok) setCampaigns(await campsRes.json());
      if (segsRes.ok) setSegments(await segsRes.json());
      if (logsRes.ok) setLogs(await logsRes.json());
    } catch (e) {
      console.error("Failed to load marketing data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDispatchCampaign = async (campaignId: string) => {
    setDispatchingId(campaignId);
    try {
      const res = await fetch(`${apiBase}/api/v1/marketing/campaigns/${campaignId}/dispatch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      if (res.ok) {
        await fetchData();
      }
    } catch (e) {
      console.error("Error dispatching campaign:", e);
    } finally {
      setDispatchingId(null);
    }
  };

  const handleCreateCampaign = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...campaignForm,
        segment_id: campaignForm.segment_id || undefined,
        budget: Number(campaignForm.budget),
      };
      const res = await fetch(`${apiBase}/api/v1/marketing/campaigns`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setShowNewCampaignModal(false);
        setCampaignForm({
          name: "",
          campaign_type: "Email",
          segment_id: "",
          subject: "",
          message_body: "",
          budget: 0,
        });
        fetchData();
      }
    } catch (e) {
      console.error("Error creating campaign:", e);
    }
  };

  const handleCreateSegment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      let filter_criteria: any = {};
      if (segmentForm.criteria_type === "students") filter_criteria = { person_type: "Student" };
      else if (segmentForm.criteria_type === "leads") filter_criteria = { status: "Lead" };
      else if (segmentForm.criteria_type === "enterprises") filter_criteria = { has_organization: true };
      else if (segmentForm.criteria_type === "paid") filter_criteria = { paid_only: true };

      const payload = {
        name: segmentForm.name,
        description: segmentForm.description,
        filter_criteria,
        is_dynamic: true,
      };

      const res = await fetch(`${apiBase}/api/v1/marketing/segments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setShowNewSegmentModal(false);
        setSegmentForm({ name: "", description: "", criteria_type: "students" });
        fetchData();
      }
    } catch (e) {
      console.error("Error creating segment:", e);
    }
  };

  const totalDelivered = logs.length;
  const activeCampaigns = campaigns.filter((c) => c.status === "Sent" || c.status === "Scheduled").length;
  const totalRecipientsEstimated = segments.reduce((a, b) => a + (b.member_count || 0), 0);

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-purple-600/20 text-purple-400 rounded-xl border border-purple-500/30">
            <Send className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-white tracking-tight">Marketing Automation</h1>
            <p className="text-xs text-slate-400">Dynamic audience segments, cross-channel campaigns & recipient delivery logs.</p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setShowNewSegmentModal(true)}
            className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition"
          >
            <Users className="w-3.5 h-3.5 text-blue-400" />
            <span>New Audience</span>
          </button>
          <button
            onClick={() => setShowNewCampaignModal(true)}
            className="px-4 py-2 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white rounded-xl text-xs font-bold shadow-lg shadow-red-600/20 flex items-center gap-1.5 transition"
          >
            <Plus className="w-4 h-4" />
            <span>Compose Campaign</span>
          </button>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Active Campaigns</span>
            <Sparkles className="w-4 h-4 text-purple-400" />
          </div>
          <p className="text-2xl font-black text-white mt-1">{activeCampaigns}</p>
          <p className="text-[11px] text-slate-400 mt-0.5">{campaigns.length} Total campaigns created</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Target Audience Pool</span>
            <Users className="w-4 h-4 text-blue-400" />
          </div>
          <p className="text-2xl font-black text-blue-400 mt-1">{totalRecipientsEstimated}</p>
          <p className="text-[11px] text-slate-400 mt-0.5">{segments.length} Dynamic segments</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Delivered Touchpoints</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-black text-emerald-400 mt-1">{totalDelivered}</p>
          <p className="text-[11px] text-emerald-400/80 mt-0.5">Logs recorded on People timelines</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Supported Channels</span>
            <MessageSquare className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-black text-white mt-1">Email & SMS</p>
          <p className="text-[11px] text-slate-400 mt-0.5">Automated direct delivery</p>
        </div>
      </div>

      {/* Main Tabs */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 shadow-xl space-y-4">
        <div className="flex items-center gap-1.5 p-1 bg-slate-950 rounded-xl border border-slate-800 w-fit">
          <button
            onClick={() => setActiveTab("campaigns")}
            className={`px-3.5 py-2 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
              activeTab === "campaigns" ? "bg-red-600 text-white shadow-md" : "text-slate-400 hover:text-white"
            }`}
          >
            <Send className="w-3.5 h-3.5" />
            <span>Campaigns ({campaigns.length})</span>
          </button>
          <button
            onClick={() => setActiveTab("segments")}
            className={`px-3.5 py-2 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
              activeTab === "segments" ? "bg-red-600 text-white shadow-md" : "text-slate-400 hover:text-white"
            }`}
          >
            <Users className="w-3.5 h-3.5" />
            <span>Dynamic Audiences ({segments.length})</span>
          </button>
          <button
            onClick={() => setActiveTab("logs")}
            className={`px-3.5 py-2 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
              activeTab === "logs" ? "bg-red-600 text-white shadow-md" : "text-slate-400 hover:text-white"
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Communication Logs ({logs.length})</span>
          </button>
        </div>

        {/* View 1: Campaigns Table */}
        {loading ? (
          <div className="py-16 text-center text-slate-400 text-xs animate-pulse">Loading marketing engine...</div>
        ) : activeTab === "campaigns" ? (
          campaigns.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-xs">No marketing campaigns found.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-3">Campaign Name</th>
                    <th className="py-3 px-3">Channel</th>
                    <th className="py-3 px-3">Subject / Preview</th>
                    <th className="py-3 px-3">Status</th>
                    <th className="py-3 px-3">Delivered</th>
                    <th className="py-3 px-3">Sent Date</th>
                    <th className="py-3 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {campaigns.map((camp) => (
                    <tr key={camp.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3.5 px-3 font-bold text-white text-sm">{camp.name}</td>
                      <td className="py-3.5 px-3">
                        <span className="px-2.5 py-1 rounded-md text-[11px] font-semibold bg-slate-950 border border-slate-800 text-purple-300">
                          {camp.campaign_type || camp.channel || "Email"}
                        </span>
                      </td>
                      <td className="py-3.5 px-3 max-w-xs truncate text-slate-300">
                        {camp.subject || camp.message_body || "—"}
                      </td>
                      <td className="py-3.5 px-3">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                            camp.status === "Sent"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                          }`}
                        >
                          {camp.status || "Draft"}
                        </span>
                      </td>
                      <td className="py-3.5 px-3 font-semibold text-slate-200">
                        {camp.delivered_count || 0} / {camp.total_recipients || 0}
                      </td>
                      <td className="py-3.5 px-3 text-slate-400">
                        {camp.sent_at ? new Date(camp.sent_at).toLocaleDateString() : "Not dispatched"}
                      </td>
                      <td className="py-3.5 px-3 text-right">
                        <button
                          disabled={dispatchingId === camp.id}
                          onClick={() => handleDispatchCampaign(camp.id)}
                          className="px-3 py-1.5 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white rounded-lg font-bold text-[11px] transition shadow-md flex items-center gap-1.5 ml-auto disabled:opacity-50"
                        >
                          {dispatchingId === camp.id ? (
                            <span>Dispatching...</span>
                          ) : (
                            <>
                              <Play className="w-3 h-3" />
                              <span>Dispatch</span>
                            </>
                          )}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : activeTab === "segments" ? (
          /* View 2: Dynamic Audiences */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {segments.map((seg) => (
              <div key={seg.id} className="bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-3 hover:border-slate-700 transition">
                <div className="flex items-start justify-between">
                  <div className="p-2 bg-blue-600/20 text-blue-400 rounded-xl border border-blue-500/30">
                    <Users className="w-5 h-5" />
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-[10px] font-black bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {seg.member_count} Members
                  </span>
                </div>
                <div>
                  <h3 className="font-bold text-white text-base">{seg.name}</h3>
                  <p className="text-xs text-slate-400 mt-0.5">{seg.description || "Dynamic auto-updating segment."}</p>
                </div>
                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                  <span>Type: <strong className="text-white">{seg.is_dynamic ? "Dynamic Real-Time" : "Static"}</strong></span>
                  <button
                    onClick={() => {
                      setCampaignForm({ ...campaignForm, segment_id: seg.id });
                      setShowNewCampaignModal(true);
                    }}
                    className="text-red-400 hover:underline text-[11px] font-semibold"
                  >
                    Target Segment →
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* View 3: Communication Logs */
          logs.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-xs">No communication logs recorded yet.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-3">Timestamp</th>
                    <th className="py-3 px-3">Channel</th>
                    <th className="py-3 px-3">Recipient</th>
                    <th className="py-3 px-3">Subject / Message</th>
                    <th className="py-3 px-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {logs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-800/40 transition">
                      <td className="py-3 px-3 font-mono text-slate-400">
                        {log.created_at ? new Date(log.created_at).toLocaleString() : "Recent"}
                      </td>
                      <td className="py-3 px-3 font-bold text-purple-400">{log.channel}</td>
                      <td className="py-3 px-3">
                        <p className="font-semibold text-white">{log.person_name || log.recipient}</p>
                        <p className="text-[11px] text-slate-400">{log.recipient}</p>
                      </td>
                      <td className="py-3 px-3 max-w-sm">
                        <p className="font-bold text-slate-200">{log.subject}</p>
                        <p className="text-[11px] text-slate-400 truncate">{log.message_body}</p>
                      </td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold text-[10px]">
                          {log.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}
      </div>

      {/* New Campaign Modal */}
      {showNewCampaignModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-lg p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">Compose Marketing Campaign</h3>
              <button onClick={() => setShowNewCampaignModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>
            <form onSubmit={handleCreateCampaign} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Campaign Title *</label>
                <input
                  type="text"
                  required
                  value={campaignForm.name}
                  onChange={(e) => setCampaignForm({ ...campaignForm, name: e.target.value })}
                  placeholder="e.g. Q3 Software & AI Course Intake Drive"
                  className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Channel</label>
                  <select
                    value={campaignForm.campaign_type}
                    onChange={(e) => setCampaignForm({ ...campaignForm, campaign_type: e.target.value })}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  >
                    <option value="Email">Email Broadcast</option>
                    <option value="SMS">SMS Message</option>
                    <option value="Notification">Platform Notification</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Target Audience Segment</label>
                  <select
                    value={campaignForm.segment_id}
                    onChange={(e) => setCampaignForm({ ...campaignForm, segment_id: e.target.value })}
                    className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                  >
                    <option value="">All Contacts (General)</option>
                    {segments.map((s) => (
                      <option key={s.id} value={s.id}>{s.name} ({s.member_count} contacts)</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Subject / Header *</label>
                <input
                  type="text"
                  required
                  value={campaignForm.subject}
                  onChange={(e) => setCampaignForm({ ...campaignForm, subject: e.target.value })}
                  placeholder="e.g. Exclusive 15% Early Bird Discount for Next Cohort"
                  className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Message Content *</label>
                <textarea
                  rows={4}
                  required
                  value={campaignForm.message_body}
                  onChange={(e) => setCampaignForm({ ...campaignForm, message_body: e.target.value })}
                  placeholder="Draft your promotional or transactional announcement here..."
                  className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                />
              </div>
              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowNewCampaignModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl"
                >
                  Save Campaign
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* New Segment Modal */}
      {showNewSegmentModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-lg p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">Create Dynamic Audience Segment</h3>
              <button onClick={() => setShowNewSegmentModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>
            <form onSubmit={handleCreateSegment} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Segment Name *</label>
                <input
                  type="text"
                  required
                  value={segmentForm.name}
                  onChange={(e) => setSegmentForm({ ...segmentForm, name: e.target.value })}
                  placeholder="e.g. Paid Software Clients"
                  className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Dynamic Filter Rule</label>
                <select
                  value={segmentForm.criteria_type}
                  onChange={(e) => setSegmentForm({ ...segmentForm, criteria_type: e.target.value })}
                  className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                >
                  <option value="students">All Enrolled Academy Students</option>
                  <option value="leads">New & Uncontacted Leads</option>
                  <option value="enterprises">Corporate & B2B Organizations</option>
                  <option value="paid">Clients with Successful Completed Payments</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Description</label>
                <input
                  type="text"
                  value={segmentForm.description}
                  onChange={(e) => setSegmentForm({ ...segmentForm, description: e.target.value })}
                  placeholder="Target criteria explanation..."
                  className="w-full bg-slate-950 text-white px-3 py-2 rounded-xl border border-slate-800 focus:outline-none"
                />
              </div>
              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowNewSegmentModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl"
                >
                  Save Segment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
