import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "../App";
import Dashboard from "../pages/Dashboard";

export default function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}
