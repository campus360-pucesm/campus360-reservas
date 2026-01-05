export default function CredentialCard({ user, qrImageUrl }) {
    if (!user) return null;

    return (
        <div className="credential-card">
            <div className="credential-header">
                <h3>CAMPUS360</h3>
                <p>CREDENCIAL DIGITAL</p>
            </div>

            <div className="credential-body">
                <div style={{ flexShrink: 0 }}>
                    <div
                        style={{
                            background: "white",
                            borderRadius: "10px",
                            padding: "8px",
                            boxShadow: "0 4px 10px rgba(0,0,0,0.18)",
                            width: "140px",
                            height: "140px",
                        }}
                    >
                        {qrImageUrl ? (
                            <img
                                src={qrImageUrl}
                                alt="QR credencial"
                                style={{ width: "100%", height: "100%", objectFit: "contain" }}
                            />
                        ) : (
                            <div
                                style={{
                                    width: "100%",
                                    height: "100%",
                                    display: "flex",
                                    justifyContent: "center",
                                    alignItems: "center",
                                    fontSize: "12px",
                                    color: "#9ca3af",
                                    textAlign: "center",
                                }}
                            >
                                Sin QR generado
                            </div>
                        )}
                    </div>
                </div>

                <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "10px" }}>
                    <div className="info-row">
                        <label>Nombre</label>
                        <span>{user.full_name}</span>
                    </div>
                    <div className="info-row">
                        <label>Email</label>
                        <span>{user.email}</span>
                    </div>
                    <div className="info-row">
                        <label>Rol</label>
                        <span
                            style={{
                                display: "inline-block",
                                background: "rgba(255,255,255,0.2)",
                                padding: "4px 10px",
                                borderRadius: "999px",
                                fontSize: "11px",
                                textTransform: "uppercase",
                                letterSpacing: "1px",
                            }}
                        >
                            {user.role}
                        </span>
                    </div>
                    <div className="info-row">
                        <label>ID</label>
                        <span style={{ fontFamily: "monospace", fontSize: "11px" }}>
                            {user.id}
                        </span>
                    </div>
                </div>
            </div>

            <div className="credential-footer">
                <small>Válido para identificación en todo el campus</small>
            </div>
        </div>
    );
}
