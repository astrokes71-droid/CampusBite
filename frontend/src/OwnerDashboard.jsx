import { useEffect, useState } from "react";
import api from "./api";

export default function OwnerDashboard({ onLogout }) {
  const [restaurants, setRestaurants] = useState([]);
  const [selected, setSelected] = useState(null);
  const [orders, setOrders] = useState([]);
  const [partners, setPartners] = useState([]);
  const [menu, setMenu] = useState([]);
  const [message, setMessage] = useState("");

  async function loadRestaurants() {
    try {
      const response = await api.get("/owner/restaurants");
      setRestaurants(response.data);
      if (response.data.length) {
        setSelected(response.data[0].id);
      }
    } catch (error) {
      setMessage(error.response?.data?.detail || error.message);
    }
  }

  async function refresh(restaurantId) {
    if (!restaurantId) return;

    try {
      const [ordersResponse, partnersResponse, menuResponse] =
        await Promise.all([
          api.get(`/owner/restaurants/${restaurantId}/orders`),
          api.get("/owner/delivery-partners"),
          api.get("/menu/"),
        ]);

      setOrders(ordersResponse.data);
      setPartners(partnersResponse.data);
      setMenu(menuResponse.data.filter(
        item => item.restaurant_id === restaurantId
      ));
    } catch (error) {
      setMessage(error.response?.data?.detail || error.message);
    }
  }

  useEffect(() => {
    loadRestaurants();
  }, []);

  useEffect(() => {
    if (selected) refresh(selected);
  }, [selected]);

  async function updateStatus(orderId, status) {
    try {
      await api.patch(`/owner/orders/${orderId}/status`, { status });
      setMessage(`Order #${orderId} updated to ${status}`);
      await refresh(selected);
    } catch (error) {
      setMessage(error.response?.data?.detail || error.message);
    }
  }

  async function assignPartner(orderId, partnerId) {
    if (!partnerId) return;

    try {
      await api.patch(`/owner/orders/${orderId}/assign`, {
        delivery_partner_id: Number(partnerId),
      });
      setMessage(`Delivery partner assigned to order #${orderId}`);
      await refresh(selected);
    } catch (error) {
      setMessage(error.response?.data?.detail || error.message);
    }
  }

  async function changeAvailability(item) {
    try {
      await api.patch(`/owner/menu/${item.id}/availability`, {
        available: !item.available,
      });
      await refresh(selected);
    } catch (error) {
      setMessage(error.response?.data?.detail || error.message);
    }
  }

  const nextStatus = {
    PLACED: "ACCEPTED",
    ACCEPTED: "PREPARING",
    PREPARING: "READY",
  };

  return (
    <main style={{ padding: 24, maxWidth: 1100, margin: "auto" }}>
      <h1>🍽️ CampusBite — Restaurant Owner</h1>
      <button onClick={onLogout}>Logout</button>

      <p role="status">{message}</p>

      <h2>My Restaurants</h2>

      <select
        value={selected || ""}
        onChange={event => setSelected(Number(event.target.value))}
      >
        {restaurants.map(restaurant => (
          <option key={restaurant.id} value={restaurant.id}>
            {restaurant.name}
          </option>
        ))}
      </select>

      <button onClick={() => refresh(selected)}>Refresh</button>

      <h2>Incoming Orders ({orders.length})</h2>

      {orders.length === 0 && <p>No orders available.</p>}

      {orders.map(order => (
        <article key={order.order_id} style={{
          background: "#fff",
          color: "#222",
          padding: 18,
          borderRadius: 12,
          marginBottom: 14,
        }}>
          <h3>Order #{order.order_id}</h3>
          <p>Status: {order.status}</p>
          <p>Total: ₹{order.total_amount}</p>

          {nextStatus[order.status] && (
            <button onClick={() =>
              updateStatus(order.order_id, nextStatus[order.status])
            }>
              Mark {nextStatus[order.status]}
            </button>
          )}

          {order.status === "READY" && (
            <select
              defaultValue=""
              onChange={event =>
                assignPartner(order.order_id, event.target.value)
              }
            >
              <option value="">Assign Delivery Partner</option>
              {partners.map(partner => (
                <option key={partner.id} value={partner.id}>
                  {partner.name}
                </option>
              ))}
            </select>
          )}
        </article>
      ))}

      <h2>Menu Availability</h2>

      {menu.map(item => (
        <div key={item.id} style={{
          background: "#fff",
          color: "#222",
          padding: 12,
          marginBottom: 8,
          borderRadius: 8,
        }}>
          <strong>{item.name}</strong> — ₹{item.price}
          <button
            style={{ marginLeft: 12 }}
            onClick={() => changeAvailability(item)}
          >
            {item.available ? "Mark Unavailable" : "Mark Available"}
          </button>
        </div>
      ))}
    </main>
  );
}
