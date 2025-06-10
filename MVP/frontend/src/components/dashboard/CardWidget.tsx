import { Card, CardContent, CardHeader, Typography, IconButton } from "@mui/material";
import { Icon } from "@mui/material";

interface CardWidgetProps {
  title: string;
  value: string | number;
  icon: string;
  color: "primary" | "secondary" | "success" | "error" | "warning" | "info";
}

export function CardWidget({ title, value, icon, color }: CardWidgetProps) {
  return (
    <Card sx={{ height: "100%" }}>
      <CardHeader
        title={title}
        avatar={
          <Icon sx={{ color: color }}>
            {icon}
          </Icon>
        }
      />
      <CardContent>
        <Typography variant="h3" component="div" align="center">
          {value}
        </Typography>
      </CardContent>
    </Card>
  );
}
