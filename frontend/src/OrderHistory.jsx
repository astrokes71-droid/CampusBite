import { useEffect, useState } from "react";

export default function OrderHistory({ authToken, onClose }) {
  const [orders, setOrders] = useState([]);
  const [menuNames, setMenuNames] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadOrders() {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/orders/history",
          {
            headers: {
              Authorization: `Bearer ${authToken}`
            },
            signal: controller.signal
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (!Array.isArray(data)) {
          throw new Error("Invalid response");
        }

        setOrders(data);

        try {
          const menuResponse = await fetch(
            "http://127.0.0.1:8000/menu/",
            { signal: controller.signal }
          );

          if (menuResponse.ok) {
            const menu = await menuResponse.json();

            if (Array.isArray(menu)) {
              const names = {};

              menu.forEach(food => {
                names[food.id] = food.name;
              });

              setMenuNames(names);
            }
          }
        } catch (menuError) {
          if (menuError.name === "AbortError") {
            throw menuError;
          }
          console.error("Menu names unavailable:", menuError);
        }
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    loadOrders();

    return () => controller.abort();
  }, [authToken]);


  const [busyOrder, setBusyOrder] = useState(null);
  const [notice, setNotice] = useState("");

  async function orderAction(order, action) {
    const orderId = order.order_id;
    let url = "";
    let method = "POST";
    let body;

    if (action === "cancel") {
      if (!window.confirm(`Cancel order #${orderId}?`)) return;
      url = `/orders/${orderId}/cancel`;
      method = "PATCH";
    } else if (action === "review") {
      const rating = Number(window.prompt("Rate your order from 1 to 5:"));
      if (!Number.isInteger(rating) || rating < 1 || rating > 5) {
        setNotice("Please enter a rating between 1 and 5.");
        return;
      }
      const comment = window.prompt("Review comment (optional):") || "";
      url = `/orders/${orderId}/review`;
      body = { rating, comment };
    } else if (action === "refund") {
      const reason = window.prompt("Why are you requesting a refund?");
      if (reason === null) return;
      if (reason.trim().length < 5) {
        setNotice("Please enter at least 5 characters.");
        return;
      }
      url = `/refunds/orders/${orderId}/request`;
      body = { reason: reason.trim() };
    }

    setBusyOrder(orderId);
    setNotice("");

    try {
      const response = await fetch(`http://127.0.0.1:8000${url}`, {
        method,
        headers: {
          Authorization: `Bearer ${authToken}`,
          ...(body ? { "Content-Type": "application/json" } : {})
        },
        ...(body ? { body: JSON.stringify(body) } : {})
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(typeof data.detail === "string"
          ? data.detail : `Request failed (${response.status})`);
      }

      setNotice(`Order #${orderId}: ${action} successful.`);

      const updated = await fetch("http://127.0.0.1:8000/orders/history", {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      if (updated.ok) setOrders(await updated.json());
    } catch (error) {
      setNotice(error.message);
    } finally {
      setBusyOrder(null);
    }
  }

  return (
    <section style={{
      padding: "24px",
      maxWidth: "900px",
      margin: "20px auto"
    }}>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center"
      }}>
        <h2>My Order History</h2>
        <button onClick={onClose}>Close</button>
      </div>

      {notice && <p role="status">{notice}</p>}
      {loading && <p>Loading your orders...</p>}
      {error && <p role="alert">Error: {error}</p>}

      {!loading && !error && orders.length === 0 && (
        <p>You haven't placed any orders yet.</p>
      )}

      {!loading && !error && orders.map(order => (
        <article
          key={order.order_id}
          style={{
            background: "white",
            color: "#222",
            padding: "20px",
            marginTop: "16px",
            borderRadius: "12px",
            boxShadow: "0 2px 10px #00000015"
          }}
        >
          <h3>Order #{order.order_id}</h3>
          <p>
            Date: {new Date(order.created_at).toLocaleString()}
          </p>
          <p>Status: {order.status}</p>
          <p><strong>Total: ₹{Number(order.total_amount).toFixed(2)}</strong></p>

          <h4>Ordered Items</h4>
          <ul>
            {(order.items || []).map((item, index) => (
              <li key={index}>
                {menuNames[item.menu_item_id] || `Item #${item.menu_item_id}`} —
                Quantity: {item.quantity} —
                ₹{Number(item.unit_price).toFixed(2)} each
              </li>
            ))}
          </ul>

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {order.status === "PLACED" && (
              <button disabled={busyOrder === order.order_id}
                onClick={() => orderAction(order, "cancel")}>
                Cancel Order
              </button>
            )}
            {order.status === "DELIVERED" && (
              <>
                <button disabled={busyOrder === order.order_id}
                  onClick={() => orderAction(order, "review")}>
                  Write Review
                </button>
                <button disabled={busyOrder === order.order_id}
                  onClick={() => orderAction(order, "refund")}>
                  Request Refund
                </button>
              </>
            )}
          </div>
        </article>
      ))}
    </section>
  );
}
