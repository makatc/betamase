import React, { useEffect, useRef, useState } from "react";

import { type CopilotTab, useAICopilot } from "./AICopilotContext";

const BRAND = "var(--mb-color-brand, #0F766E)";

const TABS: { id: CopilotTab; label: string; title: string }[] = [
  { id: "chat", label: "💬 Chat", title: "Pregunta en lenguaje natural" },
  { id: "sql", label: "🔍 SQL", title: "Genera y edita consultas SQL" },
  { id: "insights", label: "💡 Insights", title: "Resúmenes automáticos" },
];

// ─── Chat Tab ────────────────────────────────────────────────────────────────

function ChatTab() {
  const { messages, isLoading, sendMessage } = useAICopilot();
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isLoading) {
      return;
    }
    setInput("");
    await sendMessage(text);
  };

  return (
    <div
      style={{ display: "flex", flexDirection: "column", height: "100%" }}
    >
      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "12px",
          display: "flex",
          flexDirection: "column",
          gap: "8px",
        }}
      >
        {messages.length === 0 && (
          <div
            style={{
              color: "#94a3b8",
              textAlign: "center",
              marginTop: "48px",
              padding: "0 20px",
            }}
          >
            <div style={{ fontSize: "36px", marginBottom: "12px" }}>🤖</div>
            <div
              style={{
                fontWeight: "600",
                marginBottom: "8px",
                color: "#64748b",
                fontSize: "15px",
              }}
            >
              AI Data Assistant
            </div>
            <div style={{ fontSize: "13px", lineHeight: "1.6", color: "#94a3b8" }}>
              Pregúntame en lenguaje natural sobre tus datos.
              <br />
              Ej: <em>&ldquo;¿Cuál fue el revenue este trimestre?&rdquo;</em>
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              background: m.role === "user" ? BRAND : "#F1F5F9",
              color: m.role === "user" ? "white" : "#1e293b",
              padding: "10px 14px",
              borderRadius:
                m.role === "user"
                  ? "18px 18px 4px 18px"
                  : "18px 18px 18px 4px",
              maxWidth: "85%",
              fontSize: "13px",
              lineHeight: "1.55",
              whiteSpace: "pre-wrap",
            }}
          >
            {m.text}
          </div>
        ))}

        {isLoading && (
          <div
            style={{
              alignSelf: "flex-start",
              background: "#F1F5F9",
              padding: "10px 14px",
              borderRadius: "18px 18px 18px 4px",
              color: "#64748b",
              fontSize: "13px",
            }}
          >
            ···
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div
        style={{
          padding: "12px",
          borderTop: "1px solid #e2e8f0",
          display: "flex",
          gap: "8px",
          background: "white",
          flexShrink: 0,
        }}
      >
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleSend()}
          placeholder="Pregunta sobre tus datos..."
          disabled={isLoading}
          style={{
            flex: 1,
            padding: "10px 14px",
            borderRadius: "20px",
            border: "1.5px solid #e2e8f0",
            outline: "none",
            fontSize: "13px",
            background: isLoading ? "#f8fafc" : "white",
          }}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          style={{
            background: BRAND,
            color: "white",
            border: "none",
            borderRadius: "50%",
            width: "38px",
            height: "38px",
            cursor: isLoading ? "not-allowed" : "pointer",
            opacity: isLoading || !input.trim() ? 0.5 : 1,
            fontSize: "18px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          ↑
        </button>
      </div>
    </div>
  );
}

// ─── SQL Tab ─────────────────────────────────────────────────────────────────

function SQLTab() {
  const { generatedSQL, isLoading, generateSQL } = useAICopilot();
  const [prompt, setPrompt] = useState("");
  const [editableSQL, setEditableSQL] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (generatedSQL) {
      setEditableSQL(generatedSQL);
    }
  }, [generatedSQL]);

  const handleGenerate = async () => {
    await generateSQL(prompt);
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(editableSQL);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        padding: "14px",
        gap: "12px",
        overflowY: "auto",
      }}
    >
      {/* Prompt input */}
      <div>
        <label
          style={{
            fontSize: "11px",
            fontWeight: "700",
            color: "#64748b",
            display: "block",
            marginBottom: "6px",
            letterSpacing: "0.05em",
            textTransform: "uppercase",
          }}
        >
          Descripción en lenguaje natural
        </label>
        <textarea
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder="Ej: Muestra las ventas totales por mes del último año"
          rows={3}
          style={{
            width: "100%",
            padding: "10px 12px",
            borderRadius: "8px",
            border: "1.5px solid #e2e8f0",
            fontSize: "13px",
            resize: "none",
            outline: "none",
            boxSizing: "border-box",
            lineHeight: "1.5",
          }}
        />
        <button
          onClick={handleGenerate}
          disabled={isLoading || !prompt.trim()}
          style={{
            width: "100%",
            padding: "10px",
            marginTop: "8px",
            background: BRAND,
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: isLoading || !prompt.trim() ? "not-allowed" : "pointer",
            fontSize: "13px",
            fontWeight: "600",
            opacity: isLoading || !prompt.trim() ? 0.6 : 1,
            transition: "opacity 0.15s",
          }}
        >
          {isLoading ? "Generando…" : "✨ Generar SQL"}
        </button>
      </div>

      {/* Generated SQL editor */}
      {editableSQL && (
        <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "6px",
            }}
          >
            <label
              style={{
                fontSize: "11px",
                fontWeight: "700",
                color: "#64748b",
                letterSpacing: "0.05em",
                textTransform: "uppercase",
              }}
            >
              SQL Generado <span style={{ color: "#94a3b8" }}>(editable)</span>
            </label>
            <button
              onClick={handleCopy}
              style={{
                background: "none",
                border: "none",
                cursor: "pointer",
                fontSize: "12px",
                color: BRAND,
                fontWeight: "600",
              }}
            >
              {copied ? "✓ Copiado" : "📋 Copiar"}
            </button>
          </div>
          <textarea
            value={editableSQL}
            onChange={e => setEditableSQL(e.target.value)}
            style={{
              flex: 1,
              padding: "12px",
              borderRadius: "8px",
              border: "1.5px solid #e2e8f0",
              fontSize: "12px",
              fontFamily: "ui-monospace, 'Fira Code', monospace",
              resize: "none",
              outline: "none",
              background: "#f8fafc",
              minHeight: "180px",
              lineHeight: "1.6",
            }}
          />
          <p
            style={{
              fontSize: "11px",
              color: "#94a3b8",
              marginTop: "6px",
              marginBottom: 0,
            }}
          >
            ⚠️ Revisa antes de ejecutar. Solo se permiten consultas SELECT.
          </p>
        </div>
      )}
    </div>
  );
}

// ─── Insights Tab ─────────────────────────────────────────────────────────────

function InsightsTab() {
  return (
    <div
      style={{
        padding: "32px 20px",
        textAlign: "center",
        color: "#64748b",
      }}
    >
      <div style={{ fontSize: "40px", marginBottom: "16px" }}>💡</div>
      <div
        style={{
          fontSize: "15px",
          fontWeight: "600",
          marginBottom: "10px",
          color: "#475569",
        }}
      >
        Insights Automáticos
      </div>
      <div
        style={{
          fontSize: "13px",
          lineHeight: "1.7",
          color: "#94a3b8",
          maxWidth: "280px",
          margin: "0 auto",
        }}
      >
        Los insights se generan automáticamente al visualizar gráficos y
        dashboards. Navega a cualquier dashboard para ver el análisis de tus
        datos.
      </div>
    </div>
  );
}

// ─── Main Panel ───────────────────────────────────────────────────────────────

export const AICopilotPanel: React.FC = () => {
  const { isOpen, activeTab, setActiveTab, closePanel } = useAICopilot();

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        right: 0,
        bottom: 0,
        width: "380px",
        background: "white",
        boxShadow: "-4px 0 32px rgba(0,0,0,0.14)",
        zIndex: 400,
        display: "flex",
        flexDirection: "column",
        transform: isOpen ? "translateX(0)" : "translateX(100%)",
        transition: "transform 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
      }}
    >
      {/* Header */}
      <div
        style={{
          background: BRAND,
          color: "white",
          padding: "14px 16px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexShrink: 0,
        }}
      >
        <div
          style={{ display: "flex", alignItems: "center", gap: "8px" }}
        >
          <span style={{ fontSize: "18px" }}>✨</span>
          <span style={{ fontWeight: "700", fontSize: "15px" }}>
            AI Copilot
          </span>
        </div>
        <button
          onClick={closePanel}
          aria-label="Cerrar AI Copilot"
          style={{
            background: "rgba(255,255,255,0.2)",
            border: "none",
            color: "white",
            borderRadius: "50%",
            width: "28px",
            height: "28px",
            cursor: "pointer",
            fontSize: "16px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          ×
        </button>
      </div>

      {/* Tabs */}
      <div
        style={{
          display: "flex",
          borderBottom: "1px solid #e2e8f0",
          flexShrink: 0,
          background: "#fafafa",
        }}
      >
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            title={tab.title}
            style={{
              flex: 1,
              padding: "10px 4px",
              border: "none",
              cursor: "pointer",
              background: "transparent",
              fontSize: "12px",
              fontWeight: activeTab === tab.id ? "700" : "400",
              color: activeTab === tab.id ? BRAND : "#64748b",
              borderBottom:
                activeTab === tab.id
                  ? `2px solid ${BRAND}`
                  : "2px solid transparent",
              transition: "all 0.15s",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div
        style={{
          flex: 1,
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {activeTab === "chat" && <ChatTab />}
        {activeTab === "sql" && <SQLTab />}
        {activeTab === "insights" && <InsightsTab />}
      </div>
    </div>
  );
};
