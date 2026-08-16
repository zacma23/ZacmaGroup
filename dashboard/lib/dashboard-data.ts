export type ModuleKey =
  | "crm"
  | "hrm"
  | "payments"
  | "training"
  | "travel"
  | "visa"
  | "marketing";

export type DataState = "live" | "sample" | "restricted";

export interface DashboardModule {
  key: ModuleKey;
  label: string;
  description: string;
  symbol: string;
  count: number;
  unit: string;
  state: DataState;
}

export interface DashboardMetric {
  label: string;
  value: string;
  detail: string;
  state: "live" | "sample";
}

export interface DashboardData {
  generatedAt: string;
  api: {
    status: "online" | "offline";
    label: string;
    detail: string;
    responseTimeMs?: number;
  };
  dataMode: "live" | "sample";
  notice: string;
  metrics: DashboardMetric[];
  modules: DashboardModule[];
}

interface ModuleDefinition {
  key: ModuleKey;
  label: string;
  description: string;
  symbol: string;
  path: string;
  sampleCount: number;
  unit: string;
  overviewKeys: string[];
}

interface ApiResult {
  ok: boolean;
  status?: number;
  data?: unknown;
  durationMs?: number;
}

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
const REQUEST_TIMEOUT_MS = 2500;

const MODULES: ModuleDefinition[] = [
  {
    key: "crm",
    label: "CRM",
    description: "Prospects and customer relationships",
    symbol: "◒",
    path: "/api/v1/crm/leads",
    sampleCount: 24,
    unit: "leads",
    overviewKeys: ["crm", "leads", "lead_count"],
  },
  {
    key: "hrm",
    label: "People",
    description: "Team operations and employee records",
    symbol: "◎",
    path: "/api/v1/hrm/employees",
    sampleCount: 18,
    unit: "team members",
    overviewKeys: ["hrm", "employees", "employee_count"],
  },
  {
    key: "payments",
    label: "Payments",
    description: "Invoices and billing operations",
    symbol: "¤",
    path: "/api/v1/payments/invoices",
    sampleCount: 9,
    unit: "invoices",
    overviewKeys: ["payments", "invoices", "invoice_count"],
  },
  {
    key: "training",
    label: "Training",
    description: "Courses and learner progress",
    symbol: "↗",
    path: "/api/v1/training/courses",
    sampleCount: 6,
    unit: "courses",
    overviewKeys: ["training", "courses", "course_count"],
  },
  {
    key: "travel",
    label: "Travel",
    description: "Trips, bookings, and itineraries",
    symbol: "✦",
    path: "/api/v1/travel/bookings",
    sampleCount: 8,
    unit: "bookings",
    overviewKeys: ["travel", "bookings", "booking_count"],
  },
  {
    key: "visa",
    label: "Visa",
    description: "Applications and case progress",
    symbol: "⌁",
    path: "/api/v1/visa/applications",
    sampleCount: 12,
    unit: "applications",
    overviewKeys: ["visa", "applications", "application_count"],
  },
  {
    key: "marketing",
    label: "Marketing",
    description: "Campaign planning and performance",
    symbol: "◈",
    path: "/api/v1/marketing/campaigns",
    sampleCount: 4,
    unit: "campaigns",
    overviewKeys: ["marketing", "campaigns", "campaign_count"],
  },
];

function getApiBaseUrl(): string {
  const configuredUrl =
    process.env.API_BASE_URL?.trim() ?? process.env.NEXT_PUBLIC_API_URL?.trim();

  if (!configuredUrl) {
    return DEFAULT_API_BASE_URL;
  }

  try {
    return new URL(configuredUrl).toString().replace(/\/$/, "");
  } catch {
    return DEFAULT_API_BASE_URL;
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function countValue(value: unknown): number | null {
  if (Array.isArray(value)) {
    return value.length;
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (isRecord(value)) {
    const collection = Object.values(value).find(Array.isArray);
    return collection ? collection.length : null;
  }

  return null;
}

function countFromOverview(value: unknown, keys: string[]): number | null {
  if (!isRecord(value)) {
    return null;
  }

  const containers = [value, value.metrics, value.summary, value.modules].filter(isRecord);

  for (const container of containers) {
    for (const key of keys) {
      const count = countValue(container[key]);
      if (count !== null) {
        return count;
      }
    }
  }

  return null;
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

async function requestJson(url: string): Promise<ApiResult> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  const startedAt = performance.now();

  try {
    const response = await fetch(url, {
      cache: "no-store",
      headers: { Accept: "application/json" },
      signal: controller.signal,
    });

    let data: unknown;
    try {
      data = await response.json();
    } catch {
      data = undefined;
    }

    return {
      ok: response.ok,
      status: response.status,
      data,
      durationMs: Math.round(performance.now() - startedAt),
    };
  } catch {
    return { ok: false };
  } finally {
    clearTimeout(timeout);
  }
}

function getModuleState(response: ApiResult, count: number | null): DataState {
  if (response.ok && count !== null) {
    return "live";
  }

  if (response.status === 401 || response.status === 403) {
    return "restricted";
  }

  return "sample";
}

export async function getDashboardData(): Promise<DashboardData> {
  const apiBaseUrl = getApiBaseUrl();
  const [health, overview, ...moduleResponses] = await Promise.all([
    requestJson(`${apiBaseUrl}/health`),
    requestJson(`${apiBaseUrl}/api/v1/dashboard/overview`),
    ...MODULES.map((module) => requestJson(`${apiBaseUrl}${module.path}`)),
  ]);
  const apiOnline = health.ok || overview.ok;

  const modules = MODULES.map((module, index) => {
    const response = moduleResponses[index];
    const overviewCount = countFromOverview(overview.data, module.overviewKeys);
    const endpointCount = countValue(response.data);
    const liveCount = overviewCount ?? endpointCount;
    const state =
      liveCount !== null && (overview.ok || response.ok)
        ? "live"
        : getModuleState(response, endpointCount);

    return {
      key: module.key,
      label: module.label,
      description: module.description,
      symbol: module.symbol,
      count: liveCount ?? module.sampleCount,
      unit: module.unit,
      state,
    };
  });

  const hasLiveData = modules.some((module) => module.state === "live");
  const moduleFor = (key: ModuleKey) =>
    modules.find((module) => module.key === key) ?? modules[0];
  const metricState = hasLiveData ? "live" : "sample";
  const responseTimeMs = health.durationMs ?? overview.durationMs;

  return {
    generatedAt: new Date().toISOString(),
    api: {
      status: apiOnline ? "online" : "offline",
      label: apiOnline ? "Backend online" : "Backend offline",
      detail: apiOnline
        ? `The local API responded in ${responseTimeMs ?? 0} ms.`
        : "Could not reach the local FastAPI server.",
      ...(apiOnline && responseTimeMs !== undefined ? { responseTimeMs } : {}),
    },
    dataMode: hasLiveData ? "live" : "sample",
    notice: hasLiveData
      ? "Showing live records from the local API. Modules without a tenant session remain in sample mode."
      : apiOnline
        ? "The API is reachable, but module records require a tenant-authenticated session. Local sample values keep this workspace usable."
        : "The local API is unavailable, so this workspace is showing local sample values. Start the backend and refresh to reconnect.",
    metrics: [
      {
        label: "Lead pipeline",
        value: formatNumber(moduleFor("crm").count),
        detail: moduleFor("crm").unit,
        state: metricState,
      },
      {
        label: "Team directory",
        value: formatNumber(moduleFor("hrm").count),
        detail: moduleFor("hrm").unit,
        state: metricState,
      },
      {
        label: "Visa cases",
        value: formatNumber(moduleFor("visa").count),
        detail: moduleFor("visa").unit,
        state: metricState,
      },
      {
        label: "Platform API",
        value: apiOnline ? "Online" : "Offline",
        detail: apiOnline
          ? `${responseTimeMs ?? 0} ms health check`
          : "Using local fallback data",
        state: apiOnline ? "live" : "sample",
      },
    ],
    modules,
  };
}
