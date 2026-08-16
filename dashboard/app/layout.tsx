import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";
import TopBar from "../components/TopBar";
import Sidebar from "../components/Sidebar";
import { PreviewProvider } from "../components/PreviewProvider";
import PreviewBanner from "../components/PreviewBanner";
import { SidebarProvider } from "../components/SidebarProvider";
import { AuthProvider } from "../components/AuthProvider";

export const metadata: Metadata = {
  title: "ZACMA Operations Dashboard",
  description: "Local operations overview for the ZACMA Group AI Platform.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <PreviewProvider>
            <SidebarProvider>
              <div className="min-h-screen flex text-gray-100">
                <Sidebar />
                <div className="flex-1 flex flex-col">
                  <TopBar />
                  <PreviewBanner />
                  <main className="p-6 bg-slate-900 min-h-[calc(100vh-56px)]">{children}</main>
                </div>
              </div>
            </SidebarProvider>
          </PreviewProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
