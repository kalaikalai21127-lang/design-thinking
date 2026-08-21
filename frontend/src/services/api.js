import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const screeningAPI = {
  // POST /predict or /api/predict
  predict: async (sensorValue, name = 'Anonymous Patient', age = 0, gender = 'Unspecified') => {
    const response = await api.post('/predict', {
      sensor_value: parseInt(sensorValue, 10),
      name: name.trim() || 'Anonymous Patient',
      age: parseInt(age, 10) || 0,
      gender: gender || 'Unspecified',
    });
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
