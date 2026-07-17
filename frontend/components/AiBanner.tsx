import Link from "next/link";

import { Icon } from "./icons";

export function AiBanner() {
  return (
    <div className="ai-banner">
      <div className="ai-ico">{Icon.chat()}</div>
      <div>
        <b>المساعد المالي الذكي</b>
        <p>اسأل عن مصاريفك، فئات إنفاقك، أو اطلب نصيحة لتوفير المال — بإجابات مبنية على بياناتك الفعلية.</p>
      </div>
      <Link href="/assistant" className="btn btn-white">
        {Icon.spark("ic ic-sm")} ابدأ المحادثة
      </Link>
    </div>
  );
}
