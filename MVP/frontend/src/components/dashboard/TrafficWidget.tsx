import { Box, Typography, Grid } from "@mui/material";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";

interface TrafficData {
  date: string;
  visits: number;
  bounceRate: number;
}

export function TrafficWidget() {
  const { data, isLoading } = useQuery<TrafficData[]>({
    queryKey: ["traffic"],
    queryFn: async () => {
      const response = await axios.get("/api/analytics/traffic");
      return response.data;
    },
  });

  const formatData = (data: TrafficData[] | undefined) => {
    if (!data) return [];
    return data.map((item) => ({
      ...item,
      date: new Date(item.date).toLocaleDateString(),
    }));
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Traffic Overview
      </Typography>
      
      {isLoading ? (
        <Typography>Loading...</Typography>
      ) : (
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={formatData(data)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="visits"
                  stroke="#1976d2"
                  name="Visits"
                />
                <Line
                  type="monotone"
                  dataKey="bounceRate"
                  stroke="#dc004e"
                  name="Bounce Rate"
                />
              </LineChart>
            </ResponsiveContainer>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary">
              Data from SimilarWeb API
            </Typography>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
