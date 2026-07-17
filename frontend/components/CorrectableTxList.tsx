"use client";

import { useEffect, useState } from "react";

import { catIcon, Icon } from "@/components/icons";
import { api } from "@/lib/api";
import type { CategoryOption, TransactionOut } from "@/lib/types";

// The before/after list, plus the "correct" action (the engine's learning layer):
// a user fix re-labels every variant of that merchant and persists across reseeds.
export default function CorrectableTxList({ limit = 8 }: { limit?: number }) {
  const [rows, setRows] = useState<TransactionOut[] | null>(null);
  const [cats, setCats] = useState<CategoryOption[]>([]);
  const [editing, setEditing] = useState<string | null>(null); // raw being edited
  const [name, setName] = useState("");
  const [catKey, setCatKey] = useState("");
  const [saving, setSaving] = useState(false);

  const load = () => api.transactions({ limit }).then(setRows).catch(() => setRows([]));

  useEffect(() => {
    load();
    api.categories().then(setCats).catch(() => setCats([]));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function openEditor(t: TransactionOut) {
    setEditing(t.raw);
    setName(t.resolved ? t.name : "");
    const match = cats.find((c) => c.label_ar === t.cat);
    setCatKey(match?.key ?? cats[0]?.key ?? "");
  }

  async function save(raw: string) {
    if (!name.trim() || !catKey || saving) return;
    setSaving(true);
    try {
      await api.correct({ raw, category: catKey, display_name: name.trim() });
      setEditing(null);
      await load();
    } catch {
      /* keep the editor open on failure */
    } finally {
      setSaving(false);
    }
  }

  if (!rows) return <div className="skeleton">…تحميل</div>;

  return (
    <div className="ba-list">
      {rows.map((t, i) => (
        <div className="ba-item" key={`${t.raw}-${i}`}>
          <div className="ba-before">
            <span className="ba-lab pre">قبل</span>
            <span className="ba-code">{t.raw}</span>
          </div>
          <div className="ba-after">
            <div className="ba-logo">{catIcon(t.cat)}</div>
            <div className="ba-after-mid">
              <div className="ba-name">{t.resolved ? t.name : "تاجر غير معروف"}</div>
              <div className="ba-meta">
                <span className={`ba-tag${t.resolved ? "" : " unk"}`}>{t.cat}</span>
                {t.resolved && (
                  <>
                    <span>{t.city}</span>
                    <span className="ba-dot" />
                    <span>دقة {t.acc}%</span>
                  </>
                )}
              </div>
            </div>
            <button
              className="correct-btn"
              onClick={() => (editing === t.raw ? setEditing(null) : openEditor(t))}
              aria-label="تصحيح التصنيف"
            >
              {Icon.edit("ic-sm")}
              تصحيح
            </button>
          </div>

          {editing === t.raw && (
            <div className="correct-editor">
              <div className="ce-field">
                <label>الاسم الصحيح</label>
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="اسم التاجر"
                />
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
  );
}
