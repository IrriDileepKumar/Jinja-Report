import React, { useEffect, useState } from "react";
import { api, SectionDef } from "../api/client";

interface Props {
  onPick: (section: SectionDef) => void;
}

export default function SectionPicker({ onPick }: Props) {
  const [catalog, setCatalog] = useState<Array<Record<string, unknown>>>([]);
  const [filter, setFilter] = useState("");
  const [category, setCategory] = useState("");

  useEffect(() => {
    api.catalogSections().then((r) => setCatalog(r.items));
  }, []);

  const categories = Array.from(
    new Set(catalog.map((c) => String(c.category || "other")))
  ).sort();

  const filtered = catalog.filter((c) => {
    const title = String(c.title || "").toLowerCase();
    const cat = String(c.category || "");
    const q = filter.toLowerCase();
    const matchesText = title.includes(q);
    const matchesCat = !category || cat === category;
    return matchesText && matchesCat;
  });

  return (
    <div>
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}>
        <input
          type="text"
          placeholder="Search sections..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{ flex: 1, padding: "0.4rem" }}
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          style={{ padding: "0.4rem" }}
        >
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>
      <div style={{ maxHeight: "300px", overflowY: "auto" }}>
        {filtered.map((entry) => {
          const id = String(entry.catalog_id);
          const title = String(entry.title);
          const hints = (entry.default_data_hint as string[]) || [];
          return (
            <div
              key={id + title}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "0.5rem",
                borderBottom: "1px solid #f1f5f9",
              }}
            >
              <div>
                <div style={{ fontWeight: 600 }}>{title}</div>
                <div style={{ fontSize: "0.8rem", color: "#64748b" }}>
                  {hints.join(", ")}
                </div>
              </div>
              <button
                onClick={() =>
                  onPick({
                    id,
                    title,
                    data_hint: hints.length ? hints : [id],
                    chart_type: "auto",
                  })
                }
                style={{
                  padding: "0.3rem 0.6rem",
                  borderRadius: "4px",
                  border: "1px solid #cbd5e1",
                  background: "#fff",
                  cursor: "pointer",
                }}
              >
                Add
              </button>
            </div>
          );
        })}
      </div>
      <button
        onClick={() =>
          onPick({
            id: `custom_${Date.now()}`,
            title: "Custom Section",
            data_hint: ["node"],
            chart_type: "auto",
          })
        }
        style={{
          width: "100%",
          marginTop: "0.5rem",
          padding: "0.5rem",
          borderRadius: "4px",
          border: "1px dashed #cbd5e1",
          background: "#f8fafc",
          cursor: "pointer",
        }}
      >
        + Custom Section
      </button>
    </div>
  );
}
