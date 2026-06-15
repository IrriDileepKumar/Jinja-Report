const API_BASE = "/api";

export interface SectionDef {
  id: string;
  title: string;
  data_hint: string[];
  chart_type: string;
}

export interface CoverConfig {
  eyebrow: string;
  report_title: string;
  report_subtitle: string;
  accent_1: string;
  accent_2: string;
  accent_3: string;
}

export interface TemplateDraft {
  template_id: string;
  version: string;
  layout: string;
  cover: CoverConfig;
  sections: SectionDef[];
}

export interface ValidationResult {
  errors: string[];
  warnings: string[];
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

export const api = {
  catalogSections: (category?: string) =>
    get<{ items: Array<Record<string, unknown>> }>(
      `/catalog/sections${category ? `?category=${category}` : ""}`,
    ),
  catalogKeywords: () => get<{ items: string[] }>("/catalog/keywords"),
  catalogLayouts: () => get<{ items: Array<Record<string, unknown>> }>("/catalog/layouts"),
  validate: (draft: TemplateDraft) => post<ValidationResult>("/templates/validate", draft),
  generate: (draft: TemplateDraft) =>
    post<{ content: string; filename: string }>("/templates/generate", draft),
  preview: (draft: TemplateDraft) => post<{ html: string }>("/templates/preview", draft),
  saveDraft: (id: string, draft: TemplateDraft) =>
    fetch(`${API_BASE}/templates/drafts/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(draft),
    }),
  loadDraft: (id: string) => get<TemplateDraft>(`/templates/drafts/${id}`),
  listDrafts: () => get<{ ids: string[] }>("/templates/drafts"),
  importFile: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return fetch(`${API_BASE}/templates/import`, {
      method: "POST",
      body: form,
    }).then((r) => {
      if (!r.ok) throw new Error(`${r.status}: ${r.statusText}`);
      return r.json() as Promise<TemplateDraft>;
    });
  },
};
