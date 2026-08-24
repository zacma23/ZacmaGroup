"use client";

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { MessageSquare, X, Send, Bot, User, Sparkles, ArrowRight, ChevronDown } from "lucide-react";

interface ChatMessage {
  id: string;
  sender: "bot" | "user";
  text: string;
  time: string;
  actions?: Array<{ label: string; url: string }>;
  category?: string;
}

const INITIAL_GREETING: ChatMessage = {
  id: "msg-welcome",
  sender: "bot",
  text: "Hello! Welcome to Zacma. How may I help you today?\n\nI can assist you with:\n• 🎓 Course Registration (Programming, AI, Design, Video, Maintenance)\n• 🛂 Visa Services & Document Consultation\n• ✈️ Travel Booking & Itineraries\n• 📢 Marketing & Business Consulting\n• 💳 Payment & Invoicing Inquiries\n\nClick an option below or type your question!",
  time: "Just now",
  actions: [
    { label: "🎓 Course Registration", url: "/dashboard/training" },
    { label: "🛂 Visa Services", url: "/dashboard/visa" },
    { label: "✈️ Travel Services", url: "/dashboard/travel" },
    { label: "📢 Marketing Services", url: "/dashboard/marketing" },
    { label: "💳 Payment & Account", url: "/dashboard/payments" },
  ],
};

const SUGGESTION_CHIPS = [
  "What courses does Zacma offer?",
  "How do I apply for a visa?",
  "Plan a travel trip to Dubai",
  "What are the payment methods and account number?",
  "Tell me about marketing services",
];

export default function CustomerSupportChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([INITIAL_GREETING]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const query = (textToSend ?? input).trim();
    if (!query || loading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: query,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/api/v1/support/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: query }),
      });

      if (res.ok) {
        const data = await res.json();
        const botMsg: ChatMessage = {
          id: `bot-${Date.now()}`,
          sender: "bot",
          text: data.reply,
          actions: data.suggested_actions,
          category: data.category,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, botMsg]);
      } else {
        throw new Error("Chatbot API responded with an error");
      }
    } catch (e) {
      // Fallback response if backend is offline
      const fallbackReply = generateFallbackReply(query);
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-${Date.now()}`,
          sender: "bot",
          text: fallbackReply.text,
          actions: fallbackReply.actions,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const generateFallbackReply = (query: string) => {
    const q = query.toLowerCase();
    if (q.includes("visa")) {
      return {
        text: "Zacma Visa Assistant helps you with Tourist, Study, Work, and Business visas with AI document checks.",
        actions: [{ label: "Go to Visa Assistant", url: "/dashboard/visa" }],
      };
    }
    if (q.includes("course") || q.includes("training") || q.includes("program")) {
      return {
        text: "Zacma offers Programming, AI, Graphics Design, Video Editing, Web Design, Accounting, and Maintenance courses.",
        actions: [{ label: "Go to Course Registration", url: "/dashboard/training" }],
      };
    }
    if (q.includes("travel") || q.includes("flight") || q.includes("hotel")) {
      return {
        text: "Zacma Travel Agency provides full flight, hotel, and custom 5-day holiday itinerary planning.",
        actions: [{ label: "Go to Travel Agent", url: "/dashboard/travel" }],
      };
    }
    if (q.includes("pay") || q.includes("account") || q.includes("bank")) {
      return {
        text: "Official Receiving Account: 1000140145797 (Commercial Bank of Ethiopia). We also accept TeleBirr, Awash, and Abyssinia.",
        actions: [{ label: "Go to Payments & Invoicing", url: "/dashboard/payments" }],
      };
    }
    return {
      text: "Thank you for reaching out! How can I assist you with Zacma's Visa, Course Registration, Travel, Marketing, or Payment services?",
      actions: [
        { label: "Course Registration", url: "/dashboard/training" },
        { label: "Visa Services", url: "/dashboard/visa" },
        { label: "Travel Services", url: "/dashboard/travel" },
      ],
    };
  };

  return (
    <>
      {/* Floating Launcher Button */}
      <div className="fixed bottom-6 right-6 z-50">
        {!isOpen && (
          <button
            onClick={() => setIsOpen(true)}
            className="group relative flex items-center gap-3 px-4 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-full shadow-2xl transition-all duration-300 transform hover:scale-105 border border-blue-400/30"
            aria-label="Open Customer Support Chat"
          >
            <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-500"></span>
            </span>
            <div className="p-1 bg-white/20 rounded-full">
              <Bot className="w-5 h-5" />
            </div>
            <div className="text-left">
              <p className="text-xs font-semibold leading-tight">Zacma Assistant</p>
              <p className="text-[10px] text-blue-100 leading-tight">How may I help you?</p>
            </div>
          </button>
        )}
      </div>

      {/* Chat Window Container */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-full max-w-[400px] h-[580px] max-h-[90vh] bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-200">
          {/* Header */}
          <div className="p-4 bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 border-b border-slate-700/80 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-md">
                  <Bot className="w-5 h-5" />
                </div>
                <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-emerald-500 border-2 border-slate-900"></span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-white">Zacma Customer Support</h3>
                  <span className="px-1.5 py-0.5 text-[10px] font-medium bg-blue-500/20 text-blue-300 rounded border border-blue-500/30">
                    AI Bot
                  </span>
                </div>
                <p className="text-xs text-slate-400">Online · What can we help you with?</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              aria-label="Close Chat"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Message List */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-950/40 text-sm">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-2.5 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.sender === "bot" && (
                  <div className="w-7 h-7 rounded-full bg-blue-600/80 flex-shrink-0 flex items-center justify-center text-white text-xs mt-0.5 shadow-sm">
                    <Bot className="w-4 h-4" />
                  </div>
                )}
                <div className={`max-w-[82%] space-y-2`}>
                  <div
                    className={`p-3.5 rounded-2xl ${
                      msg.sender === "user"
                        ? "bg-blue-600 text-white rounded-br-none shadow-md"
                        : "bg-slate-800/90 text-slate-200 border border-slate-700/60 rounded-bl-none shadow-sm"
                    }`}
                  >
                    <p className="whitespace-pre-line leading-relaxed text-xs sm:text-sm">{msg.text}</p>
                  </div>

                  {/* Action buttons embedded in message */}
                  {msg.actions && msg.actions.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {msg.actions.map((act, idx) => (
                        <Link
                          key={idx}
                          href={act.url}
                          onClick={() => setIsOpen(false)}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs rounded-lg bg-indigo-950/80 hover:bg-indigo-900 text-indigo-200 border border-indigo-700/60 transition-all font-medium"
                        >
                          {act.label}
                          <ArrowRight className="w-3 h-3 text-indigo-400" />
                        </Link>
                      ))}
                    </div>
                  )}

                  <p
                    className={`text-[10px] px-1 text-slate-500 ${
                      msg.sender === "user" ? "text-right" : "text-left"
                    }`}
                  >
                    {msg.time}
                  </p>
                </div>
                {msg.sender === "user" && (
                  <div className="w-7 h-7 rounded-full bg-slate-700 flex-shrink-0 flex items-center justify-center text-slate-300 text-xs mt-0.5">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex gap-2.5 justify-start">
                <div className="w-7 h-7 rounded-full bg-blue-600/80 flex items-center justify-center text-white text-xs">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="p-3 bg-slate-800 border border-slate-700/60 rounded-2xl rounded-bl-none text-slate-400 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce"></span>
                  <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce [animation-delay:0.2s]"></span>
                  <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce [animation-delay:0.4s]"></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggestion Chips */}
          <div className="px-3 py-2 bg-slate-900 border-t border-slate-800/80 flex gap-1.5 overflow-x-auto no-scrollbar">
            {SUGGESTION_CHIPS.map((chip, i) => (
              <button
                key={i}
                onClick={() => handleSend(chip)}
                disabled={loading}
                className="whitespace-nowrap px-2.5 py-1 rounded-full text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 hover:border-slate-600 transition-colors flex-shrink-0"
              >
                {chip}
              </button>
            ))}
          </div>

          {/* Input Area */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="p-3 bg-slate-900 border-t border-slate-800 flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about courses, visas, travel, or payments..."
              className="flex-1 bg-slate-950 text-white placeholder-slate-500 text-xs sm:text-sm px-3.5 py-2.5 rounded-xl border border-slate-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="p-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600 text-white rounded-xl transition-all shadow-md flex-shrink-0"
              aria-label="Send message"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
