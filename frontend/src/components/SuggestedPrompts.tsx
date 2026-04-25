import { Button, Flex, Text } from "@chakra-ui/react";

const PROMPTS = [
    "📊 Compare Bitcoin vs Ethereum performance",
    "🏆 Which performed better: BTC or DOGE last 30 days?",
    "📈 Compare top 3 crypto assets this month",
    "💰 What is the current Bitcoin price?",
    "💸 If I invested $1000 in Bitcoin 2 months ago, what now?",
];

type Props = {
    onSelectPrompt: (prompt: string) => void;
};

export function SuggestedPrompts({ onSelectPrompt }: Props) {
    return (
        <Flex direction="column" gap={2} align="center" mt={3}>
            <Text fontSize="xs" color="gray.500">
                Try these examples 👇
            </Text>

            <Flex gap={2} wrap="wrap" justify="center">
                {PROMPTS.map((prompt) => (
                    <Button
                        key={prompt}
                        size="xs"
                        variant="outline"
                        colorPalette="green"
                        onClick={() => onSelectPrompt(prompt)}
                        _hover={{ bg: "green.50" }}
                    >
                        {prompt}
                    </Button>
                ))}
            </Flex>
        </Flex>
    );
}