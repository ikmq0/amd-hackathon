"use client";

import { useEffect, useMemo, useState } from "react";

import { catIcon, Icon } from "@/components/icons";
import { api } from "@/lib/api";
import type { CategoryOption, TransactionOut } from "@/lib/types";
import { fmt2 } from "@/lib/useApi";

// The full statement: every transaction, filterable by category + free-text search,
// with the inline "correct" action (the engine's learning layer) on each row.
export default function TransactionsExplorer() {
  const [rows, setRows] = useState<TransactionOut[] | null>(null);
  const [cats, setCats] = useState<CategoryOption[]>([]);
  const [activeCat, setActiveCat] = useState<string>(""); // "" = all
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [catKey, setCatKey] = useState("");
  const [saving, setSaving] = useState(false);

  const load = () =>
    api
      .transactions({ category: activeCat || undefined, search: search || undefined, limit: 500 })
      .then(setRows)
      .catch(() => setRows([]));

  useEffect(() => {
    api.categories().then(setCats).catch(() => setCats([]));
  }, []);

  // Refetch whenever the category filter changes; search is debounced below.
  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeCat]);

  useEffect(() => {
    const id = window.setTimeout(load, 250);
    return () => window.clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  const total = useMemo(() => (rows ?? []).reduce((s, t) => s + t.amt, 0), [rows]);

  function openEditor(t: TransactionOut) {
    setEditing(t.raw);
    setName(t.resolved ? t.name : "");
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
            {rows ? `${rows.length} عملية · ${fmt2(total)} ر.س` : "…تحميل"} · فلترة وتصحيح
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
        <div className="skeleton">…تحميل</div>
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
                    {t.cat} · {t.date} · {t.city}
                  </div>
                </div>
                <div className="tx-side">
                  <div className="tx-amt">{fmt2(t.amt)} ر.س</div>
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
                      {saving ? "…حفظ" : "حفظ التصحيح"}
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
