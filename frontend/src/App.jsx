import { useState } from "react";
import { FileText, MessageSquareText } from "lucide-react";
import clsx from "clsx";
import { ChatPage } from "./pages/ChatPage";
import { DocumentTranslationPage } from "./pages/DocumentTranslationPage";

const views = [
  { id: "documents", label: "Book Translation", description: "PDF, Word & books", icon: FileText },
  { id: "chat", label: "Text Translation", description: "Text & voice", icon: MessageSquareText },
];

function App() {
  const [activeView, setActiveView] = useState("documents");

  return (
    <div className="flex h-screen flex-col bg-zinc-950 text-white">
      <header className="sticky top-0 z-50 shrink-0 border-b border-white/10 bg-zinc-950/95 px-4 py-3">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-lg font-semibold">Universal Translation Assistant</h1>
            <p className="text-xs text-zinc-400">Translate text, voice, books, PDFs, Word documents, and Excel content.</p>
          </div>
          <nav className="grid w-full grid-cols-2 gap-2 rounded-lg border border-zinc-800 bg-zinc-900 p-1 sm:w-auto">
            {views.map((view) => {
              const Icon = view.icon;
              return (
                <button
                  key={view.id}
                  type="button"
                  onClick={() => setActiveView(view.id)}
                  className={clsx(
                    "flex min-w-0 items-center gap-2 rounded-md px-3 py-2 text-left transition",
                    activeView === view.id
                      ? "bg-white text-zinc-950 shadow-sm"
                      : "text-zinc-300 hover:bg-zinc-800 hover:text-white"
                  )}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-semibold">{view.label}</span>
                    <span className={clsx("block truncate text-xs", activeView === view.id ? "text-zinc-600" : "text-zinc-500")}>
                      {view.description}
                    </span>
                  </span>
                </button>
              );
            })}
          </nav>
        </div>
      </header>
      <main className="min-h-0 flex-1 overflow-hidden">
        {activeView === "documents" ? <DocumentTranslationPage /> : <ChatPage />}
      </main>
    </div>
  );
}

export default App;
