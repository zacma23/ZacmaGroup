"use client";

import React, { ReactNode } from "react";
import { usePathname } from "next/navigation";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";
import PreviewBanner from "./PreviewBanner";
import ClientHeader from "./ClientHeader";
import ClientFooter from "./ClientFooter";
import CustomerSupportChatbot from "./CustomerSupportChatbot";

export default function AppLayoutWrapper({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const isAdminDashboard = pathname.startsWith("/dashboard");

  if (isAdminDashboard) {
    return (
      <div className="min-h-screen flex text-gray-100 bg-slate-950">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <TopBar />
          <PreviewBanner />
          <main className="p-4 sm:p-6 bg-slate-900 min-h-[calc(100vh-56px)] flex-1 overflow-x-hidden">
            {children}
          </main>
        </div>
        <CustomerSupportChatbot />
      </div>
    );
  }

  // Public Client-Facing Portal Layout
  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 antialiased selection:bg-red-600 selection:text-white">
      <ClientHeader />
      <main className="flex-1 w-full">{children}</main>
      <ClientFooter />
      <CustomerSupportChatbot />
    </div>
  );
}
