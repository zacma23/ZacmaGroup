"use client";

import React, { useState, useEffect } from "react";
import {
  MessageSquare,
  Search,
  Filter,
  Send,
  Bot,
  User,
  ShieldAlert,
  CheckCircle2,
  Clock,
  Headphones,
  Reply,
} from "lucide-react";

const SAMPLE_TICKETS = [
  {
    id: "tkt-001",
    subject: "Question about German Visa Document Verification",
    full_name: "Tigist Assefa",
    email: "tigist.a@example.com",
    channel: "web",
    category: "Visa",
    priority: "high",
    status: "Open",
    created_at: "2026-08-23T10:15:00Z",
    thread: [
      {
        id: "m1",
        sender_type: "client",
        sender_name: "Tigist Assefa",
        message: "Hello, does the embassy require certified translation of my bank statement into German?",
        created_at: "2026-08-23T10:15:00Z",
      },
      {
        id: "m2",
        sender_type: "ai",
        sender_name: "Zacma AI Assistant",
        message: "German embassy accepts English or German certified statements. If in Amharic, official translation is required.",
        created_at: "2026-08-23T10:15:05Z",
      },
    ],
  },
  {
    id: "tkt-002",
    subject: "Telegram Course Inquiry — Python Full-Stack lab schedule",
    full_name: "Abebe Tech (Telegram)",
    email: "abebe@t.me",
    channel: "telegram",
    category: "Training",
    priority: "medium",
    status: "InProgress",
    created_at: "2026-08-23T09:30:00Z",
    thread: [
      {
        id: "m1",
        sender_type: "client",
        sender_name: "@AbebeTech",
        message: "Can I take the Python programming classes during the weekend evening batch?",
        created_at: "2026-08-23T09:30:00Z",
      },
    ],
  },
  {
    id: "tkt-003",
    subject: "CBE Bank Transfer Confirmation Ref ZAC-VIS-4419",
    full_name: "Solomon Girma",
    email: "solomon.g@test.com",
    channel: "web",
    category: "Payments",
    priority: "high",
    status: "Open",
    created_at: "2026-08-23T08:00:00Z",
    thread: [
      {
        id: "m1",
        sender_type: "client",
        sender_name: "Solomon Girma",
        message: "Transferred 5,000 ETB via CBE Mobile. Transaction ref: ZACMA-2026-FT260814.",
        created_at: "2026-08-23T08:00:00Z",
      },
    ],
  },
];

export default function UnifiedInboxPage() {
  const [tickets, setTickets] = useState<any[]>(SAMPLE_TICKETS);
  const [selectedTicket, setSelectedTicket] = useState<any | null>(SAMPLE_TICKETS[0]);
  const [replyText, setReplyText] = useState("");
  const [sending, setSending] = useState(false);
  const [channelFilter, setChannelFilter] = useState<"all" | "web" | "telegram">("all");

  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

  const fetchTickets = async () => {
    try {
      const res = await fetch(`${apiBase}/api/v1/support/tickets`);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setTickets(data);
          if (!selectedTicket || !data.find((t: any) => t.id === selectedTicket.id)) {
            setSelectedTicket(data[0]);
          }
        }
      }
    } catch (err) {
      console.error("Inbox fetch tickets:", err);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, []);

  const handleSendReply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!replyText.trim() || !selectedTicket) return;
    setSending(true);

    try {
      const res = await fetch(`${apiBase}/api/v1/support/tickets/${selectedTicket.id}/reply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: replyText.trim(),
          status_update: "Resolved",
        }),
      });

      if (res.ok) {
        const updated = await res.json();
        setSelectedTicket(updated);
        setTickets((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
      } else {
        const newReply = {
          id: `m-${Date.now()}`,
          sender_type: "admin",
          sender_name: "Zacma Admin Support",
          message: replyText.trim(),
          created_at: new Date().toISOString(),
        };
        setSelectedTicket((prev: any) => ({
          ...prev,
          thread: [...(prev.thread || []), newReply],
          status: "Resolved",
        }));
        setTickets((prev) =>
          prev.map((t) =>
            t.id === selectedTicket.id
              ? { ...t, thread: [...(t.thread || []), newReply], status: "Resolved" }
              : t
          )
        );
      }
    } catch (err) {
      console.error(err);
    } finally {
      setReplyText("");
      setSending(false);
    }
  };

  const filtered =
    channelFilter === "all" ? tickets : tickets.filter((t) => t.channel === channelFilter);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
          <MessageSquare className="w-6 h-6 text-blue-400" />
          Unified Conversation & Ticket Inbox
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Monitor and respond to client inquiries originating from the Web Client Portal and Telegram Bot in one place.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Tickets Queue */}
        <div className="bg-slate-950/90 border border-slate-800 rounded-2xl p-4 space-y-4">
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">All Conversations</span>
            <div className="flex items-center gap-1 text-xs">
              {["all", "web", "telegram"].map((c) => (
                <button
                  key={c}
                  onClick={() => setChannelFilter(c as any)}
                  className={`px-2 py-1 rounded-lg capitalize ${
                    channelFilter === c ? "bg-slate-800 text-white font-bold" : "text-slate-500 hover:text-slate-300"
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            {filtered.map((t) => {
              const isSelected = selectedTicket?.id === t.id;
              return (
                <div
                  key={t.id}
                  onClick={() => setSelectedTicket(t)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? "bg-slate-800/90 border-blue-500 shadow-md"
                      : "bg-slate-900/60 border-slate-800 hover:bg-slate-900"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase">{t.category}</span>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                        t.channel === "telegram"
                          ? "bg-blue-950 text-blue-300 border border-blue-800"
                          : "bg-slate-800 text-slate-300"
                      }`}
                    >
                      {t.channel === "telegram" ? "Telegram Bot" : "Web Portal"}
                    </span>
                  </div>

                  <h4 className="text-xs font-bold text-white mt-1 line-clamp-1">{t.subject}</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5">{t.full_name}</p>

                  <div className="flex items-center justify-between pt-2 mt-2 border-t border-slate-800/80 text-[10px] text-slate-500">
                    <span>Status: {t.status}</span>
                    <span>{new Date(t.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Active Thread View & Admin Reply */}
        <div className="lg:col-span-2 bg-slate-950/90 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between space-y-4">
          {selectedTicket ? (
            <>
              {/* Thread Header */}
              <div className="pb-4 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{selectedTicket.full_name}</span>
                    <span className="text-xs text-slate-500 font-mono">({selectedTicket.email})</span>
                  </div>
                  <h3 className="text-sm font-bold text-slate-200 mt-0.5">{selectedTicket.subject}</h3>
                </div>
                <span className="px-2.5 py-1 bg-emerald-500/20 text-emerald-400 text-xs font-bold rounded-full border border-emerald-500/30">
                  {selectedTicket.status}
                </span>
              </div>

              {/* Messages Container */}
              <div className="flex-1 space-y-3 max-h-96 overflow-y-auto pr-2">
                {selectedTicket.thread?.map((msg: any) => {
                  const isAdmin = msg.sender_type === "admin";
                  const isAi = msg.sender_type === "ai";
                  return (
                    <div
                      key={msg.id}
                      className={`flex gap-3 ${isAdmin ? "justify-end" : "justify-start"}`}
                    >
                      {!isAdmin && (
                        <div
                          className={`w-7 h-7 rounded-full flex items-center justify-center text-xs flex-shrink-0 mt-0.5 ${
                            isAi ? "bg-blue-600 text-white" : "bg-slate-800 text-slate-300"
                          }`}
                        >
                          {isAi ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                        </div>
                      )}

                      <div
                        className={`p-3.5 rounded-2xl max-w-[80%] text-xs sm:text-sm space-y-1 ${
                          isAdmin
                            ? "bg-blue-600 text-white rounded-br-none"
                            : isAi
                            ? "bg-slate-800 text-slate-200 border border-slate-700"
                            : "bg-slate-900 text-slate-300 border border-slate-800"
                        }`}
                      >
                        <div className="flex items-center justify-between gap-4 text-[10px] text-slate-400">
                          <span className="font-bold text-slate-200">{msg.sender_name}</span>
                          {msg.created_at && (
                            <span>
                              {new Date(msg.created_at).toLocaleTimeString([], {
                                hour: "2-digit",
                                minute: "2-digit",
                              })}
                            </span>
                          )}
                        </div>
                        <p className="whitespace-pre-line leading-relaxed">{msg.message}</p>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Admin Reply Input */}
              <form onSubmit={handleSendReply} className="pt-3 border-t border-slate-800 flex items-center gap-2">
                <input
                  type="text"
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  placeholder="Type an official admin reply (takes over conversation)..."
                  className="flex-1 bg-slate-900 text-white placeholder-slate-500 text-xs sm:text-sm px-4 py-2.5 rounded-xl border border-slate-700 focus:border-blue-500 focus:outline-none"
                />
                <button
                  type="submit"
                  disabled={!replyText.trim() || sending}
                  className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl shadow transition-all flex items-center gap-1.5 disabled:opacity-40"
                >
                  <Reply className="w-3.5 h-3.5" />
                  <span>Reply</span>
                </button>
              </form>
            </>
          ) : (
            <div className="py-20 text-center text-xs text-slate-500">
              Select a conversation from the queue on the left to view details and reply.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
