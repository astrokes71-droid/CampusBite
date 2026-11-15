import { useEffect, useState } from "react";
import api from "./api";

export default function OwnerDashboard({ onLogout }) {
  const [restaurants, setRestaurants] = useState([]);
  const [selected, setSelected] = useState(null);
  const [orders, setOrders] = useState([]);
  const [partners, setPartners] = useState([]);
  const [menu, setMenu] = useState([]);
  const [message, setMessage] = useState("");
  const [reminders, setReminders] = useState([]);
  const [refunds, setRefunds] = useState([]);

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


  async function loadRefunds() {
    try {
      const response = await api.get("/refunds/owner/pending");
      setRefunds(response.data);
    } catch (error) {
      setMessage(error.response?.data?.detail || error.message);
    }
  }

  async function decideRefund(refundId, approved) {
    if (!window.confirm(
      `${approved ? "Approve" : "Reject"} refund #${refundId}?`
    )) return;

    try {
      await api.patch(`/refunds/owner/${refundId}/decision`, {
        approved
      });

      setMessage(
        `Refund #${refundId} ${approved ? "approved" : "rejected"}`
      );

      await loadRefunds();
      await refresh(selected);
    } catch (error) {
      setMessage(error.response?.data?.detail || error.message);
    }
  }


  async function loadReminders() {
    try {
      const response = await api.get("/owner/reminders");
      setReminders(response.data);
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
      await loadReminders();
      await loadRefunds();
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


  async function createDish() {
    if (!selected) return;

    const name = window.prompt("Enter new dish name:");
    if (name === null) return;

    const priceText = window.prompt("Enter price in rupees:");
    if (priceText === null) return;

    const price = Number(priceText);

    if (name.trim().length < 2 ||
        !Number.isFinite(price) || price <= 0) {
      setMessage("Enter a valid dish name and positive price.");
      return;
    }

    try {
      await api.post(`/owner/restaurants/${selected}/menu`, {
        name: name.trim(),
        price,
        available: true
      });

      setMessage(`Dish "${name.trim()}" created successfully`);
      await refresh(selected);
    } catch (error) {
      setMessage(error.response?.data?.detail || error.message);
    }
  }

  async function editDish(item) {
    const name = window.prompt("Edit dish name:", item.name);
    if (name === null) return;

    const priceText = window.prompt("Edit price:", String(item.price));
    if (priceText === null) return;

    const price = Number(priceText);

    if (name.trim().length < 2 ||
        !Number.isFinite(price) || price <= 0) {
      setMessage("Enter a valid dish name and positive price.");
      return;
    }

    try {
      await api.patch(`/owner/menu/${item.id}`, {
        name: name.trim(),
        price
      });

      setMessage(`Dish #${item.id} updated successfully`);
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


      <h2>Delayed Order Reminders ({reminders.length})</h2>

      {reminders.length === 0 && (
        <p>No delayed orders currently require attention.</p>
      )}

      {reminders.map(reminder => (
        <article key={reminder.reminder_id} style={{
          background: "#fff3cd",
          color: "#5c4200",
          padding: 14,
          borderRadius: 10,
          marginBottom: 10
        }}>
          <strong>Order #{reminder.order_id}</strong>
          <p>{reminder.message}</p>
          <small>Status: {reminder.status}</small>
        </article>
      ))}

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


      <h2>Pending Refund Requests ({refunds.length})</h2>

      {refunds.length === 0 && <p>No pending refunds.</p>}

      {refunds.map(refund => (
        <article key={refund.refund_id} style={{
          background: "#fff",
          color: "#222",
          padding: 16,
          borderRadius: 10,
          marginBottom: 12
        }}>
          <strong>Order #{refund.order_id}</strong>
          <p>Refund amount: ₹{refund.amount}</p>

          <button onClick={() =>
            decideRefund(refund.refund_id, true)
          }>
            Approve Refund
          </button>

          <button
            style={{ marginLeft: 8 }}
            onClick={() =>
              decideRefund(refund.refund_id, false)
            }
          >
            Reject Refund
          </button>
        </article>
      ))}

      <h2>Menu Availability</h2>
      <button
        type="button"
        onClick={createDish}
        style={{ marginBottom: 16 }}
      >
        + Create New Dish
      </button>


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
          <button
            type="button"
            style={{ marginLeft: 8 }}
            onClick={() => editDish(item)}
          >
            Edit Dish
          </button>
        </div>
      ))}
    </main>
  );
}
