import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'Unable to connect to the prediction service.';
    if (error.response?.data?.detail) {
      if (typeof error.response.data.detail === 'string') {
        message = error.response.data.detail;
      } else if (Array.isArray(error.response.data.detail)) {
        message = error.response.data.detail.map((d) => d.msg || `${d.loc?.join('.')}: invalid`).join(', ');
      }
    } else if (error.message) {
      message = error.message;
    }
    return Promise.reject(new Error(message));
  }
);

export const checkHealth = async () => {
  const { data } = await api.get('/health');
  return data;
};

export const getMetadata = async () => {
  const { data } = await api.get('/meta');
  return data;
};

export const predictOne = async (appointmentData) => {
  const { data } = await api.post('/predict', appointmentData);
  return data;
};

export const predictBatch = async (appointmentsList) => {
  const { data } = await api.post('/predict_batch', appointmentsList);
  return data;
};

export default api;
