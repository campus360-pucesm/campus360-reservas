import "../styles/style.css";

export default function AccessHistory({ history }) {
    if (!history || history.length === 0) {
        return (
            <div className="info-card">
                <p style={{ color: "#6b7280" }}>No hay accesos registrados</p>
            </div>
        );
    }

    return (
        <div className="info-card">
            <h3>Historial de Accesos</h3>

            <div style={{ marginTop: "20px" }}>
                {history.map((item) => (
                    <div
                        key={item.id}
                        className="history-item"
                        style={{
                            padding: "12px",
                            background: "var(--light)",
                            borderRadius: "8px",
                            marginBottom: "8px",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                        }}
                    >
                        <strong style={{ color: "var(--primary)" }}>
                            {item.location_code}
                        </strong>
                        <small style={{ color: "#6b7280" }}>
                            {new Date(item.timestamp).toLocaleString("es-ES")}
                        </small>
                    </div>
                ))}
            </div>
        </div>
    );
}
