import { Box, Typography, Grid } from "@mui/material";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from "recharts";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";

interface SentimentData {
  sentiment: "positive" | "negative" | "neutral";
  count: number;
}

const COLORS = ["#1976d2", "#dc004e", "#4caf50"];

export function SentimentWidget() {
  const { data, isLoading } = useQuery<SentimentData[]>({
    queryKey: ["sentiment"],
    queryFn: async () => {
      const response = await axios.get("/api/analytics/sentiment");
      return response.data;
    },
  });

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Social Sentiment
      </Typography>
      
      {isLoading ? (
        <Typography>Loading...</Typography>
      ) : (
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  fill="#8884d8"
                  paddingAngle={5}
                  dataKey="count"
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary">
              Data from Facebook, Instagram, and Twitter
            </Typography>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
