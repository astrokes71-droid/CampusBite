import OwnerDashboard from "./OwnerDashboard";
import DeliveryDashboard from "./DeliveryDashboard";
import OrderHistory from "./OrderHistory";
import Auth from "./Auth";
import foodImages from "./foodImages.json";
import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [authToken, setAuthToken] = useState(
    () => sessionStorage.getItem("campusbite_token")
  );
  const [userRole, setUserRole] = useState(
    () => sessionStorage.getItem("campusbite_role") || "customer"
  );
  const [showOrders, setShowOrders] = useState(false);
  const [showAuth, setShowAuth] = useState(false);

  const handleLogin = (token, role = 'customer') => {
    setUserRole(role);
    sessionStorage.setItem('campusbite_role', role);
    setAuthToken(token);
    sessionStorage.setItem("campusbite_token", token);
    setShowAuth(false);
  };

  const handleLogout = () => {
    setAuthToken(null);
    sessionStorage.removeItem("campusbite_token");
    sessionStorage.removeItem("campusbite_role");
    setUserRole("customer");
    setShowAuth(false);
  };

  const [menu, setMenu] = useState([]);
  const [search, setSearch] = useState("");
  const [cart, setCart] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_URL}/menu/`)
      .then((response) => {
        if (!response.ok) throw new Error("Unable to load menu");
        return response.json();
      })
      .then((data) => setMenu(data))
      .catch(() => setError("Could not connect to CampusBite backend"))
      .finally(() => setLoading(false));
  }, []);

  const addToCart = (item) => {
    setCart((previous) => ({
      ...previous,
      [item.id]: (previous[item.id] || 0) + 1,
    }));
  };

  const removeFromCart = (item) => {
    setCart((previous) => {
      const updated = { ...previous };
      if (updated[item.id] > 1) updated[item.id] -= 1;
      else delete updated[item.id];
      return updated;
    });
  };

  const totalItems = Object.values(cart).reduce((a, b) => a + b, 0);

  const totalPrice = menu.reduce(
    (sum, item) => sum + item.price * (cart[item.id] || 0),
    0
  );

  if (authToken && userRole === "restaurant_owner") {
    return <OwnerDashboard onLogout={handleLogout} />;
  }

  if (authToken && userRole === "delivery_partner") {
    return <DeliveryDashboard onLogout={handleLogout} />;
  }

  return (
    <div className="app">
      <header className="navbar">
        <h1>🍔 CampusBite</h1>
        <button
  type="button"
  onClick={() =>
    document.getElementById("campusbite-cart")?.scrollIntoView({
      behavior: "smooth"
    })
  }
>
  🛒 Cart ({totalItems})
</button>
      </header>

      {!authToken && (
          <button
            type="button"
            onClick={() => setShowAuth(!showAuth)}
          >
            {showAuth ? "Close Login" : "Login / Register"}
          </button>
        )}

        {authToken && (
          <>
          <button
  type="button"
  onClick={() => setShowOrders(value => !value)}
>
  {showOrders ? "Hide Orders" : "My Orders"}
</button>

<button type="button" onClick={handleLogout}>
            Logout
          </button>
          </>
        )}

        {showAuth && !authToken && (
          <Auth onLogin={handleLogin} />
        )}

        <section className="hero">
        <h2>Delicious Food, Right on Campus</h2>
        <p>Explore your favourite meals from Campus Cafe</p>
      </section>

      <main className="content">
        <h2>Explore Our Menu</h2>

        {loading && <p>Loading menu...</p>}
        {error && <p className="error">{error}</p>}

        <input
          className="search-bar"
          type="text"
          placeholder="🔍 Search burgers, pizza, momos..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <div className="menu-grid">
          {menu
            .filter((item) =>
              item.name.toLowerCase().includes(search.toLowerCase())
            )
            .map((item) => (
            <article className="food-card" key={item.id}>
              <div className="food-icon"><img
  src={foodImages[item.name] || "/food-images/placeholder.svg"}
  alt={item.name}
  className="food-photo"
  loading="lazy"
  onError={(event) => {
    event.currentTarget.onerror = null;
    event.currentTarget.src = "/food-images/placeholder.svg";
  }}
/></div>
              <h3>{item.name}</h3>
              <p className="price">₹{item.price.toFixed(2)}</p>

              {item.available ? (
                <button onClick={() => addToCart(item)}>
                  Add to Cart +
                </button>
              ) : (
                <button disabled>Unavailable</button>
              )}
            </article>
          ))}
        </div>

        <section id="campusbite-cart" className="cart-section">
          <h2>🛒 Your Cart</h2>

          {totalItems === 0 ? (
            <p>Your cart is empty.</p>
          ) : (
            <>
              {menu
                .filter((item) => cart[item.id])
                .map((item) => (
                  <div className="cart-item" key={item.id}>
                    <span>{item.name}</span>
                    <div>
                      <button onClick={() => removeFromCart(item)}>-</button>
                      <strong> {cart[item.id]} </strong>
                      <button onClick={() => addToCart(item)}>+</button>
                    </div>
                    <span>₹{(item.price * cart[item.id]).toFixed(2)}</span>
                  </div>
                ))}

              <h3>Total: ₹{totalPrice.toFixed(2)}</h3>
              <button
  type="button"
  onClick={async () => {
  if (!authToken) {
    window.alert("Please log in before checkout.");
    return;
  }

  const items = Object.entries(cart)
    .filter(([, quantity]) => quantity > 0)
    .map(([menu_item_id, quantity]) => ({
      menu_item_id: Number(menu_item_id),
      quantity
    }));

  if (!items.length) {
    window.alert("Your cart is empty.");
    return;
  }

  if (!window.confirm("Confirm DEMO checkout? No real payment will be charged.")) return;

  try {
    const response = await fetch(`${API_URL}/orders/demo-checkout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authToken}`
      },
      body: JSON.stringify({ items })
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(
        typeof result.detail === "string"
          ? result.detail
          : "Checkout failed"
      );
    }

    window.alert(`Demo order saved! Order ID: ${result.order_id}`);
    setCart({});
  } catch (error) {
    window.alert(`Checkout error: ${error.message}`);
  }
}}
  style={{
    background: "#ff7043",
    color: "white",
    border: "none",
    padding: "14px 25px",
    borderRadius: "10px",
    cursor: "pointer",
    fontSize: "18px"
  }}
>
  Pay Now (Demo) — ₹{totalPrice.toFixed(2)}
</button>
            </>
          )}
        </section>
      {authToken && showOrders && (
  <OrderHistory
    authToken={authToken}
    onClose={() => setShowOrders(false)}
  />
)}
</main>
    </div>
  );
}

export default App;
