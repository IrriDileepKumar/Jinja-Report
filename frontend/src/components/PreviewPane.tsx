import React from "react";

interface Props {
  html: string;
}

export default function PreviewPane({ html }: Props) {
  return (
    <iframe
      title="Preview"
      srcDoc={html}
      style={{
        width: "100%",
        height: "600px",
        border: "1px solid #e2e8f0",
        borderRadius: "6px",
        background: "#fff",
      }}
    />
  );
}
