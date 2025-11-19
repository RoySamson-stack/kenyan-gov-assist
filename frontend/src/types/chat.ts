export type MessageRole = "user" | "assistant";

export type MessageStatus = "default" | "error";

export interface MessageSource {
  source: string;
  page?: string;
  document_type?: string;
  relevance?: string;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  status?: MessageStatus;
  sources?: MessageSource[];
}
