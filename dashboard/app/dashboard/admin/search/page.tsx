"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import {
  Search,
  Sparkles,
  ExternalLink,
  Layers,
  DollarSign,
  Users,
  Shield,
  FileText,
  Clock,
  CheckCircle2,
  AlertCircle,
  Phone,
  Mail,
  Copy,
  Check,
  Eye,
  X,
  ArrowRight,
  TrendingUp,
  Briefcase,
  Plane,
  GraduationCap,
  HelpCircle,
  Cpu,
} from "lucide-react";
import AdminSearchFilterSort, {
  PaginationState,
  SearchFacetItem,
} from "@/components/AdminSearchFilterSort";
import { useAuth } from "@/components/AuthProvider";

interface SearchResultItem {
  id: string;
  module: string;
  entity_type: string;
  title: string;
  subtitle?: string;
  status?: string;
  email?: string;
  phone?: string;
  amount?: number;
  currency?: string;
  priority?: string;
  category?: string;
  created_at?: string;
  updated_at?: string;
  reference_code?: string;
  detail_url?: string;
  metadata?: Record<string, any>;
}

export default function AdminGlobalSearchPage() {
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
  const { role } = useAuth();

  // Search & Filter State
  const [query, setQuery] = useState("");
  const [selectedModule, setSelectedModule] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [sortBy, setSortBy] = useState("newest");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [isAiMode, setIsAiMode] = useState(false);

  // Results State
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [moduleFacets, setModuleFacets] = useState<SearchFacetItem[]>([]);
  const [statusFacets, setStatusFacets] = useState<SearchFacetItem[]>([]);
  const [pagination, setPagination] = useState<PaginationState>({
    page: 1,
    page_size: 25,
    total_count: 0,
    total_pages: 1,
    has_next: false,
    has_prev: false,
  });
  const [loading, setLoading] = useState(false);

  // AI Search Result Details
  const [aiInsight, setAiInsight] = useState<{
    parsedIntent?: string;
    summary?: string;
    totalFound?: number;
  } | null>(null);

  // Detail Modal
  const [selectedItem, setSelectedItem] = useState<SearchResultItem | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Fetch standard search
  const executeStandardSearch = useCallback(
    async (pageToFetch = pagination.page, pageSizeToFetch = pagination.page_size) => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (query.trim()) params.append("q", query.trim());
        if (selectedModule !== "all") params.append("module", selectedModule);
        if (selectedStatus !== "all") params.append("status", selectedStatus);
        if (sortBy) params.append("sort_by", sortBy);
        if (dateFrom) params.append("date_from", dateFrom);
        if (dateTo) params.append("date_to", dateTo);
        params.append("page", pageToFetch.toString());
        params.append("page_size", pageSizeToFetch.toString());

        const token = localStorage.getItem("access_token");
        const headers: Record<string, string> = {};
        if (token) headers["Authorization"] = `Bearer ${token}`;

        const res = await fetch(`${apiBase}/api/v1/admin/search?${params.toString()}`, { headers });
        if (res.ok) {
          const data = await res.json();
          setResults(data.results || []);
          setModuleFacets(data.module_facets || []);
          setStatusFacets(data.status_facets || []);
          if (data.pagination) setPagination(data.pagination);
          setAiInsight(null);
        }
      } catch (err) {
        console.error("Search failed:", err);
      } finally {
        setLoading(false);
      }
    },
    [apiBase, query, selectedModule, selectedStatus, sortBy, dateFrom, dateTo, pagination.page, pagination.page_size]
  );

  // Fetch AI natural search
  const executeAiSearch = useCallback(
    async (naturalPrompt: string) => {
      if (!naturalPrompt.trim()) return;
      setLoading(true);
      try {
        const token = localStorage.getItem("access_token");
        const headers: Record<string, string> = { "Content-Type": "application/json" };
        if (token) headers["Authorization"] = `Bearer ${token}`;

        const res = await fetch(`${apiBase}/api/v1/admin/search/ai`, {
          method: "POST",
          headers,
          body: JSON.stringify({ query: naturalPrompt, max_results: pagination.page_size }),
        });

        if (res.ok) {
          const data = await res.json();
          setResults(data.results || []);
          setAiInsight({
            parsedIntent: data.parsed_intent,
            summary: data.ai_summary,
            totalFound: data.total_found,
          });
          setPagination({
            page: 1,
            page_size: pagination.page_size,
            total_count: data.total_found,
            total_pages: Math.max(1, Math.ceil(data.total_found / pagination.page_size)),
            has_next: false,
            has_prev: false,
          });
        }
      } catch (err) {
        console.error("AI Search failed:", err);
      } finally {
        setLoading(false);
      }
    },
    [apiBase, pagination.page_size]
  );

  // Trigger search on filter change
  useEffect(() => {
    if (isAiMode) {
      if (query.length >= 3) {
        const debounce = setTimeout(() => executeAiSearch(query), 500);
        return () => clearTimeout(debounce);
      }
    } else {
      const debounce = setTimeout(() => executeStandardSearch(1, pagination.page_size), 300);
      return () => clearTimeout(debounce);
    }
  }, [query, selectedModule, selectedStatus, sortBy, dateFrom, dateTo, isAiMode, executeStandardSearch, executeAiSearch, pagination.page_size]);

  const handlePageChange = (newPage: number) => {
    setPagination((prev) => ({ ...prev, page: newPage }));
    executeStandardSearch(newPage, pagination.page_size);
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPagination((prev) => ({ ...prev, page_size: newPageSize, page: 1 }));
    executeStandardSearch(1, newPageSize);
  };

  const handleReset = () => {
    setQuery("");
    setSelectedModule("all");
    setSelectedStatus("all");
    setSortBy("newest");
    setDateFrom("");
    setDateTo("");
    setIsAiMode(false);
    setAiInsight(null);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(text);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getModuleBadge = (mod: string) => {
    switch (mod.toLowerCase()) {
      case "payments":
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-950/80 text-emerald-300 border border-emerald-800/60">Payments</span>;
      case "visa":
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-950/80 text-blue-300 border border-blue-800/60">Visa</span>;
      case "training":
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-purple-950/80 text-purple-300 border border-purple-800/60">Training</span>;
      case "travel":
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-950/80 text-amber-300 border border-amber-800/60">Travel</span>;
      case "crm":
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">CRM</span>;
      case "people":
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-sky-950/80 text-sky-300 border border-sky-800/60">People</span>;
      case "support":
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-950/80 text-rose-300 border border-rose-800/60">Support</span>;
      case "software":
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-indigo-950/80 text-indigo-300 border border-indigo-800/60">Software</span>;
      case "automation":
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-fuchsia-950/80 text-fuchsia-300 border border-fuchsia-800/60">Automation</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-800 text-gray-300 border border-gray-700">{mod}</span>;
    }
  };

  const getStatusBadge = (status?: string) => {
    if (!status) return null;
    const s = status.toLowerCase();
    if (s === "active" || s === "successful" || s === "confirmed" || s === "published") {
      return <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">{status}</span>;
    }
    if (s === "pending" || s === "open" || s === "submitted" || s === "under review") {
      return <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">{status}</span>;
    }
    if (s === "unpaid" || s === "failed" || s === "cancelled" || s === "overdue") {
      return <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">{status}</span>;
    }
    return <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-800 text-gray-300 border border-gray-700">{status}</span>;
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* 1. Header & Navigation Hub */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 text-cyan-400">
              <Search className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                <span>Enterprise Search & Discovery</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">
                  All Modules
                </span>
              </h1>
              <p className="text-sm text-gray-400">
                Server-side search, multi-criteria sorting, and authorized Natural Language AI querying.
              </p>
            </div>
          </div>
        </div>

        {/* Quick Module Jumps */}
        <div className="flex items-center gap-2">
          <Link
            href="/dashboard/admin/reviews"
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 hover:bg-slate-800 text-amber-300 border border-amber-800/40 flex items-center gap-1.5 transition-colors"
          >
            <span>Case Reviews</span>
          </Link>
          <Link
            href="/dashboard/payments"
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 hover:bg-slate-800 text-emerald-300 border border-emerald-800/40 flex items-center gap-1.5 transition-colors"
          >
            <span>Payments</span>
          </Link>
        </div>
      </div>

      {/* 2. Search, Filter, Sort & AI Bar Component */}
      <AdminSearchFilterSort
        query={query}
        onQueryChange={setQuery}
        selectedModule={selectedModule}
        onModuleChange={setSelectedModule}
        selectedStatus={selectedStatus}
        onStatusChange={setSelectedStatus}
        sortBy={sortBy}
        onSortChange={setSortBy}
        dateFrom={dateFrom}
        onDateFromChange={setDateFrom}
        dateTo={dateTo}
        onDateToChange={setDateTo}
        pagination={pagination}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
        moduleFacets={moduleFacets}
        statusFacets={statusFacets}
        onReset={handleReset}
        loading={loading}
        isAiMode={isAiMode}
        onToggleAiMode={() => setIsAiMode(!isAiMode)}
        onAiPromptSelect={(prompt) => {
          setIsAiMode(true);
          setQuery(prompt);
          executeAiSearch(prompt);
        }}
      />

      {/* 3. Grounded AI Insight Card (when in AI Mode or active AI query) */}
      {aiInsight && (
        <div className="bg-gradient-to-r from-indigo-950/60 via-slate-900 to-indigo-950/40 border border-indigo-700/40 rounded-xl p-4 shadow-lg space-y-2.5 animate-fadeIn">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-indigo-300 text-xs font-semibold uppercase tracking-wider">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span>Grounded AI Query Intelligence</span>
            </div>
            <span className="text-xs text-indigo-400 font-mono">
              {aiInsight.parsedIntent}
            </span>
          </div>
          <p className="text-sm text-indigo-100 leading-relaxed font-normal">
            {aiInsight.summary}
          </p>
        </div>
      )}

      {/* 4. Results List / Table View */}
      {results.length === 0 && !loading ? (
        <div className="bg-slate-900 border border-gray-800 rounded-xl p-12 text-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-slate-800 text-gray-400 flex items-center justify-center mx-auto border border-gray-700">
            <Search className="w-8 h-8" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">No matching records found.</h3>
            <p className="text-sm text-gray-400 max-w-md mx-auto mt-1">
              {query
                ? `No records found matching query "${query}" under current filters.`
                : "No records found under the selected filters."}
            </p>
          </div>
          <button
            onClick={handleReset}
            className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium transition-colors inline-flex items-center gap-2"
          >
            <span>Clear All Filters</span>
          </button>
        </div>
      ) : (
        <div className="bg-slate-900 border border-gray-800 rounded-xl overflow-hidden shadow-lg">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-300">
              <thead className="bg-slate-950/80 text-xs font-semibold text-gray-400 uppercase tracking-wider border-b border-gray-800">
                <tr>
                  <th className="px-4 py-3.5">Record / Title</th>
                  <th className="px-4 py-3.5">Module</th>
                  <th className="px-4 py-3.5">Status</th>
                  <th className="px-4 py-3.5">Contact</th>
                  <th className="px-4 py-3.5">Value / Amount</th>
                  <th className="px-4 py-3.5">Created Date</th>
                  <th className="px-4 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/80">
                {results.map((item) => (
                  <tr
                    key={`${item.entity_type}-${item.id}`}
                    className="hover:bg-slate-800/50 transition-colors group cursor-pointer"
                    onClick={() => setSelectedItem(item)}
                  >
                    {/* Title & Subtitle */}
                    <td className="px-4 py-3.5 max-w-xs">
                      <div className="font-medium text-white group-hover:text-cyan-300 transition-colors truncate">
                        {item.title}
                      </div>
                      {item.subtitle && (
                        <div className="text-xs text-gray-400 truncate mt-0.5">
                          {item.subtitle}
                        </div>
                      )}
                      {item.reference_code && (
                        <div className="text-[11px] text-gray-500 font-mono mt-0.5 flex items-center gap-1">
                          <span>Ref: {item.reference_code}</span>
                        </div>
                      )}
                    </td>

                    {/* Module Badge */}
                    <td className="px-4 py-3.5 whitespace-nowrap">
                      {getModuleBadge(item.module)}
                    </td>

                    {/* Status */}
                    <td className="px-4 py-3.5 whitespace-nowrap">
                      {getStatusBadge(item.status)}
                    </td>

                    {/* Contact */}
                    <td className="px-4 py-3.5 max-w-[200px]">
                      {item.email ? (
                        <div className="flex items-center gap-1.5 text-xs text-gray-300 truncate">
                          <Mail className="w-3 h-3 text-gray-500 flex-shrink-0" />
                          <span className="truncate">{item.email}</span>
                        </div>
                      ) : null}
                      {item.phone ? (
                        <div className="flex items-center gap-1.5 text-xs text-gray-400 truncate mt-0.5">
                          <Phone className="w-3 h-3 text-gray-500 flex-shrink-0" />
                          <span>{item.phone}</span>
                        </div>
                      ) : null}
                      {!item.email && !item.phone && (
                        <span className="text-xs text-gray-600">—</span>
                      )}
                    </td>

                    {/* Amount */}
                    <td className="px-4 py-3.5 whitespace-nowrap">
                      {item.amount !== null && item.amount !== undefined ? (
                        <div className="font-medium text-emerald-400">
                          {item.amount.toLocaleString(undefined, {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          })}{" "}
                          <span className="text-xs text-emerald-500/80">
                            {item.currency || "ETB"}
                          </span>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-600">—</span>
                      )}
                    </td>

                    {/* Date */}
                    <td className="px-4 py-3.5 whitespace-nowrap text-xs text-gray-400">
                      {item.created_at ? item.created_at.slice(0, 10) : "—"}
                    </td>

                    {/* Actions */}
                    <td className="px-4 py-3.5 whitespace-nowrap text-right">
                      <div className="flex items-center justify-end gap-1.5" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => setSelectedItem(item)}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-gray-300 hover:text-white transition-colors"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        {item.detail_url && (
                          <Link
                            href={item.detail_url}
                            className="p-1.5 rounded-lg bg-slate-800 hover:bg-cyan-900/50 text-gray-300 hover:text-cyan-300 transition-colors"
                            title="Open Module"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </Link>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 5. Detail Modal */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="bg-slate-900 border border-gray-700 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl space-y-5 p-6">
            {/* Modal Header */}
            <div className="flex items-start justify-between border-b border-gray-800 pb-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  {getModuleBadge(selectedItem.module)}
                  {getStatusBadge(selectedItem.status)}
                </div>
                <h3 className="text-xl font-bold text-white">{selectedItem.title}</h3>
                {selectedItem.subtitle && (
                  <p className="text-sm text-gray-400">{selectedItem.subtitle}</p>
                )}
              </div>
              <button
                onClick={() => setSelectedItem(null)}
                className="p-1.5 rounded-lg bg-slate-800 text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div className="bg-slate-950 border border-gray-800 rounded-lg p-3">
                <div className="text-xs text-gray-500">Reference / ID</div>
                <div className="text-sm font-mono text-cyan-300 font-semibold truncate flex items-center justify-between">
                  <span>{selectedItem.reference_code || selectedItem.id}</span>
                  <button
                    onClick={() => copyToClipboard(selectedItem.reference_code || selectedItem.id)}
                    className="text-gray-500 hover:text-white"
                    title="Copy ID"
                  >
                    {copiedId === (selectedItem.reference_code || selectedItem.id) ? (
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <Copy className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>
              </div>

              {selectedItem.amount !== null && selectedItem.amount !== undefined ? (
                <div className="bg-slate-950 border border-gray-800 rounded-lg p-3">
                  <div className="text-xs text-gray-500">Monetary Value</div>
                  <div className="text-sm font-semibold text-emerald-400">
                    {selectedItem.amount.toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}{" "}
                    {selectedItem.currency || "ETB"}
                  </div>
                </div>
              ) : null}

              <div className="bg-slate-950 border border-gray-800 rounded-lg p-3">
                <div className="text-xs text-gray-500">Created Timestamp</div>
                <div className="text-xs text-gray-300 font-mono">
                  {selectedItem.created_at || "N/A"}
                </div>
              </div>
            </div>

            {/* Contact Information */}
            {(selectedItem.email || selectedItem.phone) && (
              <div className="bg-slate-950 border border-gray-800 rounded-lg p-4 space-y-2">
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Contact Information
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                  {selectedItem.email && (
                    <div className="flex items-center gap-2 text-gray-300">
                      <Mail className="w-4 h-4 text-gray-500" />
                      <span>{selectedItem.email}</span>
                    </div>
                  )}
                  {selectedItem.phone && (
                    <div className="flex items-center gap-2 text-gray-300">
                      <Phone className="w-4 h-4 text-gray-500" />
                      <span>{selectedItem.phone}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Metadata & Raw Attributes */}
            {selectedItem.metadata && Object.keys(selectedItem.metadata).length > 0 && (
              <div className="bg-slate-950 border border-gray-800 rounded-lg p-4 space-y-2">
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Specific Attributes
                </div>
                <pre className="text-xs font-mono text-gray-300 bg-slate-900 p-3 rounded overflow-x-auto">
                  {JSON.stringify(selectedItem.metadata, null, 2)}
                </pre>
              </div>
            )}

            {/* Modal Actions */}
            <div className="flex items-center justify-end gap-3 pt-3 border-t border-gray-800">
              <button
                onClick={() => setSelectedItem(null)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-gray-300 text-sm font-medium"
              >
                Close
              </button>
              {selectedItem.detail_url && (
                <Link
                  href={selectedItem.detail_url}
                  className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium flex items-center gap-2"
                >
                  <span>Open In {selectedItem.module}</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
