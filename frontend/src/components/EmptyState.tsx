import type { FC } from "react";
import { Sparkles } from "lucide-react";

interface EmptyStateProps {
  onSelect: (prompt: string) => void;
}

const suggestions = [
  "What are my rights as a Kenyan citizen?",
  "How do I apply for a business permit?",
  "What documents do I need for a passport?",
  "How can I access healthcare services?",
];

export const EmptyState: FC<EmptyStateProps> = ({ onSelect }) => {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="mb-8 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-blue-500/20 to-indigo-600/20">
        <Sparkles className="h-8 w-8 text-blue-400" />
      </div>
      <h2 className="mb-2 text-2xl font-semibold text-white">
        How can I help you today?
      </h2>
      <p className="mb-8 text-white/60">
        Ask me anything about Kenyan government services or healthcare
      </p>
      <div className="grid w-full max-w-2xl grid-cols-1 gap-3 sm:grid-cols-2">
        {suggestions.map((suggestion, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onSelect(suggestion)}
            className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-left text-sm text-white/80 transition hover:border-white/20 hover:bg-white/10"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
};
