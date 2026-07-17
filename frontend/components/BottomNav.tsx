"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Icon } from "./icons";

const TABS = [
  { href: "/", label: "الرئيسية", icon: Icon.home },
  { href: "/transactions", label: "العمليات", icon: Icon.compare },
  { href: "/dashboard", label: "لوحتي", icon: Icon.trend },
  { href: "/assistant", label: "المساعد", icon: () => Icon.chat() },
];

export default function BottomNav() {
  const pathname = usePathname();
  return (
    <nav className="bottom-nav">
      {TABS.map((t) => {
        const active = t.href === "/" ? pathname === "/" : pathname.startsWith(t.href);
        return (
          <Link key={t.href} href={t.href} className={`tab${active ? " active" : ""}`}>
            {t.icon()}
            {t.label}
          </Link>
        );
      })}
    </nav>
  );
}
