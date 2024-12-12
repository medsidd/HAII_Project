import React from "react";
import { Box, Typography } from "@mui/material";

function Header({ title }) {
  return (
    <Box
      sx={{
        backgroundColor: "#a99abd", 
        padding: "16px",
        textAlign: "left",
      }}
    >
      <Typography
        variant="h4"
        sx={{
          fontFamily: "monospace", // Change this to your desired font
          fontSize: "2rem",                  // Adjust font size if needed
          color: "#fff",                     // White text color
        }}
      >
        {title}
      </Typography>
    </Box>
  );
}

export default Header;
