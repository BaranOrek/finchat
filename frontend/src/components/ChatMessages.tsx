import { Box, Flex, Text } from "@chakra-ui/react";

import type { Message } from "../types/chat";
import { EmptyState } from "./EmptyState";
import { LoadingMessage } from "./LoadingMessage";
import { MiniChart } from "./MiniChart";

type Props = {
  messages: Message[];
  loading: boolean;
  chatRef: React.RefObject<HTMLDivElement | null>;
  onSelectPrompt: (prompt: string) => void;
};

export function ChatMessages({
  messages,
  loading,
  chatRef,
  onSelectPrompt,
}: Props) {
  return (
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
      {messages.length === 0 && <EmptyState onSelectPrompt={onSelectPrompt} />}

      {messages.map((message, index) => {
        const isUser = message.role === "user";

        return (
          <Flex
            key={`${message.role}-${index}`}
            justify={isUser ? "flex-end" : "flex-start"}
          >
            <Box
              maxW={{ base: "88%", sm: "80%" }}
              w={
                message.role === "assistant" && message.chart
                  ? "100%"
                  : "fit-content"
              }
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

      {loading && <LoadingMessage />}
    </Flex>
  );
}