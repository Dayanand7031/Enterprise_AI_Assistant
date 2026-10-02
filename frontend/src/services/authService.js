import api from "./api";

export const login = async (email, password) => {
  const response = await api.post("/api/auth/login", {
    email,
    password,
  });

  const { access_token, refresh_token } = response.data;

  localStorage.setItem("access_token", access_token);

  if (refresh_token) {
    localStorage.setItem("refresh_token", refresh_token);
  }

  return response.data;
};

export const logout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
};

export const isAuthenticated = () => {
  return Boolean(localStorage.getItem("access_token"));
};


export const signup = async (
  name,
  email,
  password
) => {
  const response = await api.post(
    "/api/auth/register",
    {
      name,
      email,
      password,
    }
  );

  return response.data;
};
