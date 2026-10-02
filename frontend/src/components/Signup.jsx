import { useState } from "react";
import { signup } from "../services/authService";

function Signup({ onSignup }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    // Password validation
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setLoading(true);

    try {
      const data = await signup(
        name,
        email,
        password
      );

      setSuccess(
        data.message ||
        "Account created successfully."
      );

      // Move to login after successful signup
      if (onSignup) {
        setTimeout(() => {
          onSignup();
        }, 1200);
      }

    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
        "Signup failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">

      <form
        onSubmit={handleSubmit}
        className="login-form"
      >

        <h1>Create Account</h1>

        <p>
          Create your Enterprise AI Assistant account
        </p>

        {error && (
          <div className="login-error">
            {error}
          </div>
        )}

        {success && (
          <div className="signup-success">
            {success}
          </div>
        )}

        {/* Name */}

        <input
          type="text"
          placeholder="Full Name"
          value={name}
          onChange={(e) =>
            setName(e.target.value)
          }
          required
        />

        {/* Email */}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
          required
        />

        {/* Password */}

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
          required
        />

        {/* Confirm Password */}

        <input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) =>
            setConfirmPassword(e.target.value)
          }
          required
        />

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Creating Account..."
            : "Create Account"}
        </button>

        <div className="auth-switch">
          Already have an account?

          <button
            type="button"
            className="link-button"
            onClick={() => {
              window.location.href = "/login";
            }}
          >
            Login
          </button>

        </div>

      </form>

    </div>
  );
}

export default Signup;