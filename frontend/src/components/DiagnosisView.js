import React, { useState, useEffect } from "react";
import axios from "axios";

const DiagnosisView = () => {
  const [diagnosis, setDiagnosis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDiagnosis = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:5000/diagnose");
            console.log("Diagnosis Data:", response.data);
            setDiagnosis(response.data.diagnosis || []);
        } catch (err) {
            console.error("Error fetching diagnosis:", err);
            setError("Failed to fetch diagnosis data.");
        } finally {
            setLoading(false);
        }
    };

    fetchDiagnosis();
  }, []);

  console.log("Diagnosis State:", diagnosis);


  if (loading) {
    return <div>Loading diagnosis...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div>
      <button onClick={() => (window.location.href = "/")}>Back to Chat</button>
      <h1>mentAI Health Diagnosis</h1>
      <ul>
        {diagnosis.map((d, index) => (
          <li key={index}>
            {d.condition}: {d.confidence}%
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DiagnosisView;
