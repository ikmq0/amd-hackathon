import type { Metadata } from "next";
import { IBM_Plex_Mono, IBM_Plex_Sans_Arabic } from "next/font/google";

import BottomNav from "@/components/BottomNav";
import Sidebar from "@/components/Sidebar";
import "./globals.css";

const ibm = IBM_Plex_Sans_Arabic({
  subsets: ["arabic", "latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-ibm",
  display: "swap",
});

const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "مِدْ — لوحة التحكم",
  description: "محرك فك تشفير العمليات البنكية — توضيح التجّار وتصنيف المصاريف",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ar" dir="rtl" className={`${ibm.variable} ${mono.variable}`}>
      <body>
        <div className="app">
          <Sidebar />
          <div className="device">
            <div className="screen">{children}</div>
            <BottomNav />
          </div>
        </div>
      </body>
    </html>
  );
}
