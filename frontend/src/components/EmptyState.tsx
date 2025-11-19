import type { FC } from "react";

const suggestions = [
  "Constitution and laws",
  "Business registration",
  "Land rights",
  "Permits and licenses",
  "Youth programs",
  "Healthcare services",
];

export const EmptyState: FC<{ onSelect: (prompt: string) => void }> = ({ onSelect }) => {
  return (
    <div className="text-center">
      <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.3em] text-white/60">
        <span className="h-2 w-2 rounded-full bg-emerald-400" />
        Live assistant
      </span>
      <h2 className="mt-6 text-2xl font-semibold text-white">How can I help you today?</h2>
      <p className="mt-2 text-base text-white/70">
        Explore popular topics or ask your own question about government services.
      </p>

      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        {suggestions.map((item) => (
          <button
            key={item}
            onClick={() => onSelect(item)}
            className="rounded-3xl border border-white/10 bg-white/5 px-5 py-4 text-left text-sm font-medium text-white/80 transition hover:border-white/30 hover:bg-white/10"
          >
            {item}
          </button>
        ))}
      </div>
    </div>
  );
};
