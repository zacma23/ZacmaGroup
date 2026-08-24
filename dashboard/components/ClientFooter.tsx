"use client";

import React from "react";
import Link from "next/link";
import {
  ShieldCheck,
  Plane,
  GraduationCap,
  Megaphone,
  Mail,
  Phone,
  MapPin,
  Send,
  CreditCard,
  Building2,
  ExternalLink,
  HeartHandshake,
} from "lucide-react";

export default function ClientFooter() {
  return (
    <footer className="bg-slate-950 border-t border-slate-800 text-slate-400 text-sm">
      {/* Official Payment Accounts Highlight Bar */}
      <div className="bg-gradient-to-r from-blue-950 via-slate-900 to-indigo-950 border-b border-slate-800/80 py-6 px-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-left">
            <div className="p-3 bg-emerald-600/20 rounded-xl border border-emerald-500/30 text-emerald-400">
              <CreditCard className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider font-semibold text-emerald-300">
                Automated Payment Gateway
              </p>
              <p className="text-lg font-bold text-white font-mono tracking-wide">
                Chapa Direct Secure Checkout <span className="text-xs text-slate-300 font-sans font-normal">(Instant Settlement & Verification)</span>
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="px-3 py-1.5 bg-slate-900 border border-slate-700/70 rounded-lg text-slate-300 font-medium">
              📱 TeleBirr
            </span>
            <span className="px-3 py-1.5 bg-slate-900 border border-slate-700/70 rounded-lg text-slate-300 font-medium">
              🏦 CBE Birr
            </span>
            <span className="px-3 py-1.5 bg-slate-900 border border-slate-700/70 rounded-lg text-slate-300 font-medium">
              🏦 Awash Bank
            </span>
            <span className="px-3 py-1.5 bg-slate-900 border border-slate-700/70 rounded-lg text-slate-300 font-medium">
              🏛️ Bank of Abyssinia
            </span>
            <Link
              href="/track"
              className="px-3 py-1.5 bg-emerald-600/90 hover:bg-emerald-600 text-white rounded-lg font-semibold transition-colors"
            >
              Track Payment →
            </Link>
          </div>
        </div>
      </div>

      {/* Main Footer Links */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Brand Intro */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-red-600 to-indigo-900 flex items-center justify-center text-white font-black text-xl border border-red-500/40">
                Z
              </div>
              <span className="text-lg font-black text-white tracking-tight">
                <span className="text-red-500">ZACMA</span> TECHNOLOGY GROUP
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed max-w-sm">
              Zacma Technology Group is a multi-disciplinary business solutions corporation operating premier
              services in international visa consulting, accredited career training, corporate travel management, and
              digital growth marketing.
            </p>
            <div className="flex items-center gap-3 pt-2">
              <a
                href="https://t.me/ZacmaGroup"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-950 border border-blue-800 text-blue-300 hover:text-white text-xs font-semibold transition-colors"
              >
                <Send className="w-3.5 h-3.5" />
                Telegram Channel
              </a>
              <a
                href="https://zacmaa.net"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-300 hover:text-white text-xs font-medium transition-colors"
              >
                <ExternalLink className="w-3.5 h-3.5" />
                zacmaa.net
              </a>
            </div>
          </div>

          {/* Sub-Brands */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-white">Our Sub-Brands</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/visa" className="hover:text-white flex items-center gap-1.5 transition-colors">
                  <ShieldCheck className="w-3.5 h-3.5 text-red-400" />
                  Zacma Visa Assistant
                </Link>
              </li>
              <li>
                <Link href="/travel" className="hover:text-white flex items-center gap-1.5 transition-colors">
                  <Plane className="w-3.5 h-3.5 text-blue-400" />
                  Zacma Travel Agent
                </Link>
              </li>
              <li>
                <Link href="/training" className="hover:text-white flex items-center gap-1.5 transition-colors">
                  <GraduationCap className="w-3.5 h-3.5 text-emerald-400" />
                  Zacma Training
                </Link>
              </li>
              <li>
                <Link href="/marketing" className="hover:text-white flex items-center gap-1.5 transition-colors">
                  <Megaphone className="w-3.5 h-3.5 text-purple-400" />
                  Zacma Marketing
                </Link>
              </li>
            </ul>
          </div>

          {/* Client Quick Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-white">Client Portal</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/track" className="hover:text-white transition-colors">
                  Track My Request
                </Link>
              </li>
              <li>
                <Link href="/portal" className="hover:text-white transition-colors">
                  Client Dashboard Login
                </Link>
              </li>
              <li>
                <Link href="/contact" className="hover:text-white transition-colors">
                  Customer Support & Help
                </Link>
              </li>
              <li>
                <Link href="/dashboard/crm" className="hover:text-white transition-colors">
                  Admin Back-Office Portal
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact Details */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-white">Contact & Office</h4>
            <ul className="space-y-2 text-xs">
              <li className="flex items-start gap-2">
                <MapPin className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                <span>Bole Sub-City, Addis Ababa, Ethiopia</span>
              </li>
              <li className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-blue-400 flex-shrink-0" />
                <span>+251-911-223344 / +251-922-334455</span>
              </li>
              <li className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>support@zacmaa.net</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom copyright */}
        <div className="mt-12 pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
          <p>© {new Date().getFullYear()} Zacma Technology Group. All rights reserved.</p>
          <div className="flex items-center gap-4 text-xs">
            <Link href="/contact" className="hover:text-slate-400">
              Privacy Policy
            </Link>
            <span>·</span>
            <Link href="/contact" className="hover:text-slate-400">
              Terms of Service
            </Link>
            <span>·</span>
            <a href="https://zacmaa.net" target="_blank" rel="noreferrer" className="hover:text-slate-400">
              zacmaa.net
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
