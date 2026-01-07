import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { crearReserva } from "../api/reservas.api";

const CrearReserva = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { recurso, tipo } = location.state || {};

  const [formData, setFormData] = useState({
    fecha: "",
    horaInicio: "",
    horaFin: "",
    proposito: "",
    participantes: 1
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!recurso) {
    return (
      <div className="center-container">
        <div className="card">
          <h2>No se seleccionó ningún recurso</h2>
          <button onClick={() => navigate("/dashboard")} className="btn btn-primary">
            Volver al Dashboard
          </button>
        </div>
      </div>
    );
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.fecha || !formData.horaInicio || !formData.horaFin) {
      setError("Por favor completa todos los campos requeridos");
      return;
    }

    if (formData.horaInicio >= formData.horaFin) {
      setError("La hora de fin debe ser posterior a la hora de inicio");
      return;
    }

    setLoading(true);
    try {
      const reservaData = {
        recurso_id: recurso.id,
        tipo_recurso: tipo,
        fecha: formData.fecha,
        hora_inicio: formData.horaInicio,
        hora_fin: formData.horaFin,
        proposito: formData.proposito,
        participantes: formData.participantes
      };

      await crearReserva(reservaData);
      navigate("/mis-reservas", {
        state: { message: "Reserva creada exitosamente" }
      });
    } catch (err) {
      setError(err.response?.data?.message || "Error al crear la reserva");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "800px", margin: "0 auto" }}>
      <button
        onClick={() => navigate(-1)}
        className="btn btn-secondary"
        style={{ width: "auto", padding: "10px 20px", marginBottom: "24px" }}
      >
        ← Volver
      </button>

      <div className="admin-card" style={{ marginBottom: "24px" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "700", marginBottom: "8px" }}>
          Nueva reserva
        </h1>
        <p style={{ color: "var(--text-light)", marginBottom: "16px" }}>
          {tipo === "sala" ? "Sala/Laboratorio" : tipo}
        </p>

        <div style={{ background: "var(--bg)", padding: "16px", borderRadius: "var(--radius)" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-light)", marginBottom: "4px" }}>
            Recurso seleccionado
          </div>
          <div style={{ fontSize: "1.25rem", fontWeight: "700", marginBottom: "4px" }}>
            {recurso.nombre}
          </div>
          <div style={{ fontSize: "0.875rem", color: "var(--text-light)" }}>
            Código: {recurso.codigo}
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="admin-card">
        <h2 className="dashboard-section-title">Datos de la reserva</h2>

        {error && <div className="alert alert-error">{error}</div>}

        <div className="form-group">
          <label>Fecha *</label>
          <input
            type="date"
            value={formData.fecha}
            onChange={(e) => handleInputChange("fecha", e.target.value)}
            min={new Date().toISOString().split("T")[0]}
            required
          />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
          <div className="form-group">
            <label>Hora de inicio *</label>
            <input
              type="time"
              value={formData.horaInicio}
              onChange={(e) => handleInputChange("horaInicio", e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Hora de fin *</label>
            <input
              type="time"
              value={formData.horaFin}
              onChange={(e) => handleInputChange("horaFin", e.target.value)}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label>Propósito de la reserva *</label>
          <textarea
            value={formData.proposito}
            onChange={(e) => handleInputChange("proposito", e.target.value)}
            placeholder="Describe brevemente el uso que le darás al recurso..."
            rows="4"
            style={{
              width: "100%",
              padding: "12px 14px",
              border: "1.5px solid var(--border)",
              borderRadius: "var(--radius)",
              fontSize: "15px",
              fontFamily: "inherit",
              resize: "vertical"
            }}
            required
          />
        </div>

        {(tipo === "sala" || tipo === "laboratorio") && (
          <div className="form-group">
            <label>Número de participantes</label>
            <input
              type="number"
              min="1"
              max={recurso.capacidad || 50}
              value={formData.participantes}
              onChange={(e) => handleInputChange("participantes", parseInt(e.target.value))}
            />
            {recurso.capacidad && (
              <p style={{ fontSize: "0.875rem", color: "var(--text-light)", marginTop: "4px" }}>
                Capacidad máxima: {recurso.capacidad} personas
              </p>
            )}
          </div>
        )}

        <div style={{ background: "var(--bg)", padding: "16px", borderRadius: "var(--radius)", marginTop: "16px" }}>
          <p style={{ fontSize: "0.875rem", color: "var(--text-light)", margin: 0 }}>
            📌 Al confirmar tu reserva, recibirás un código QR que deberás presentar al momento del check-in.
          </p>
        </div>

        <div style={{ display: "flex", gap: "12px", marginTop: "24px" }}>
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="btn btn-secondary"
            style={{ flex: 1 }}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ flex: 1 }}
          >
            {loading ? "Creando..." : "Crear Reserva"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CrearReserva;