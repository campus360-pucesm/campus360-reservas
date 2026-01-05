import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "../pages/Dashboard";
import RecursosPorTipo from "../pages/RecursosPorTipo";
import CrearReserva from "../pages/CrearReserva";
import MisReservas from "../pages/MisReservas";
import CheckInQR from "../pages/CheckInQR";

export default function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="/dashboard" element={<Dashboard />} />

        {/* Listado por tipo */}
        <Route path="/recursos/:tipo" element={<RecursosPorTipo />} />

        {/* Crear reserva: recibe recurso_id por query */}
        <Route path="/reservar" element={<CrearReserva />} />

        {/* Mis reservas */}
        <Route path="/mis-reservas" element={<MisReservas />} />

        {/* Check-in QR */}
        <Route path="/checkin" element={<CheckInQR />} />

        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  );
}
