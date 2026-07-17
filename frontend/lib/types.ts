// Mirrors the backend Pydantic contract (app/schemas).

export interface DecodeResult {
  raw: string;
  normalized: string;
  merchant: string | null;
  merchant_id: string | null;
  category: string;
  category_label_ar: string;
  city: string | null;
  channel: string | null;
  confidence: number;
  resolved_by: "exact" | "alias" | "fuzzy" | "vector" | "unknown";
  resolved: boolean;
  logo: string | null;
  brand_color: string | null;
  schema_version: string;
}

export interface TransactionOut {
  name: string;
  raw: string;
  cat: string;
  city: string;
  date: string;
  amt: number;
  acc: number;
  resolved: boolean;
}

export interface MerchantStats {
  name: string;
  cat: string;
  count: number;
  total: number;
  acc: number;
}

export interface BreakdownSlice {
  name: string;
  val: number;
  color: string;
}

export interface MonthPoint {
  m: string;
  v: number;
  key?: string; // 'YYYY-MM' — present on monthly spend, used for month filtering
}

export interface Stats {
  total_spend: number;
  tx_count: number;
  accuracy_pct: number;
  avg_latency_ms: number;
  coverage_pct: number;
  cache_hit_rate: number;
  resolved_by: Record<string, number>;
}

export interface ReportResult {
  month: string;
  month_label: string;
  report_markdown: string;
}

export interface ChatResult {
  answer: string;
}

export interface CategoryOption {
  key: string;
  label_ar: string;
  color: string;
}

export interface CorrectResult {
  updated: number;
  category: string;
  category_label_ar: string;
  display_name: string;
}
