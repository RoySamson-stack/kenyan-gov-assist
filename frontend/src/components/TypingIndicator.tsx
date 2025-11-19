import type { FC } from "react";

export const TypingIndicator: FC = () => {
  return (
    <div className="flex items-center gap-2 rounded-3xl border border-white/10 bg-white/10 px-4 py-3 text-white/80">
      <div className="flex items-center gap-1.5">
        <span className="h-2 w-2 animate-bounce rounded-full bg-white/60" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-white/60 [animation-delay:0.15s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-white/60 [animation-delay:0.3s]" />
      </div>
      <span className="text-xs uppercase tracking-[0.35em] text-white/60">
        typing
      </span>
    </div>
  );
};
