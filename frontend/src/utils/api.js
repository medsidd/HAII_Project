import axios from "axios";

// Base API URL
export const BASE_URL = "http://127.0.0.1:5000";


// Create an axios instance with default configurations
const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true, // Include credentials for cross-origin requests
  headers: {
    "Content-Type": "application/json",
  },
});

// Fetch diagnosis results
export const fetchDiagnosis = async () => {
  try {
    const response = await api.get("/diagnose");
    return response.data;
  } catch (error) {
    console.error("Error fetching diagnosis:", error);
    throw error;
  }
};

// Fetch trend chart data
export const fetchTrendChart = async () => {
  try {
    const response = await api.get("/trends");
    return response.data; // Ensure backend provides chart data as JSON
  } catch (error) {
    console.error("Error fetching trend chart:", error);
    throw error;
  }
};

// Send chat message
export const sendChatMessage = async (message) => {
  try {
    const response = await api.post("/chat", { message });
    return response.data;
  } catch (error) {
    console.error("Error in API call:", error);
    throw error;
  }
};
