import React from "react";

import { useAICopilot } from "./AICopilotContext";

/**
 * Button shown in the AppBar to toggle the AI Copilot panel.
 * Must be rendered inside AICopilotProvider.
 */
export const AIBarButton: React.FC = () => {
  const { isOpen, openPanel, closePanel } = useAICopilot();

  return (
    <button
      onClick={() => (isOpen ? closePanel() : openPanel("chat"))}
      title={isOpen ? "Cerrar AI Copilot" : "Abrir AI Copilot"}
      style={{
        display: "flex",
        alignItems: "center",
        gap: "5px",
        padding: "5px 12px",
        background: isOpen ? "var(--mb-color-brand, #0F766E)" : "transparent",
        color: isOpen ? "white" : "var(--mb-color-brand, #0F766E)",
        border: "1.5px solid var(--mb-color-brand, #0F766E)",
        borderRadius: "20px",
        cursor: "pointer",
        fontSize: "12px",
        fontWeight: "600",
        transition: "all 0.15s",
        whiteSpace: "nowrap",
        height: "32px",
      }}
    >
      <span>✨</span>
      <span>Ask AI</span>
    </button>
  );
};
