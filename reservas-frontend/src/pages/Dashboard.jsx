import { useState, useEffect, useMemo } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { getEstadisticasReservas } from "../api/reservas.api";
import "../styles/components/dashboard.css";
import "../styles/components/navbar.css";

const AUTH_APP_URL = import.meta.env.VITE_AUTH_APP_URL || "http://localhost:5173";

const getUser = () => {
  const u = localStorage.getItem("campus360_user");
  return u ? JSON.parse(u) : null;
};

const clearSession = () => {
  localStorage.removeItem("campus360_token");
  localStorage.removeItem("campus360_user");
};

const getRoleLabel = (role) => {
  switch (role) {
    case "admin": return "Administrador";
    case "teacher": return "Profesor";
    case "student": return "Estudiante";
    default: return role || "Usuario";
  }
};

const getRoleBadgeColor = (role) => {
  switch (role) {
    case "admin": return "#dc2626";
    case "teacher": return "#2563eb";
    case "student": return "#16a34a";
    default: return "#6b7280";
  }
};

const Dashboard = () => {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const user = useMemo(() => getUser(), []);

  const categorias = [
    {
      id: "sala",
      titulo: "Salas de Estudio",
      descripcion: "Espacios colaborativos para sesiones de estudio grupal",
      icon: "🏢",
    },
    {
      id: "laboratorio",
      titulo: "Laboratorios de Computación",
      descripcion: "Laboratorios especializados con equipos de última generación",
      icon: "💻",
    },
    {
      id: "equipo",
      titulo: "Equipos",
      descripcion: "Dispositivos tecnológicos disponibles para préstamo",
      icon: "📹",
    },
    {
      id: "parqueadero",
      titulo: "Estaciones de Parqueadero",
      descripcion: "Espacios de parqueo asignados temporalmente",
      icon: "🚗",
    },
    {
      id: "cubiculo",
      titulo: "Cubículos de Biblioteca",
      descripcion: "Espacios individuales de estudio en la biblioteca",
      icon: "📚",
    },
  ];

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await getEstadisticasReservas();
      setStats(response.data);
    } catch (error) {
      console.error("Error loading stats, usando datos de prueba:", error);
      setStats({
        sala: { total: 10, disponibles: 5 },
        laboratorio: { total: 8, disponibles: 3 },
        equipo: { total: 15, disponibles: 10 },
        parqueadero: { total: 20, disponibles: 15 },
        cubiculo: { total: 12, disponibles: 8 }
      });
    } finally {
      setLoading(false);
    }
  };

  const getTotalRecursos = () => {
    if (!stats) return 0;
    return Object.values(stats).reduce((acc, cat) => acc + cat.total, 0);
  };

  const getTotalDisponibles = () => {
    if (!stats) return 0;
    return Object.values(stats).reduce((acc, cat) => acc + cat.disponibles, 0);
  };

  const getTotalEnUso = () => {
    if (!stats) return 0;
    return Object.values(stats).reduce(
      (acc, cat) => acc + (cat.total - cat.disponibles),
      0
    );
  };

  const goAuth = () => (window.location.href = `${AUTH_APP_URL}/dashboard`);

  const logout = () => {
    clearSession();
    window.location.href = `${AUTH_APP_URL}/`;
  };

  return (
    <div style={{ padding: "20px", maxWidth: "1400px", margin: "0 auto" }}>
      {/* Navbar */}
      <div className="navbar-container">
        <div className="navbar-left">
          <div className="navbar-title">CAMPUS360 — Reservas</div>
          <div className="navbar-user-info">
            <span className="navbar-user-name">{user?.full_name || "Usuario"}</span>
            <span className="navbar-user-email">{user?.email || "test@example.com"}</span>
            <span
              className="navbar-role-badge"
              style={{ background: getRoleBadgeColor(user?.role) }}
            >
              {getRoleLabel(user?.role)}
            </span>
          </div>
        </div>

        <div className="navbar-right">
          <button
            onClick={() => navigate("/dashboard")}
            className={`nav-button ${pathname === "/dashboard" ? "active" : ""}`}
          >
            🧭 Dashboard
          </button>

          <button
            onClick={() => navigate("/mis-reservas")}
            className={`nav-button ${pathname.startsWith("/mis-reservas") ? "active" : ""}`}
          >
            📌 Mis reservas
          </button>

          <button
            onClick={() => navigate("/checkin")}
            className={`nav-button ${pathname.startsWith("/checkin") ? "active" : ""}`}
          >
            ✅ Check-in (QR)
          </button>

          <button onClick={goAuth} className="nav-button-auth">
            🔁 Volver a Auth
          </button>

          <button onClick={logout} className="nav-button-logout">
            Cerrar sesión
          </button>
        </div>
      </div>

      {/* Dashboard Content */}
      <div className="dashboard-container">
        {/* Quick Stats */}
        {stats && (
          <div className="card-grid stats-grid">
            <div className="admin-card stat-card">
              <div className="stat-card-inner">
                <div className="stat-icon stat-icon-default">📊</div>
                <div className="stat-content">
                  <div className="stat-value">{getTotalRecursos()}</div>
                  <div className="stat-label">Total de Recursos</div>
                </div>
              </div>
            </div>

            <div className="admin-card stat-card">
              <div className="stat-card-inner">
                <div className="stat-icon stat-icon-success">✅</div>
                <div className="stat-content">
                  <div className="stat-value stat-value-success">
                    {getTotalDisponibles()}
                  </div>
                  <div className="stat-label">Disponibles Ahora</div>
                </div>
              </div>
            </div>

            <div className="admin-card stat-card">
              <div className="stat-card-inner">
                <div className="stat-icon stat-icon-info">🔒</div>
                <div className="stat-content">
                  <div className="stat-value stat-value-primary">
                    {getTotalEnUso()}
                  </div>
                  <div className="stat-label">En Uso</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Section Title */}
        <div className="dashboard-section">
          <h2 className="dashboard-section-title">Recursos Disponibles</h2>
          <p className="dashboard-section-subtitle">
            Selecciona una categoría para ver los recursos disponibles
          </p>
        </div>

        {/* Categories Grid */}
        <div className="card-grid">
          {categorias.map((categoria) => (
            <div
              key={categoria.id}
              className="admin-card category-card"
              onClick={() => navigate(`/recursos/${categoria.id}`)}
            >
              <div className="category-header">
                <div className="category-icon">{categoria.icon}</div>
                <h3 className="category-title">{categoria.titulo}</h3>
              </div>

              <p className="category-description">{categoria.descripcion}</p>

              {stats && stats[categoria.id] && (
                <div className="category-stats">
                  <div className="category-stat-item">
                    <div className="category-stat-label">Disponibles</div>
                    <div className="category-stat-value category-stat-value-success">
                      {stats[categoria.id].disponibles}
                    </div>
                  </div>
                  <div className="category-stat-item">
                    <div className="category-stat-label">Total</div>
                    <div className="category-stat-value">
                      {stats[categoria.id].total}
                    </div>
                  </div>
                </div>
              )}

              <button className="btn btn-primary category-button">
                Ver Recursos →
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;