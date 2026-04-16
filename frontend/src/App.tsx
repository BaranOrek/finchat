import { useEffect, useMemo, useRef, useState } from "react";
import {
  Box,
  Button,
  Flex,
  Input,
  Text,
  Select,
  createListCollection,
} from "@chakra-ui/react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import axios from "axios";

type ChartPoint = {
  time: string;
  price: number;
};

type ChartData = {
  label: string;
  points: ChartPoint[];
};

type Message = {
  role: "user" | "assistant";
  content: string;
  chart?: ChartData | null;
};

type ChatThread = {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const THREADS_STORAGE_KEY = "finchat_threads";
const ACTIVE_THREAD_STORAGE_KEY = "finchat_active_thread_id";

if (!API_BASE_URL) {
  throw new Error("VITE_API_BASE_URL is not defined");
}

function loadThreads(): ChatThread[] {
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

function loadActiveThreadId(): string | null {
  try {
    return localStorage.getItem(ACTIVE_THREAD_STORAGE_KEY);
  } catch {
    return null;
  }
}

function createEmptyThread(): ChatThread {
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

function buildThreadTitle(firstMessage: string): string {
  const trimmed = firstMessage.trim();
  if (!trimmed) return "New chat";
  return trimmed.length > 30 ? `${trimmed.slice(0, 30)}...` : trimmed;
}

// function MiniChart({ chart }: { chart: ChartData }) {
//   const formattedData = chart.points.map((point) => ({
//     time: point.time,
//     price: point.price,
//   }));

//   return (
//     <Box mt={3} w="full" maxW="100%" h={{ base: "140px", sm: "180px" }} minW={0} overflow="hidden">
//       <Text
//         fontSize="xs"
//         color="gray.500"
//         mb={2}
//         wordBreak="break-word"
//       >
//         {chart.label}
//       </Text>
//       <ResponsiveContainer width="100%" height="100%">
//         <LineChart data={formattedData}>
//           <XAxis dataKey="time" hide />
//           <YAxis hide domain={["auto", "auto"]} />
//           <Tooltip />
//           <Line
//             type="monotone"
//             dataKey="price"
//             stroke="currentColor"
//             dot={false}
//             strokeWidth={2}
//           />
//         </LineChart>
//       </ResponsiveContainer>
//     </Box>
//   );
// }

function MiniChart({ chart }: { chart: ChartData }) {
  const formattedData = chart.points.map((point) => ({
    time: point.time,
    price: point.price,
  }));

  return (
    <Box mt={3} w="full" maxW="100%" h={{ base: "140px", sm: "180px" }} minW={0} overflow="hidden">
      <Text fontSize="xs" color="gray.500" mb={2} wordBreak="break-word">
        {chart.label}
      </Text>

      <Box w="100%" h="calc(100% - 24px)" minW={0}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={formattedData}>
            <XAxis dataKey="time" hide />
            <YAxis hide domain={["auto", "auto"]} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="price"
              stroke="currentColor"
              dot={false}
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
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

  const threadOptions = createListCollection({
    items: threads.map((thread) => ({
      label: thread.title,
      value: thread.id,
    })),
  });

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

  const sendMessage = async () => {
    if (!input.trim() || loading || !activeThread) return;

    const userMessage: Message = {
      role: "user",
      content: input.trim(),
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
    } catch (error) {
      console.error("Chat request failed:", error);

      const assistantMessage: Message = {
        role: "assistant",
        content: "Something went wrong while contacting the server.",
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

  const handleKeyDown = async (
    event: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (event.key === "Enter") {
      await sendMessage();
    }
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
      <Flex
        bg="green.500"
        color="white"
        px={4}
        py={3}
        align={{ base: "stretch", sm: "center" }}
        justify="space-between"
        direction={{ base: "column", sm: "row" }}
        gap={2}
      >
        <Text fontWeight="bold" fontSize="lg">
          FinChat
        </Text>

        <Button
          size="sm"
          variant="solid"
          colorPalette="green"
          onClick={handleNewChat}
          w={{ base: "100%", sm: "auto" }}
        >
          New Chat
        </Button>
      </Flex>

      <Box
        bg="white"
        px={3}
        py={2}
        borderBottom="1px solid"
        borderColor="gray.200"
        flexShrink={0}
      >
        <Text fontSize="xs" color="gray.500" mb={2}>
          Previous chats
        </Text>

        <Select.Root
          collection={threadOptions}
          value={activeThreadId ? [activeThreadId] : []}
          onValueChange={(details) => {
            const nextValue = details.value[0];
            if (nextValue) {
              setActiveThreadId(nextValue);
            }
          }}
          size="sm"
        >
          <Select.HiddenSelect />
          <Select.Control>
            <Select.Trigger>
              <Select.ValueText placeholder="Select a chat" />
            </Select.Trigger>
            <Select.IndicatorGroup>
              <Select.Indicator />
            </Select.IndicatorGroup>
          </Select.Control>
          <Select.Positioner>
            <Select.Content>
              {threadOptions.items.map((item) => (
                <Select.Item item={item} key={item.value}>
                  {item.label}
                  <Select.ItemIndicator />
                </Select.Item>
              ))}
            </Select.Content>
          </Select.Positioner>
        </Select.Root>
      </Box>

      <Flex
        ref={chatRef}
        direction="column"
        flex="1"
        minH={0}
        overflowY="auto"
        px={3}
        py={4}
        gap={3}
      >
        {messages.length === 0 && (
          <Text color="gray.500" fontSize="sm" textAlign="center" mt={4}>
            Ask about Bitcoin, Ethereum, or market prices.
          </Text>
        )}

        {messages.map((message, index) => {
          const isUser = message.role === "user";

          return (
            <Flex key={index} justify={isUser ? "flex-end" : "flex-start"}>
              <Box
                maxW={{ base: "88%", sm: "80%" }}
                w={message.role === "assistant" && message.chart ? "100%" : "fit-content"}
                minW="0"
                px={4}
                py={3}
                borderRadius="2xl"
                bg={isUser ? "green.100" : "white"}
                boxShadow="sm"
                overflow="hidden"
              >
                <Text fontSize="sm" whiteSpace="pre-wrap" wordBreak="break-word">
                  {message.content}
                </Text>
                {message.role === "assistant" && message.chart ? (
                  <MiniChart chart={message.chart} />
                ) : null}
              </Box>
            </Flex>
          );
        })}

        {loading && (
          <Flex justify="flex-start">
            <Box px={4} py={3} borderRadius="2xl" bg="white" boxShadow="sm">
              <Text fontSize="sm" color="gray.500">
                Thinking...
              </Text>
            </Box>
          </Flex>
        )}
      </Flex>

      <Box
        bg="white"
        borderTop="1px solid"
        borderColor="gray.200"
        p={3}
        flexShrink={0}
      >
        <Flex gap={2} align="stretch">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="What is the current Bitcoin price?"
            bg="white"
            disabled={loading}
          />
          <Button
            colorPalette="green"
            onClick={sendMessage}
            loading={loading}
            loadingText="Sending"
          >
            Send
          </Button>
        </Flex>
      </Box>
    </Flex>
  );
}