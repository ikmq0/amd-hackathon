"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { DecodeResult } from "@/lib/types";

import { Icon, catIcon } from "./icons";

const SAMPLES = [
  "MCD_2938_RYD*SP",
  "JAHEZ*DLVR_88_APP",
  "INMA_E_PAY_9482",
  "NOON*ECOM_SA_4491",
  "ZZZ_9999_XX",
];

const TIER_LABEL: Record<string, string> = {
  exact: "مطابقة مباشرة",
  alias: "مطابقة اسم",
  fuzzy: "مطابقة تقريبية",
  vector: "مطابقة دلالية",
  unknown: "غير مطابَق",
};

export default function DecodeShowcase() {
  const [raw, setRaw] = useState(SAMPLES[0]);
  const [res, setRes] = useState<DecodeResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function run(value?: string) {
    const q = value ?? raw;
    if (value !== undefined) setRaw(value);
    setLoading(true);
    try {
      setRes(await api.decode(q));
    } catch {
      setRes(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    run(SAMPLES[0]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="card">
      <div className="card-head">
        <div>
          <h2>من الغموض إلى الوضوح</h2>
          <div className="sub">الصق وصف عملية بنكية وشاهد توضيحه فورًا</div>
        </div>
      </div>

      <div className="decode-input">
        <input
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && run()}
          spellCheck={false}
        />
        <button className="btn btn-primary" onClick={() => run()}>
          توضيح
        </button>
      </div>
      <div className="chips-row">
        {SAMPLES.map((s) => (
          <span key={s} className="sample-chip" onClick={() => run(s)}>
            {s}
          </span>
        ))}
      </div>

      <div className="decode-body">
        <div>
          <div className="col-label">الوصف كما يصل من البنك</div>
          <div className="raw-box">
            <code>{raw}</code>
          </div>
          <div className="raw-meta">رمز مبهم · لا يمكن قراءته أو تتبّعه</div>
        </div>

        <div className="decode-arrow">{Icon.arrow()}</div>

        <div>
          <div className="col-label">بعد التوضيح</div>
          {loading || !res ? (
            <div className="result-card">
              <div className="skeleton">…جارٍ التوضيح</div>
            </div>
          ) : res.resolved ? (
            <div className="result-card">
              <div className="result-top">
                <div className="result-ico">{catIcon(res.category_label_ar)}</div>
                <div className="result-name">
                  {res.merchant}
                  <small>{res.category_label_ar}</small>
                </div>
              </div>
              <div className="result-grid">
                <Field k="الفئة" v={res.category_label_ar} />
                <Field k="المدينة" v={res.city ?? "—"} />
                <Field k="القناة" v={res.channel ?? "—"} />
                <Field k="طريقة التوضيح" v={TIER_LABEL[res.resolved_by]} />
              </div>
              <div className="result-foot">
                <span className="chip chip-green">
                  {Icon.check()} دقة {Math.round(res.confidence * 100)}%
                </span>
                <span className="chip chip-soft">بيانات موحّدة</span>
              </div>
            </div>
          ) : (
            <div className="result-card">
              <div className="result-top">
                <div className="result-ico">{Icon.store()}</div>
                <div className="result-name">
                  تاجر غير معروف
                  <small>لم تتم المطابقة مع الدليل</small>
                </div>
              </div>
              <div className="result-foot">
                <span className="chip chip-warn">بدون تخمين — نتيجة صريحة</span>
                <span className="chip chip-soft">لا هلوسة</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Field({ k, v }: { k: string; v: string }) {
  return (
    <div className="rg-item">
      <span className="rg-k">{k}</span>
      <span className="rg-v">{v}</span>
    </div>
  );
}
