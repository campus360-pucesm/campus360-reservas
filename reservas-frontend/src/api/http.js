import axios from "axios";

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor para agregar token
http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("campus360_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor para manejar errores
http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token inválido o expirado
      localStorage.removeItem("campus360_token");
      localStorage.removeItem("campus360_user");
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

// Export default y named export
export default http;
export { http };