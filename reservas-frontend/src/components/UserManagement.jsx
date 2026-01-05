import { useEffect, useState } from "react";
import { api } from "../api/api";
import Button from "../components/Button";
import Alert from "../components/Alert";
import "../styles/style.css";

export default function UserManagement() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [alert, setAlert] = useState({ type: "", message: "" });
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [formData, setFormData] = useState({
        email: "",
        password: "",
        full_name: "",
        role: "student"
    });
    const [editingUser, setEditingUser] = useState(null);

    const showAlert = (type, message) => {
        setAlert({ type, message });
        setTimeout(() => setAlert({ type: "", message: "" }), 4000);
    };

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const res = await api("/admin/users");
            const data = await res.json();
            setUsers(data);
        } catch (err) {
            showAlert("error", "Error al cargar usuarios: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleCreateUser = async (e) => {
        e.preventDefault();
        try {
            await api("/admin/users", {
                method: "POST",
                body: JSON.stringify(formData)
            });
            showAlert("success", "Usuario creado exitosamente");
            setShowCreateForm(false);
            setFormData({ email: "", password: "", full_name: "", role: "student" });
            fetchUsers();
        } catch (err) {
            showAlert("error", "Error al crear usuario: " + err.message);
        }
    };

    const handleUpdateUser = async (e) => {
        e.preventDefault();
        try {
            const updateData = { ...formData };
            if (!updateData.password) {
                delete updateData.password; // No enviar password si está vacío
            }
            
            await api(`/admin/users/${editingUser.id}`, {
                method: "PUT",
                body: JSON.stringify(updateData)
            });
            showAlert("success", "Usuario actualizado exitosamente");
            setEditingUser(null);
            setFormData({ email: "", password: "", full_name: "", role: "student" });
            fetchUsers();
        } catch (err) {
            showAlert("error", "Error al actualizar usuario: " + err.message);
        }
    };

    const handleDeleteUser = async (userId, userName) => {
        if (!confirm(`¿Estás seguro de eliminar al usuario ${userName}?`)) {
            return;
        }
        
        try {
            await api(`/admin/users/${userId}`, {
                method: "DELETE"
            });
            showAlert("success", "Usuario eliminado exitosamente");
            fetchUsers();
        } catch (err) {
            showAlert("error", "Error al eliminar usuario: " + err.message);
        }
    };

    const startEdit = (user) => {
        setEditingUser(user);
        setFormData({
            email: user.email,
            password: "",
            full_name: user.full_name,
            role: user.role
        });
        setShowCreateForm(false);
    };

    const cancelEdit = () => {
        setEditingUser(null);
        setFormData({ email: "", password: "", full_name: "", role: "student" });
    };

    const getRoleBadgeColor = (role) => {
        switch (role) {
            case "admin": return "#dc2626";
            case "teacher": return "#2563eb";
            case "student": return "#16a34a";
            default: return "#6b7280";
        }
    };

    const getRoleLabel = (role) => {
        switch (role) {
            case "admin": return "Administrador";
            case "teacher": return "Profesor";
            case "student": return "Estudiante";
            default: return role;
        }
    };

    return (
        <div className="admin-card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
                <div>
                    <h3 style={{ marginBottom: "6px" }}>Gestión de Usuarios</h3>
                    <p style={{ color: "#6b7280", fontSize: "14px" }}>
                        Crear, editar y eliminar usuarios del sistema
                    </p>
                </div>
                <Button onClick={() => {
                    setShowCreateForm(!showCreateForm);
                    setEditingUser(null);
                    setFormData({ email: "", password: "", full_name: "", role: "student" });
                }}>
                    {showCreateForm ? "Cancelar" : "+ Crear Usuario"}
                </Button>
            </div>

            <Alert type={alert.type} message={alert.message} />

            {/* Create/Edit Form */}
            {(showCreateForm || editingUser) && (
                <div style={{ 
                    background: "#f9fafb", 
                    padding: "20px", 
                    borderRadius: "8px", 
                    marginBottom: "20px" 
                }}>
                    <h4 style={{ marginBottom: "16px" }}>
                        {editingUser ? "Editar Usuario" : "Crear Nuevo Usuario"}
                    </h4>
                    <form onSubmit={editingUser ? handleUpdateUser : handleCreateUser}>
                        <div className="form-group">
                            <label>Email *</label>
                            <input
                                type="email"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Nombre Completo *</label>
                            <input
                                type="text"
                                value={formData.full_name}
                                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Rol *</label>
                            <select
                                value={formData.role}
                                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                                required
                            >
                                <option value="student">Estudiante</option>
                                <option value="teacher">Profesor</option>
                                <option value="admin">Administrador</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>
                                Contraseña {editingUser && "(dejar vacío para no cambiar)"}
                                {!editingUser && " *"}
                            </label>
                            <input
                                type="password"
                                value={formData.password}
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                required={!editingUser}
                                minLength={6}
                            />
                        </div>

                        <div style={{ display: "flex", gap: "10px" }}>
                            <Button type="submit">
                                {editingUser ? "Actualizar" : "Crear"}
                            </Button>
                            <Button 
                                type="button" 
                                variant="secondary" 
                                onClick={editingUser ? cancelEdit : () => setShowCreateForm(false)}
                            >
                                Cancelar
                            </Button>
                        </div>
                    </form>
                </div>
            )}

            {/* Users Table */}
            {loading ? (
                <p style={{ textAlign: "center", color: "#6b7280" }}>Cargando usuarios...</p>
            ) : users.length === 0 ? (
                <p style={{ textAlign: "center", color: "#6b7280" }}>No hay usuarios registrados</p>
            ) : (
                <div style={{ overflowX: "auto" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                        <thead>
                            <tr style={{ borderBottom: "2px solid #e5e7eb" }}>
                                <th style={{ padding: "12px", textAlign: "left" }}>Nombre</th>
                                <th style={{ padding: "12px", textAlign: "left" }}>Email</th>
                                <th style={{ padding: "12px", textAlign: "left" }}>Rol</th>
                                <th style={{ padding: "12px", textAlign: "left" }}>Fecha Creación</th>
                                <th style={{ padding: "12px", textAlign: "center" }}>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map((user) => (
                                <tr key={user.id} style={{ borderBottom: "1px solid #e5e7eb" }}>
                                    <td style={{ padding: "12px" }}>{user.full_name}</td>
                                    <td style={{ padding: "12px" }}>{user.email}</td>
                                    <td style={{ padding: "12px" }}>
                                        <span style={{
                                            background: getRoleBadgeColor(user.role),
                                            color: "white",
                                            padding: "4px 12px",
                                            borderRadius: "12px",
                                            fontSize: "12px",
                                            fontWeight: "500"
                                        }}>
                                            {getRoleLabel(user.role)}
                                        </span>
                                    </td>
                                    <td style={{ padding: "12px", fontSize: "14px", color: "#6b7280" }}>
                                        {new Date(user.created_at).toLocaleDateString()}
                                    </td>
                                    <td style={{ padding: "12px", textAlign: "center" }}>
                                        <div style={{ display: "flex", gap: "8px", justifyContent: "center" }}>
                                            <button
                                                className="btn btn-secondary"
                                                style={{ padding: "6px 12px", fontSize: "14px" }}
                                                onClick={() => startEdit(user)}
                                            >
                                                Editar
                                            </button>
                                            <button
                                                className="btn btn-secondary"
                                                style={{ 
                                                    padding: "6px 12px", 
                                                    fontSize: "14px",
                                                    background: "#dc2626",
                                                    borderColor: "#dc2626"
                                                }}
                                                onClick={() => handleDeleteUser(user.id, user.full_name)}
                                            >
                                                Eliminar
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
