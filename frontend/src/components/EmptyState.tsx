import { Box, Text } from "@chakra-ui/react";

import { SuggestedPrompts } from "./SuggestedPrompts";

type Props = {
  onSelectPrompt: (prompt: string) => void;
};

export function EmptyState({ onSelectPrompt }: Props) {
  return (
    <Box textAlign="center" mt={6} px={4}>
      <Text fontSize="md" fontWeight="semibold" color="gray.700">
        Welcome to FinChat
      </Text>

      <Text color="gray.500" fontSize="sm" mt={1}>
        Ask about crypto prices, recent movement, or custom timeframe trends.
      </Text>

      <SuggestedPrompts onSelectPrompt={onSelectPrompt} />
    </Box>
  );
}