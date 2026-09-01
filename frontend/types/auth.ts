// Mirrors backend/app/api/schemas.py (UserResponse, TokenResponse) exactly —
// keep these in sync if the backend shape changes.

export type AuthProvider = "manual" | "google";

export interface User {
  id: string;
  name: string;
  email: string;
  auth_provider: AuthProvider;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface SignupPayload {
  name: string;
  email: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface GoogleLoginPayload {
  id_token: string;
}
