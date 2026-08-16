"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

interface PreviewContextValue {
  previewMode: boolean;
  customerName?: string | null;
  enterPreview: (name?: string | null) => void;
  exitPreview: () => void;
}

const STORAGE_KEY = "zacma_preview_mode";
const PreviewContext = createContext<PreviewContextValue | undefined>(undefined);

export function PreviewProvider({ children }: { children: React.ReactNode }) {
  const [previewMode, setPreviewMode] = useState(false);
  const [customerName, setCustomerName] = useState<string | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed?.previewMode) {
          setPreviewMode(true);
          setCustomerName(parsed.customerName ?? "Sample Customer");
        }
      }
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ previewMode, customerName }));
    } catch {
      // ignore
    }
  }, [previewMode, customerName]);

  function enterPreview(name?: string | null) {
    const cname = name ?? "Sample Customer";
    setCustomerName(cname);
    setPreviewMode(true);
    try {
      // persist as cookie so server components can read it
      document.cookie = `zacma_preview_customer=${encodeURIComponent(cname)}; path=/`;
    } catch {
      // ignore
    }
  }

  function exitPreview() {
    setCustomerName(null);
    setPreviewMode(false);
    try {
      // remove cookie
      document.cookie = `zacma_preview_customer=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
    } catch {
      // ignore
    }
  }

  const value: PreviewContextValue = {
    previewMode,
    customerName,
    enterPreview,
    exitPreview,
  };

  return <PreviewContext.Provider value={value}>{children}</PreviewContext.Provider>;
}

export function usePreview() {
  const ctx = useContext(PreviewContext);
  if (!ctx) throw new Error("usePreview must be used within PreviewProvider");
  return ctx;
}
