import TopBar from "./TopBar";

export default function AppLayout({ title, subtitle, children, right }) {
  return (
    <div style={{ minHeight: "100vh", padding: "40px 20px" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <TopBar />
        <div style={{
          background: "var(--card)",
          border: "1px solid var(--border)",
          borderRadius: 18,
          boxShadow: "var(--shadow)",
          padding: 24,
          marginTop: 18,
        }}>
          <div style={{ display:"flex", justifyContent:"space-between", gap: 16, alignItems:"center" }}>
            <div>
              <h2 style={{ margin:0, fontSize: 28 }}>{title}</h2>
              {subtitle && <p style={{ margin:"6px 0 0", color:"var(--muted)" }}>{subtitle}</p>}
            </div>
            {right}
          </div>

          <div style={{ marginTop: 18 }}>{children}</div>
        </div>
      </div>
    </div>
  );
}
