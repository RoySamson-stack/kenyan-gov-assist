"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { v4 as uuid } from "uuid";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  sources?: string[];
  isError?: boolean;
}

interface Topic {
  icon: string;
  label: string;
}

interface Suggestion {
  icon: string;
  title: string;
  text: string;
}

const topics: Record<string, Topic[]> = {
  serikali: [
    { icon: "🏢", label: "Business Registration" },
    { icon: "🏡", label: "Land & Property" },
    { icon: "💰", label: "KRA & Taxation" },
    { icon: "📜", label: "Constitution & Rights" },
    { icon: "🪪", label: "ID & Documents" },
    { icon: "🎓", label: "Education & HELB" },
  ],
  afya: [
    { icon: "💊", label: "Medication Terms" },
    { icon: "🩺", label: "Diagnosis Translation" },
    { icon: "🏥", label: "Hospital Procedures" },
    { icon: "🤱", label: "Maternal Health" },
    { icon: "🧪", label: "Lab Results" },
    { icon: "📋", label: "Consent Forms" },
  ],
};

const suggestions: Record<string, Suggestion[]> = {
  serikali: [
    { icon: "🏢", title: "Register a business", text: "Steps to register an SME with the Registrar of Companies" },
    { icon: "🏡", title: "Land title transfer", text: "Documents needed for property ownership transfer" },
    { icon: "💰", title: "File KRA returns", text: "How to file my income tax returns on iTax" },
    { icon: "📜", title: "My rights under Article 43", text: "Economic and social rights guaranteed by the Constitution" },
  ],
  afya: [
    { icon: "💊", title: "Translate prescription", text: "Explain medication dosage instructions in Swahili" },
    { icon: "🩺", title: "Diagnosis terms", text: "What does 'hypertension' mean in Kiswahili?" },
    { icon: "🤱", title: "Antenatal care", text: "Explain ANC visit schedule to a patient in Swahili" },
    { icon: "📋", title: "Consent translation", text: "Translate surgical consent form into Kiswahili" },
  ],
};

const modeConfig = {
  serikali: {
    icon: "🏛️",
    title: "Serikali Yangu — Civic Assistant",
    subtitle: "Business registration · Land titles · Tax · Constitution · Government services",
    badge: "📚 RAG · Local Model",
    welcomeEmoji: "🏛️",
    welcomeTitle: "Habari! How can I help you today?",
    welcomeSub: "Ask me anything about Kenyan government services, laws, and policies. You can also drop a PDF for document-specific answers.",
    placeholder: "Ask about government services, laws, policies…",
  },
  afya: {
    icon: "🏥",
    title: "AfyaTranslate — Healthcare Translation",
    subtitle: "English ↔ Kiswahili · Medical terminology · Clinician-patient communication",
    badge: "🔄 Translation Memory",
    welcomeEmoji: "🏥",
    welcomeTitle: "Karibu! Ready to translate medical conversations",
    welcomeSub: "Translate between English and Kiswahili for clinical consultations. Includes medical term glossary and consent forms.",
    placeholder: "Type a medical term or phrase to translate…",
  },
};

const historyItems = [
  { title: "How do I register a business in Kenya?", date: "Today, 10:32 AM" },
  { title: "Land title transfer requirements", date: "Yesterday" },
  { title: "KRA PIN registration process", date: "Mon, Mar 16" },
  { title: "AfyaTranslate: Diabetes patient", date: "Sun, Mar 15" },
  { title: "Constitutional rights — Article 43", date: "Fri, Mar 13" },
];

export default function Home() {
  const [mode, setMode] = useState<"serikali" | "afya">("serikali");
  const [lang, setLang] = useState<"en" | "sw">("en");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [chatStarted, setChatStarted] = useState(false);
  const [translation, setTranslation] = useState<{ en: string; sw: string } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const autoResize = () => {
    const textarea = inputRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
    }
  };

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || isTyping) return;

    const userMessage: Message = {
      id: uuid(),
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setChatStarted(true);
    setIsTyping(true);

    if (inputRef.current) {
      inputRef.current.style.height = "auto";
    }

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "";
      const endpoint = baseUrl ? `${baseUrl}/api/chat` : "/api/chat";

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          language: lang === "en" ? "english" : "swahili",
          use_rag: true,
          domain: mode === "afya" ? "health" : "civic",
        }),
      });

      if (!response.ok) {
        throw new Error("Server error");
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: uuid(),
        role: "assistant",
        content: data.response,
        timestamp: new Date().toISOString(),
        sources: data.sources?.map((s: { source: string }) => s.source) || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (mode === "afya") {
        setTranslation({
          en: text,
          sw: data.response,
        });
      }
    } catch {
      const errorMessage: Message = {
        id: uuid(),
        role: "assistant",
        content: "Something went wrong. Please try again.",
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [input, isTyping, lang, mode]);

  const handleSuggestion = (title: string) => {
    setInput(title);
    inputRef.current?.focus();
  };

  const handleTopicClick = (label: string) => {
    setInput(label + " — ");
    inputRef.current?.focus();
  };

  const newChat = () => {
    setMessages([]);
    setChatStarted(false);
    setUploadedFile(null);
    setTranslation(null);
  };

  const simulateUpload = () => {
    const names = ["Land_Registration_Act_2012.pdf", "Companies_Act_2015.pdf", "Kenya_Constitution_2010.pdf", "KRA_Income_Tax_Guide.pdf"];
    const name = names[Math.floor(Math.random() * names.length)];
    setUploadedFile(name);
  };

  const config = modeConfig[mode];

  return (
    <div id="app" className={mode === "afya" ? "mode-afya" : ""}>
      {/* TOPBAR */}
      <div className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="18" cy="18" r="17" fill="rgba(255,255,255,0.1)" stroke="rgba(255,255,255,0.2)" strokeWidth="1"/>
              <path d="M18 6 L22 14 L30 14 L24 20 L26 28 L18 23 L10 28 L12 20 L6 14 L14 14 Z" fill="none" stroke="#d4a843" strokeWidth="1.5" strokeLinejoin="round"/>
              <circle cx="18" cy="18" r="4" fill="#d4a843" opacity="0.8"/>
            </svg>
          </div>
          <div className="brand-text">
            <div className="brand-name">Serikali Yangu</div>
            <div className="brand-sub">Kenya Gov Assistant</div>
          </div>
        </div>

        <div className="mode-toggle">
          <button
            className={`mode-btn ${mode === "serikali" ? "active" : ""}`}
            onClick={() => setMode("serikali")}
          >
            🏛️ Serikali Yangu
          </button>
          <button
            className={`mode-btn ${mode === "afya" ? "active" : ""}`}
            onClick={() => setMode("afya")}
          >
            🏥 AfyaTranslate
          </button>
        </div>

        <div className="topbar-actions">
          <div className="lang-toggle">
            <button
              className={`lang-btn ${lang === "en" ? "active" : ""}`}
              onClick={() => setLang("en")}
            >
              EN
            </button>
            <button
              className={`lang-btn ${lang === "sw" ? "active" : ""}`}
              onClick={() => setLang("sw")}
            >
              SW
            </button>
          </div>
          <button className="icon-btn" title="Settings">⚙️</button>
          <button className="icon-btn" title="Profile">👤</button>
        </div>
      </div>

      {/* KENYA FLAG STRIPE */}
      <div className="flag-stripe"></div>

      {/* LAYOUT */}
      <div className="layout">
        {/* SIDEBAR */}
        <div className="sidebar">
          <div className="sidebar-section">
            <button className="new-chat-btn" onClick={newChat}>
              ✏️ New Conversation
            </button>

            <div className="sidebar-label">Quick Topics</div>
            <div className="quick-topics">
              {topics[mode].map((topic, i) => (
                <div
                  key={topic.label}
                  className={`topic-chip ${i === 0 ? "active" : ""}`}
                  onClick={() => handleTopicClick(topic.label)}
                >
                  <span className="topic-icon">{topic.icon}</span>
                  {topic.label}
                </div>
              ))}
            </div>
          </div>

          <div className="sidebar-divider"></div>

          {/* PDF UPLOAD */}
          {!uploadedFile ? (
            <div className="upload-zone" onClick={simulateUpload}>
              <div className="upload-icon">📄</div>
              <div className="upload-text">
                <strong>Drop a Government PDF</strong>
                <br />
                Laws, policies, circulars, forms
              </div>
            </div>
          ) : (
            <div className="uploaded-doc">
              <span>📄</span>
              <span className="doc-name">{uploadedFile}</span>
              <span style={{ color: "#2d8b47", fontSize: 11 }}>✓</span>
            </div>
          )}

          <div className="sidebar-divider"></div>

          <div className="sidebar-section" style={{ paddingBottom: 0 }}>
            <div className="sidebar-label">Recent Chats</div>
          </div>

          <div className="history-list">
            {historyItems.map((item) => (
              <div key={item.title} className="history-item">
                <div className="history-title">{item.title}</div>
                <div className="history-date">{item.date}</div>
              </div>
            ))}
          </div>
        </div>

        {/* CHAT AREA */}
        <div className="chat-area">
          {/* MODE BANNER */}
          <div className="mode-banner">
            <div className="mode-banner-icon">{config.icon}</div>
            <div className="mode-banner-text">
              <div className="mode-banner-title">{config.title}</div>
              <div className="mode-banner-sub">{config.subtitle}</div>
            </div>
            <div className="source-badge">{config.badge}</div>
          </div>

          {/* MESSAGES */}
          <div className="messages">
            {!chatStarted ? (
              <div className="welcome">
                <div className="welcome-emblem">{config.welcomeEmoji}</div>
                <div>
                  <div className="welcome-title">{config.welcomeTitle}</div>
                  <div className="welcome-sub">{config.welcomeSub}</div>
                </div>
                <div className="welcome-suggestions">
                  {suggestions[mode].map((s) => (
                    <div
                      key={s.title}
                      className="suggestion-card"
                      onClick={() => handleSuggestion(s.title)}
                    >
                      <div className="suggestion-icon">{s.icon}</div>
                      <div className="suggestion-text">
                        <strong>{s.title}</strong>
                        {s.text}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg) => (
                  <div key={msg.id} className={`message ${msg.role}`}>
                    <div className="msg-avatar ai">🇰🇪</div>
                    <div className="msg-body">
                      <div
                        className="msg-bubble"
                        style={{ whiteSpace: "pre-wrap" }}
                      >
                        {msg.content.split("**").map((part, i) =>
                          i % 2 === 1 ? <strong key={i}>{part}</strong> : part
                        )}
                      </div>
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="citations">
                          {msg.sources.map((source, i) => (
                            <div key={i} className="citation">
                              📄 {source}
                            </div>
                          ))}
                        </div>
                      )}
                      <div className="msg-meta">
                        <span>
                          Llama 3.2 · ChromaDB
                          {uploadedFile && ` · from ${uploadedFile}`}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="message ai">
                    <div className="msg-avatar ai">🇰🇪</div>
                    <div className="msg-body">
                      <div className="typing-indicator">
                        <div className="typing-dot"></div>
                        <div className="typing-dot"></div>
                        <div className="typing-dot"></div>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* INPUT AREA */}
          <div className="input-area">
            <div className="input-wrapper">
              <div className="input-top">
                <textarea
                  ref={inputRef}
                  className="chat-input"
                  placeholder={config.placeholder}
                  value={input}
                  onChange={(e) => {
                    setInput(e.target.value);
                    autoResize();
                  }}
                  onKeyDown={handleKeyDown}
                  rows={1}
                />
                <button
                  className="send-btn"
                  onClick={handleSend}
                  disabled={!input.trim() || isTyping}
                >
                  ➤
                </button>
              </div>
              <div className="input-bottom">
                <div className="input-action" onClick={simulateUpload}>
                  📎 Attach PDF
                </div>
                <div className="input-action">🎙️ Voice</div>
                <div className="input-hint">
                  Powered by Llama 3.2 · ChromaDB RAG
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* AFYA TRANSLATION PANEL */}
        {mode === "afya" && (
          <div className={`translation-panel ${mode === "afya" ? "visible" : ""}`}>
            <div className="trans-header">
              <div className="trans-title">Live Translation</div>
              <div className="trans-sub">English ↔ Kiswahili · Medical Terms</div>
            </div>
            {translation ? (
              <>
                <div className="trans-item">
                  <div className="trans-lang">English</div>
                  <div className="trans-text">{translation.en}</div>
                </div>
                <div className="trans-item">
                  <div className="trans-lang">Kiswahili</div>
                  <div className="trans-text">{translation.sw}</div>
                  <div className="trans-medical-badge">⚕️ Medical Term Verified</div>
                </div>
              </>
            ) : (
              <div style={{ padding: "24px 18px", textAlign: "center", color: "var(--text-light)", fontSize: 13, lineHeight: 1.6 }}>
                Start a conversation.
                <br />
                Translations will appear here.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
