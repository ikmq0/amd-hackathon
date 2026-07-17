"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Icon } from "./icons";

const NAV = [
  { href: "/", label: "الرئيسية", icon: Icon.home },
  { href: "/transactions", label: "العمليات", icon: Icon.compare },
  { href: "/dashboard", label: "لوحتي المالية", icon: Icon.trend },
  { href: "/assistant", label: "المساعد الذكي", icon: () => Icon.chat() },
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-word">مِدْ</span>
      </div>
      <nav className="side-nav">
        {NAV.map((n) => {
          const active = n.href === "/" ? pathname === "/" : pathname.startsWith(n.href);
          return (
            <Link key={n.href} href={n.href} className={`nav-item${active ? " active" : ""}`}>
              {n.icon()} {n.label}
            </Link>
          );
        })}
      </nav>
      <div className="sidebar-foot">
        <div className="account">
          <div className="acc-avatar">خ</div>
          <div>
            <div className="acc-name">خالد محمود</div>
            <div className="acc-sub">حسابك الشخصي</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
