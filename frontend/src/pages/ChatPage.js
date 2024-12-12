import React from "react";
import { Box } from "@mui/material";
import Header from "/Users/medsidd/mental_health_app/frontend/src/components/Header.js";
import ChatInterface from "/Users/medsidd/mental_health_app/frontend/src/components/ChatInterface.js";

function ChatPage() {
  return (
    <Box>
      <Header title="mentAI" />
      <ChatInterface />
    </Box>
  );
}

export default ChatPage;
