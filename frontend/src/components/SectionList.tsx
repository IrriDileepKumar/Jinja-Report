import React, { useState } from "react";
import { SectionDef } from "../api/client";
import SectionEditor from "./SectionEditor";

interface Props {
  sections: SectionDef[];
  keywords: string[];
  onChange: (sections: SectionDef[]) => void;
}

export default function SectionList({ sections, keywords, onChange }: Props) {
  const [dragIndex, setDragIndex] = useState<number | null>(null);

  const move = (from: number, to: number) => {
    const next = [...sections];
    const [item] = next.splice(from, 1);
    next.splice(to, 0, item);
    onChange(next);
  };

  const updateSection = (idx: number, updated: SectionDef) => {
    const next = [...sections];
    next[idx] = updated;
    onChange(next);
  };

  const removeSection = (idx: number) => {
    const next = [...sections];
    next.splice(idx, 1);
    onChange(next);
  };

  return (
    <div style={{ display: "grid", gap: "0.5rem" }}>
      {sections.map((sec, idx) => (
        <div
          key={sec.id + idx}
          draggable
          onDragStart={() => setDragIndex(idx)}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            if (dragIndex !== null && dragIndex !== idx) {
              move(dragIndex, idx);
            }
            setDragIndex(null);
          }}
          style={{
            background: "#fff",
            border: "1px solid #e2e8f0",
            borderRadius: "6px",
            padding: "0.75rem",
            cursor: "grab",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "0.5rem",
            }}
          >
            <strong>
              {idx + 1}. {sec.title}
            </strong>
            <button
              onClick={() => removeSection(idx)}
              style={{
                border: "none",
                background: "transparent",
                color: "#dc2626",
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              Remove
            </button>
          </div>
          <SectionEditor
            section={sec}
            keywords={keywords}
            onChange={(s) => updateSection(idx, s)}
          />
        </div>
      ))}
    </div>
  );
}
