import type { FC, KeyboardEvent } from "react";
import { Send, Sparkles } from "lucide-react";

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
  placeholder?: string;
}

export const ChatInput: FC<ChatInputProps> = ({
  value,
  onChange,
  onSubmit,
  disabled,
  placeholder = "Ask a question...",
}) => {
  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey && !disabled && value.trim()) {
      event.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="relative flex items-end gap-3 rounded-2xl border border-white/20 bg-white/5 px-4 py-3 shadow-lg backdrop-blur-sm">
      <button
        type="button"
        className="hidden sm:flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg text-white/60 hover:bg-white/10 hover:text-white/80 transition"
      >
        <Sparkles className="h-4 w-4" />
      </button>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        rows={1}
        className="flex-1 resize-none bg-transparent text-[15px] text-white placeholder-white/40 outline-none overflow-hidden"
        style={{
          maxHeight: "200px",
          minHeight: "24px",
        }}
        disabled={disabled}
        onInput={(e) => {
          const target = e.target as HTMLTextAreaElement;
          target.style.height = "auto";
          target.style.height = `${target.scrollHeight}px`;
        }}
      />
      <button
        type="button"
        onClick={onSubmit}
        disabled={disabled || !value.trim()}
        className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-white/10 text-white transition hover:bg-white/20 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <Send className="h-4 w-4" />
      </button>
    </div>
  );
};
