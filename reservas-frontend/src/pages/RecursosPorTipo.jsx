import { useParams, useNavigate } from "react-router-dom";

export default function RecursosPorTipo() {
  const { tipo } = useParams();
  const navigate = useNavigate();

  return (
    <div>
      <h1>Recursos: {tipo}</h1>
      <p>Listado de recursos disponibles por tipo</p>

      <button onClick={() => navigate("/dashboard")}>
        Volver al dashboard
      </button>
    </div>
  );
}
