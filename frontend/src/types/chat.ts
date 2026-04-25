export type ChartPoint = {
    time: string;
    price: number;
  };
  
  export type ChartData = {
    label: string;
    points: ChartPoint[];
  };
  
  export type Message = {
    role: "user" | "assistant";
    content: string;
    chart?: ChartData | null;
  };
  
  export type ChatThread = {
    id: string;
    title: string;
    messages: Message[];
    createdAt: string;
  };