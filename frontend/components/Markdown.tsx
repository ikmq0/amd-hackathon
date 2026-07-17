import type { ReactNode } from "react";

// Minimal, dependency-free Markdown renderer for the LLM monthly report.
// Handles the shapes Gemini returns: headings (#, ##, ###), **bold**, bullet
// lists (-, *, •), and paragraphs. No raw HTML injection.

function inline(text: string, keyBase: string): ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
  return parts.map((p, i) =>
    p.startsWith("**") && p.endsWith("**") ? (
      <strong key={`${keyBase}-b${i}`}>{p.slice(2, -2)}</strong>
    ) : (
      <span key={`${keyBase}-t${i}`}>{p}</span>
    ),
  );
}

export function Markdown({ text }: { text: string }) {
  const lines = text.replace(/\r/g, "").split("\n");
  const blocks: ReactNode[] = [];
  let list: ReactNode[] = [];

  const flushList = () => {
    if (list.length) {
      blocks.push(
        <ul className="md-list" key={`ul-${blocks.length}`}>
          {list}
        </ul>,
      );
      list = [];
    }
  };

  lines.forEach((raw, i) => {
    const line = raw.trim();
    if (!line) {
      flushList();
      return;
    }
    const bullet = line.match(/^[-*•]\s+(.*)$/);
    if (bullet) {
      list.push(<li key={`li-${i}`}>{inline(bullet[1], `li-${i}`)}</li>);
      return;
    }
    flushList();
    const heading = line.match(/^(#{1,6})\s+(.*)$/);
    if (heading) {
      blocks.push(
        <h3 className="md-h" key={`h-${i}`}>
          {inline(heading[2], `h-${i}`)}
        </h3>,
      );
      return;
    }
    blocks.push(
      <p className="md-p" key={`p-${i}`}>
        {inline(line, `p-${i}`)}
      </p>,
    );
  });
  flushList();

  return <div className="md">{blocks}</div>;
}
