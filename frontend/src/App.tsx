import { useEffect, useMemo, useRef, useState } from "react";
import {
  Flex,
} from "@chakra-ui/react";
import type { ChatThread, Message } from "./types/chat";
import { ChatInput, ChatMessages, ChatHeader, ChatThreadSelector } from "./components";
import {
  ACTIVE_THREAD_STORAGE_KEY,
  THREADS_STORAGE_KEY,
  loadActiveThreadId,
  loadThreads,
} from "./utils/threadStorage";
import {
  buildThreadTitle,
  createEmptyThread,
} from "./utils/threadHelpers";
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error("VITE_API_BASE_URL is not defined");
}

export default function App() {
  const [threads, setThreads] = useState<ChatThread[]>(() => {
    const stored = loadThreads();
    return stored.length > 0 ? stored : [createEmptyThread()];
  });

  const [activeThreadId, setActiveThreadId] = useState<string | null>(() => {
    const storedId = loadActiveThreadId();
    const storedThreads = loadThreads();

    if (storedId && storedThreads.some((thread) => thread.id === storedId)) {
      return storedId;
    }

    if (storedThreads.length > 0) {
      return storedThreads[0].id;
    }

    return null;
  });

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    localStorage.setItem(THREADS_STORAGE_KEY, JSON.stringify(threads));
  }, [threads]);

  useEffect(() => {
    if (activeThreadId) {
      localStorage.setItem(ACTIVE_THREAD_STORAGE_KEY, activeThreadId);
    }
  }, [activeThreadId]);

  useEffect(() => {
    if (!activeThreadId && threads.length > 0) {
      setActiveThreadId(threads[0].id);
    }
  }, [threads, activeThreadId]);

  const activeThread = useMemo(() => {
    return threads.find((thread) => thread.id === activeThreadId) ?? null;
  }, [threads, activeThreadId]);

  const messages = activeThread?.messages ?? [];

  const scrollToBottom = () => {
    setTimeout(() => {
      if (chatRef.current) {
        chatRef.current.scrollTop = chatRef.current.scrollHeight;
      }
    }, 50);
  };

  const handleNewChat = () => {
    const newThread = createEmptyThread();
    setThreads((prev) => [newThread, ...prev]);
    setActiveThreadId(newThread.id);
    setInput("");
  };

  const sendMessage = async (overrideInput?: string) => {
    const messageContent = overrideInput?.trim() || input.trim();

    if (!messageContent || loading || !activeThread) return;

    const userMessage: Message = {
      role: "user",
      content: messageContent,
    };

    const updatedMessages = [...activeThread.messages, userMessage];

    setThreads((prev) =>
      prev.map((thread) =>
        thread.id === activeThread.id
          ? {
            ...thread,
            title:
              thread.messages.length === 0
                ? buildThreadTitle(userMessage.content)
                : thread.title,
            messages: updatedMessages,
          }
          : thread
      )
    );

    setInput("");
    setLoading(true);
    scrollToBottom();

    try {
      const response = await axios.post(`${API_BASE_URL}/chat/`, {
        messages: updatedMessages,
      });

      const assistantMessage: Message = {
        role: "assistant",
        content: response.data.reply,
        chart: response.data.chart ?? null,
      };

      setThreads((prev) =>
        prev.map((thread) =>
          thread.id === activeThread.id
            ? {
              ...thread,
              messages: [...updatedMessages, assistantMessage],
            }
            : thread
        )
      );
    } catch (error: any) {
      console.error("Chat request failed:", error);

      let errorMessage = "Something went wrong. Please try again.";

      if (error?.response?.data?.error?.message) {
        errorMessage = error.response.data.error.message;
      }

      const assistantMessage: Message = {
        role: "assistant",
        content: errorMessage,
      };

      setThreads((prev) =>
        prev.map((thread) =>
          thread.id === activeThread.id
            ? {
              ...thread,
              messages: [...updatedMessages, assistantMessage],
            }
            : thread
        )
      );
    } finally {
      setLoading(false);
      scrollToBottom();
    }
  };

  const handleSelectPrompt = async (prompt: string) => {
    setInput(prompt);
    await sendMessage(prompt);
  };


  return (
    <Flex
      direction="column"
      h="100vh"
      w="100%"
      maxW="480px"
      mx="auto"
      bg="gray.100"
      overflow="hidden"
      borderLeft={{ base: "none", md: "1px solid" }}
      borderRight={{ base: "none", md: "1px solid" }}
      borderColor="gray.200"
    >
      <ChatHeader onNewChat={handleNewChat} />

      <ChatThreadSelector
        threads={threads}
        activeThreadId={activeThreadId}
        onChange={setActiveThreadId}
      />

      <ChatMessages
        messages={messages}
        loading={loading}
        chatRef={chatRef}
        onSelectPrompt={handleSelectPrompt}
      />

      <ChatInput
        input={input}
        setInput={setInput}
        onSend={() => sendMessage()}
        loading={loading}
      />
    </Flex>
  );
}