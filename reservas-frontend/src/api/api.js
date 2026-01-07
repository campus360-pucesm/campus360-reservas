import http from "./http"; // Cambiado: default import en lugar de named

export const getRecursosPorTipo = (tipo) => {
  return http.get(`/recursos?tipo=${tipo}`);
};

export const getRecurso = (id) => {
  return http.get(`/recursos/${id}`);
};

export const getDisponibilidad = (tipo, fecha) => {
  return http.get(`/recursos/disponibilidad`, {
    params: { tipo, fecha }
  });
};

// También puedes mantener tu API object si lo prefieres
export const RecursosAPI = {
  listar: (params) => http.get("/recursos", { params }).then(r => r.data),
  obtener: (id) => http.get(`/recursos/${id}`).then(r => r.data),
  disponibilidad: (id, fecha) =>
    http.get(`/recursos/${id}/disponibilidad`, { params: { fecha } }).then(r => r.data),

  // shortcuts
  salas: () => http.get("/recursos/salas").then(r => r.data),
  labs: () => http.get("/recursos/laboratorios").then(r => r.data),
  equipos: () => http.get("/recursos/equipos").then(r => r.data),
  parqueaderos: () => http.get("/recursos/parqueaderos").then(r => r.data),
  biblioteca: () => http.get("/recursos/biblioteca").then(r => r.data),
};