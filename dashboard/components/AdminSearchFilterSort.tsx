"use client";

import React, { useState } from "react";
import {
  Search,
  X,
  Filter,
  ArrowUpDown,
  Calendar,
  Sparkles,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  SlidersHorizontal,
} from "lucide-react";

export interface SearchFacetItem {
  key: string;
  label: string;
  count: number;
}

export interface PaginationState {
  page: number;
  page_size: number;
  total_count: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

interface AdminSearchFilterSortProps {
  query: string;
  onQueryChange: (q: string) => void;
  selectedModule: string;
  onModuleChange: (mod: string) => void;
  selectedStatus: string;
  onStatusChange: (stat: string) => void;
  sortBy: string;
  onSortChange: (sort: string) => void;
  dateFrom: string;
  onDateFromChange: (d: string) => void;
  dateTo: string;
  onDateToChange: (d: string) => void;
  pagination: PaginationState;
  onPageChange: (newPage: number) => void;
  onPageSizeChange: (newPageSize: number) => void;
  moduleFacets?: SearchFacetItem[];
  statusFacets?: SearchFacetItem[];
  onReset: () => void;
  loading?: boolean;
  isAiMode?: boolean;
  onToggleAiMode?: () => void;
  onAiPromptSelect?: (prompt: string) => void;
}

export const MODULE_OPTIONS = [
  { value: "all", label: "All Business Lines" },
  { value: "training", label: "Training & Students" },
  { value: "visa", label: "Visa Applications" },
  { value: "travel", label: "Travel & Bookings" },
  { value: "payments", label: "Payments & Invoices" },
  { value: "support", label: "Customer Support" },
  { value: "crm", label: "CRM & Deals" },
  { value: "people", label: "People & Orgs" },
  { value: "software", label: "Software Projects" },
  { value: "staff", label: "Staff & HR" },
  { value: "users", label: "Platform Users" },
  { value: "automation", label: "Automation Jobs" },
];

export const STATUS_OPTIONS = [
  { value: "all", label: "All Statuses" },
  { value: "active", label: "Active" },
  { value: "pending", label: "Pending" },
  { value: "successful", label: "Successful" },
  { value: "unpaid", label: "Unpaid / Due" },
  { value: "open", label: "Open" },
  { value: "closed", label: "Closed" },
  { value: "confirmed", label: "Confirmed" },
  { value: "cancelled", label: "Cancelled" },
];

export const SORT_OPTIONS = [
  { value: "newest", label: "Newest First" },
  { value: "oldest", label: "Oldest First" },
  { value: "name_asc", label: "Name / Title (A → Z)" },
  { value: "name_desc", label: "Name / Title (Z → A)" },
  { value: "amount_desc", label: "Highest Amount" },
  { value: "amount_asc", label: "Lowest Amount" },
  { value: "priority", label: "Highest Priority" },
  { value: "status", label: "Status" },
  { value: "recent_activity", label: "Most Recent Activity" },
];

export const SAMPLE_AI_QUERIES = [
  "Show customers who requested visa services this month",
  "Find unpaid travel bookings",
  "Show support conversations related to Dubai visas",
  "Find all customers whose booking was cancelled",
  "Show active deals over 100,000 ETB",
  "Find students enrolled in AI courses",
];

export default function AdminSearchFilterSort({
  query,
  onQueryChange,
  selectedModule,
  onModuleChange,
  selectedStatus,
  onStatusChange,
  sortBy,
  onSortChange,
  dateFrom,
  onDateFromChange,
  dateTo,
  onDateToChange,
  pagination,
  onPageChange,
  onPageSizeChange,
  moduleFacets = [],
  statusFacets = [],
  onReset,
  loading = false,
  isAiMode = false,
  onToggleAiMode,
  onAiPromptSelect,
}: AdminSearchFilterSortProps) {
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  const hasActiveFilters =
    query.trim() !== "" ||
    selectedModule !== "all" ||
    selectedStatus !== "all" ||
    dateFrom !== "" ||
    dateTo !== "" ||
    sortBy !== "newest";

  return (
    <div className="bg-slate-900 border border-gray-800 rounded-xl p-4 shadow-lg space-y-4">
      {/* 1. Main Search Bar & Mode Switcher */}
      <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        <div className="relative flex-1">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
            {isAiMode ? (
              <Sparkles className="w-5 h-5 text-indigo-400 animate-pulse" />
            ) : (
              <Search className="w-5 h-5 text-gray-400" />
            )}
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder={
              isAiMode
                ? "Ask natural language question (e.g. 'Show customers who requested visa services this month')..."
                : "Search by keyword, name, email, phone, reference code, status, ID..."
            }
            className={`w-full pl-10 pr-10 py-2.5 bg-slate-950 border rounded-lg text-sm text-gray-100 placeholder-gray-500 focus:outline-none transition-all ${
              isAiMode
                ? "border-indigo-500/60 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/20"
                : "border-gray-700 focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
            }`}
          />
          {query ? (
            <button
              onClick={() => onQueryChange("")}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-200"
              title="Clear query"
            >
              <X className="w-4 h-4" />
            </button>
          ) : null}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {onToggleAiMode ? (
            <button
              onClick={onToggleAiMode}
              className={`flex items-center gap-2 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isAiMode
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30 ring-1 ring-indigo-400"
                  : "bg-slate-800 text-indigo-300 hover:bg-slate-700 border border-indigo-900/50"
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>{isAiMode ? "AI Search Active" : "AI Natural Search"}</span>
            </button>
          ) : null}

          <button
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            className={`flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium border transition-colors ${
              showAdvancedFilters || hasActiveFilters
                ? "bg-slate-800 border-cyan-500 text-cyan-300"
                : "bg-slate-950 border-gray-800 text-gray-300 hover:bg-slate-800"
            }`}
          >
            <SlidersHorizontal className="w-4 h-4" />
            <span>Filters</span>
            {hasActiveFilters ? (
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
            ) : null}
          </button>

          {hasActiveFilters ? (
            <button
              onClick={onReset}
              className="flex items-center gap-1.5 px-3 py-2.5 rounded-lg text-sm font-medium bg-rose-950/40 text-rose-300 border border-rose-800/40 hover:bg-rose-900/40 transition-colors"
              title="Reset all filters"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          ) : null}
        </div>
      </div>

      {/* 2. Sample AI Prompt Suggestions (when in AI Mode) */}
      {isAiMode && onAiPromptSelect ? (
        <div className="bg-indigo-950/30 border border-indigo-900/40 rounded-lg p-3 space-y-2">
          <div className="text-xs font-semibold text-indigo-300 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Suggested Admin Prompts:</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {SAMPLE_AI_QUERIES.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => onAiPromptSelect(prompt)}
                className="text-xs px-2.5 py-1 rounded-md bg-indigo-900/50 hover:bg-indigo-800/60 text-indigo-200 border border-indigo-700/50 transition-colors text-left"
              >
                &ldquo;{prompt}&rdquo;
              </button>
            ))}
          </div>
        </div>
      ) : null}

      {/* 3. Advanced Filter & Sort Bar */}
      {showAdvancedFilters ? (
        <div className="pt-3 border-t border-gray-800 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Module Selector */}
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">
              Business Line / Module
            </label>
            <select
              value={selectedModule}
              onChange={(e) => onModuleChange(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-gray-700 rounded-lg text-sm text-gray-200 focus:outline-none focus:border-cyan-500"
            >
              {MODULE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Status Selector */}
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">
              Lifecycle Status
            </label>
            <select
              value={selectedStatus}
              onChange={(e) => onStatusChange(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-gray-700 rounded-lg text-sm text-gray-200 focus:outline-none focus:border-cyan-500"
            >
              {STATUS_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Sort By */}
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1 flex items-center gap-1">
              <ArrowUpDown className="w-3 h-3 text-gray-400" />
              <span>Sort By</span>
            </label>
            <select
              value={sortBy}
              onChange={(e) => onSortChange(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-gray-700 rounded-lg text-sm text-gray-200 focus:outline-none focus:border-cyan-500"
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Date Filter */}
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1 flex items-center gap-1">
              <Calendar className="w-3 h-3 text-gray-400" />
              <span>Date Range</span>
            </label>
            <div className="flex items-center gap-1.5">
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => onDateFromChange(e.target.value)}
                className="w-1/2 px-2 py-1.5 bg-slate-950 border border-gray-700 rounded-lg text-xs text-gray-200 focus:outline-none focus:border-cyan-500"
                title="From Date"
              />
              <span className="text-gray-500 text-xs">–</span>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => onDateToChange(e.target.value)}
                className="w-1/2 px-2 py-1.5 bg-slate-950 border border-gray-700 rounded-lg text-xs text-gray-200 focus:outline-none focus:border-cyan-500"
                title="To Date"
              />
            </div>
          </div>
        </div>
      ) : null}

      {/* 4. Facet Quick Chips (Module & Status Counts) */}
      {moduleFacets.length > 0 && (
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs no-scrollbar">
          <button
            onClick={() => onModuleChange("all")}
            className={`px-2.5 py-1 rounded-full whitespace-nowrap font-medium transition-colors ${
              selectedModule === "all"
                ? "bg-cyan-600 text-white"
                : "bg-slate-800 text-gray-300 hover:bg-slate-700 border border-gray-700"
            }`}
          >
            All ({pagination.total_count})
          </button>
          {moduleFacets.map((facet) => (
            <button
              key={facet.key}
              onClick={() => onModuleChange(facet.key)}
              className={`px-2.5 py-1 rounded-full whitespace-nowrap font-medium transition-colors ${
                selectedModule.toLowerCase() === facet.key.toLowerCase()
                  ? "bg-cyan-600 text-white"
                  : "bg-slate-800 text-gray-300 hover:bg-slate-700 border border-gray-700"
              }`}
            >
              {facet.label} ({facet.count})
            </button>
          ))}
        </div>
      )}

      {/* 5. Pagination & Result Summary Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-gray-800 text-xs text-gray-400">
        <div className="flex items-center gap-2">
          <span>
            Showing{" "}
            <strong className="text-gray-200">
              {pagination.total_count === 0
                ? 0
                : (pagination.page - 1) * pagination.page_size + 1}
            </strong>{" "}
            to{" "}
            <strong className="text-gray-200">
              {Math.min(
                pagination.page * pagination.page_size,
                pagination.total_count
              )}
            </strong>{" "}
            of <strong className="text-cyan-400">{pagination.total_count}</strong>{" "}
            results
          </span>

          {loading ? (
            <span className="flex items-center gap-1 text-cyan-400 animate-pulse ml-2">
              <RefreshCw className="w-3 h-3 animate-spin" />
              <span>Querying...</span>
            </span>
          ) : null}
        </div>

        {/* Page navigation */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 mr-2">
            <span>Per page:</span>
            <select
              value={pagination.page_size}
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
              className="bg-slate-950 border border-gray-700 rounded px-1.5 py-0.5 text-xs text-gray-200 focus:outline-none"
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>

          <button
            disabled={!pagination.has_prev || loading}
            onClick={() => onPageChange(pagination.page - 1)}
            className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-gray-200 border border-gray-700"
            title="Previous Page"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <span className="px-2 font-medium text-gray-200">
            Page {pagination.page} of {pagination.total_pages}
          </span>

          <button
            disabled={!pagination.has_next || loading}
            onClick={() => onPageChange(pagination.page + 1)}
            className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-gray-200 border border-gray-700"
            title="Next Page"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
