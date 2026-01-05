import { http } from "./http";

export const ReservasAPI = {
  crear: (payload) => http.post("/reservas", payload).then(r => r.data),
  listarPorUsuario: (usuario_id, params = {}) =>
    http.get(`/reservas/usuario/${usuario_id}`, { params }).then(r => r.data),
  cancelar: (reserva_id, usuario_id, motivo) =>
    http.delete(`/reservas/${reserva_id}`, { params: { usuario_id, motivo } }).then(r => r.data),
  obtener: (reserva_id) => http.get(`/reservas/${reserva_id}`).then(r => r.data),
};
