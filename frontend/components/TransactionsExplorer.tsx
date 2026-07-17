"use client";

import { useEffect, useMemo, useState } from "react";

import { catIcon, Icon } from "@/components/icons";
import { api } from "@/lib/api";
import type { CategoryOption, MonthOption, TransactionOut } from "@/lib/types";
import { fmt2 } from "@/lib/useApi";

// The full statement: every transaction, filterable by category + month + city +
// free-text search, with the inline "correct" action (the engine's learning layer).
export default function TransactionsExplorer() {
  const [rows, setRows] = useState<TransactionOut[] | null>(null);
  const [cats, setCats] = useState<CategoryOption[]>([]);
  const [months, setMonths] = useState<MonthOption[]>([]);
  const [cities, setCities] = useState<string[]>([]);
  const [activeCat, setActiveCat] = useState("");
  const [month, setMonth] = useState("");
  const [city, setCity] = useState("");
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [catKey, setCatKey] = useState("");
  const [saving, setSaving] = useState(false);

  const load = () =>
    api
      .transactions({
        category: activeCat || undefined,
        search: search || undefined,
        month: month || undefined,
        city: city || undefined,
        limit: 1000,
      })
      .then(setRows)
      .catch(() => setRows([]));

  useEffect(() => {
    api.categories().then(setCats).catch(() => setCats([]));
    api
      .transactionFilters()
      .then((f) => {
        setMonths(f.months);
        setCities(f.cities);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeCat, month, city]);

  useEffect(() => {
    const id = window.setTimeout(load, 250);
    return () => window.clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  const spend = useMemo(
    () => (rows ?? []).filter((t) => !t.income).reduce((s, t) => s + Math.abs(t.amt), 0),
    [rows],
  );

  function openEditor(t: TransactionOut) {
    setEditing(t.raw);
    setName(t.name);
    setCatKey(cats.find((c) => c.label_ar === t.cat)?.key ?? cats[0]?.key ?? "");
  }

  async function save(raw: string) {
    if (!name.trim() || !catKey || saving) return;
    setSaving(true);
    try {
      await api.correct({ raw, category: catKey, display_name: name.trim() });
      setEditing(null);
      await load();
    } catch {
      /* keep editor open on failure */
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="card">
      <div className="card-head">
        <div>
          <h2>كل العمليات</h2>
          <div className="sub">
            {rows ? `${rows.length} عملية · صرف ر.س ${fmt2(spend)}` : "تحميل…"} · فلترة وتصحيح
          </div>
        </div>
      </div>

      <div className="tx-search">
        {Icon.search("ic-sm")}
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="ابحث باسم التاجر أو الوصف الخام…"
        />
      </div>

      <div className="tx-selects">
        <select value={month} onChange={(e) => setMonth(e.target.value)}>
          <option value="">كل الأشهر</option>
          {months.map((m) => (
            <option key={m.key} value={m.key}>
              {m.label}
            </option>
          ))}
        </select>
        <select value={city} onChange={(e) => setCity(e.target.value)}>
          <option value="">كل المدن</option>
          {cities.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      <div className="filters">
        <button className={`f${activeCat === "" ? " active" : ""}`} onClick={() => setActiveCat("")}>
          الكل
        </button>
        {cats.map((c) => (
          <button
            key={c.key}
            className={`f${activeCat === c.label_ar ? " active" : ""}`}
            onClick={() => setActiveCat(c.label_ar)}
          >
            {c.label_ar}
          </button>
        ))}
      </div>

      {!rows ? (
        <div className="skeleton">تحميل…</div>
      ) : rows.length === 0 ? (
        <div className="report-empty">لا توجد عمليات مطابقة لبحثك.</div>
      ) : (
        <div className="tx-table">
          {rows.map((t, i) => (
            <div key={`${t.raw}-${i}`}>
              <div className="tx-row">
                <div className="tx-logo">{catIcon(t.cat)}</div>
                <div className="tx-mid">
                  <div className="tx-name">{t.resolved ? t.name : "تاجر غير معروف"}</div>
                  <div className="tx-cat">
                    {t.cat} · {t.date}
                    {t.city !== "—" ? ` · ${t.city}` : ""}
                  </div>
                </div>
                <div className="tx-side">
                  <div className={`tx-amt${t.income ? " in" : ""}`}>
                    ر.س {t.income ? "+" : ""}
                    {fmt2(Math.abs(t.amt))}
                  </div>
                  <div className={`tx-acc${t.resolved ? "" : " unk"}`}>
                    {t.resolved ? `دقة ${t.acc}%` : "غير مؤكد"}
                  </div>
                </div>
                <button
                  className="correct-btn"
                  onClick={() => (editing === t.raw ? setEditing(null) : openEditor(t))}
                  aria-label="تصحيح التصنيف"
                >
                  {Icon.edit("ic-sm")}
                </button>
              </div>

              {editing === t.raw && (
                <div className="correct-editor">
                  <div className="ce-field">
                    <label>الاسم الصحيح</label>
                    <input value={name} onChange={(e) => setName(e.target.value)} placeholder="اسم التاجر" />
                  </div>
                  <div className="ce-field">
                    <label>الفئة</label>
                    <select value={catKey} onChange={(e) => setCatKey(e.target.value)}>
                      {cats.map((c) => (
                        <option key={c.key} value={c.key}>
                          {c.label_ar}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="ce-actions">
                    <button className="btn btn-ghost btn-sm" onClick={() => setEditing(null)}>
                      إلغاء
                    </button>
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => save(t.raw)}
                      disabled={saving || !name.trim()}
                    >
                      {saving ? "حفظ…" : "حفظ التصحيح"}
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
