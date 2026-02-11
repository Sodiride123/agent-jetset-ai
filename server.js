const express = require('express');
const cors = require('cors');
const path = require('path');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3004;
const BACKEND_URL = 'http://localhost:9002';

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'frontend/dist')));

// API proxy endpoints
app.post('/api/chat', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/chat`, req.body, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 120000
    });
    res.json(response.data);
  } catch (error) {
    console.error('API Error:', error.message);
    res.status(error.response?.status || 500).json({
      error: 'Failed to process request',
      details: error.message
    });
  }
});

app.post('/api/reset', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/reset`, req.body, {
      headers: { 'Content-Type': 'application/json' }
    });
    res.json(response.data);
  } catch (error) {
    console.error('API Error:', error.message);
    res.status(error.response?.status || 500).json({
      error: 'Failed to reset conversation',
      details: error.message
    });
  }
});

app.get('/api/health', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/health`);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ status: 'unhealthy', error: error.message });
  }
});

// Handles any requests that don't match the ones above
app.use((req, res) => {
  res.sendFile(path.join(__dirname, 'frontend/dist/index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`JetSet AI server running on port ${PORT}`);
  console.log(`Frontend: http://localhost:${PORT}`);
  console.log(`API: http://localhost:${PORT}/api/*`);
});