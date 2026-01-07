import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Helper para obtener headers con token
const getHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

// Obtener estadísticas generales para el dashboard
export const getEstadisticasReservas = async () => {
  try {
    const response = await axios.get(`${API_URL}/estadisticas`, {
      headers: getHeaders(),
    });
    return response;
  } catch (error) {
    console.error('Error al obtener estadísticas:', error);
    throw error;
  }
};

// Obtener todas las reservas del usuario autenticado
export const getMisReservas = async () => {
  try {
    const response = await axios.get(`${API_URL}/reservas/mis-reservas`, {
      headers: getHeaders(),
    });
    return response;
  } catch (error) {
    console.error('Error al obtener reservas:', error);
    throw error;
  }
};

// Crear una nueva reserva
export const crearReserva = async (data) => {
  try {
    const response = await axios.post(`${API_URL}/reservas`, data, {
      headers: getHeaders(),
    });
    return response;
  } catch (error) {
    console.error('Error al crear reserva:', error);
    throw error;
  }
};

// Cancelar una reserva existente
export const cancelarReserva = async (id) => {
  try {
    const response = await axios.delete(`${API_URL}/reservas/${id}`, {
      headers: getHeaders(),
    });
    return response;
  } catch (error) {
    console.error('Error al cancelar reserva:', error);
    throw error;
  }
};

// Obtener detalle de una reserva específica
export const getReservaById = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/reservas/${id}`, {
      headers: getHeaders(),
    });
    return response;
  } catch (error) {
    console.error('Error al obtener reserva:', error);
    throw error;
  }
};