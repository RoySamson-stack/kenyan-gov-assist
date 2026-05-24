import { useCallback, useState, useRef, useEffect } from "react";
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
  { code: "luo", label: "Dholuo" },
  { code: "kamba", label: "Kikamba" },
  { code: "kalenjin", label: "Kalenjin" },
];

export const ChatPage = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState<string>("english");
  const [targetLanguage, setTargetLanguage] = useState<string>("swahili");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleVoiceTranscript = useCallback((text: string) => {
    setInput(text);
  }, []);

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
        const response = await fetch(`${
          import.meta.env.VITE_API_URL || "http://localhost:8001"
        }/api/translate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: content,
            source_language: language,
            target_language: targetLanguage,
            domain: "general",
          }),
        });

        if (!response.ok) {
          throw new Error("Server error. Please try again.");
        }

        const data = await response.json();
        const assistantMessage: ChatMessage = {
          id: uuid(),
          role: "assistant",
          content: data.data?.translation || data.translation || "Translation failed",
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
    [input, language, targetLanguage, loading]
  );

  const handleSubmit = () => {
    void sendMessage();
  };

  const handleSuggestionSelect = (prompt: string) => {
    setInput(prompt);
  };

  return (
    <div className="flex h-full min-h-0 flex-col bg-slate-950 text-white">
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

      <div className="shrink-0 border-t border-white/10 bg-slate-950/90 backdrop-blur-sm">
        <div className="mx-auto max-w-3xl px-4 py-4">
          <div className="mb-3 grid gap-2 text-xs text-white/60 sm:grid-cols-2">
            <label className="flex items-center gap-2">
              <span className="shrink-0">From</span>
              <select
                value={language}
                onChange={(event) => setLanguage(event.target.value)}
                className="min-w-0 flex-1 rounded-md border border-white/10 bg-white/10 px-2 py-1.5 text-white outline-none"
              >
                {languages.map((item) => (
                  <option key={item.code} value={item.code}>{item.label}</option>
                ))}
              </select>
            </label>
            <label className="flex items-center gap-2">
              <span className="shrink-0">To</span>
              <select
                value={targetLanguage}
                onChange={(event) => setTargetLanguage(event.target.value)}
                className="min-w-0 flex-1 rounded-md border border-white/10 bg-white/10 px-2 py-1.5 text-white outline-none"
              >
                {languages.filter((item) => item.code !== language).map((item) => (
                  <option key={item.code} value={item.code}>{item.label}</option>
                ))}
              </select>
            </label>
          </div>
          <ChatInput
            value={input}
            onChange={setInput}
            onSubmit={handleSubmit}
            onVoiceTranscript={handleVoiceTranscript}
            language={language}
            disabled={loading}
            placeholder="Type or speak text to translate..."
          />
          <p className="mt-2 text-center text-xs text-white/40">
            Text and voice translation available
          </p>
        </div>
      </div>
    </div>
  );
};
