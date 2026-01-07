import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

export default function AppLayout() {
  return (
    <div style={{ padding: "20px", maxWidth: "1400px", margin: "0 auto" }}>
      <Navbar />
      <Outlet />
    </div>
  );
}