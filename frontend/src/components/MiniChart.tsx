import { Box, Text } from "@chakra-ui/react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

type ChartPoint = {
  time: string;
  price: number;
};

type ChartSeries = {
  label: string;
  points: ChartPoint[];
};

type ChartData = {
  label: string;
  points?: ChartPoint[];
  series?: ChartSeries[];
  is_normalized?: boolean;
};

export function MiniChart({ chart }: { chart: ChartData }) {
  const isMultiSeries = chart.series && chart.series.length > 0;

  let data: any[] = [];

  if (isMultiSeries) {
    const timeMap = new Map<string, Record<string, string | number>>();
  
    chart.series!.forEach((series) => {
      series.points.forEach((point) => {
        if (!timeMap.has(point.time)) {
          timeMap.set(point.time, { time: point.time });
        }
  
        timeMap.get(point.time)![series.label] = point.price;
      });
    });
  
    data = Array.from(timeMap.values()).sort(
      (a, b) => Number(a.time) - Number(b.time)
    );
  } else {
    data = (chart.points || []).map((p) => ({
      time: p.time,
      price: p.price,
    }));
  }

  const colors = ["#38A169", "#3182CE", "#DD6B20", "#805AD5", "#D53F8C"];

  return (
    <Box mt={3} w="full" h={{ base: "230px", sm: "260px" }} minW={0}>
      <Text fontSize="xs" color="gray.500" mb={1} textAlign="center">
        {chart.label}
      </Text>
  
      {chart.is_normalized && (
        <Text fontSize="xs" color="gray.400" mb={2} textAlign="center">
          Indexed to 100 (performance comparison)
        </Text>
      )}
  
      <Box w="100%" h={chart.is_normalized ? "170px" : "180px"} minW={0}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis dataKey="time" hide />
            <YAxis hide domain={["auto", "auto"]} />
            <Tooltip />
            {isMultiSeries && <Legend />}
  
            {isMultiSeries
              ? chart.series!.map((series, index) => (
                  <Line
                    key={series.label}
                    type="monotone"
                    dataKey={series.label}
                    stroke={colors[index % colors.length]}
                    dot={false}
                    strokeWidth={2}
                    connectNulls
                  />
                ))
              : (
                  <Line
                    type="monotone"
                    dataKey="price"
                    stroke="#38A169"
                    dot={false}
                    strokeWidth={2}
                    connectNulls
                  />
                )}
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
}