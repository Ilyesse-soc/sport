"use client";

import { useState } from "react";

type AuthState = {
  token: string;
  userId: string;
};

const EMPTY_STATE: AuthState = { token: "", userId: "" };

export function useAuth() {
  const [state, setState] = useState<AuthState>(() => {
    if (typeof window === "undefined") {
      return EMPTY_STATE;
    }
    return {
      token: window.localStorage.getItem("sport_token") || "",
      userId: window.localStorage.getItem("sport_user_id") || "",
    };
  });

  const saveAuth = (token: string, userId: string) => {
    window.localStorage.setItem("sport_token", token);
    window.localStorage.setItem("sport_user_id", userId);
    setState({ token, userId });
  };

  const logout = () => {
    window.localStorage.removeItem("sport_token");
    window.localStorage.removeItem("sport_user_id");
    setState(EMPTY_STATE);
  };

  return { ...state, saveAuth, logout, isLoggedIn: !!state.token };
}
