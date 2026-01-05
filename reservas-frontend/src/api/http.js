import axios from "axios";

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
});

// Si luego usas JWT del módulo auth:
http.interceptors.request.use((config) => {
  const token = localStorage.getItem("campus360_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
