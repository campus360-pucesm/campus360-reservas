import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { getMisReservas, cancelarReserva } from "../api/reservas.api";

const MisReservas = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [reservas, setReservas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(location.state?.message || null);

  useEffect(() => {
    loadReservas();
  }, []);

  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => setMessage(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  const loadReservas = async () => {
    setLoading(true);
    try {
      const response = await getMisReservas();
      setReservas(response.data);
    } catch (error) {
      console.error("Error loading reservas:", error);
      // Datos de prueba
      setReservas([
        {
          id: 1,
          codigo: "RES-001",
          recurso: { nombre: "Sala de Estudio 1", codigo: "SALA-101" },
          tipo_recurso: "sala",
          fecha: "2026-01-10",
          hora_inicio: "10:00",
          hora_fin: "12:00",
          estado: "activa",
          proposito: "Estudio grupal de matemáticas"
        },
        {
          id: 2,
          codigo: "RES-002",
          recurso: { nombre: "Laboratorio de Computación 2", codigo: "LAB-102" },
          tipo_recurso: "laboratorio",
          fecha: "2026-01-08",
          hora_inicio: "14:00",
          hora_fin: "16:00",
          estado: "completada",
          proposito: "Práctica de programación"
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelar = async (id) => {
    if (!confirm("¿Estás seguro de cancelar esta reserva?")) return;

    try {
      await cancelarReserva(id);
      setReservas(reservas.map(r =>
        r.id === id ? { ...r, estado: "cancelada" } : r
      ));
      setMessage("Reserva cancelada exitosamente");
    } catch (error) {
      console.error("Error canceling reserva:", error);
      alert("Error al cancelar la reserva");
    }
  };

  const getEstadoBadge = (estado) => {
    const estilos = {
      activa: { bg: "#d1fae5", color: "#065f46", text: "Activa" },
      completada: { bg: "#dbeafe", color: "#1e40af", text: "Completada" },
      cancelada: { bg: "#fee2e2", color: "#991b1b", text: "Cancelada" },
      pendiente: { bg: "#fef3c7", color: "#92400e", text: "Pendiente" }
    };

    const estilo = estilos[estado] || estilos.pendiente;

    return (
      <span
        style={{
          padding: "4px 12px",
          borderRadius: "999px",
          fontSize: "0.75rem",
          fontWeight: "700",
          background: estilo.bg,
          color: estilo.color
        }}
      >
        {estilo.text}
      </span>
    );
  };

  return (
    <div style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
      <button
        onClick={() => navigate("/dashboard")}
        className="btn btn-secondary"
        style={{ width: "auto", padding: "10px 20px", marginBottom: "24px" }}
      >
        ← Volver al Dashboard
      </button>

      <div style={{ marginBottom: "24px" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "700", marginBottom: "8px" }}>
          Mis reservas
        </h1>
        <p style={{ color: "var(--text-light)" }}>
          Gestiona y visualiza tus reservas activas y pasadas
        </p>
      </div>

      {message && (
        <div className="alert alert-success" style={{ marginBottom: "24px" }}>
          {message}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: "center", padding: "40px" }}>
          <p>Cargando reservas...</p>
        </div>
      ) : reservas.length === 0 ? (
        <div className="admin-card" style={{ textAlign: "center", padding: "40px" }}>
          <h3 style={{ marginBottom: "8px" }}>No tienes reservas</h3>
          <p style={{ color: "var(--text-light)", marginBottom: "16px" }}>
            Explora los recursos disponibles y crea tu primera reserva
          </p>
          <button
            onClick={() => navigate("/dashboard")}
            className="btn btn-primary"
            style={{ width: "auto", padding: "12px 24px" }}
          >
            Explorar Recursos
          </button>
        </div>
      ) : (
        <div className="card-grid">
          {reservas.map((reserva) => (
            <div key={reserva.id} className="admin-card">
              {/* Header */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "16px" }}>
                <div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-light)", marginBottom: "4px" }}>
                    CÓDIGO DE RESERVA
                  </div>
                  <div style={{ fontSize: "1.125rem", fontWeight: "700" }}>
                    {reserva.codigo}
                  </div>
                </div>
                {getEstadoBadge(reserva.estado)}
              </div>

              {/* Recurso */}
              <h3 style={{ fontSize: "1.125rem", fontWeight: "700", marginBottom: "4px" }}>
                {reserva.recurso?.nombre || "Recurso"}
              </h3>
              <p style={{ fontSize: "0.875rem", color: "var(--text-light)", marginBottom: "16px" }}>
                {reserva.recurso?.codigo || ""}
              </p>

              {/* Detalles */}
              <div style={{ background: "var(--bg)", padding: "12px", borderRadius: "8px", marginBottom: "16px" }}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                  <div>
                    <div style={{ fontSize: "0.75rem", color: "var(--text-light)", marginBottom: "4px" }}>
                      Fecha
                    </div>
                    <div style={{ fontSize: "0.875rem", fontWeight: "600" }}>
                      {new Date(reserva.fecha + "T00:00:00").toLocaleDateString("es-ES", {
                        day: "2-digit",
                        month: "short",
                        year: "numeric"
                      })}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: "0.75rem", color: "var(--text-light)", marginBottom: "4px" }}>
                      Horario
                    </div>
                    <div style={{ fontSize: "0.875rem", fontWeight: "600" }}>
                      {reserva.hora_inicio} - {reserva.hora_fin}
                    </div>
                  </div>
                </div>

                {reserva.proposito && (
                  <div style={{ marginTop: "12px", paddingTop: "12px", borderTop: "1px solid var(--border)" }}>
                    <div style={{ fontSize: "0.75rem", color: "var(--text-light)", marginBottom: "4px" }}>
                      Propósito
                    </div>
                    <div style={{ fontSize: "0.875rem" }}>
                      {reserva.proposito}
                    </div>
                  </div>
                )}
              </div>

              {/* Acciones */}
              {reserva.estado === "activa" && (
                <div style={{ display: "flex", gap: "8px" }}>
                  <button
                    onClick={() => navigate("/checkin", { state: { reserva } })}
                    className="btn btn-primary"
                    style={{ flex: 1 }}
                  >
                    Ver QR
                  </button>
                  <button
                    onClick={() => handleCancelar(reserva.id)}
                    className="btn btn-secondary"
                    style={{ flex: 1 }}
                  >
                    Cancelar
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MisReservas;