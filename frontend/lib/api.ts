// Typed client for the مِدْ backend.

import type {
  BreakdownSlice,
  CategoryOption,
  ChatResult,
  CorrectResult,
  DecodeResult,
  MerchantStats,
  MonthPoint,
  ReportResult,
  Stats,
  TransactionFilters,
  TransactionOut,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`GET ${path} -> ${res.status}`);
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = `${res.status}`;
    try {
      detail = (await res.json())?.detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new Error(`POST ${path} -> ${detail}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  decode: async (raw: string): Promise<DecodeResult> => {
    const res = await fetch(`${BASE}/decode`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw }),
    });
    if (!res.ok) throw new Error(`decode -> ${res.status}`);
    return res.json();
  },
  transactions: (params?: {
    category?: string;
    search?: string;
    limit?: number;
    month?: string;
    city?: string;
  }) => {
    const q = new URLSearchParams();
    if (params?.category) q.set("category", params.category);
    if (params?.search) q.set("search", params.search);
    if (params?.limit) q.set("limit", String(params.limit));
    if (params?.month) q.set("month", params.month);
    if (params?.city) q.set("city", params.city);
    const qs = q.toString();
    return get<TransactionOut[]>(`/transactions${qs ? `?${qs}` : ""}`);
  },
  transactionFilters: () => get<TransactionFilters>("/transactions/filters"),
  merchants: () => get<MerchantStats[]>("/merchants"),
  breakdown: (month?: string) =>
    get<BreakdownSlice[]>(
      `/analytics/breakdown${month ? `?month=${encodeURIComponent(month)}` : ""}`,
    ),
  monthly: () => get<MonthPoint[]>("/analytics/monthly"),
  accuracy: () => get<MonthPoint[]>("/analytics/accuracy"),
  stats: () => get<Stats>("/stats"),

  // Layer 3 (LLM) + corrections — the Khawarizm engine functions.
  report: (month?: string) => post<ReportResult>("/report", { month: month ?? null }),
  chat: (message: string) => post<ChatResult>("/chat", { message }),
  categories: () => get<CategoryOption[]>("/categories"),
  correct: (body: { raw: string; category: string; display_name: string }) =>
    post<CorrectResult>("/correct", body),
};
