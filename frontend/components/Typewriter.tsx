"use client";

import { useEffect, useState } from "react";

import { Markdown } from "@/components/Markdown";

// Reveals bot text progressively (a "writing" effect), re-rendering the Markdown
// each frame. Longer answers reveal in bigger chunks so they still finish quickly.
// A dangling "**" (bold opener whose closer isn't revealed yet) is hidden so no
// stray asterisks flash mid-type.
export function Typewriter({
  text,
  animate = true,
  onUpdate,
}: {
  text: string;
  animate?: boolean;
  onUpdate?: () => void;
}) {
  const [n, setN] = useState(animate ? 0 : text.length);

  useEffect(() => {
    if (!animate) {
      setN(text.length);
      return;
    }
    setN(0);
    if (!text) return;
    const step = Math.max(1, Math.round(text.length / 90)); // ~90 ticks total
    let i = 0;
    const id = window.setInterval(() => {
      i = Math.min(text.length, i + step);
      setN(i);
      onUpdate?.();
      if (i >= text.length) window.clearInterval(id);
    }, 20);
    return () => window.clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [text, animate]);

  let shown = text.slice(0, n);
  const stars = (shown.match(/\*\*/g) || []).length;
  if (stars % 2 === 1) shown = shown.slice(0, shown.lastIndexOf("**"));

  return (
    <span className={n < text.length ? "typing-cursor" : undefined}>
      <Markdown text={shown} />
    </span>
  );
}
