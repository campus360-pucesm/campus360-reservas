import { useNavigate } from "react-router-dom";
import AppLayout from "../components/AppLayout";

const tiles = [
  { key:"sala_estudio", label:"Salas de estudio", desc:"Capacidad 10" },
  { key:"laboratorio", label:"Laboratorios", desc:"Capacidad 20" },
  { key:"equipo", label:"Equipos", desc:"Préstamos" },
  { key:"parqueadero", label:"Parqueaderos", desc:"1 vehículo" },
  { key:"modulo_biblioteca", label:"Cubículos biblioteca", desc:"Capacidad 4" },
];

export default function Dashboard() {
  const nav = useNavigate();

  return (
    <AppLayout
      title="Dashboard de espacios"
      subtitle="Selecciona un tipo de recurso para ver disponibilidad y reservar."
      right={
        <button
          onClick={() => nav("/checkin")}
          style={{
            background:"var(--primary)",
            color:"#fff",
            border:"none",
            borderRadius: 12,
            padding:"10px 14px",
            cursor:"pointer",
            fontWeight:700
          }}
        >
          Check-in (QR)
        </button>
      }
    >
      <div style={{ display:"grid", gridTemplateColumns:"repeat(3, 1fr)", gap: 14 }}>
        {tiles.map(t => (
          <div
            key={t.key}
            onClick={() => nav(`/recursos/${t.key}`)}
            style={{
              border:"1px solid var(--border)",
              borderRadius: 16,
              padding: 16,
              cursor:"pointer",
              background:"#fff",
              boxShadow:"0 6px 16px rgba(17,24,39,.06)"
            }}
          >
            <div style={{ fontWeight:800, fontSize:16 }}>{t.label}</div>
            <div style={{ color:"var(--muted)", marginTop: 6 }}>{t.desc}</div>
            <div style={{ marginTop: 12, color:"var(--primary)", fontWeight:700 }}>
              Ver disponibilidad →
            </div>
          </div>
        ))}
      </div>
    </AppLayout>
  );
}
