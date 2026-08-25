/**
 * Supabase Authentication & Client Adapter for ZACMA Group.
 *
 * Connects to Supabase Authentication & REST API when configured,
 * routing through the ZACMA Backend API Gateway to guarantee server-side
 * role validation, Row Level Security (RLS) enforcement, and secure HttpOnly sessions.
 */

export interface SupabaseAuthUser {
  id: string;
  email: string;
  fullName: string;
  role: string;
  tenantId: string;
  token: string;
  status?: string;
}

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || "http://localhost:54321";
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
const rawApiBase = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
const API_BASE = rawApiBase.endsWith("/api/v1") ? rawApiBase : `${rawApiBase}/api/v1`;

export const SupabaseAuthClient = {
  /**
   * Check if Supabase client keys are configured
   */
  isConfigured(): boolean {
    return Boolean(SUPABASE_URL && SUPABASE_ANON_KEY && SUPABASE_ANON_KEY !== "replace-me");
  },

  /**
   * Sign in with Email & Password via ZACMA Gateway & Supabase Auth
   */
  async signInWithEmail(email: string, password: string, rememberMe: boolean = false): Promise<SupabaseAuthUser> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password, remember_me: rememberMe }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(err.detail || "Invalid credentials");
    }

    const data = await res.json();
    return {
      id: data.user_id || `usr-${data.email}`,
      email: data.email,
      fullName: data.full_name,
      role: data.role,
      tenantId: data.tenant_id,
      token: data.access_token,
      status: "active",
    };
  },

  /**
   * Register a new user with Supabase Auth (role locked to 'client')
   */
  async register(params: {
    email: string;
    password: string;
    fullName: string;
    phone?: string;
    address?: string;
    educationLevel?: string;
  }): Promise<SupabaseAuthUser> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        email: params.email,
        password: params.password,
        full_name: params.fullName,
        phone: params.phone,
        address: params.address,
        education_level: params.educationLevel || "Diploma",
        role: "client", // Privilege escalation defense
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Registration failed" }));
      throw new Error(err.detail || "Registration failed");
    }

    const data = await res.json();
    return {
      id: data.user_id,
      email: data.email,
      fullName: data.full_name,
      role: data.role,
      tenantId: data.tenant_id,
      token: data.access_token,
      status: "active",
    };
  },

  /**
   * Invalidate session and sign out
   */
  async signOut(token?: string | null): Promise<void> {
    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
      await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        headers,
        credentials: "include",
      });
    } catch {}
  },
};
