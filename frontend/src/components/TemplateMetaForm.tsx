import React from "react";
import { TemplateDraft } from "../api/client";

interface Props {
  draft: TemplateDraft;
  onChange: (d: TemplateDraft) => void;
}

export default function TemplateMetaForm({ draft, onChange }: Props) {
  return (
    <div style={{ display: "grid", gap: "0.5rem" }}>
      <label>
        Template ID
        <input
          type="text"
          value={draft.template_id}
          onChange={(e) =>
            onChange({ ...draft, template_id: e.target.value })
          }
          style={{ width: "100%", padding: "0.4rem", marginTop: "0.2rem" }}
        />
      </label>
      <label>
        Version
        <input
          type="text"
          value={draft.version}
          onChange={(e) =>
            onChange({ ...draft, version: e.target.value })
          }
          style={{ width: "100%", padding: "0.4rem", marginTop: "0.2rem" }}
        />
      </label>
    </div>
  );
}
