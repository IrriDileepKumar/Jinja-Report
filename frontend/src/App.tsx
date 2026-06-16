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

const PRESETS: { label: string; draft: TemplateDraft }[] = [
  {
    label: "Operational Report",
    draft: {
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
        { id: "cpu_usage", title: "CPU Utilization", data_hint: ["node", "cpu", "utilization"], chart_type: "auto" },
        { id: "memory_usage", title: "Memory Usage", data_hint: ["node", "memory", "ram"], chart_type: "auto" },
      ],
    },
  },
  {
    label: "Power Analysis",
    draft: {
      template_id: "power_analysis",
      version: "1.0",
      layout: "base_extended",
      cover: {
        eyebrow: "Infrastructure Intelligence",
        report_title: "Power Analysis Report",
        report_subtitle: "Last 10 days",
        accent_1: "#22d3ee",
        accent_2: "#6366f1",
        accent_3: "#8b5cf6",
      },
      sections: [
        { id: "total_power", title: "Total Power Consumption", data_hint: ["power", "consumption", "watts", "idrac"], chart_type: "auto" },
        { id: "power_per_device", title: "Power per Device", data_hint: ["power", "consumption", "watts", "idrac"], chart_type: "auto" },
        { id: "power_capacity", title: "Power Capacity vs Consumed", data_hint: ["power", "capacity", "watts", "idrac"], chart_type: "auto" },
        { id: "psu_efficiency", title: "PSU Efficiency", data_hint: ["psu", "efficiency", "idrac"], chart_type: "auto" },
        { id: "psu_input_voltage", title: "PSU Input Voltage", data_hint: ["psu", "voltage", "input", "idrac"], chart_type: "auto" },
        { id: "psu_output_watts", title: "PSU Output Wattage", data_hint: ["psu", "output", "watts", "idrac"], chart_type: "auto" },
        { id: "power_peak", title: "Peak Power Consumption", data_hint: ["power", "peak", "max", "watts", "idrac"], chart_type: "auto" },
        { id: "psu_health", title: "PSU Health Status", data_hint: ["psu", "health", "idrac"], chart_type: "auto" },
      ],
    },
  },
  {
    label: "GPU Performance",
    draft: {
      template_id: "gpu_performance",
      version: "1.0",
      layout: "base_extended",
      cover: {
        eyebrow: "Infrastructure Intelligence",
        report_title: "GPU Performance Report",
        report_subtitle: "GPU metrics summary",
        accent_1: "#10b981",
        accent_2: "#6366f1",
        accent_3: "#f59e0b",
      },
      sections: [
        { id: "gpu_utilization", title: "GPU Utilization", data_hint: ["gpu", "utilization"], chart_type: "auto" },
        { id: "gpu_memory", title: "GPU Memory Usage", data_hint: ["gpu", "memory"], chart_type: "auto" },
        { id: "gpu_power", title: "GPU Power Draw", data_hint: ["gpu", "power"], chart_type: "auto" },
        { id: "gpu_temperature", title: "GPU Temperature", data_hint: ["gpu", "thermal", "temperature"], chart_type: "auto" },
      ],
    },
  },
  {
    label: "Datacenter Health",
    draft: {
      template_id: "datacenter_health",
      version: "1.0",
      layout: "base_extended",
      cover: {
        eyebrow: "Infrastructure Intelligence",
        report_title: "Datacenter Health Report",
        report_subtitle: "Full datacenter health overview",
        accent_1: "#f43f5e",
        accent_2: "#6366f1",
        accent_3: "#8b5cf6",
      },
      sections: [
        { id: "cpu_usage", title: "CPU Utilization", data_hint: ["node", "cpu", "utilization"], chart_type: "auto" },
        { id: "memory_usage", title: "Memory Usage", data_hint: ["node", "memory", "ram"], chart_type: "auto" },
        { id: "system_temperature", title: "System Temperature", data_hint: ["temperature", "thermal", "sensor", "idrac"], chart_type: "auto" },
        { id: "power_consumption", title: "Power Consumption", data_hint: ["power", "consumption", "watts", "idrac"], chart_type: "auto" },
        { id: "fan_speed", title: "Fan Speed", data_hint: ["fan", "speed", "rpm", "idrac"], chart_type: "auto" },
        { id: "system_health", title: "System Health", data_hint: ["system", "health", "idrac"], chart_type: "auto" },
      ],
    },
  },
];

const DEFAULT_DRAFT: TemplateDraft = PRESETS[0].draft;

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
    <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "1rem" }}>
      {/* Preset Selector */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
          marginBottom: "1rem",
          padding: "0.75rem 1rem",
          background: "#f8fafc",
          borderRadius: "8px",
          border: "1px solid #e2e8f0",
          flexWrap: "wrap",
        }}
      >
        <span style={{ fontWeight: 600, fontSize: "0.875rem", color: "#64748b", marginRight: "0.25rem" }}>
          Start from preset:
        </span>
        {PRESETS.map((preset) => {
          const isActive = draft.template_id === preset.draft.template_id;
          return (
            <button
              key={preset.label}
              onClick={() => setDraft(preset.draft)}
              style={{
                padding: "0.4rem 1rem",
                borderRadius: "20px",
                border: isActive ? "2px solid #6366f1" : "1px solid #cbd5e1",
                background: isActive ? "#6366f1" : "#fff",
                color: isActive ? "#fff" : "#334155",
                fontWeight: isActive ? 600 : 400,
                fontSize: "0.875rem",
                cursor: "pointer",
                transition: "all 0.15s ease",
              }}
            >
              {preset.label}
            </button>
          );
        })}
      </div>

    <div
      style={{
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
    </div>
  );
}
