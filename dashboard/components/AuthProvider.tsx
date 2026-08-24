"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

export interface UserSession {
  role: string | null;
  email?: string | null;
  fullName?: string | null;
  token?: string | null;
  userId?: string | null;
  phone?: string | null;
}

interface AuthContextValue extends UserSession {
  login: (role: string, email?: string, token?: string, fullName?: string, phone?: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);
const STORAGE_KEY = "zacma_user";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<UserSession>({
    role: null,
    email: null,
    fullName: null,
    token: null,
    userId: null,
    phone: null,
  });

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        setSession({
          role: parsed.role ?? null,
          email: parsed.email ?? null,
          fullName: parsed.fullName ?? null,
          token: parsed.token ?? null,
          userId: parsed.userId ?? null,
          phone: parsed.phone ?? null,
        });
      }
    } catch {}
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
    } catch {}
  }, [session]);

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

  function login(
    r: string,
    e?: string,
    token?: string,
    fullName?: string,
    phone?: string,
  ) {
    const newSession: UserSession = {
      role: r,
      email: e ?? null,
      fullName: fullName ?? (e ? e.split("@")[0] : "User"),
      token: token ?? null,
      userId: e ? `usr-${Math.abs(e.split("").reduce((a, b) => ((a << 5) - a) + b.charCodeAt(0), 0)) % 100000}` : null,
      phone: phone ?? null,
    };
    setSession(newSession);
    setCookieRole(r, e);
  }

  function logout() {
    setSession({
      role: null,
      email: null,
      fullName: null,
      token: null,
      userId: null,
      phone: null,
    });
    setCookieRole(null);
  }

  return (
    <AuthContext.Provider
      value={{
        ...session,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
