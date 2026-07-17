"use client";

import Link from "next/link";

import { Icon } from "@/components/icons";
import { TxTable } from "@/components/TxTable";
import { api } from "@/lib/api";
import { fmt0, useApi } from "@/lib/useApi";

export default function OverviewPage() {
  const stats = useApi(() => api.stats()).data;
  const recent = useApi(() => api.transactions({ limit: 5 })).data;

  return (
    <>
      <div className="phead">
        <div className="phead-top">
          <div>
            <div className="phead-hi">أهلًا،</div>
            <div className="phead-name">خالد محمود</div>
          </div>
        </div>
        <div className="balance">
          <div className="balance-k">إجمالي مصاريفك هذا الشهر</div>
          <div className="balance-v">
            {stats ? fmt0(stats.total_spend) : "…"}
            <span>ر.س</span>
          </div>
        </div>
      </div>

      <div className="sec" style={{ marginTop: 18 }}>
        <div className="cols even">
          <div className="rows">
            <Link href="/transactions" className="row">
              <div className="row-ico">{Icon.compare()}</div>
              <div className="row-mid">
                <div className="row-title">العمليات</div>
                <div className="row-sub">من رمز مبهم إلى اسم تاجر واضح</div>
              </div>
              <div className="row-chev">{Icon.chevron()}</div>
            </Link>
            <Link href="/dashboard" className="row">
              <div className="row-ico">{Icon.trend()}</div>
              <div className="row-mid">
                <div className="row-title">لوحتي المالية</div>
                <div className="row-sub">تحليل إنفاقك ونصائح تلقائية</div>
              </div>
              <div className="row-chev">{Icon.chevron()}</div>
            </Link>
            <Link href="/assistant" className="row">
              <div className="row-ico">{Icon.chat()}</div>
              <div className="row-mid">
                <div className="row-title">المساعد الذكي</div>
                <div className="row-sub">اسأل عن مصاريفك</div>
              </div>
              <div className="row-chev">{Icon.chevron()}</div>
            </Link>
          </div>

          <div>
            <div className="sec-title" style={{ marginTop: 0 }}>
              <h2>أحدث العمليات</h2>
              <Link className="link" href="/transactions">
                الكل ←
              </Link>
            </div>
            <div className="card">
              {recent ? <TxTable rows={recent} /> : <div className="skeleton">…تحميل</div>}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
