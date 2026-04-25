import type { ChatThread } from "../types/chat";

export const THREADS_STORAGE_KEY = "finchat_threads";
export const ACTIVE_THREAD_STORAGE_KEY = "finchat_active_thread_id";

export function loadThreads(): ChatThread[] {
  try {
    const raw = localStorage.getItem(THREADS_STORAGE_KEY);

    if (!raw) return [];

    const parsed = JSON.parse(raw);

    if (!Array.isArray(parsed)) return [];

    return parsed.filter(
      (thread) =>
        thread &&
        typeof thread.id === "string" &&
        typeof thread.title === "string" &&
        Array.isArray(thread.messages) &&
        typeof thread.createdAt === "string"
    );
  } catch {
    return [];
  }
}

export function loadActiveThreadId(): string | null {
  try {
    return localStorage.getItem(ACTIVE_THREAD_STORAGE_KEY);
  } catch {
    return null;
  }
}