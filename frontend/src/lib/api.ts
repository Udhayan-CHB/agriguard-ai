import axios from 'axios';
import Cookies from 'js-cookie';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

api.interceptors.request.use((config) => {
  const token = Cookies.get('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = (username: string, password: string) =>
  api.post('/api/v1/auth/login', { username, password });

export const signup = (username: string, password: string) =>
  api.post('/api/v1/auth/signup', { username, password });

// Farm Profile
export const createFarmProfile = (data: {
  username: string;
  location: string;
  crop: string;
  farm_size_hectares: number;
  problem?: string;
}) => api.post('/api/v1/farm/', data);

// Chat
export const chatWithAgent = (data: {
  username: string;
  farm_profile_id: number;
  message: string;
}) => api.post('/api/v1/chat/', data);

// Report
export const generateReport = (farm_profile_id: number) =>
  api.post('/api/v1/report/', { farm_profile_id });