import { useState } from "react";
import api from "./api";

export default function Auth({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage("");
    setLoading(true);

    try {
      if (mode === "register") {
        await api.post("/auth/register", {
          name,
          email,
          password
        });

        setMessage("Registration successful! Please login.");
        setMode("login");
      } else {
        const response = await api.post("/auth/login", {
          email,
          password
        });

        onLogin(response.data.access_token);
      }
    } catch (error) {
      setMessage(
        error.response?.data?.detail
          ? JSON.stringify(error.response.data.detail)
          : "Authentication failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="auth-panel">
      <h2>
        {mode === "login" ? "Login to CampusBite" : "Create Account"}
      </h2>

      <form onSubmit={handleSubmit}>
        {mode === "register" && (
          <input
            type="text"
            placeholder="Full Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        )}

        <input
          type="email"
          placeholder="Email Address"
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

        <button type="submit" disabled={loading}>
          {loading
            ? "Please wait..."
            : mode === "login"
            ? "Login"
            : "Register"}
        </button>
      </form>

      <p>{message}</p>

      <button
        type="button"
        onClick={() => {
          setMode(mode === "login" ? "register" : "login");
          setMessage("");
        }}
      >
        {mode === "login"
          ? "New user? Register"
          : "Already registered? Login"}
      </button>
    </section>
  );
}
