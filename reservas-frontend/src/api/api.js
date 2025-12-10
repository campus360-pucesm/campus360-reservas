const API_URL = import.meta.env.VITE_API_URL;

// Generic GET
export async function apiGet(path) {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) throw new Error("Error en la petición");
  return res.json();
}

// Specific endpoints
export const getHealth = () => apiGet("/health/");
export const getReservas = () => apiGet("/reservas/");
