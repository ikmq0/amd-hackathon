"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Donut, TrendBars } from "@/components/charts";
import { Icon } from "@/components/icons";
import ReportCard from "@/components/ReportCard";
import { Kpi, PageHeader } from "@/components/ui";
import { api } from "@/lib/api";
import { buildAdvice, type InsightData } from "@/lib/insights";
import type { BreakdownSlice } from "@/lib/types";
import { fmt0, useApi } from "@/lib/useApi";

export default function DashboardPage() {
  const stats = useApi(() => api.stats()).data;
  const fullBreakdown = useApi(() => api.breakdown()).data;
  const monthly = useApi(() => api.monthly()).data;
  const merchants = useApi(() => api.merchants()).data;

  // Which month the distribution donut is scoped to (null = whole period).
  const [selectedMonth, setSelectedMonth] = useState<string | null>(null);
  const [monthBreakdown, setMonthBreakdown] = useState<BreakdownSlice[] | null>(null);

  useEffect(() => {
    if (!selectedMonth) return;
    let live = true;
    api.breakdown(selectedMonth).then((d) => live && setMonthBreakdown(d));
    return () => {
      live = false;
    };
  }, [selectedMonth]);

  // Whole-period slices come from the initial fetch; a picked month uses the
  // scoped fetch (kept from the previous month until the new one resolves).
  const donut = selectedMonth ? monthBreakdown : fullBreakdown;
  const total = donut?.reduce((s, b) => s + b.val, 0) ?? 0;
  const scopeLabel = selectedMonth
    ? (monthly?.find((m) => m.key === selectedMonth)?.m ?? "")
    : "كل الفترة";

  // Advice always reflects the whole period, independent of the donut scope.
  const ready = stats && fullBreakdown && monthly && merchants;
  const advice = ready
    ? buildAdvice({ stats, breakdown: fullBreakdown, monthly, merchants } as InsightData)
    : [];

  return (
    <>
      <PageHeader title="لوحتي المالية" subtitle="نظرة على إنفاقك مع نصائح تُولّد تلقائيًا." />

      <div className="sec" style={{ marginTop: 18 }}>
        <div className="kpis">
          <Kpi
            icon={Icon.wallet()}
            value={stats ? fmt0(stats.total_spend) : "…"}
            unit="ر.س"
            label="إجمالي الإنفاق"
          />
          <Kpi
            icon={Icon.check()}
            value={stats ? `${stats.accuracy_pct}%` : "…"}
            label="دقة التصنيف"
          />
        </div>

        <div className="gap" />
        <Link href="/assistant" className="ai-banner">
          <div className="ai-ico">{Icon.chat()}</div>
          <div>
            <b>اسأل مساعدك المالي</b>
            <p>إجابات ونصائح مبنية على بياناتك.</p>
          </div>
        </Link>

        <div className="cols even" style={{ marginTop: 6 }}>
          <div>
            <div className="sec-title" style={{ marginTop: 0 }}>
              <h2>الإنفاق الشهري</h2>
              <span className="scope-hint">اضغط شهرًا للتصفية</span>
            </div>
            <div className="card">
              {monthly ? (
                <TrendBars
                  data={monthly}
                  selectedKey={selectedMonth}
                  onSelect={(k) => setSelectedMonth((prev) => (prev === k ? null : k))}
                />
              ) : (
                <div className="skeleton">تحميل…</div>
              )}
            </div>

            <div className="sec-title">
              <h2>نصائح تلقائية</h2>
            </div>
            <div className="card">
              {ready ? (
                advice.slice(0, 3).map((a, i) => (
                  <div className="advice" key={i}>
                    <div className="advice-ico">{Icon.bulb()}</div>
                    <div>
                      <b>{a.title}</b>
                      <p>{a.body}</p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="skeleton">تحميل…</div>
              )}
            </div>
          </div>
          <div>
            <div className="sec-title" style={{ marginTop: 0 }}>
              <h2>توزيع الإنفاق</h2>
              {selectedMonth ? (
                <button
                  type="button"
                  className="scope-chip"
                  onClick={() => setSelectedMonth(null)}
                >
                  {scopeLabel}
                  <span className="scope-x">{Icon.close()}</span>
                </button>
              ) : (
                <span className="scope-hint">{scopeLabel}</span>
              )}
            </div>
            <div className="card">
              {donut ? (
                <Donut data={donut} total={total} animKey={selectedMonth ?? "all"} />
              ) : (
                <div className="skeleton">تحميل…</div>
              )}
            </div>
          </div>
        </div>

        <div className="sec-title">
          <h2>تقريرك الذكي</h2>
        </div>
        <ReportCard />
      </div>
    </>
  );
}
