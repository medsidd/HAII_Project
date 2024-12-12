import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ChatPage from "/Users/medsidd/mental_health_app/frontend/src/pages/ChatPage.js";
import DiagnosisView from "./components/DiagnosisView";
import DiagnosisPage from "./pages/DiagnosisPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<ChatPage />} />
        <Route path="/diagnosis" element={<DiagnosisPage />} />
      </Routes>
    </Router>
  );
}

export default App;
