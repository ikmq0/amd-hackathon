"use client";

import { useEffect, useRef, useState } from "react";

import type { BreakdownSlice, MonthPoint } from "@/lib/types";
import { fmt0 } from "@/lib/useApi";

/** Eased count-up so a changing total animates instead of snapping. */
function useCountUp(value: number, ms = 600): number {
  const [shown, setShown] = useState(value);
  const from = useRef(value);
  useEffect(() => {
    const start = from.current;
    const delta = value - start;
    if (delta === 0) return;
    let raf = 0;
    let t0: number | null = null;
    const tick = (t: number) => {
      if (t0 === null) t0 = t;
      const p = Math.min((t - t0) / ms, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setShown(start + delta * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
      else from.current = value;
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value, ms]);
  return shown;
}

export function Donut({
  data,
  total,
  animKey,
}: {
  data: BreakdownSlice[];
  total: number;
  animKey?: string; // change to replay the enter animation (e.g. selected month)
}) {
  const sum = data.reduce((s, d) => s + d.val, 0) || 1;
  const stops = data
    .reduce<{ acc: number; parts: string[] }>(
      ({ acc, parts }, d) => {
        const start = (acc / sum) * 360;
        const end = ((acc + d.val) / sum) * 360;
        parts.push(`${d.color} ${start}deg ${end}deg`);
        return { acc: acc + d.val, parts };
      },
      { acc: 0, parts: [] },
    )
    .parts.join(",");
  const shown = useCountUp(total);
  return (
    <>
      <div className="donut-wrap">
        <div
          key={animKey}
          className="donut donut-anim"
          style={{ background: `conic-gradient(${stops})` }}
        >
          <div className="donut-center">
            <span className="donut-total">{fmt0(shown)}</span>
            <span className="donut-cur">ر.س</span>
          </div>
        </div>
      </div>
      <ul className="legend" key={animKey}>
        {data.map((d, i) => (
          <li key={d.name} style={{ animationDelay: `${i * 45}ms` }}>
            <span className="lg-dot" style={{ background: d.color }} />
            <span className="lg-name">{d.name}</span>
            <span className="lg-val">{fmt0(d.val)}</span>
            <span className="lg-pct">{Math.round((d.val / sum) * 100)}%</span>
          </li>
        ))}
      </ul>
    </>
  );
}

export function TrendBars({
  data,
  selectedKey,
  onSelect,
}: {
  data: MonthPoint[];
  selectedKey?: string | null;
  onSelect?: (key: string) => void;
}) {
  const max = Math.max(...data.map((d) => d.v), 1);
  // Active (green) column: the explicitly selected month, else the latest.
  const activeIdx = selectedKey
    ? data.findIndex((d) => d.key === selectedKey)
    : data.length - 1;
  const clickable = !!onSelect;
  return (
    <div className="trend">
      {data.map((d, i) => {
        const active = i === activeIdx;
        const sel = !!selectedKey && d.key === selectedKey;
        const cls = `bar-col${active ? " hi" : ""}${sel ? " sel" : ""}${
          clickable ? " tap" : ""
        }`;
        const inner = (
          <>
            <div className="bar-val">{(d.v / 1000).toFixed(1)}k</div>
            <div className="bar" style={{ height: `${Math.round((d.v / max) * 100)}%` }} />
            <div className="bar-lbl">{d.m}</div>
          </>
        );
        return clickable ? (
          <button
            type="button"
            key={d.key ?? i}
            className={cls}
            aria-pressed={sel}
            onClick={() => d.key && onSelect(d.key)}
          >
            {inner}
          </button>
        ) : (
          <div key={d.key ?? i} className={cls}>
            {inner}
          </div>
        );
      })}
    </div>
  );
}

export function LineChart({ data }: { data: MonthPoint[] }) {
  const W = 520;
  const H = 180;
  const pad = 24;
  const vals = data.map((d) => d.v);
  const min = Math.min(...vals) - 3;
  const max = Math.max(...vals) + 3;
  const span = max - min || 1;
  const pts = data.map((d, i) => {
    const x = pad + (i * (W - pad * 2)) / Math.max(data.length - 1, 1);
    const y = H - pad - ((d.v - min) / span) * (H - pad * 2);
    return [x, y] as const;
  });
  const path = pts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ");
  const area =
    `M${pad} ${H - pad} ` +
    pts.map((p) => `L${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ") +
    ` L${W - pad} ${H - pad} Z`;
  const gl = [0, 1, 2, 3].map((i) => {
    const y = pad + (i * (H - pad * 2)) / 3;
    return <line key={i} className="grid-l" x1={pad} y1={y} x2={W - pad} y2={y} />;
  });
  return (
    <>
      <svg className="line-chart" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
        {gl}
        <path className="area" d={area} />
        <path className="path" d={path} />
        {pts.map((p, i) => (
          <circle key={i} className="dot" cx={p[0].toFixed(1)} cy={p[1].toFixed(1)} r={3.5} />
        ))}
      </svg>
      <div className="axis-x">
        {data.map((d, i) => (
          <span key={i}>{d.m}</span>
        ))}
      </div>
    </>
  );
}
