import { useEffect, useState } from "react";
import { getHealth, getReservas } from "./api/api";

function App() {
  const [health, setHealth] = useState(null);
  const [reservas, setReservas] = useState([]);

  useEffect(() => {
    getHealth().then(setHealth);
    getReservas().then(setReservas);
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>Campus360 - Reservas Frontend</h1>

      <h2>Estado del Backend:</h2>
      <pre>{JSON.stringify(health, null, 2)}</pre>

      <h2>Reservas:</h2>
      <pre>{JSON.stringify(reservas, null, 2)}</pre>
    </div>
  );
}

export default App;
