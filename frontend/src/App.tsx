import React, { useEffect, useRef, useState } from "react";
import {
  api,
  CoverConfig,
  SectionDef,
  TemplateDraft,
  ValidationResult,
} from "./api/client";
import TemplateMetaForm from "./components/TemplateMetaForm";
import CoverEditor from "./components/CoverEditor";
import SectionList from "./components/SectionList";
import SectionPicker from "./components/SectionPicker";
import PreviewPane from "./components/PreviewPane";
import ExportPanel from "./components/ExportPanel";

const DEFAULT_DRAFT: TemplateDraft = {
  template_id: "my_report",
  version: "1.0",
  layout: "base_extended",
  cover: {
    eyebrow: "Infrastructure Intelligence",
    report_title: "Operational Report",
    report_subtitle: "Telemetry summary for the selected period.",
    accent_1: "#22d3ee",
    accent_2: "#6366f1",
    accent_3: "#8b5cf6",
  },
  sections: [
    {
      id: "cpu_usage",
      title: "CPU Utilization",
      data_hint: ["node", "cpu", "utilization"],
      chart_type: "auto",
    },
    {
      id: "memory_usage",
      title: "Memory Usage",
      data_hint: ["node", "memory", "ram"],
      chart_type: "auto",
    },
  ],
};

export default function App() {
  const [draft, setDraft] = useState<TemplateDraft>(DEFAULT_DRAFT);
  const [validation, setValidation] = useState<ValidationResult>({
    errors: [],
    warnings: [],
  });
  const [previewHtml, setPreviewHtml] = useState("");
  const [keywords, setKeywords] = useState<string[]>([]);
  const [showPicker, setShowPicker] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    api.catalogKeywords().then((r) => setKeywords(r.items));
  }, []);

  useEffect(() => {
    api.validate(draft).then((r) => setValidation(r));
  }, [draft]);

  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      api
        .preview(draft)
        .then((r) => setPreviewHtml(r.html))
        .catch(() => setPreviewHtml("<p>Preview error</p>"));
    }, 400);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [draft]);

  const addSection = (sec: SectionDef) => {
    setDraft({ ...draft, sections: [...draft.sections, sec] });
    setShowPicker(false);
  };

  return (
    <div
      style={{
        maxWidth: "1200px",
        margin: "0 auto",
        padding: "1rem",
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "1rem",
      }}
    >
      <div style={{ display: "grid", gap: "1rem" }}>
        <div
          style={{
            background: "#fff",
            padding: "1rem",
            borderRadius: "8px",
            border: "1px solid #e2e8f0",
          }}
        >
          <h2 style={{ marginTop: 0 }}>Template</h2>
          <TemplateMetaForm draft={draft} onChange={setDraft} />
        </div>
        <div
          style={{
            background: "#fff",
            padding: "1rem",
            borderRadius: "8px",
            border: "1px solid #e2e8f0",
          }}
        >
          <h2 style={{ marginTop: 0 }}>Cover</h2>
          <CoverEditor draft={draft} onChange={setDraft} />
        </div>
        <div
          style={{
            background: "#fff",
            padding: "1rem",
            borderRadius: "8px",
            border: "1px solid #e2e8f0",
          }}
        >
          <h2 style={{ marginTop: 0 }}>Sections</h2>
          <SectionList
            sections={draft.sections}
            keywords={keywords}
            onChange={(sections) => setDraft({ ...draft, sections })}
          />
          <button
            onClick={() => setShowPicker(true)}
            style={{
              marginTop: "0.5rem",
              padding: "0.5rem",
              width: "100%",
              borderRadius: "4px",
              border: "1px dashed #cbd5e1",
              background: "#f8fafc",
              cursor: "pointer",
            }}
          >
            + Add Section
          </button>
          {showPicker && (
            <div
              style={{
                marginTop: "0.5rem",
                padding: "0.75rem",
                borderRadius: "6px",
                border: "1px solid #e2e8f0",
                background: "#fff",
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
                <strong>Section Catalog</strong>
                <button
                  onClick={() => setShowPicker(false)}
                  style={{
                    border: "none",
                    background: "transparent",
                    cursor: "pointer",
                    fontWeight: 700,
                  }}
                >
                  ×
                </button>
              </div>
              <SectionPicker onPick={addSection} />
            </div>
          )}
        </div>
        <div
          style={{
            background: "#fff",
            padding: "1rem",
            borderRadius: "8px",
            border: "1px solid #e2e8f0",
          }}
        >
          <h2 style={{ marginTop: 0 }}>Export</h2>
          <ExportPanel draft={draft} validation={validation} />
        </div>
      </div>
      <div>
        <div
          style={{
            background: "#fff",
            padding: "1rem",
            borderRadius: "8px",
            border: "1px solid #e2e8f0",
          }}
        >
          <h2 style={{ marginTop: 0 }}>Preview</h2>
          <PreviewPane html={previewHtml} />
        </div>
      </div>
    </div>
  );
}
