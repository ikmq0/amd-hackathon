"use client";

import { useState } from "react";

import { Markdown } from "@/components/Markdown";
import { api } from "@/lib/api";
import type { ReportResult } from "@/lib/types";

// Generates the monthly Arabic report via the backend LLM (Layer 3). The model
// only phrases text over already-categorized aggregates — no raw descriptors,
// nothing to hallucinate.
export default function ReportCard() {
  const [report, setReport] = useState<ReportResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      setReport(await api.report());
    } catch (e) {
      const msg = String(e);
      setError(
        msg.includes("GEMINI_API_KEY") || msg.includes("503")
          ? "خدمة التقرير غير مفعّلة. أضِف مفتاح Gemini في backend/.env لتفعيلها."
          : "تعذّر إنشاء التقرير حاليًا. حاول مرة أخرى.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <div className="card-head">
        <div>
          <h2>التقرير الشهري</h2>
          <div className="sub">
            {report ? report.month_label : "ملخّص ذكي لإنفاقك، مبني على عملياتك الفعلية"}
          </div>
        </div>
        <button className="btn btn-primary btn-sm" onClick={generate} disabled={loading}>
          {loading ? "جارٍ التوليد…" : report ? "تحديث" : "توليد التقرير"}
        </button>
      </div>

      {error && <div className="report-note warn">{error}</div>}

      {!report && !error && !loading && (
        <div className="report-empty">
          اضغط «توليد التقرير» للحصول على ملخّص شهري لمصاريفك وأبرز فئات إنفاقك.
        </div>
      )}

      {loading && !report && <div className="skeleton">يكتب المساعد تقريرك…</div>}

      {report && (
        <div className="report-body">
          <Markdown text={report.report_markdown} />
        </div>
      )}
    </div>
  );
}
