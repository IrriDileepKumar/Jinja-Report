import React from "react";
import { TemplateDraft } from "../api/client";

interface Props {
  draft: TemplateDraft;
  onChange: (d: TemplateDraft) => void;
}

export default function CoverEditor({ draft, onChange }: Props) {
  const updateCover = (patch: Partial<TemplateDraft["cover"]>) => {
    onChange({ ...draft, cover: { ...draft.cover, ...patch } });
  };

  return (
    <div style={{ display: "grid", gap: "0.5rem" }}>
      <label>
        Eyebrow
        <input
          type="text"
          value={draft.cover.eyebrow}
          onChange={(e) => updateCover({ eyebrow: e.target.value })}
          style={{ width: "100%", padding: "0.4rem", marginTop: "0.2rem" }}
        />
      </label>
      <label>
        Report Title
        <input
          type="text"
          value={draft.cover.report_title}
          onChange={(e) => updateCover({ report_title: e.target.value })}
          style={{ width: "100%", padding: "0.4rem", marginTop: "0.2rem" }}
        />
      </label>
      <label>
        Subtitle
        <textarea
          value={draft.cover.report_subtitle}
          onChange={(e) => updateCover({ report_subtitle: e.target.value })}
          rows={3}
          style={{ width: "100%", padding: "0.4rem", marginTop: "0.2rem" }}
        />
      </label>
      <div style={{ display: "flex", gap: "0.5rem" }}>
        {(["accent_1", "accent_2", "accent_3"] as const).map((key) => (
          <label key={key} style={{ flex: 1 }}>
            {key.replace("_", " ").toUpperCase()}
            <input
              type="color"
              value={draft.cover[key]}
              onChange={(e) => updateCover({ [key]: e.target.value })}
              style={{ width: "100%", height: "2rem", marginTop: "0.2rem" }}
            />
          </label>
        ))}
      </div>
    </div>
  );
}
