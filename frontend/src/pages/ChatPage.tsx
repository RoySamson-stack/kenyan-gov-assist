import { useCallback, useState, useRef, useEffect } from "react";
import clsx from "clsx";
import type { ChatMessage, MessageSource } from "../types/chat";
import { v4 as uuid } from "uuid";
import {
  ChatInput,
  EmptyState,
  MessageList,
  TypingIndicator,
} from "../components";

const languages = [
  { code: "english", label: "English" },
  { code: "swahili", label: "Kiswahili" },
  { code: "kikuyu", label: "Gĩkũyũ" },
];

const domainOptions = [
  {
    id: "civic",
    label: "Serikali Yangu",
    description: "Government & citizen services",
  },
  {
    id: "health",
    label: "AfyaTranslate",
    description: "Clinician ↔ patient support",
  },
] as const;

export const ChatPage = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState<string>("english");
  const [domain, setDomain] = useState<(typeof domainOptions)[number]["id"]>("civic");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const sendMessage = useCallback(
    async (customPrompt?: string) => {
      const content = (customPrompt ?? input).trim();
      if (!content || loading) return;

      const userMessage: ChatMessage = {
        id: uuid(),
        role: "user",
        content,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      if (!customPrompt) {
        setInput("");
      }
      setLoading(true);

      try {
        const response = await fetch("http://localhost:8001/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: content,
            language,
            use_rag: true,
            domain,
          }),
        });

        if (!response.ok) {
          throw new Error("Server error. Please try again.");
        }

        const data = await response.json();
        const assistantMessage: ChatMessage = {
          id: uuid(),
          role: "assistant",
          content: data.response,
          timestamp: new Date().toISOString(),
          sources: (data.sources ?? []) as MessageSource[],
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (error) {
        const assistantMessage: ChatMessage = {
          id: uuid(),
          role: "assistant",
          content:
            error instanceof Error
              ? error.message
              : "Something went wrong. Please try again.",
          timestamp: new Date().toISOString(),
          status: "error",
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } finally {
        setLoading(false);
      }
    },
    [domain, input, language, loading]
  );

  const handleSubmit = () => {
    void sendMessage();
  };

  const handleSuggestionSelect = (prompt: string) => {
    setInput(prompt);
  };

  return (
    <div className="flex h-screen flex-col bg-slate-950 text-white">
      {/* Top Header - Minimal */}
      <div className="border-b border-white/10 bg-slate-950/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <h1 className="text-lg font-semibold">
              {domain === "civic" ? "Serikali Yangu" : "AfyaTranslate AI"}
            </h1>
            <div className="flex gap-2">
              {domainOptions.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setDomain(item.id)}
                  className={clsx(
                    "rounded-lg px-3 py-1.5 text-xs font-medium transition",
                    domain === item.id
                      ? "bg-white/10 text-white"
                      : "text-white/60 hover:text-white/80"
                  )}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
          <div className="flex gap-2">
            {languages.map((item) => (
              <button
                key={item.code}
                type="button"
                onClick={() => setLanguage(item.code)}
                className={clsx(
                  "rounded-lg px-3 py-1.5 text-xs font-medium transition",
                  language === item.code
                    ? "bg-white/10 text-white"
                    : "text-white/60 hover:text-white/80"
                )}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Chat Area - Centered like ChatGPT */}
      <div
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto"
        style={{ scrollbarWidth: "thin" }}
      >
        <div className="mx-auto max-w-3xl px-4 py-8">
          {messages.length === 0 ? (
            <EmptyState onSelect={handleSuggestionSelect} />
          ) : (
            <MessageList messages={messages} />
          )}
          {loading && (
            <div className="mt-6">
              <TypingIndicator />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area - Fixed at bottom */}
      <div className="border-t border-white/10 bg-slate-950/80 backdrop-blur-sm">
        <div className="mx-auto max-w-3xl px-4 py-4">
          <ChatInput
            value={input}
            onChange={setInput}
            onSubmit={handleSubmit}
            disabled={loading}
            placeholder={
              domain === "civic"
                ? "Ask about Kenyan government services..."
                : "Ask about health, symptoms, or medical information..."
            }
          />
          <p className="mt-2 text-center text-xs text-white/40">
            Powered by Ollama • Responses cite official documents when available
          </p>
        </div>
      </div>
    </div>
  );
};
