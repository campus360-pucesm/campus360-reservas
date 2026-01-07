import { useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
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
    case "admin":
      return "Administrador";
    case "teacher":
      return "Profesor";
    case "student":
      return "Estudiante";
    default:
      return role || "Usuario";
  }
};

const getRoleBadgeColor = (role) => {
  switch (role) {
    case "admin":
      return "#dc2626";
    case "teacher":
      return "#2563eb";
    case "student":
      return "#16a34a";
    default:
      return "#6b7280";
  }
};

const NavButton = ({ active, onClick, children }) => (
  <button onClick={onClick} className={`nav-button ${active ? "active" : ""}`}>
    {children}
  </button>
);

export default function Navbar() {
  const nav = useNavigate();
  const { pathname } = useLocation();

  const user = useMemo(() => getUser(), []);

  const goAuth = () => (window.location.href = `${AUTH_APP_URL}/dashboard`);

  const logout = () => {
    clearSession();
    window.location.href = `${AUTH_APP_URL}/`;
  };

  return (
    <div className="navbar-container">
      {/* LEFT: title + user */}
      <div className="navbar-left">
        <div className="navbar-title">CAMPUS360 — Reservas</div>

        <div className="navbar-user-info">
          <span className="navbar-user-name">
            {user?.full_name || "Usuario"}
          </span>

          <span className="navbar-user-email">{user?.email || ""}</span>

          <span
            className="navbar-role-badge"
            style={{ background: getRoleBadgeColor(user?.role) }}
          >
            {getRoleLabel(user?.role)}
          </span>
        </div>
      </div>

      {/* RIGHT: nav actions */}
      <div className="navbar-right">
        <NavButton
          active={pathname === "/dashboard"}
          onClick={() => nav("/dashboard")}
        >
          🧭 Dashboard
        </NavButton>

        <NavButton
          active={pathname.startsWith("/mis-reservas")}
          onClick={() => nav("/mis-reservas")}
        >
          📌 Mis reservas
        </NavButton>

        <NavButton
          active={pathname.startsWith("/checkin")}
          onClick={() => nav("/checkin")}
        >
          ✅ Check-in (QR)
        </NavButton>

        <button onClick={goAuth} className="nav-button-auth">
          🔁 Volver a Auth
        </button>

        <button onClick={logout} className="nav-button-logout">
          Cerrar sesión
        </button>
      </div>
    </div>
  );
}