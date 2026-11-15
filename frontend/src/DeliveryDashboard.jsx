import { useEffect, useState } from "react";
import api from "./api";

export default function DeliveryDashboard({ onLogout }) {
  const [orders, setOrders] = useState([]);
  const [message, setMessage] = useState("");

  async function refresh() {
    try {
      const response = await api.get("/delivery/orders");
      setOrders(response.data);
    } catch (error) {
      setMessage(error.response?.data?.detail || error.message);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function updateStatus(orderId, status) {
    try {
      await api.patch(`/delivery/orders/${orderId}/status`, { status });
      setMessage(`Order #${orderId}: ${status}`);
      await refresh();
    } catch (error) {
      setMessage(error.response?.data?.detail || error.message);
    }
  }

  return (
    <main style={{ padding: 24, maxWidth: 1000, margin: "auto" }}>
      <h1 style={{ color: "#222" }}>🚴 CampusBite — Delivery Dashboard</h1>
      <button onClick={onLogout}>Logout</button>
      <button onClick={refresh}>Refresh Orders</button>

      <p role="status">{message}</p>

      <h2>My Assigned Orders</h2>

      {orders.length === 0 && <p>No assigned orders yet.</p>}

      <h2 style={{ color: "#222" }}>Active Orders</h2>
{orders.filter(order => !["DELIVERED", "REFUNDED"].includes(order.status)).map(order => (
        <article key={order.order_id} style={{
          background: "#fff",
          color: "#222",
          padding: 20,
          borderRadius: 12,
          marginBottom: 14,
        }}>
          <h3>Order #{order.order_id}</h3>
          <p>Status: {order.status}</p>
          <p>Total: ₹{order.total_amount}</p>

          {order.status === "ASSIGNED" && (
            <button onClick={() =>
              updateStatus(order.order_id, "OUT_FOR_DELIVERY")
            }>
              Mark Out for Delivery
            </button>
          )}

          {order.status === "OUT_FOR_DELIVERY" && (
            <button onClick={() =>
              updateStatus(order.order_id, "DELIVERED")
            }>
              Mark Delivered
            </button>
          )}
        </article>
      ))}
<h2 style={{ color: "#222", marginTop: 32 }}>Delivery History</h2>
{orders.filter(order => ["DELIVERED", "REFUNDED"].includes(order.status)).map(order => (
        <article key={order.order_id} style={{
          background: "#fff",
          color: "#222",
          padding: 20,
          borderRadius: 12,
          marginBottom: 14,
        }}>
          <h3>Order #{order.order_id}</h3>
          <p>Status: {order.status}</p>
          <p>Total: ₹{order.total_amount}</p>

          {order.status === "ASSIGNED" && (
            <button onClick={() =>
              updateStatus(order.order_id, "OUT_FOR_DELIVERY")
            }>
              Mark Out for Delivery
            </button>
          )}

          {order.status === "OUT_FOR_DELIVERY" && (
            <button onClick={() =>
              updateStatus(order.order_id, "DELIVERED")
            }>
              Mark Delivered
            </button>
          )}
        </article>
      ))}
    </main>
  );
}
