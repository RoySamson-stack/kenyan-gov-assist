import { useCallback, useMemo, useState } from "react";
import clsx from "clsx";
import type { ChatMessage, MessageSource } from "../types/chat";
import { v4 as uuid } from "uuid";
import {
  ChatInput,
  EmptyState,
  Header,
  MessageList,
  TypingIndicator,
} from "../components";
import { theme } from "../styles/theme";

const languages = [
  { code: "english", label: "English" },
  { code: "swahili", label: "Kiswahili" },
];

const documentFilters = [
  { id: "all", label: "All documents" },
  { id: "constitution", label: "Constitution" },
  { id: "business", label: "Business" },
  { id: "permits", label: "Permits & licenses" },
  { id: "land", label: "Land & housing" },
];

export const ChatPage = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState<string>("english");
  const [documentFilter, setDocumentFilter] = useState<string>("all");

  const activeDocumentType = useMemo(
    () => (documentFilter === "all" ? undefined : documentFilter),
    [documentFilter]
  );

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
        const response = await fetch("http://localhost:8000/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: content,
            language,
            use_rag: true,
            document_type: activeDocumentType,
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
    [activeDocumentType, input, language, loading]
  );

  const handleSubmit = () => {
    void sendMessage();
  };

  const handleSuggestionSelect = (prompt: string) => {
    setInput(prompt);
  };

  return (
    <div
      className="relative min-h-screen overflow-hidden bg-slate-950 text-white"
      style={{ backgroundImage: theme.colors.background }}
    >
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-[20%] top-[15%] h-[420px] w-[420px] rounded-full bg-blue-500/40 blur-[160px]" />
        <div className="absolute bottom-[10%] right-[12%] h-[360px] w-[360px] rounded-full bg-sky-400/30 blur-[140px]" />
        <div className="absolute left-[25%] top-[40%] h-[300px] w-[300px] rounded-full bg-indigo-500/35 blur-[160px]" />
      </div>

      <div className="relative z-10 mx-auto flex min-h-screen max-w-5xl flex-col gap-8 px-4 py-10 sm:px-6 lg:px-10">
        <Header
          title="Serikali Yangu"
          subtitle="Get instant guidance on Kenyan government services, rights, and resources"
        />

        <section className="rounded-[28px] border border-white/10 bg-white/5 p-5 text-white shadow-[0_24px_80px_rgba(12,10,29,0.65)] backdrop-blur-2xl">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-white/60">Language</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {languages.map((item) => (
                  <button
                    key={item.code}
                    type="button"
                    onClick={() => setLanguage(item.code)}
                    className={clsx(
                      "rounded-full border px-4 py-2 text-sm font-medium transition",
                      language === item.code
                        ? "border-white/50 bg-white/20 text-white"
                        : "border-white/10 text-white/70 hover:border-white/40"
                    )}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-white/60">Document focus</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {documentFilters.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setDocumentFilter(item.id)}
                    className={clsx(
                      "rounded-full border px-4 py-2 text-sm font-medium transition",
                      documentFilter === item.id
                        ? "border-emerald-300/80 bg-emerald-400/20 text-white"
                        : "border-white/10 text-white/70 hover:border-white/40"
                    )}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="flex-1 overflow-hidden rounded-[32px] border border-white/10 bg-slate-950/40 p-6 shadow-[0_30px_80px_rgba(15,23,42,0.45)] backdrop-blur-2xl">
          <div className="flex h-full flex-col gap-6">
            <div className="flex-1 overflow-y-auto pr-3">
              {messages.length ? (
                <MessageList messages={messages} />
              ) : (
                <EmptyState onSelect={handleSuggestionSelect} />
              )}
              {loading && (
                <div className="mt-6">
                  <TypingIndicator />
                </div>
              )}
            </div>
            <ChatInput value={input} onChange={setInput} onSubmit={handleSubmit} disabled={loading} />
            <div className="flex flex-col gap-2 text-center text-[12px] text-white/50">
              <p>Responses cite official Kenyan documents when available.</p>
              <p>Always verify important information through official portals.</p>
            </div>
          </div>
        </section>
        <div className="rounded-3xl border border-white/10 bg-white/5 px-6 py-4 text-center text-sm text-white/70">
          Powered by Ollama • Backed by Kenyan government PDFs • Last sync via ingestion script
        </div>
      </div>
    </div>
  );
};
