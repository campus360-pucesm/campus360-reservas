import { http } from "./http";

export const CheckinAPI = {
  realizar: (payload) => http.post("/checkin", payload).then(r => r.data),
  estadoReserva: (reserva_id) => http.get(`/checkin/estado/${reserva_id}`).then(r => r.data),
  historialUsuario: (usuario_id, params = {}) =>
    http.get(`/checkin/usuario/${usuario_id}`, { params }).then(r => r.data),
  simular: (codigo_qr) => http.get(`/checkin/simular/${codigo_qr}`).then(r => r.data),
};
