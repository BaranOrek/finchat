import type { ChatThread } from "../types/chat";

export function createEmptyThread(): ChatThread {
  const id =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : String(Date.now());

  return {
    id,
    title: "New chat",
    messages: [],
    createdAt: new Date().toISOString(),
  };
}

export function buildThreadTitle(firstMessage: string): string {
  const trimmed = firstMessage.trim();

  if (!trimmed) return "New chat";

  return trimmed.length > 30 ? `${trimmed.slice(0, 30)}...` : trimmed;
}