import { Box, Flex, Text } from "@chakra-ui/react";

export function LoadingMessage() {
  return (
    <Flex justify="flex-start">
      <Box px={4} py={3} borderRadius="2xl" bg="white" boxShadow="sm">
        <Text fontSize="sm" color="gray.500">
          Thinking...
        </Text>
      </Box>
    </Flex>
  );
}