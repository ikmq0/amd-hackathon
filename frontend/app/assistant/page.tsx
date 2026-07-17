"use client";

import { useEffect, useRef, useState } from "react";

import { Icon } from "@/components/icons";
import { Typewriter } from "@/components/Typewriter";
import { PageHeader } from "@/components/ui";
import { api } from "@/lib/api";
import { answerQuestion, buildSuggestions, SUGGESTED, type InsightData } from "@/lib/insights";

interface Msg {
  role: "bot" | "user";
  text: string;
  animate?: boolean;
}

export default function AssistantPage() {
  const [data, setData] = useState<InsightData | null>(null);
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "bot",
      text: "أهلًا، أنا مساعدك المالي في مِدْ. أجيب عن أسئلتك اعتمادًا على عملياتك الفعلية — بدون تخمين. كيف أقدر أساعدك؟",
      animate: true,
    },
  ]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const logRef = useRef<HTMLDivElement>(null);

  const scrollDown = () =>
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: "smooth" });

  useEffect(() => {
    Promise.all([api.stats(), api.breakdown(), api.merchants(), api.monthly()])
      .then(([stats, breakdown, merchants, monthly]) =>
        setData({ stats, breakdown, merchants, monthly }),
      )
      .catch(() => setData(null));
  }, []);

  useEffect(() => {
    scrollDown();
  }, [messages, typing]);

  const suggestions = data ? buildSuggestions(data) : SUGGESTED;

  async function ask(qRaw?: string) {
    const q = (qRaw ?? input).trim();
    if (!q || typing) return;
    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setTyping(true);
    // Real LLM answer, grounded on the user's aggregates. If the backend LLM is
    // unavailable (no key / offline), degrade to the computed local answer so the
    // assistant never dead-ends.
    let reply: string;
    try {
      reply = (await api.chat(q)).answer;
    } catch {
      reply = data
        ? answerQuestion(q, data)
        : "تعذّر الوصول إلى المساعد حاليًا. حاول مرة أخرى بعد قليل.";
    }
    setTyping(false);
    setMessages((m) => [...m, { role: "bot", text: reply, animate: true }]);
  }

  return (
    <>
      <PageHeader
        title="المساعد الذكي"
        subtitle="اسأل عن مصاريفك واحصل على إجابات مبنية على بياناتك."
      />

      <div className="sec" style={{ marginTop: 18 }}>
        <div className="chat-wrap">
          <div className="chat-log" ref={logRef}>
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.role}`}>
                {m.role === "bot" ? (
                  <Typewriter text={m.text} animate={!!m.animate} onUpdate={scrollDown} />
                ) : (
                  m.text
                )}
              </div>
            ))}
            {typing && (
              <div className="msg bot typing-bubble">
                <span className="dots">
                  <i />
                  <i />
                  <i />
                </span>
              </div>
            )}
          </div>

          <div className="suggest">
            {suggestions.map((s) => (
              <span key={s} onClick={() => ask(s)}>
                {s}
              </span>
            ))}
          </div>

          <div className="chat-input">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && ask()}
              placeholder="اكتب سؤالك المالي…"
            />
            <button className="chat-send" onClick={() => ask()} aria-label="إرسال">
              {Icon.send("ic")}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
