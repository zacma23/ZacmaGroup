import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";
import { PreviewProvider } from "../components/PreviewProvider";
import { SidebarProvider } from "../components/SidebarProvider";
import { AuthProvider } from "../components/AuthProvider";
import AppLayoutWrapper from "../components/AppLayoutWrapper";

export const metadata: Metadata = {
  title: "Zacma Technology Group — Client Portal & Business Platform",
  description: "Unified Client Portal for Visa Consulting, Travel Agency, Training Institute, and Marketing Services.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>
        <AuthProvider>
          <PreviewProvider>
            <SidebarProvider>
              <AppLayoutWrapper>{children}</AppLayoutWrapper>
            </SidebarProvider>
          </PreviewProvider>
        </AuthProvider>
      </body>
    </html>
  );
}

