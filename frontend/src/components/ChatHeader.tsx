import { Button, Flex, Text } from "@chakra-ui/react";

type Props = {
  onNewChat: () => void;
};

export function ChatHeader({ onNewChat }: Props) {
  return (
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
        onClick={onNewChat}
        w={{ base: "100%", sm: "auto" }}
      >
        New Chat
      </Button>
    </Flex>
  );
}