import React, { useState } from "react";
import { SectionDef } from "../api/client";

interface Props {
  section: SectionDef;
  keywords: string[];
  onChange: (s: SectionDef) => void;
}

export default function SectionEditor({ section, keywords, onChange }: Props) {
  const [kwInput, setKwInput] = useState("");

  const addKeyword = (kw: string) => {
    const trimmed = kw.trim();
    if (!trimmed) return;
    if (section.data_hint.includes(trimmed)) return;
    onChange({ ...section, data_hint: [...section.data_hint, trimmed] });
    setKwInput("");
  };

  const removeKeyword = (idx: number) => {
    const next = [...section.data_hint];
    next.splice(idx, 1);
    onChange({ ...section, data_hint: next });
  };

  const suggestions = keywords.filter(
    (k) =>
      kwInput.length > 0 &&
      k.toLowerCase().includes(kwInput.toLowerCase()) &&
      !section.data_hint.includes(k)
  ).slice(0, 6);

  return (
    <div style={{ display: "grid", gap: "0.5rem", padding: "0.5rem 0" }}>
      <label>
        Title
        <input
          type="text"
          value={section.title}
          onChange={(e) => onChange({ ...section, title: e.target.value })}
          style={{ width: "100%", padding: "0.4rem", marginTop: "0.2rem" }}
        />
      </label>
      <label>
        ID
        <input
          type="text"
          value={section.id}
          onChange={(e) => onChange({ ...section, id: e.target.value })}
          style={{ width: "100%", padding: "0.4rem", marginTop: "0.2rem" }}
        />
      </label>
      <div>
        <div style={{ fontSize: "0.85rem", marginBottom: "0.25rem" }}>
          Data Hints
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.3rem" }}>
          {section.data_hint.map((kw, i) => (
            <span
              key={i}
              style={{
                background: "#e2e8f0",
                padding: "0.2rem 0.5rem",
                borderRadius: "999px",
                fontSize: "0.85rem",
                display: "inline-flex",
                alignItems: "center",
                gap: "0.3rem",
              }}
            >
              {kw}
              <button
                onClick={() => removeKeyword(i)}
                style={{
                  border: "none",
                  background: "transparent",
                  cursor: "pointer",
                  fontWeight: 700,
                }}
              >
                ×
              </button>
            </span>
          ))}
        </div>
        <input
          type="text"
          value={kwInput}
          onChange={(e) => setKwInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              addKeyword(kwInput);
            }
          }}
          placeholder="Add keyword..."
          style={{ width: "100%", padding: "0.4rem", marginTop: "0.3rem" }}
        />
        {suggestions.length > 0 && (
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "0.3rem",
              marginTop: "0.3rem",
            }}
          >
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => addKeyword(s)}
                style={{
                  fontSize: "0.8rem",
                  padding: "0.2rem 0.4rem",
                  borderRadius: "4px",
                  border: "1px solid #cbd5e1",
                  background: "#fff",
                }}
              >
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
      <label>
        Chart Type
        <select
          value={section.chart_type}
          onChange={(e) =>
            onChange({ ...section, chart_type: e.target.value })
          }
          style={{ width: "100%", padding: "0.4rem", marginTop: "0.2rem" }}
        >
          <option value="auto">auto</option>
          <option value="line">line</option>
          <option value="bar">bar</option>
          <option value="area">area</option>
        </select>
      </label>
    </div>
  );
}
