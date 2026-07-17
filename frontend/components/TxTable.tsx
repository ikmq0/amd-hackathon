import type { TransactionOut } from "@/lib/types";
import { fmt2 } from "@/lib/useApi";

import { catIcon } from "./icons";

export function TxTable({ rows }: { rows: TransactionOut[] }) {
  return (
    <div className="tx-table">
      {rows.map((t, i) => (
        <div className="tx-row" key={i}>
          <div className="tx-logo">{catIcon(t.cat)}</div>
          <div className="tx-mid">
            <div className="tx-name">{t.resolved ? t.name : "تاجر غير معروف"}</div>
            <div className="tx-cat">
              {t.cat} · {t.date}
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
        </div>
      ))}
    </div>
  );
}
