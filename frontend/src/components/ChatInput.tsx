import type { FC, KeyboardEvent } from "react";
import { SendHorizontal, Sparkles } from "lucide-react";

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
}

export const ChatInput: FC<ChatInputProps> = ({ value, onChange, onSubmit, disabled }) => {
  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter" && !disabled && value.trim()) {
      event.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="relative flex items-center gap-3 rounded-[24px] border border-white/10 bg-white/10 px-4 py-3 shadow-[0_18px_40px_rgba(15,23,42,0.2)] backdrop-blur-lg">
      <Sparkles className="hidden sm:block h-5 w-5 text-white/60" />
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        type="text"
        placeholder="Ask about Kenyan government services..."
        className="flex-1 bg-transparent text-sm sm:text-base text-white placeholder-white/40 outline-none"
        disabled={disabled}
      />
      <button
        type="button"
        onClick={onSubmit}
        disabled={disabled || !value.trim()}
        className="group h-11 w-11 flex-none rounded-full bg-gradient-to-br from-blue-500 via-blue-600 to-indigo-600 p-[1px] transition-transform duration-200 disabled:opacity-60"
      >
        <span className="flex h-full w-full items-center justify-center rounded-full bg-slate-900/80 text-white transition-all duration-200 group-hover:bg-transparent">
          <SendHorizontal className="h-5 w-5 transition-transform duration-200 group-hover:translate-x-1" />
        </span>
      </button>
    </div>
  );
};
