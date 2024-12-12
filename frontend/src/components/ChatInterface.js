import React, { useState, useEffect } from "react";
import { Box, TextField, Button, Typography } from "@mui/material";
import axios from "axios";
import { sendChatMessage } from "/Users/medsidd/mental_health_app/frontend/src/utils/api.js";
import { BASE_URL } from "/Users/medsidd/mental_health_app/frontend/src/utils/api.js";


function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");

  // Load chat history from localStorage on component mount
  useEffect(() => {
    const storedMessages = localStorage.getItem("chatMessages");
    if (storedMessages) {
      setMessages(JSON.parse(storedMessages));
    }
  }, []);

  // Save chat history to localStorage whenever messages are updated
  useEffect(() => {
    localStorage.setItem("chatMessages", JSON.stringify(messages));
  }, [messages]);


  const sendMessage = async () => {
    if (userInput.trim() === "") return;
    const userMessage = { sender: "user", text: userInput, timestamp: new Date() };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await sendChatMessage(userInput);
      console.log("API Response:", response); // Log the API response
      const aiMessage = { sender: "ai", text: response.response, timestamp: new Date() };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Error sending chat message:", error); // Log the error
    }

    setUserInput("");
  };

  return (
    <Box p={4} display="flex" flexDirection="column" justifyContent="space-between" height="85vh" sx={{ backgroundColor: "#f5fbfb" }}>
      <Box flexGrow={1} overflow="auto" mb={2}>
        {messages.map((msg, index) => (
          <Box
            key={index}
            display="flex"
            justifyContent={msg.sender === "user" ? "flex-end" : "flex-start"}
            mb={1}
          >
            <Box
              bgcolor={msg.sender === "user" ? "#A8D5E2" : "#F4D9C6"}
              p={2}
              borderRadius={4}
              maxWidth="60%"
            >
              <Typography variant="body1">{msg.text}</Typography>
              <Typography variant="caption" display="block" textAlign="right">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </Typography>
            </Box>
          </Box>
        ))}
      </Box>
      <Box display="flex">
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && sendMessage()}
        />
        <Button variant="contained" color="primary" onClick={sendMessage}>
          Send
        </Button>
        <Button
          variant="contained"
          color="secondary"
          onClick={() => (window.location.href = "/diagnosis")}
        >
          Diagnose
        </Button>
        <Button
        variant="contained"
        color="secondary"
        onClick={async () => {
          await axios.post(`${BASE_URL}/reset`);
          setMessages([]);
        }}
      >
        Reset Conversation
      </Button>


      </Box>
    </Box>
  );
}

export default ChatInterface;
