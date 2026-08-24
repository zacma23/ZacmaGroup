"use client";

import React, { useEffect, useState } from "react";
import {
  CreditCard,
  Building,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Clock,
  RefreshCw,
  Plus,
  Edit3,
  Search,
  Filter,
  DollarSign,
  ArrowUpRight,
  TrendingUp,
  AlertTriangle,
  Lock,
  Layers,
  Activity,
  Zap,
  Check,
  ExternalLink,
} from "lucide-react";

interface ProviderBalance {
  provider_id: string;
  provider_name: string;
  provider_code: string;
  provider_type: string;
  is_active: boolean;
  currency: string;
  supports_balance_api: boolean;
  balance_available_from_api: boolean;
  provider_reported_balance: number | null;
  internal_platform_balance: number;
  pending_balance: number;
  status_message: string;
}

interface BalanceSummary {
  total_received: number;
  pending_balance: number;
  available_balance: number;
  total_transferred: number;
  total_refunded: number;
  total_volume: number;
  today_transactions_count: number;
  today_transactions_volume: number;
  month_transactions_count: number;
  month_transactions_volume: number;
  successful_count: number;
  failed_count: number;
  currency: string;
  provider_balances: ProviderBalance[];
}

interface TransactionItem {
  id: string;
  public_reference: string;
  customer_name: string;
  customer_email?: string;
  customer_phone?: string;
  provider_code: string;
  payment_method: string;
  amount: number;
  fee: number;
  net_amount: number;
  currency: string;
  status: string;
  payment_purpose: string;
  description?: string;
  provider_transaction_id?: string;
  provider_reference?: string;
  checkout_url?: string;
  verification_status?: string;
  created_at: string;
  completed_at?: string;
}

interface ProviderItem {
  id: string;
  provider_name: string;
  provider_code: string;
  provider_type: string;
  is_active: boolean;
  is_default: boolean;
  priority: number;
  environment: string;
  currency: string;
  account_name?: string;
  account_number?: string;
  customer_payment_number?: string;
  instructions?: string;
  api_endpoint?: string;
  callback_url?: string;
  webhook_url?: string;
  supports_balance_api: boolean;
  transaction_fee_percent: number;
  transaction_fee_fixed: number;
  has_secret_key: boolean;
  masked_secret_key?: string;
  masked_api_key?: string;
  merchant_id?: string;
}

export default function PaymentsPlatformPage() {
  const [activeTab, setActiveTab] = useState<"balance" | "transactions" | "providers">("balance");
  const [loading, setLoading] = useState<boolean>(true);
  const [balanceData, setBalanceData] = useState<BalanceSummary | null>(null);
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [providers, setProviders] = useState<ProviderItem[]>([]);

  // Search & Filters
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [providerFilter, setProviderFilter] = useState<string>("all");

  // Add / Edit Provider Modal
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [editingProvider, setEditingProvider] = useState<ProviderItem | null>(null);
  const [formData, setFormData] = useState<any>({
    provider_name: "",
    provider_code: "",
    provider_type: "bank_transfer",
    is_active: true,
    is_default: false,
    environment: "test",
    currency: "ETB",
    account_name: "",
    account_number: "",
    customer_payment_number: "",
    instructions: "",
    api_endpoint: "",
    secret_key: "",
    api_key: "",
    merchant_id: "",
    webhook_secret: "",
    transaction_fee_percent: 0.0,
  });

  const [actionNotice, setActionNotice] = useState<string | null>(null);
  const [testingId, setTestingId] = useState<string | null>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const fetchData = async () => {
    setLoading(true);
    try {
      // 1. Balances
      const balRes = await fetch(`${apiBase}/api/v1/payments/admin/balances`);
      if (balRes.ok) {
        setBalanceData(await balRes.json());
      }

      // 2. Transactions
      const txRes = await fetch(`${apiBase}/api/v1/payments/admin/transactions`);
      if (txRes.ok) {
        setTransactions(await txRes.json());
      }

      // 3. Providers
      const provRes = await fetch(`${apiBase}/api/v1/payments/admin/providers`);
      if (provRes.ok) {
        setProviders(await provRes.json());
      }
    } catch (err) {
      console.error("Error fetching payments data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleTestConnection = async (providerId: string) => {
    setTestingId(providerId);
    setActionNotice(null);
    try {
      const res = await fetch(`${apiBase}/api/v1/payments/admin/providers/${providerId}/test`, {
        method: "POST",
      });
      const data = await res.json();
      setActionNotice(data.message || (data.success ? "Connection successful!" : "Test failed"));
    } catch (err: any) {
      setActionNotice(`Test error: ${err.message}`);
    } finally {
      setTestingId(null);
    }
  };

  const handleToggleActive = async (prov: ProviderItem) => {
    try {
      await fetch(`${apiBase}/api/v1/payments/admin/providers/${prov.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !prov.is_active }),
      });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleVerifyTransaction = async (publicRef: string) => {
    try {
      const res = await fetch(`${apiBase}/api/v1/payments/admin/transactions/${publicRef}/verify`, {
        method: "POST",
      });
      const data = await res.json();
      setActionNotice(data.message);
      fetchData();
    } catch (err: any) {
      setActionNotice(`Verification error: ${err.message}`);
    }
  };

  const handleSaveProvider = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingProvider) {
        await fetch(`${apiBase}/api/v1/payments/admin/providers/${editingProvider.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        });
        setActionNotice(`Provider '${formData.provider_name}' updated successfully.`);
      } else {
        await fetch(`${apiBase}/api/v1/payments/admin/providers`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        });
        setActionNotice(`Provider '${formData.provider_name}' created successfully.`);
      }
      setShowAddModal(false);
      setEditingProvider(null);
      fetchData();
    } catch (err: any) {
      setActionNotice(`Save error: ${err.message}`);
    }
  };

  const openEditModal = (p: ProviderItem) => {
    setEditingProvider(p);
    setFormData({
      provider_name: p.provider_name,
      provider_code: p.provider_code,
      provider_type: p.provider_type,
      is_active: p.is_active,
      is_default: p.is_default,
      environment: p.environment,
      currency: p.currency,
      account_name: p.account_name || "",
      account_number: p.account_number || "",
      customer_payment_number: p.customer_payment_number || "",
      instructions: p.instructions || "",
      api_endpoint: p.api_endpoint || "",
      secret_key: "",
      api_key: "",
      merchant_id: p.merchant_id || "",
      webhook_secret: "",
      transaction_fee_percent: p.transaction_fee_percent,
    });
    setShowAddModal(true);
  };

  const filteredTransactions = transactions.filter((t) => {
    const matchesSearch =
      t.public_reference.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (t.customer_email || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
      (t.provider_reference || "").toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === "all" || t.status.toLowerCase() === statusFilter.toLowerCase();
    const matchesProvider = providerFilter === "all" || t.provider_code.toLowerCase() === providerFilter.toLowerCase();

    return matchesSearch && matchesStatus && matchesProvider;
  });

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-2xl">
            <CreditCard className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">Payment Management Platform</h1>
            <p className="text-xs text-slate-400">
              Provider-based multi-channel payment gateway, balance analytics & dynamic bank management.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => setActiveTab("balance")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
              activeTab === "balance"
                ? "bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20"
                : "bg-slate-800 text-slate-300 hover:text-white"
            }`}
          >
            Balance & Overview
          </button>
          <button
            onClick={() => setActiveTab("transactions")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
              activeTab === "transactions"
                ? "bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20"
                : "bg-slate-800 text-slate-300 hover:text-white"
            }`}
          >
            Transactions Ledger ({transactions.length})
          </button>
          <button
            onClick={() => setActiveTab("providers")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
              activeTab === "providers"
                ? "bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/20"
                : "bg-slate-800 text-slate-300 hover:text-white"
            }`}
          >
            Providers & Settings ({providers.length})
          </button>
          <button
            onClick={fetchData}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs transition"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {actionNotice && (
        <div className="p-4 bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-xs rounded-2xl flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>{actionNotice}</span>
          </div>
          <button onClick={() => setActionNotice(null)} className="text-slate-400 hover:text-white">
            ✕
          </button>
        </div>
      )}

      {/* TAB 1: BALANCE & OVERVIEW */}
      {activeTab === "balance" && (
        <div className="space-y-6">
          {/* Top Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl bg-slate-900 border border-emerald-500/30 space-y-2 shadow-lg">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-semibold uppercase tracking-wider">Available Balance</span>
                <DollarSign className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-black text-white font-mono">
                {balanceData?.available_balance.toLocaleString() || "0.00"} <span className="text-xs text-emerald-400">ETB</span>
              </div>
              <p className="text-[11px] text-slate-400">Total verified net platform balance</p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900 border border-amber-500/30 space-y-2 shadow-lg">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-semibold uppercase tracking-wider">Pending Balance</span>
                <Clock className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-2xl font-black text-amber-300 font-mono">
                {balanceData?.pending_balance.toLocaleString() || "0.00"} <span className="text-xs text-amber-400">ETB</span>
              </div>
              <p className="text-[11px] text-slate-400">Awaiting bank verification & checkout completion</p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900 border border-blue-500/30 space-y-2 shadow-lg">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-semibold uppercase tracking-wider">Total Received</span>
                <TrendingUp className="w-4 h-4 text-blue-400" />
              </div>
              <div className="text-2xl font-black text-blue-300 font-mono">
                {balanceData?.total_received.toLocaleString() || "0.00"} <span className="text-xs text-blue-400">ETB</span>
              </div>
              <p className="text-[11px] text-slate-400">Lifetime successfully processed volume</p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2 shadow-lg">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-semibold uppercase tracking-wider">Transaction Success</span>
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-black text-white font-mono">
                {balanceData?.successful_count || 0}{" "}
                <span className="text-xs text-slate-400 font-normal">/ {(balanceData?.successful_count || 0) + (balanceData?.failed_count || 0)}</span>
              </div>
              <p className="text-[11px] text-slate-400">{balanceData?.failed_count || 0} failed or cancelled</p>
            </div>
          </div>

          {/* Provider-Reported vs Internal Platform Balance Breakdown */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Building className="w-4 h-4 text-emerald-400" /> Provider Balance Breakdown
                </h3>
                <p className="text-xs text-slate-400">
                  Explicitly differentiates between provider API-reported balance and internal platform ledger balance.
                </p>
              </div>
              <span className="px-3 py-1 bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded-xl font-mono">
                Active Providers: {providers.filter((p) => p.is_active).length}
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 font-bold uppercase tracking-wider border-b border-slate-800">
                  <tr>
                    <th className="p-3.5">Provider</th>
                    <th className="p-3.5">Type & Mode</th>
                    <th className="p-3.5">Provider API Balance</th>
                    <th className="p-3.5">Internal Platform Ledger</th>
                    <th className="p-3.5">Pending Amount</th>
                    <th className="p-3.5">Status & API State</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-medium">
                  {balanceData?.provider_balances.map((pb) => (
                    <tr key={pb.provider_id} className="hover:bg-slate-800/40 transition">
                      <td className="p-3.5 font-bold text-white">
                        <div className="flex items-center gap-2">
                          <span>{pb.provider_name}</span>
                          {pb.is_active ? (
                            <span className="w-2 h-2 rounded-full bg-emerald-400" title="Active" />
                          ) : (
                            <span className="w-2 h-2 rounded-full bg-slate-600" title="Inactive" />
                          )}
                        </div>
                        <div className="text-[10px] text-slate-400 font-mono uppercase">{pb.provider_code}</div>
                      </td>

                      <td className="p-3.5">
                        <span className="px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 text-[10px] font-mono capitalize">
                          {pb.provider_type.replace("_", " ")}
                        </span>
                      </td>

                      <td className="p-3.5 font-mono">
                        {pb.balance_available_from_api && pb.provider_reported_balance !== null ? (
                          <span className="text-emerald-300 font-bold">
                            {pb.provider_reported_balance.toLocaleString()} {pb.currency}
                          </span>
                        ) : (
                          <span className="text-slate-500 italic text-[11px]">
                            Balance unavailable from provider API
                          </span>
                        )}
                      </td>

                      <td className="p-3.5 font-mono font-bold text-white">
                        {pb.internal_platform_balance.toLocaleString()} {pb.currency}
                      </td>

                      <td className="p-3.5 font-mono text-amber-300">
                        {pb.pending_balance.toLocaleString()} {pb.currency}
                      </td>

                      <td className="p-3.5">
                        <span className="text-[11px] text-slate-400">{pb.status_message}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: TRANSACTIONS LEDGER */}
      {activeTab === "transactions" && (
        <div className="space-y-4">
          {/* Search and Filters */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
              <input
                type="text"
                placeholder="Search reference, customer, email..."
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
              <option value="successful">Successful</option>
              <option value="pending">Pending</option>
              <option value="initiated">Initiated</option>
              <option value="failed">Failed</option>
            </select>

            <select
              value={providerFilter}
              onChange={(e) => setProviderFilter(e.target.value)}
              className="px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="all">All Providers</option>
              <option value="chapa">Chapa</option>
              <option value="cbe">CBE</option>
              <option value="telebirr">TeleBirr</option>
              <option value="awash">Awash Bank</option>
            </select>
          </div>

          {/* Ledger Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 font-bold uppercase tracking-wider border-b border-slate-800">
                  <tr>
                    <th className="p-4">Reference</th>
                    <th className="p-4">Customer</th>
                    <th className="p-4">Provider / Method</th>
                    <th className="p-4">Amount & Net</th>
                    <th className="p-4">Status</th>
                    <th className="p-4">Date</th>
                    <th className="p-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredTransactions.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="p-8 text-center text-slate-500">
                        {loading ? "Loading ledger..." : "No payment transactions match your query."}
                      </td>
                    </tr>
                  ) : (
                    filteredTransactions.map((tx) => (
                      <tr key={tx.id} className="hover:bg-slate-800/40 transition">
                        <td className="p-4">
                          <div className="font-mono font-bold text-amber-400 text-sm">{tx.public_reference}</div>
                          <div className="text-[10px] text-slate-400">{tx.payment_purpose}</div>
                        </td>

                        <td className="p-4">
                          <div className="font-bold text-white">{tx.customer_name}</div>
                          <div className="text-slate-400">{tx.customer_email || tx.customer_phone || "—"}</div>
                        </td>

                        <td className="p-4">
                          <div className="font-semibold text-emerald-400">{tx.payment_method}</div>
                          <div className="text-[10px] text-slate-500 uppercase">{tx.provider_code}</div>
                        </td>

                        <td className="p-4 font-mono">
                          <div className="font-bold text-white">
                            {tx.amount.toLocaleString()} {tx.currency}
                          </div>
                          {tx.fee > 0 && <div className="text-[10px] text-slate-400">Fee: {tx.fee} ETB</div>}
                        </td>

                        <td className="p-4">
                          <span
                            className={`px-2.5 py-1 rounded-full text-xs font-bold border ${
                              tx.status === "successful"
                                ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                                : tx.status === "failed"
                                ? "bg-rose-500/20 text-rose-300 border-rose-500/30"
                                : "bg-amber-500/20 text-amber-300 border-amber-500/30"
                            }`}
                          >
                            {tx.status}
                          </span>
                        </td>

                        <td className="p-4 text-slate-400 text-[11px]">
                          {new Date(tx.created_at).toLocaleDateString()}
                        </td>

                        <td className="p-4 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            {tx.status !== "successful" && (
                              <button
                                onClick={() => handleVerifyTransaction(tx.public_reference)}
                                className="px-2.5 py-1 bg-emerald-950/80 border border-emerald-700 hover:bg-emerald-900 text-emerald-300 rounded-lg text-xs font-bold transition"
                                title="Server-side Verify"
                              >
                                Verify
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: PROVIDERS & SETTINGS */}
      {activeTab === "providers" && (
        <div className="space-y-4">
          {/* Telegram Payment Bot Banner */}
          <div className="p-4 bg-gradient-to-r from-blue-950/60 to-slate-900 border border-blue-500/30 rounded-3xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl">
            <div className="flex items-center gap-3.5">
              <div className="p-2.5 bg-blue-600/20 text-blue-400 rounded-2xl border border-blue-500/30">
                <Zap className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-bold text-white">Telegram Payment & Support Bot</h4>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    LIVE & CONNECTED
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Bot: <span className="font-mono text-blue-300 font-bold">@ZacmaBusinessSupportAI_bot</span> · Dispatches interactive invoices & receipts directly to Telegram
                </p>
              </div>
            </div>

            <button
              onClick={async () => {
                try {
                  const res = await fetch(`${apiBase}/api/v1/support/telegram/bot-info`);
                  const data = await res.json();
                  setActionNotice(data.ok ? `Telegram Bot @${data.result?.username} is active and responding!` : "Telegram Bot check failed");
                } catch (e: any) {
                  setActionNotice(`Telegram error: ${e.message}`);
                }
              }}
              className="px-3.5 py-1.5 bg-blue-600/20 hover:bg-blue-600 text-blue-300 hover:text-white rounded-xl text-xs font-bold border border-blue-500/30 transition flex items-center gap-1.5"
            >
              <ExternalLink className="w-3.5 h-3.5" /> Check Bot Status
            </button>
          </div>

          <div className="flex justify-between items-center bg-slate-900/50 p-4 rounded-2xl border border-slate-800">
            <div>
              <h3 className="text-sm font-bold text-white">Configured Payment Providers</h3>
              <p className="text-xs text-slate-400">
                Add and manage payment channels. Secret credentials are encrypted and never sent to clients.
              </p>
            </div>
            <button
              onClick={() => {
                setEditingProvider(null);
                setFormData({
                  provider_name: "",
                  provider_code: "",
                  provider_type: "bank_transfer",
                  is_active: true,
                  is_default: false,
                  environment: "test",
                  currency: "ETB",
                  account_name: "",
                  account_number: "",
                  customer_payment_number: "",
                  instructions: "",
                  api_endpoint: "",
                  secret_key: "",
                  api_key: "",
                  merchant_id: "",
                  webhook_secret: "",
                  transaction_fee_percent: 0.0,
                });
                setShowAddModal(true);
              }}
              className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl text-xs flex items-center gap-1.5 transition shadow-lg shadow-emerald-500/20"
            >
              <Plus className="w-4 h-4" /> Add Payment Provider
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {providers.map((p) => (
              <div
                key={p.id}
                className={`p-5 rounded-3xl border transition bg-slate-900 ${
                  p.is_active ? "border-slate-800 shadow-xl" : "border-slate-800/40 opacity-70"
                }`}
              >
                <div className="flex items-start justify-between gap-3 border-b border-slate-800 pb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-bold text-white text-base">{p.provider_name}</h4>
                      {p.is_default && (
                        <span className="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-bold border border-amber-500/30">
                          Default
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 font-mono mt-0.5 uppercase">{p.provider_code} • {p.provider_type}</p>
                  </div>

                  <span
                    className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${
                      p.is_active
                        ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                        : "bg-slate-800 text-slate-400 border-slate-700"
                    }`}
                  >
                    {p.is_active ? "ACTIVE" : "DISABLED"}
                  </span>
                </div>

                <div className="space-y-2 py-3 text-xs text-slate-300">
                  {p.account_number && (
                    <div className="flex justify-between">
                      <span className="text-slate-400">Account Number:</span>
                      <span className="font-mono font-bold text-emerald-400">{p.account_number}</span>
                    </div>
                  )}
                  {p.account_name && (
                    <div className="flex justify-between">
                      <span className="text-slate-400">Account Name:</span>
                      <span className="font-medium text-white">{p.account_name}</span>
                    </div>
                  )}
                  {p.customer_payment_number && (
                    <div className="flex justify-between">
                      <span className="text-slate-400">Payment / Merchant No:</span>
                      <span className="font-mono text-amber-300">{p.customer_payment_number}</span>
                    </div>
                  )}
                  {p.masked_secret_key && (
                    <div className="flex justify-between">
                      <span className="text-slate-400 flex items-center gap-1">
                        <Lock className="w-3 h-3 text-emerald-400" /> Secret Key:
                      </span>
                      <span className="font-mono text-slate-400">{p.masked_secret_key}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-slate-400">Environment:</span>
                    <span className="font-mono uppercase text-blue-300 font-bold">{p.environment}</span>
                  </div>
                  {p.instructions && (
                    <p className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 text-[11px] text-slate-400 line-clamp-2">
                      {p.instructions}
                    </p>
                  )}
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-slate-800 gap-2">
                  <button
                    onClick={() => handleTestConnection(p.id)}
                    disabled={testingId === p.id}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition"
                  >
                    <Zap className={`w-3.5 h-3.5 ${testingId === p.id ? "animate-spin text-amber-400" : "text-amber-400"}`} />
                    <span>{testingId === p.id ? "Testing..." : "Test Connection"}</span>
                  </button>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleToggleActive(p)}
                      className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                        p.is_active
                          ? "bg-rose-950/60 border border-rose-800 hover:bg-rose-900 text-rose-300"
                          : "bg-emerald-950/60 border border-emerald-800 hover:bg-emerald-900 text-emerald-300"
                      }`}
                    >
                      {p.is_active ? "Disable" : "Enable"}
                    </button>
                    <button
                      onClick={() => openEditModal(p)}
                      className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs transition"
                      title="Edit Provider Settings"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add / Edit Provider Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-white">
                {editingProvider ? `Edit Provider: ${editingProvider.provider_name}` : "Add Payment Provider"}
              </h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveProvider} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-semibold">Provider Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Chapa or CBE"
                    value={formData.provider_name}
                    onChange={(e) => setFormData({ ...formData, provider_name: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1 font-semibold">Provider Code *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. chapa or cbe"
                    value={formData.provider_code}
                    onChange={(e) => setFormData({ ...formData, provider_code: e.target.value.toLowerCase() })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-semibold">Provider Type</label>
                  <select
                    value={formData.provider_type}
                    onChange={(e) => setFormData({ ...formData, provider_type: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="gateway">Online Gateway (Hosted Checkout)</option>
                    <option value="bank_transfer">Bank Transfer</option>
                    <option value="mobile_money">Mobile Money (Telebirr / Wallets)</option>
                    <option value="custom">Custom Provider</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1 font-semibold">Environment</label>
                  <select
                    value={formData.environment}
                    onChange={(e) => setFormData({ ...formData, environment: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="test">Test / Sandbox</option>
                    <option value="live">Live / Production</option>
                  </select>
                </div>
              </div>

              {/* Bank Transfer / Mobile Money Specific Info */}
              <div className="p-3.5 bg-slate-950 rounded-2xl border border-slate-800 space-y-3">
                <span className="font-bold text-slate-300 block">Customer-Facing Account Information</span>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-400 mb-1">Account Name</label>
                    <input
                      type="text"
                      placeholder="e.g. Zacma Group PLC"
                      value={formData.account_name}
                      onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Account Number</label>
                    <input
                      type="text"
                      placeholder="Configurable account number"
                      value={formData.account_number}
                      onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Customer Payment / Merchant Number</label>
                  <input
                    type="text"
                    placeholder="e.g. +251911000001 or CBE-PAY-CODE"
                    value={formData.customer_payment_number}
                    onChange={(e) => setFormData({ ...formData, customer_payment_number: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
              </div>

              {/* API Credentials */}
              <div className="p-3.5 bg-slate-950 rounded-2xl border border-slate-800 space-y-3">
                <span className="font-bold text-slate-300 flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-amber-400" /> Secure API Credentials
                </span>
                <div>
                  <label className="block text-slate-400 mb-1">Secret Key (CHAPA_SECRET_KEY / Private Key)</label>
                  <input
                    type="password"
                    placeholder={editingProvider?.has_secret_key ? "•••••••••••• (Leave blank to keep existing)" : "Enter Secret Key"}
                    value={formData.secret_key}
                    onChange={(e) => setFormData({ ...formData, secret_key: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-slate-400 mb-1">Public / API Key</label>
                    <input
                      type="text"
                      placeholder="Public API Key"
                      value={formData.api_key}
                      onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Merchant ID</label>
                    <input
                      type="text"
                      placeholder="Merchant ID"
                      value={formData.merchant_id}
                      onChange={(e) => setFormData({ ...formData, merchant_id: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-emerald-500 font-mono"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Custom Customer Payment Instructions</label>
                <textarea
                  rows={2}
                  placeholder="Instructions displayed to clients upon checkout..."
                  value={formData.instructions}
                  onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 cursor-pointer text-slate-300">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="rounded text-emerald-500 focus:ring-emerald-500"
                  />
                  <span>Active Provider</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer text-slate-300">
                  <input
                    type="checkbox"
                    checked={formData.is_default}
                    onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                    className="rounded text-amber-500 focus:ring-amber-500"
                  />
                  <span>Set as Default</span>
                </label>
              </div>

              <div className="flex gap-2 pt-2 border-t border-slate-800">
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl transition"
                >
                  {editingProvider ? "Save Provider Changes" : "Create Provider"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
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
