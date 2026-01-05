import { createContext, useContext, useMemo, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // En tu auth, guarda estos datos en localStorage al login
  const [user] = useState(() => {
    const raw = localStorage.getItem("campus360_user");
    return raw ? JSON.parse(raw) : null;
  });

  const value = useMemo(() => ({
    user,
    isLogged: Boolean(user),
  }), [user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
