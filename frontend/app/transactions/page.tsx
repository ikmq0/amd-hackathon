"use client";

import CorrectableTxList from "@/components/CorrectableTxList";
import DecodeShowcase from "@/components/DecodeShowcase";
import { Icon } from "@/components/icons";
import TransactionsExplorer from "@/components/TransactionsExplorer";
import { PageHeader } from "@/components/ui";
import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";

function latency(ms: number) {
  return ms < 1 ? ms.toFixed(2) : String(Math.round(ms));
}

export default function BeforeAfterPage() {
  const stats = useApi(() => api.stats()).data;

  const metrics = [
    { label: "قابلية القراءة", before: "غير مقروء", after: "واضح" },
    { label: "دقة التعرّف", before: "—", after: stats ? `${stats.accuracy_pct}%` : "…" },
    { label: "التصنيف", before: "يدوي", after: "تلقائي" },
    { label: "زمن المعالجة", before: "دقائق", after: stats ? `${latency(stats.avg_latency_ms)}ms` : "…" },
  ];

  return (
    <>
      <PageHeader
        title="العمليات"
        subtitle="من رمز مبهم غير قابل للقراءة إلى اسم تاجر واضح مصنّف — استعرض كل عملياتك وصحّح أي تصنيف."
      />

      <div className="sec" style={{ marginTop: 18 }}>
        <div className="ba-metrics">
          {metrics.map((m) => (
            <div className="mcmp" key={m.label}>
              <div className="mcmp-label">{m.label}</div>
              <div className="mcmp-row">
                <span className="mcmp-before">{m.before}</span>
                <span className="mcmp-arrow">{Icon.arrow()}</span>
                <span className="mcmp-after">{m.after}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="cols" style={{ marginTop: 18 }}>
          <DecodeShowcase />

          <div className="card">
            <div className="card-head">
              <div>
                <h2>مقارنة عملياتك</h2>
                <div className="sub">الوصف الخام ← بعد التوضيح · صحّح أي تصنيف</div>
              </div>
            </div>
            <CorrectableTxList limit={8} />
          </div>
        </div>

        <div className="sec-title">
          <h2>سجلّ العمليات الكامل</h2>
        </div>
        <TransactionsExplorer />
      </div>
    </>
  );
}
