import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const screeningAPI = {
  // POST /predict or /api/predict (Supports AS7262 spectral channels object or legacy sensorValue)
  predict: async (payload, name = 'Anonymous Patient', age = 0, gender = 'Unspecified') => {
    let body = {};
    if (typeof payload === 'object' && payload !== null) {
      const channels = payload.channels || payload;
      body = {
        sensor_type: 'AS7262',
        channels: {
          violet: parseFloat(channels.violet || 0),
          blue: parseFloat(channels.blue || 0),
          green: parseFloat(channels.green || 0),
          yellow: parseFloat(channels.yellow || 0),
          orange: parseFloat(channels.orange || 0),
          red: parseFloat(channels.red || 0)
        },
        violet: parseFloat(channels.violet || 0),
        blue: parseFloat(channels.blue || 0),
        green: parseFloat(channels.green || 0),
        yellow: parseFloat(channels.yellow || 0),
        orange: parseFloat(channels.orange || 0),
        red: parseFloat(channels.red || 0),
        name: (payload.name || name).trim() || 'Anonymous Patient',
        age: parseInt(payload.age ?? age, 10) || 0,
        gender: payload.gender || gender || 'Unspecified',
        sensor_value: payload.sensor_value ?? 0
      };
    } else {
      body = {
        sensor_value: parseInt(payload, 10),
        name: name.trim() || 'Anonymous Patient',
        age: parseInt(age, 10) || 0,
        gender: gender || 'Unspecified',
      };
    }
    const response = await api.post('/predict', body);
    return response.data;
  },


  // Dedicated Hardware Telemetry Endpoint: POST /api/sensor/readings
  sendSensorReadings: async (payload) => {
    const response = await api.post('/sensor/readings', payload);
    return response.data;
  },

  // Real-Time Hardware Stream: GET /api/latest
  getLatest: async () => {
    const response = await api.get('/latest');
    return response.data;
  },

  // GET /history or /api/history
  getHistory: async () => {
    const response = await api.get('/history');
    return response.data;
  },

  // GET /statistics or /api/statistics
  getStatistics: async () => {
    const response = await api.get('/statistics');
    return response.data;
  },

  // DELETE /record/{id} or /api/record/{id}
  deleteRecord: async (id) => {
    const response = await api.delete(`/record/${id}`);
    return response.data;
  },

  // GET /export-dataset URL
  getExportUrl: () => {
    return '/api/export-dataset';
  }
};

export default api;
