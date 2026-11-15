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
        </article>
      ))}
    </section>
  );
}
