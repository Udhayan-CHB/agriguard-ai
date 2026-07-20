import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

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