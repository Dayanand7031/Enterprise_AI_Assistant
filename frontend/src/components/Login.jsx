import { useState } from "react";
import { login } from "../services/authService";

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const data = await login(email, password);

      onLogin(data);
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
        "Login failed. Please check your credentials."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">

        <h1>Enterprise AI Assistant</h1>

        <p>Sign in to continue</p>

        {error && (
          <div className="login-error">
            {error}
          </div>
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button
          type="submit"
          disabled={loading}
        >
          {loading ? "Signing in..." : "Login"}
        </button>

        <div className="auth-switch">
            Don't have an account?

            <button
                type="button"
                className="link-button"
                onClick={() => {
                window.location.href = "/signup";
                }}
            >
                Create Account
            </button>
            </div>

      </form>
    </div>
  );
}

export default Login;