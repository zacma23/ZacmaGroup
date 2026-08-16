"use client";

import React, { createContext, useContext, useState } from "react";

interface SidebarContextValue {
  open: boolean;
  setOpen: (v: boolean) => void;
  toggle: () => void;
}

const SidebarContext = createContext<SidebarContextValue | undefined>(undefined);

export function SidebarProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const toggle = () => setOpen((s) => !s);
  return <SidebarContext.Provider value={{ open, setOpen, toggle }}>{children}</SidebarContext.Provider>;
}

export function useSidebar() {
  const ctx = useContext(SidebarContext);
  if (!ctx) throw new Error("useSidebar must be used within SidebarProvider");
  return ctx;
}
