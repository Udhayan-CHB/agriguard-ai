"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { login as apiLogin, signup as apiSignup } from "@/lib/api";
import Cookies from "js-cookie";

interface User {
  username: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  signup: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // On mount, read from cookies
    const storedToken = Cookies.get("token");
    const storedUser = Cookies.get("user");
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    const res = await apiLogin(username, password);
    const { access_token, role } = res.data;
    const userData = { username, role };
    Cookies.set("token", access_token, { expires: 1 });
    Cookies.set("user", JSON.stringify(userData), { expires: 1 });
    setToken(access_token);
    setUser(userData);
    router.push("/chat");
  };

  const signup = async (username: string, password: string) => {
    const res = await apiSignup(username, password);
    const { access_token, role } = res.data;
    const userData = { username, role };
    Cookies.set("token", access_token, { expires: 1 });
    Cookies.set("user", JSON.stringify(userData), { expires: 1 });
    setToken(access_token);
    setUser(userData);
    router.push("/chat");
  };

  const logout = () => {
    Cookies.remove("token");
    Cookies.remove("user");
    setToken(null);
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, token, login, signup, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
};