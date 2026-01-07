import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { realizarCheckin } from "../api/checkin.api";

const CheckInQR = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const reservaFromState = location.state?.reserva;

  const [codigoManual, setCodigoManual] = useState("");
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCheckin = async (codigo) => {
    setLoading(true);
    setError(null);
    try {
      const response = await realizarCheckin(codigo);
      setResultado(response.data);
    } catch (err) {
      setError(err.response?.data?.message || "Código inválido o expirado");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!codigoManual.trim()) {
      setError("Por favor ingresa un código");
      return;
    }
    handleCheckin(codigoManual);
  };

  return (
    <div style={{ padding: "20px", maxWidth: "800px", margin: "0 auto" }}>
      <button
        onClick={() => navigate("/mis-reservas")}
        className="btn btn-secondary"
        style={{ width: "auto", padding: "10px 20px", marginBottom: "24px" }}
      >
        ← Volver a Mis Reservas
      </button>

      <div className="admin-card" style={{ marginBottom: "24px", textAlign: "center" }}>
        <div style={{ fontSize: "4rem", marginBottom: "16px" }}>📱</div>
        <h1 style={{ fontSize: "2rem", fontWeight: "700", marginBottom: "8px" }}>
          Check-in
        </h1>
        <p style={{ color: "var(--text-light)" }}>
          Escanea el código QR de tu reserva o ingresa el código manualmente
        </p>
      </div>

      {/* Si viene de una reserva específica */}
      {reservaFromState && !resultado && (
        <div className="admin-card" style={{ marginBottom: "24px" }}>
          <h2 className="dashboard-section-title">Tu código QR</h2>
          
          <div style={{ background: "#fff", padding: "32px", borderRadius: "var(--radius)", textAlign: "center", marginBottom: "16px" }}>
            {/* Aquí iría el QR real con una librería como qrcode.react */}
            <div
              style={{
                width: "200px",
                height: "200px",
                margin: "0 auto",
                background: "#f0f0f0",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                borderRadius: "8px"
              }}
            >
              <span style={{ color: "#666" }}>QR Code</span>
            </div>
          </div>

          <div style={{ textAlign: "center", marginBottom: "16px" }}>
            <div style={{ fontSize: "0.75rem", color: "var(--text-light)", marginBottom: "4px" }}>
              CÓDIGO DE RESERVA
            </div>
            <div style={{ fontSize: "1.5rem", fontWeight: "700", fontFamily: "monospace" }}>
              {reservaFromState.codigo}
            </div>
          </div>

          <div style={{ background: "var(--bg)", padding: "16px", borderRadius: "var(--radius)" }}>
            <p style={{ fontSize: "0.875rem", color: "var(--text-light)", margin: 0 }}>
              📌 Presenta este código en el punto de check-in o escanéalo con el lector QR
            </p>
          </div>
        </div>
      )}

      {/* Formulario de check-in manual */}
      {!resultado && (
        <div className="admin-card">
          <h2 className="dashboard-section-title">Ingresar código manualmente</h2>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Código de reserva</label>
              <input
                type="text"
                value={codigoManual}
                onChange={(e) => setCodigoManual(e.target.value.toUpperCase())}
                placeholder="Ej: RES-ABC123"
                style={{ textAlign: "center", fontFamily: "monospace", fontSize: "1.125rem" }}
              />
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? "Verificando..." : "Realizar Check-in"}
            </button>
          </form>
        </div>
      )}

      {/* Resultado del check-in */}
      {resultado && (
        <div className="admin-card" style={{ textAlign: "center" }}>
          <div
            style={{
              width: "80px",
              height: "80px",
              margin: "0 auto 16px",
              background: "var(--success)",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "2.5rem"
            }}
          >
            ✓
          </div>

          <h2 style={{ fontSize: "1.5rem", fontWeight: "700", marginBottom: "8px" }}>
            ¡Check-in Exitoso!
          </h2>
          <p style={{ color: "var(--text-light)", marginBottom: "24px" }}>
            Tu reserva ha sido confirmada
          </p>

          <div style={{ background: "var(--bg)", padding: "16px", borderRadius: "var(--radius)", marginBottom: "24px", textAlign: "left" }}>
            <div style={{ marginBottom: "12px" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-light)", marginBottom: "4px" }}>
                Recurso
              </div>
              <div style={{ fontWeight: "600" }}>
                {resultado.recurso || "Recurso"}
              </div>
            </div>
            <div style={{ marginBottom: "12px" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-light)", marginBottom: "4px" }}>
                Código
              </div>
              <div style={{ fontWeight: "600", fontFamily: "monospace" }}>
                {resultado.codigo || codigoManual}
              </div>
            </div>
            <div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-light)", marginBottom: "4px" }}>
                Hora de entrada
              </div>
              <div style={{ fontWeight: "600" }}>
                {new Date().toLocaleTimeString("es-ES", {
                  hour: "2-digit",
                  minute: "2-digit"
                })}
              </div>
            </div>
          </div>

          <div className="alert alert-success" style={{ marginBottom: "16px" }}>
            ✨ Disfruta de tu reserva. Recuerda respetar el horario establecido.
          </div>

          <div style={{ display: "flex", gap: "12px" }}>
            <button
              onClick={() => {
                setResultado(null);
                setCodigoManual("");
              }}
              className="btn btn-secondary"
              style={{ flex: 1 }}
            >
              Nuevo Check-in
            </button>
            <button
              onClick={() => navigate("/mis-reservas")}
              className="btn btn-primary"
              style={{ flex: 1 }}
            >
              Ver Reservas
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CheckInQR;