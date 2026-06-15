import React, { useRef, useState } from "react";
import { api, TemplateDraft, ValidationResult } from "../api/client";

interface Props {
  draft: TemplateDraft;
  validation: ValidationResult;
}

export default function ExportPanel({ draft, validation }: Props) {
  const [importing, setImporting] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const download = async () => {
    const { content, filename } = await api.generate(draft);
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const onImport = async (file: File) => {
    setImporting(true);
    try {
      await api.importFile(file);
      alert("Import successful (check console for draft).");
    } catch (e) {
      alert(`Import failed: ${e}`);
    } finally {
      setImporting(false);
    }
  };

  const hasErrors = validation.errors.length > 0;

  return (
    <div style={{ display: "grid", gap: "0.5rem" }}>
      <button
        onClick={download}
        disabled={hasErrors}
        style={{
          padding: "0.6rem",
          borderRadius: "6px",
          border: "none",
          background: hasErrors ? "#e2e8f0" : "#0f172a",
          color: hasErrors ? "#64748b" : "#fff",
          cursor: hasErrors ? "not-allowed" : "pointer",
        }}
      >
        Export .html.j2
      </button>
      {hasErrors && (
        <div style={{ color: "#dc2626", fontSize: "0.85rem" }}>
          Fix errors before export.
        </div>
      )}
      <div style={{ fontSize: "0.85rem", color: "#64748b" }}>
        Errors: {validation.errors.length} | Warnings:{" "}
        {validation.warnings.length}
      </div>
      <div>
        <input
          type="file"
          accept=".html.j2"
          ref={fileRef}
          style={{ display: "none" }}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) onImport(file);
            if (fileRef.current) fileRef.current.value = "";
          }}
        />
        <button
          onClick={() => fileRef.current?.click()}
          disabled={importing}
          style={{
            padding: "0.6rem",
            borderRadius: "6px",
            border: "1px solid #cbd5e1",
            background: "#fff",
            cursor: "pointer",
            width: "100%",
          }}
        >
          {importing ? "Importing..." : "Import .html.j2"}
        </button>
      </div>
    </div>
  );
}
