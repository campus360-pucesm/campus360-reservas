import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getRecursosPorTipo } from "../api/recursos.api";

const RecursosPorTipo = () => {
  const { tipo } = useParams();
  const navigate = useNavigate();
  const [recursos, setRecursos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtroDisponibilidad, setFiltroDisponibilidad] = useState("todos");

  const tipoInfo = {
    sala: {
      titulo: "Salas de Estudio",
      icon: "🏢"
    },
    laboratorio: {
      titulo: "Laboratorios",
      icon: "💻"
    },
    equipo: {
      titulo: "Equipos",
      icon: "📹"
    },
    parqueadero: {
      titulo: "Estaciones de Parqueadero",
      icon: "🚗"
    },
    cubiculo: {
      titulo: "Cubículos de Biblioteca",
      icon: "📚"
    }
  };

  const currentTipo = tipoInfo[tipo] || tipoInfo.sala;

  useEffect(() => {
    loadRecursos();
  }, [tipo]);

  const loadRecursos = async () => {
    setLoading(true);
    try {
      const response = await getRecursosPorTipo(tipo);
      setRecursos(response.data);
    } catch (error) {
      console.error("Error cargando recursos:", error);
      // Datos de prueba
      setRecursos([
        {
          id: 1,
          codigo: "SALA-101",
          nombre: "Sala de Estudio 1",
          capacidad: 8,
          ubicacion: "Piso 1, Edificio A",
          disponible: true,
          equipamiento: ["Proyector", "Pizarra", "WiFi"]
        },
        {
          id: 2,
          codigo: "SALA-102",
          nombre: "Sala de Estudio 2",
          capacidad: 12,
          ubicacion: "Piso 1, Edificio A",
          disponible: false,
          equipamiento: ["Proyector", "Pantalla", "WiFi"]
        },
        {
          id: 3,
          codigo: "SALA-201",
          nombre: "Sala de Estudio 3",
          capacidad: 6,
          ubicacion: "Piso 2, Edificio A",
          disponible: true,
          equipamiento: ["Pizarra", "WiFi"]
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const recursosFiltrados = recursos.filter(recurso => {
    if (filtroDisponibilidad === "todos") return true;
    if (filtroDisponibilidad === "disponibles") return recurso.disponible;
    return !recurso.disponible;
  });

  const handleReservar = (recurso) => {
    navigate("/reservar", { state: { recurso, tipo } });
  };

  return (
    <div style={{ padding: "20px", maxWidth: "1400px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: "24px" }}>
        <button
          onClick={() => navigate("/dashboard")}
          className="btn btn-secondary"
          style={{ width: "auto", padding: "10px 20px", marginBottom: "16px" }}
        >
          ← Volver al Dashboard
        </button>

        <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "16px" }}>
          <div style={{ fontSize: "3rem" }}>{currentTipo.icon}</div>
          <div>
            <h1 style={{ fontSize: "2rem", fontWeight: "700", margin: 0 }}>
              Disponibilidad de recursos
            </h1>
            <p style={{ color: "var(--text-light)", margin: 0 }}>
              {currentTipo.titulo}
            </p>
          </div>
        </div>

        {/* Filtros */}
        <div style={{ display: "flex", gap: "8px" }}>
          <button
            onClick={() => setFiltroDisponibilidad("todos")}
            className={`btn ${filtroDisponibilidad === "todos" ? "btn-primary" : "btn-secondary"}`}
            style={{ width: "auto", padding: "10px 20px" }}
          >
            Todos
          </button>
          <button
            onClick={() => setFiltroDisponibilidad("disponibles")}
            className={`btn ${filtroDisponibilidad === "disponibles" ? "btn-primary" : "btn-secondary"}`}
            style={{ width: "auto", padding: "10px 20px" }}
          >
            Disponibles
          </button>
          <button
            onClick={() => setFiltroDisponibilidad("ocupados")}
            className={`btn ${filtroDisponibilidad === "ocupados" ? "btn-primary" : "btn-secondary"}`}
            style={{ width: "auto", padding: "10px 20px" }}
          >
            Ocupados
          </button>
        </div>
      </div>

      {/* Lista de recursos */}
      {loading ? (
        <div style={{ textAlign: "center", padding: "40px" }}>
          <p>Cargando recursos...</p>
        </div>
      ) : recursosFiltrados.length === 0 ? (
        <div className="admin-card" style={{ textAlign: "center", padding: "40px" }}>
          <p>No se encontraron recursos</p>
        </div>
      ) : (
        <div className="card-grid">
          {recursosFiltrados.map((recurso) => (
            <div key={recurso.id} className="admin-card">
              {/* Header del recurso */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "16px" }}>
                <div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-light)", marginBottom: "4px" }}>
                    CÓDIGO
                  </div>
                  <div style={{ fontSize: "1.25rem", fontWeight: "700" }}>
                    {recurso.codigo}
                  </div>
                </div>
                <span
                  style={{
                    padding: "4px 12px",
                    borderRadius: "999px",
                    fontSize: "0.75rem",
                    fontWeight: "700",
                    background: recurso.disponible ? "#d1fae5" : "#fee2e2",
                    color: recurso.disponible ? "#065f46" : "#991b1b"
                  }}
                >
                  {recurso.disponible ? "Disponible" : "Ocupado"}
                </span>
              </div>

              {/* Nombre */}
              <h3 style={{ fontSize: "1.125rem", fontWeight: "700", marginBottom: "8px" }}>
                {recurso.nombre}
              </h3>

              {/* Info */}
              <div style={{ marginBottom: "16px" }}>
                {recurso.capacidad && (
                  <div style={{ fontSize: "0.875rem", color: "var(--text-light)", marginBottom: "4px" }}>
                    👥 Capacidad: {recurso.capacidad} personas
                  </div>
                )}
                {recurso.ubicacion && (
                  <div style={{ fontSize: "0.875rem", color: "var(--text-light)" }}>
                    📍 {recurso.ubicacion}
                  </div>
                )}
              </div>

              {/* Equipamiento */}
              {recurso.equipamiento && recurso.equipamiento.length > 0 && (
                <div style={{ marginBottom: "16px" }}>
                  <div style={{ fontSize: "0.75rem", fontWeight: "600", marginBottom: "8px", color: "var(--text-light)" }}>
                    EQUIPAMIENTO
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                    {recurso.equipamiento.map((item, idx) => (
                      <span
                        key={idx}
                        style={{
                          padding: "4px 12px",
                          background: "var(--bg)",
                          borderRadius: "6px",
                          fontSize: "0.75rem",
                          color: "var(--text-light)"
                        }}
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Botón */}
              <button
                onClick={() => handleReservar(recurso)}
                disabled={!recurso.disponible}
                className="btn btn-primary"
                style={{
                  opacity: recurso.disponible ? 1 : 0.5,
                  cursor: recurso.disponible ? "pointer" : "not-allowed"
                }}
              >
                {recurso.disponible ? "Reservar →" : "No disponible"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RecursosPorTipo;