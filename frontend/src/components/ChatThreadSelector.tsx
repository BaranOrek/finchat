import { Box, Text, Select, createListCollection } from "@chakra-ui/react";

type Props = {
  threads: { id: string; title: string }[];
  activeThreadId: string | null;
  onChange: (id: string) => void;
};

export function ChatThreadSelector({
  threads,
  activeThreadId,
  onChange,
}: Props) {
  const threadOptions = createListCollection({
    items: threads.map((thread) => ({
      label: thread.title,
      value: thread.id,
    })),
  });

  return (
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
            onChange(nextValue);
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
  );
}