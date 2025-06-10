import { Box, Typography, Grid, Paper, Rating } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";

interface Review {
  id: string;
  product: string;
  rating: number;
  comment: string;
  source: string;
  createdAt: string;
}

export function ReviewsWidget() {
  const { data, isLoading } = useQuery<Review[]>({
    queryKey: ["reviews"],
    queryFn: async () => {
      const response = await axios.get("/api/reviews/recent");
      return response.data;
    },
  });

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Recent Reviews
      </Typography>
      
      {isLoading ? (
        <Typography>Loading...</Typography>
      ) : (
        <Grid container spacing={2}>
          {data?.map((review) => (
            <Grid item xs={12} key={review.id}>
              <Paper sx={{ p: 2 }}>
                <Grid container spacing={1}>
                  <Grid item>
                    <Rating value={review.rating} precision={0.5} readOnly />
                  </Grid>
                  <Grid item xs>
                    <Typography variant="body2" color="text.secondary">
                      {review.product}
                    </Typography>
                    <Typography variant="body1">
                      {review.comment}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {review.source} • {new Date(review.createdAt).toLocaleDateString()}
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
