import { useState } from "react";
import api from "./api";

const suggestions = [
  "Summarize my last five orders",
  "Which orders are still not delivered?",
  "How much did I spend this week?",
  "Which food items have I ordered most frequently?"
];

export default function AIInsights() {
  const [question, setQuestion] = useState(suggestions[0]);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function askAI(event) {
    event.preventDefault();
    if (loading || question.trim().length < 5) return;

    setLoading(true);
    setError("");
    setAnswer("");

    try {
      const response = await api.post("/ai/order-insights", {
        question: question.trim()
      });
      setAnswer(response.data.answer);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Unable to generate insights right now."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section style={{
      background: "#fff",
      color: "#222",
      padding: 24,
      borderRadius: 14,
      margin: "24px auto",
      maxWidth: 900
    }}>
      <h2>🤖 AI Order Insights</h2>
      <p>Ask questions about your previous CampusBite orders.</p>

      <form onSubmit={askAI}>
        <select
          value={suggestions.includes(question) ? question : ""}
          onChange={event => setQuestion(event.target.value)}
          style={{ padding: 10, maxWidth: "100%", marginBottom: 12 }}
        >
          {!suggestions.includes(question) && (
            <option value="">Custom question</option>
          )}
          {suggestions.map(item => (
            <option key={item} value={item}>{item}</option>
          ))}
        </select>

        <textarea
          value={question}
          onChange={event => setQuestion(event.target.value)}
          rows={3}
          maxLength={500}
          style={{
            display: "block",
            width: "100%",
            boxSizing: "border-box",
            padding: 12,
            marginBottom: 12
          }}
        />

        <button type="submit" disabled={loading || question.trim().length < 5}>
          {loading ? "Generating..." : "Generate AI Insight"}
        </button>
      </form>

      {error && <p role="alert" style={{ color: "#b42318" }}>{error}</p>}

      {answer && (
        <div style={{
          background: "#f4f7fb",
          padding: 16,
          borderRadius: 10,
          marginTop: 16,
          whiteSpace: "pre-wrap"
        }}>
          {answer}
        </div>
      )}
    </section>
  );
}
