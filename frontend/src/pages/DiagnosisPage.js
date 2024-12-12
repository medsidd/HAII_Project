import React, { useState, useEffect } from "react";
import { Box, Button, Typography, Card, CardContent, CircularProgress, Grid } from "@mui/material";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function DiagnosisPage() {
  const navigate = useNavigate();
  const [diagnosis, setDiagnosis] = useState([]);
  const [chartUrls, setChartUrls] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDiagnosisAndTrends = async () => {
      try {
        const diagnosisResponse = await axios.get("http://127.0.0.1:5000/diagnose");
        setDiagnosis(diagnosisResponse.data.diagnosis || []);

        const trendsResponse = await axios.get("http://127.0.0.1:5000/trends");
        setChartUrls(trendsResponse.data.charts || {});
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to fetch data.");
      } finally {
        setLoading(false);
      }
    };

    fetchDiagnosisAndTrends();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="85vh">
        <CircularProgress />
        <Typography ml={2}>Loading diagnosis...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" flexDirection="column" alignItems="center" mt={4}>
        <Typography color="error" variant="h6">{error}</Typography>
        <Button variant="contained" onClick={() => navigate("/")}>
          Back to Chat
        </Button>
      </Box>
    );
  }

  return (
    <Box p={4} sx={{ backgroundColor: "#f5fbfb" }}>
      {/* Back Button */}
      <Button variant="outlined" color="primary" onClick={() => navigate("/")}>
        Back to Chat
      </Button>

      {/* Diagnosis Header */}
      <Typography variant="h4" mt={4} gutterBottom fontFamily="monospace">
        mentAI Health Diagnosis
      </Typography>

      {/* Diagnosis Cards */}
      <Grid container spacing={3}>
        {diagnosis.map((item, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Card sx={{ backgroundColor: "#EECAD5", boxShadow: 3 }}>
              <CardContent>
                <Typography variant="h5" color="primary">
                  {item.condition}
                </Typography>
                <Typography variant="body1" mt={2}>
                  Confidence: {item.confidence}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Trends Header */}
      <Typography variant="h5" mt={6} gutterBottom fontFamily="monospace">
        Severity Trends
      </Typography>

      {/* Trend Charts */}
      <Grid container spacing={3} mt={4}>
        {diagnosis.map((item, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Typography variant="h6">{item.condition}</Typography>
            {chartUrls[item.condition] ? (
              <img
                src={chartUrls[item.condition]}
                alt={`Trend for ${item.condition}`}
                style={{ width: "100%", borderRadius: "8px", backgroundColor: "#f7f9fc" }}
              />
            ) : (
              <Typography variant="body2" color="textSecondary">
                No chart available.
              </Typography>
            )}
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default DiagnosisPage;
