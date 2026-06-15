"""Generate .html.j2 content from a TemplateDraft."""

from __future__ import annotations

import yaml

from .models import TemplateDraft
from .validator import validate_draft


def generate_html_j2(draft: TemplateDraft) -> str:
    """Generate a complete .html.j2 file string from a draft.

    Args:
        draft: The template draft to render.

    Returns:
        Complete file content as a string.

    Raises:
        ValueError: If draft validation fails.
    """
    result = validate_draft(draft)
    if result.errors:
        raise ValueError("Draft validation failed: " + "; ".join(result.errors))

    front_matter = {
        "template_id": draft.template_id,
        "version": draft.version,
        "sections": [
            {
                "id": s.id,
                "title": s.title,
                "data_hint": s.data_hint,
                "chart_type": s.chart_type,
            }
            for s in draft.sections
        ],
    }

    yaml_str = yaml.safe_dump(
        front_matter,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ).strip()

    cover = draft.cover
    lines = [
        "{# ---",
        yaml_str,
        "--- #}",
        '{% extends "_base.html.j2" %}',
        "",
        f"{{% block eyebrow %}}{cover.eyebrow}{{% endblock %}}",
        f"{{% block report_title %}}{cover.report_title}{{% endblock %}}",
        "{% block report_subtitle %}",
        cover.report_subtitle,
        "{% endblock %}",
        f"{{% block accent_1 %}}{cover.accent_1}{{% endblock %}}",
        f"{{% block accent_2 %}}{cover.accent_2}{{% endblock %}}",
        f"{{% block accent_3 %}}{cover.accent_3}{{% endblock %}}",
        "",
    ]
    return "\n".join(lines) + "\n"
