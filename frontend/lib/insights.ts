// Data-grounded advice + assistant answers.
// Everything here is COMPUTED from the real API data — no invented facts (no hallucination).

import type { BreakdownSlice, MerchantStats, MonthPoint, Stats } from "./types";

export interface InsightData {
  stats: Stats;
  breakdown: BreakdownSlice[];
  merchants: MerchantStats[];
  monthly: MonthPoint[];
}

const fmt = (n: number) => Math.round(n).toLocaleString("en-US");

export interface Advice {
  title: string;
  body: string;
}

export function buildAdvice(d: InsightData): Advice[] {
  const out: Advice[] = [];
  const total = d.breakdown.reduce((s, b) => s + b.val, 0) || 1;
  const top = [...d.breakdown].sort((a, b) => b.val - a.val)[0];
  if (top) {
    out.push({
      title: `أعلى فئة إنفاق: ${top.name}`,
      body: `صرفت ${fmt(top.val)} ر.س على «${top.name}»، أي ${Math.round(
        (top.val / total) * 100,
      )}% من إجمالي مصاريفك. راقب هذه الفئة لأنها الأكبر تأثيرًا على ميزانيتك.`,
    });
  }

  const food = d.breakdown
    .filter((b) => b.name.includes("مطاعم") || b.name.includes("توصيل"))
    .reduce((s, b) => s + b.val, 0);
  if (food > 0) {
    const share = Math.round((food / total) * 100);
    out.push({
      title: "المطاعم والتوصيل",
      body:
        share >= 20
          ? `إنفاقك على المطاعم والتوصيل يشكّل ${share}% من مصاريفك. تقليصه بنسبة الربع قد يوفّر لك نحو ${fmt(
              food * 0.25,
            )} ر.س شهريًا.`
          : `إنفاقك على المطاعم والتوصيل معتدل (${share}%). استمر في هذا الاتزان.`,
    });
  }

  const topM = [...d.merchants].sort((a, b) => b.total - a.total)[0];
  if (topM) {
    out.push({
      title: `أكثر متجر إنفاقًا: ${topM.name}`,
      body: `أنفقت ${fmt(topM.total)} ر.س لدى «${topM.name}» عبر ${topM.count} عملية. ضع لها حدًّا شهريًا إن رغبت بضبط الصرف.`,
    });
  }

  if (d.monthly.length >= 2) {
    const last = d.monthly[d.monthly.length - 1];
    const prev = d.monthly[d.monthly.length - 2];
    const diff = last.v - prev.v;
    const pct = prev.v ? Math.round((diff / prev.v) * 100) : 0;
    out.push({
      title: diff >= 0 ? "إنفاقك في ارتفاع" : "إنفاقك في انخفاض",
      body: `مصاريف ${last.m} (${fmt(last.v)} ر.س) ${
        diff >= 0 ? "أعلى" : "أقل"
      } من ${prev.m} بنسبة ${Math.abs(pct)}%.`,
    });
  }

  return out;
}

export const SUGGESTED = [
  "كم أنفقت هذا الشهر؟",
  "ما أكثر فئة إنفاق؟",
  "من هو أكثر متجر أنفقت لديه؟",
  "أعطني نصيحة لتوفير المال",
  "ما دقة توضيح عملياتي؟",
];

// Specific, generated-from-the-data prompts — they name the user's real top
// category, top merchant, and most recent months so every chip is relevant.
export function buildSuggestions(d: InsightData | null): string[] {
  if (!d) return SUGGESTED;
  const cats = [...d.breakdown].sort((a, b) => b.val - a.val);
  const top = cats[0]?.name;
  const second = cats[1]?.name;
  const topM = [...d.merchants].sort((a, b) => b.total - a.total)[0];
  const months = d.monthly;

  const out: string[] = [];
  if (top) out.push(`كم أنفقت على ${top}؟`);
  if (topM) out.push(`ما مجموع إنفاقي لدى ${topM.name}؟`);
  if (top) out.push(`كيف يمكنني التوفير في ${top}؟`);
  if (months.length >= 2) {
    const a = months[months.length - 2].m;
    const b = months[months.length - 1].m;
    out.push(`قارن إنفاقي بين ${a} و${b}`);
  }
  if (top && second) out.push(`أيهما أعلى إنفاقًا: ${top} أم ${second}؟`);
  return out.length ? out.slice(0, 5) : SUGGESTED;
}

export function answerQuestion(q: string, d: InsightData): string {
  const t = q.trim();
  const total = d.breakdown.reduce((s, b) => s + b.val, 0);
  const sortedCat = [...d.breakdown].sort((a, b) => b.val - a.val);
  const sortedM = [...d.merchants].sort((a, b) => b.total - a.total);

  const has = (...w: string[]) => w.some((x) => t.includes(x));

  if (has("كم", "إجمالي", "أنفقت", "صرفت", "مصاريف")) {
    return `إجمالي مصاريفك ${fmt(d.stats.total_spend)} ر.س عبر ${fmt(
      d.stats.tx_count,
    )} عملية. أعلى فئة هي «${sortedCat[0]?.name}» بـ ${fmt(sortedCat[0]?.val ?? 0)} ر.س.`;
  }
  if (has("فئة", "فئات", "أعلى", "أكثر صرف", "تصنيف")) {
    const top3 = sortedCat
      .slice(0, 3)
      .map((c) => `${c.name} (${fmt(c.val)} ر.س)`)
      .join("، ");
    return `أعلى فئات إنفاقك: ${top3}.`;
  }
  if (has("متجر", "تاجر", "محل")) {
    const m = sortedM[0];
    return m
      ? `أكثر متجر أنفقت لديه هو «${m.name}» بمبلغ ${fmt(m.total)} ر.س عبر ${m.count} عملية.`
      : "لا توجد بيانات متاجر بعد.";
  }
  if (has("نصيحة", "وفر", "توفير", "ادخار", "أدخر", "ميزانية")) {
    const food = d.breakdown
      .filter((b) => b.name.includes("مطاعم") || b.name.includes("توصيل"))
      .reduce((s, b) => s + b.val, 0);
    if (food > 0) {
      return `نصيحة: إنفاقك على المطاعم والتوصيل ${fmt(
        food,
      )} ر.س. لو خصّصت له ميزانية شهرية وقلّصته بمقدار الربع، توفّر نحو ${fmt(
        food * 0.25,
      )} ر.س شهريًا.`;
    }
    return "نصيحة: حدّد ميزانية شهرية لأعلى فئتين إنفاقًا وراقبهما أسبوعيًا.";
  }
  if (has("دقة", "توضيح", "معروف", "هلوسة")) {
    return `تم توضيح ${d.stats.coverage_pct}% من عملياتك تلقائيًا بدقة تعرّف ${d.stats.accuracy_pct}% ومتوسط زمن ${d.stats.avg_latency_ms} ملّي ثانية. العمليات غير المؤكدة تُعرض كـ«غير معروف» بدون أي تخمين.`;
  }
  if (has("مرحبا", "السلام", "هلا", "اهلا", "أهلا")) {
    return "أهلًا بك، أنا مساعدك المالي. اسألني عن مصاريفك، فئات إنفاقك، أو اطلب نصيحة للتوفير.";
  }

  return `يمكنني مساعدتك في تحليل مصاريفك. إجمالي إنفاقك ${fmt(
    d.stats.total_spend,
  )} ر.س، وأعلى فئة «${sortedCat[0]?.name}». جرّب أحد الأسئلة المقترحة بالأسفل.`;
}
