import { Box, Button, Flex, Input } from "@chakra-ui/react";

type Props = {
    input: string;
    setInput: (value: string) => void;
    onSend: () => Promise<void> | void;
    loading: boolean;
};

export function ChatInput({ input, setInput, onSend, loading }: Props) {
    const handleKeyDown = async (
        event: React.KeyboardEvent<HTMLInputElement>
    ) => {
        if (event.key === "Enter") {
            await onSend();
        }
    };

    return (
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
                    onClick={() => onSend()}
                    loading={loading}
                    loadingText="Sending"
                >
                    Send
                </Button>
            </Flex>
        </Box>
    );
}