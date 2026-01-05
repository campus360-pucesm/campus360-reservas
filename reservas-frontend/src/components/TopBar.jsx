import { useNavigate } from "react-router-dom";

export default function TopBar() {
  const nav = useNavigate();

  // Mock user solo para UI
  const user = {
    full_name: "Usuario Demo",
    email: "demo@campus360.com",
  };

  return (
    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", gap: 12 }}>
      <div style={{ display:"flex", gap:10, alignItems:"center" }}>
        <div style={{
          width: 42, height: 42, borderRadius: 12,
          background: "linear-gradient(135deg, var(--primary), #7C3AED)",
          display:"grid", placeItems:"center", color:"#fff", fontWeight:800
        }}>C</div>
        <div>
          <div style={{ fontWeight:800, fontSize:18 }}>CAMPUS360</div>
          <div style={{ fontSize:12, color:"var(--muted)" }}>Reservas de recursos</div>
        </div>
      </div>

      <div style={{ display:"flex", alignItems:"center", gap:12 }}>
        <div style={{ textAlign:"right" }}>
          <div style={{ fontWeight:700 }}>{user.full_name}</div>
          <div style={{ fontSize:12, color:"var(--muted)" }}>{user.email}</div>
        </div>

        <button
          onClick={() => nav("/mis-reservas")}
          style={{
            border:"1px solid var(--border)",
            background:"#fff",
            borderRadius: 12,
            padding:"10px 14px",
            cursor:"pointer"
          }}
        >
          Mis reservas
        </button>
      </div>
    </div>
  );
}
