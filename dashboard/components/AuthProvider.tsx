"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

interface AuthContextValue {
  role: string | null;
  email?: string | null;
  login: (role: string, email?: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);
const STORAGE_KEY = "zacma_user";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [role, setRole] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        setRole(parsed.role ?? null);
        setEmail(parsed.email ?? null);
      }
    } catch {}
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ role, email }));
    } catch {}
  }, [role, email]);

  function setCookieRole(r: string | null, e?: string | null) {
    try {
      if (r) {
        document.cookie = `zacma_user_role=${encodeURIComponent(r)}; path=/`;
        if (e) document.cookie = `zacma_user_email=${encodeURIComponent(e)}; path=/`;
      } else {
        document.cookie = `zacma_user_role=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
        document.cookie = `zacma_user_email=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
      }
    } catch {}
  }

  function login(r: string, e?: string) {
    setRole(r);
    setEmail(e ?? null);
    setCookieRole(r, e);
  }

  function logout() {
    setRole(null);
    setEmail(null);
    setCookieRole(null);
  }

  return <AuthContext.Provider value={{ role, email, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
