import type { FC } from "react";
import type { ChatMessage } from "../types/chat";
import clsx from "clsx";
import { User, Bot } from "lucide-react";

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble: FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === "user";
  const isError = message.status === "error";

  return (
    <div
      className={clsx(
        "group relative flex gap-4 px-4 py-6",
        isUser ? "bg-slate-950" : "bg-slate-950"
      )}
    >
      {/* Avatar */}
      <div className="flex-shrink-0">
        {isUser ? (
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-indigo-600">
            <User className="h-4 w-4 text-white" />
          </div>
        ) : (
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-teal-600">
            <Bot className="h-4 w-4 text-white" />
          </div>
        )}
      </div>

      {/* Message Content */}
      <div className="flex-1 min-w-0">
        <div className="prose prose-invert max-w-none">
          <div
            className={clsx(
              "text-[15px] leading-7 text-white/90",
              isError && "text-red-400"
            )}
          >
            {message.content.split("\n").map((line, idx) => (
              <p key={idx} className="mb-3 last:mb-0">
                {line || "\u00A0"}
              </p>
            ))}
          </div>

          {/* Sources */}
          {!isUser && message.sources && message.sources.length > 0 && (
            <div className="mt-4 rounded-lg border border-white/10 bg-white/5 p-3">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-white/50">
                Sources
              </p>
              <div className="space-y-2">
                {message.sources.map((source, index) => (
                  <div
                    key={`${source.source}-${index}`}
                    className="text-xs text-white/70"
                  >
                    <span className="font-medium text-white/90">
                      {index + 1}. {source.source}
                    </span>
                    {source.page && (
                      <span className="ml-2 text-white/50">
                        • Page {source.page}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
