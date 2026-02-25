import React, {
  createContext,
  useCallback,
  useContext,
  useState,
} from "react";

import { getAIMiddlewareURL } from "../flags";

export type CopilotTab = "chat" | "sql" | "insights";

export interface ChatMessage {
  role: "user" | "ai";
  text: string;
}

interface AICopilotContextType {
  isOpen: boolean;
  activeTab: CopilotTab;
  messages: ChatMessage[];
  isLoading: boolean;
  generatedSQL: string;
  openPanel: (tab?: CopilotTab, query?: string) => void;
  closePanel: () => void;
  setActiveTab: (tab: CopilotTab) => void;
  sendMessage: (text: string) => Promise<void>;
  generateSQL: (text: string) => Promise<void>;
  clearMessages: () => void;
}

const AICopilotContext = createContext<AICopilotContextType | null>(null);

export const useAICopilot = (): AICopilotContextType => {
  const ctx = useContext(AICopilotContext);
  if (!ctx) {
    throw new Error("useAICopilot must be used within AICopilotProvider");
  }
  return ctx;
};

export const AICopilotProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<CopilotTab>("chat");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [generatedSQL, setGeneratedSQL] = useState("");

  const openPanel = useCallback(
    (tab: CopilotTab = "chat", query?: string) => {
      setIsOpen(true);
      setActiveTab(tab);
      if (query) {
        // Auto-send if a query is passed (e.g. from search bar)
        setMessages(prev => [...prev, { role: "user", text: query }]);
      }
    },
    [],
  );

  const closePanel = useCallback(() => {
    setIsOpen(false);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim()) {
        return;
      }
      const userMsg: ChatMessage = { role: "user", text };
      const updatedMessages = [...messages, userMsg];
      setMessages(updatedMessages);
      setIsLoading(true);

      try {
        const aiUrl = getAIMiddlewareURL();
        const res = await fetch(`${aiUrl}/api/ai/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
        });
        const data = await res.json();
        setMessages([
          ...updatedMessages,
          { role: "ai", text: data.reply ?? "Sin respuesta del asistente." },
        ]);
      } catch {
        setMessages([
          ...updatedMessages,
          {
            role: "ai",
            text: "Error de conexión con el asistente AI.",
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [messages],
  );

  const generateSQL = useCallback(async (text: string) => {
    if (!text.trim()) {
      return;
    }
    setIsLoading(true);
    setGeneratedSQL("");

    try {
      const aiUrl = getAIMiddlewareURL();
      const res = await fetch(`${aiUrl}/api/ai/generate-sql`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ natural_language: text }),
      });
      const data = await res.json();
      setGeneratedSQL(data.sql ?? "-- No SQL generado");
    } catch {
      setGeneratedSQL("-- Error al generar SQL");
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <AICopilotContext.Provider
      value={{
        isOpen,
        activeTab,
        messages,
        isLoading,
        generatedSQL,
        openPanel,
        closePanel,
        setActiveTab,
        sendMessage,
        generateSQL,
        clearMessages,
      }}
    >
      {children}
    </AICopilotContext.Provider>
  );
};
