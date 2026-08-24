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
    let isMounted = true;
    const hydrateAndVerify = async () => {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) {
          const parsed = JSON.parse(raw);
          const currentSession: UserSession = {
            role: parsed.role ?? null,
            email: parsed.email ?? null,
            fullName: parsed.fullName ?? null,
            token: parsed.token ?? null,
            userId: parsed.userId ?? null,
            phone: parsed.phone ?? null,
          };
          if (isMounted) setSession(currentSession);

          if (parsed.token) {
            const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
            const res = await fetch(`${apiBase}/api/v1/auth/me`, {
              headers: { Authorization: `Bearer ${parsed.token}` },
              credentials: "include",
            }).catch(() => null);

            if (res && res.status === 401 && isMounted) {
              logout();
            } else if (res && res.ok && isMounted) {
              const freshUser = await res.json().catch(() => null);
              if (freshUser && freshUser.role) {
                setSession((prev) => ({
                  ...prev,
                  role: freshUser.role,
                  email: freshUser.email,
                  fullName: freshUser.full_name,
                }));
              }
            }
          }
        }
      } catch {}
    };

    hydrateAndVerify();
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
    } catch {}
  }, [session]);

  function setCookieRole(r: string | null, e?: string | null, t?: string | null) {
    try {
      if (r) {
        document.cookie = `zacma_user_role=${encodeURIComponent(r)}; path=/`;
        if (e) document.cookie = `zacma_user_email=${encodeURIComponent(e)}; path=/`;
        if (t) document.cookie = `zacma_session=${encodeURIComponent(t)}; path=/`;
      } else {
        document.cookie = `zacma_user_role=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
        document.cookie = `zacma_user_email=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
        document.cookie = `zacma_session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;`;
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
    setCookieRole(r, e, token);
  }

  function logout() {
    const currentToken = session.token;
    setSession({
      role: null,
      email: null,
      fullName: null,
      token: null,
      userId: null,
      phone: null,
    });
    setCookieRole(null);
    if (currentToken) {
      const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
      fetch(`${apiBase}/api/v1/auth/logout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${currentToken}`,
        },
        credentials: "include",
      }).catch(() => null);
    }
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
