import type { FC } from "react";
import type { ChatMessage } from "../types/chat";
import clsx from "clsx";

interface MessageBubbleProps {
  message: ChatMessage;
}

const avatarMap: Record<ChatMessage["role"], string> = {
  user: "https://api.dicebear.com/8.x/initials/svg?seed=User",
  assistant: "https://api.dicebear.com/8.x/shapes/svg?seed=Assistant",
};

export const MessageBubble: FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === "user";
  const isError = message.status === "error";

  const bubbleClasses = clsx(
    "relative max-w-[75%] rounded-3xl px-5 py-4 text-sm sm:text-base shadow-[0_18px_40px_rgba(15,23,42,0.25)] transition-transform",
    {
      "origin-bottom-right rounded-br-md bg-gradient-to-br from-blue-500 via-blue-600 to-indigo-600 text-white":
        isUser,
      "origin-bottom-left rounded-bl-md border border-white/10 bg-white/10 text-white":
        !isUser && !isError,
      "origin-bottom-left rounded-bl-md border border-red-200/40 bg-red-500/10 text-red-50":
        isError,
    }
  );

  return (
    <div className={clsx("flex w-full gap-3", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <img
          src={avatarMap[message.role]}
          alt="Assistant avatar"
          className="h-10 w-10 flex-none rounded-2xl border border-white/10 bg-white/10 object-cover"
        />
      )}
      <div className={bubbleClasses}>
        <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-4 rounded-2xl border border-white/10 bg-black/10 px-4 py-3 text-[12px] text-white/70">
            <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.3em] text-white/50">
              Sources
            </p>
            <ul className="space-y-1">
              {message.sources.map((source, index) => (
                <li key={`${source.source}-${index}`} className="flex flex-col">
                  <span className="font-medium text-white/80">
                    {index + 1}. {source.source}
                  </span>
                  <span className="text-white/60">
                    {source.document_type ? `${source.document_type} • ` : ""}
                    {source.page ? `Page ${source.page}` : "Page ?"}
                    {source.relevance ? ` • Relevance ${source.relevance}` : ""}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <span
          className={clsx(
            "mt-3 block text-[11px]",
            isError ? "text-red-100/70" : "text-white/60"
          )}
        >
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
      {isUser && (
        <img
          src={avatarMap[message.role]}
          alt="User avatar"
          className="h-10 w-10 flex-none rounded-2xl border border-white/10 bg-white/10 object-cover"
        />
      )}
    </div>
  );
};
