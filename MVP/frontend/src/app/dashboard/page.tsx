import { Box, Grid, Paper, Typography } from "@mui/material";
import { CardWidget } from "@/components/dashboard/CardWidget";
import { TrafficWidget } from "@/components/dashboard/TrafficWidget";
import { SentimentWidget } from "@/components/dashboard/SentimentWidget";
import { ReviewsWidget } from "@/components/dashboard/ReviewsWidget";

export default function DashboardPage() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Overview Cards */}
        <Grid item xs={12} md={4}>
          <CardWidget
            title="Total Brands"
            value="125"
            icon="store"
            color="primary"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <CardWidget
            title="Active Products"
            value="850"
            icon="shopping_bag"
            color="success"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <CardWidget
            title="Social Mentions"
            value="2,500"
            icon="public"
            color="info"
          />
        </Grid>

        {/* Main Widgets */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: "100%" }}>
            <TrafficWidget />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: "100%" }}>
            <SentimentWidget />
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <ReviewsWidget />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
