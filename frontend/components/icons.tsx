// Minimal monochrome line icons (no emoji, no colorful badges).
import type { ReactNode } from "react";

const S = (children: ReactNode, cls = "ic") => (
  <svg className={cls} viewBox="0 0 24 24">
    {children}
  </svg>
);

export const Icon = {
  dashboard: () =>
    S(
      <>
        <rect x="3" y="3" width="7.5" height="7.5" rx="1.6" />
        <rect x="13.5" y="3" width="7.5" height="7.5" rx="1.6" />
        <rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.6" />
        <rect x="3" y="13.5" width="7.5" height="7.5" rx="1.6" />
      </>,
    ),
  transactions: () =>
    S(
      <>
        <path d="M16 3l4 4-4 4" />
        <path d="M20 7H8" />
        <path d="M8 21l-4-4 4-4" />
        <path d="M4 17h12" />
      </>,
    ),
  store: () =>
    S(
      <>
        <path d="M4 10.5V20h16v-9.5" />
        <path d="M3 4h18l1 5a3 3 0 01-6 0 3 3 0 01-6 0 3 3 0 01-6 0l1-5z" />
        <path d="M10 20v-5h4v5" />
      </>,
    ),
  analytics: () =>
    S(
      <>
        <path d="M4 4v16h16" />
        <path d="M8 16v-4" />
        <path d="M13 16V8" />
        <path d="M18 16v-6" />
      </>,
    ),
  settings: () =>
    S(
      <>
        <circle cx="12" cy="12" r="3.2" />
        <path d="M12 2.5v3M12 18.5v3M21.5 12h-3M5.5 12h-3M18.7 5.3l-2.1 2.1M7.4 16.6l-2.1 2.1M18.7 18.7l-2.1-2.1M7.4 7.4L5.3 5.3" />
      </>,
    ),
  wallet: () =>
    S(
      <>
        <rect x="2.5" y="5.5" width="19" height="13" rx="2.5" />
        <path d="M2.5 10h19" />
        <path d="M15.5 14.5h3" />
      </>,
    ),
  receipt: () =>
    S(
      <>
        <path d="M6 3h12v18l-2.5-1.5L13 21l-2.5-1.5L8 21l-2-1.5V3z" />
        <path d="M9 8h6M9 12h6" />
      </>,
    ),
  check: () =>
    S(
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M8 12.4l2.6 2.6L16 9.4" />
      </>,
    ),
  clock: () =>
    S(
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v5.2l3.2 2" />
      </>,
    ),
  search: (cls?: string) =>
    S(
      <>
        <circle cx="11" cy="11" r="7" />
        <path d="M20 20l-3.3-3.3" />
      </>,
      cls ?? "ic",
    ),
  arrow: () =>
    S(
      <>
        <path d="M19 12H5" />
        <path d="M11 6l-6 6 6 6" />
      </>,
    ),
  chevron: () => S(<path d="M15 6l-6 6 6 6" />),
  close: () => S(<path d="M6 6l12 12M18 6L6 18" />),
  food: () =>
    S(
      <>
        <path d="M6 3v6a2 2 0 004 0V3" />
        <path d="M8 9v12" />
        <path d="M17 3c-1.6 1-2.3 4-2.3 6.2 0 1.8 1 2.8 2.3 2.8v9" />
      </>,
    ),
  bag: () =>
    S(
      <>
        <path d="M6 8h12l-1 12H7L6 8z" />
        <path d="M9 8V6.5a3 3 0 016 0V8" />
      </>,
    ),
  cart: () =>
    S(
      <>
        <circle cx="9.5" cy="20" r="1.3" />
        <circle cx="17" cy="20" r="1.3" />
        <path d="M3 4h2.2l2 11h10l1.9-8H6.4" />
      </>,
    ),
  signal: () =>
    S(
      <>
        <path d="M5 20v-4" />
        <path d="M10 20v-8" />
        <path d="M15 20v-12" />
        <path d="M20 20V4" />
      </>,
    ),
  compare: () =>
    S(
      <>
        <path d="M8 4L4 8l4 4" />
        <path d="M4 8h11" />
        <path d="M16 20l4-4-4-4" />
        <path d="M20 16H9" />
      </>,
    ),
  chat: (cls?: string) =>
    S(
      <>
        <path d="M4 5h16v11H9l-4 4V5z" />
        <path d="M8.5 10.5h.01M12 10.5h.01M15.5 10.5h.01" />
      </>,
      cls,
    ),
  spark: (cls?: string) =>
    S(
      <>
        <path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3z" />
      </>,
      cls,
    ),
  bulb: () =>
    S(
      <>
        <path d="M9 18h6" />
        <path d="M10 21h4" />
        <path d="M12 3a6 6 0 00-4 10.5c.8.7 1 1 1 2.5h6c0-1.5.2-1.8 1-2.5A6 6 0 0012 3z" />
      </>,
    ),
  send: (cls?: string) =>
    S(
      <>
        <path d="M20 4L4 11l6 2 2 6 8-15z" />
        <path d="M10 13l4-4" />
      </>,
      cls,
    ),
  overview: () =>
    S(
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 12l4-2M12 12v5" />
      </>,
    ),
  home: () =>
    S(
      <>
        <path d="M3 11l9-8 9 8" />
        <path d="M5 9.5V20h14V9.5" />
        <path d="M9.5 20v-6h5v6" />
      </>,
    ),
  car: () =>
    S(
      <>
        <path d="M3 13l2-5.5A2 2 0 017 6h10a2 2 0 011.9 1.5L21 13v5h-2v-2H5v2H3v-5z" />
        <circle cx="7.5" cy="16" r="1.2" />
        <circle cx="16.5" cy="16" r="1.2" />
      </>,
    ),
  plane: () =>
    S(<path d="M21 15.5l-8-2V6.5a1.5 1.5 0 00-3 0V13.5l-8 2v2l8-1.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-3l8 1.5z" />),
  book: () =>
    S(
      <>
        <path d="M5 4h11a2 2 0 012 2v14H7a2 2 0 01-2-2V4z" />
        <path d="M5 18a2 2 0 012-2h11" />
      </>,
    ),
  heart: () =>
    S(<path d="M12 20s-7-4.5-9-9a4.5 4.5 0 018-3 4.5 4.5 0 018 3c-2 4.5-9 9-9 9z" />),
  building: () =>
    S(
      <>
        <path d="M5 21V5a1 1 0 011-1h9a1 1 0 011 1v16" />
        <path d="M16 10h3a1 1 0 011 1v10" />
        <path d="M8 8h2M8 12h2M8 16h2" />
      </>,
    ),
  play: () =>
    S(
      <>
        <rect x="3" y="5" width="18" height="14" rx="2.5" />
        <path d="M10 9l5 3-5 3V9z" />
      </>,
    ),
  cash: () =>
    S(
      <>
        <rect x="2.5" y="6" width="19" height="12" rx="2" />
        <circle cx="12" cy="12" r="2.5" />
        <path d="M6 9v6M18 9v6" />
      </>,
    ),
  health: () =>
    S(
      <>
        <rect x="4" y="4" width="16" height="16" rx="4" />
        <path d="M12 8v8M8 12h8" />
      </>,
    ),
  transfer: () =>
    S(
      <>
        <path d="M7 7h11l-3-3" />
        <path d="M17 17H6l3 3" />
      </>,
    ),
  income: () =>
    S(
      <>
        <path d="M12 4v10" />
        <path d="M8 10l4 4 4-4" />
        <path d="M5 20h14" />
      </>,
    ),
  trend: () =>
    S(
      <>
        <path d="M4 15l5-5 3 3 6-7" />
        <path d="M18 6h-3M18 6v3" />
      </>,
    ),
  edit: (cls?: string) =>
    S(
      <>
        <path d="M4 20h4L18.5 9.5a2 2 0 00-2.8-2.8L5 17v3z" />
        <path d="M13.5 6.5l4 4" />
      </>,
      cls,
    ),
};

// Arabic category label -> category icon (covers the 15-category taxonomy).
export function catIcon(cat: string) {
  switch (cat) {
    case "مطاعم":
    case "مطاعم وطعام":
      return Icon.food();
    case "توصيل طعام":
      return Icon.food();
    case "تسوّق":
      return Icon.bag();
    case "بقالة":
    case "بقالة وتموين":
      return Icon.cart();
    case "اتصالات":
      return Icon.signal();
    case "نقل ووقود":
      return Icon.car();
    case "فواتير ومرافق":
      return Icon.receipt();
    case "صحة وصيدليات":
      return Icon.health();
    case "ترفيه واشتراكات":
      return Icon.play();
    case "سفر وطيران":
      return Icon.plane();
    case "تعليم":
      return Icon.book();
    case "خدمات حكومية":
      return Icon.building();
    case "صدقات وتبرعات":
      return Icon.heart();
    case "تحويلات":
      return Icon.transfer();
    case "دخل ورواتب":
      return Icon.income();
    case "سحب نقدي":
      return Icon.cash();
    default:
      return Icon.store();
  }
}
