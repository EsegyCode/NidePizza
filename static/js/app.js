document.addEventListener("DOMContentLoaded", () => {
  // Mobile navigation toggle
  const toggleBtn = document.getElementById("mobile-nav-toggle");
  const navLinks = document.getElementById("primary-nav-links");
  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener("click", () => {
      navLinks.classList.toggle("open");
    });
  }

  // Toast helper
  const toastEl = document.getElementById("nide-toast");
  let toastTimer = null;
  function showToast(message) {
    if (!toastEl) return;
    toastEl.textContent = message;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("show"), 2600);
  }

  // AJAX Add to Cart with graceful fallback
  document.querySelectorAll("form.js-add-to-cart").forEach((form) => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = form.querySelector("button[type='submit']");
      if (btn) btn.disabled = true;

      try {
        const res = await fetch(form.action, {
          method: "POST",
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        if (!res.ok) throw new Error("Request failed");
        const data = await res.json();
        const badge = document.getElementById("nav-cart-count");
        if (badge && typeof data.cart_count === "number") {
          badge.textContent = data.cart_count;
        }
        showToast(`Added "${data.product_name}" to cart`);
      } catch (err) {
        form.submit();
      } finally {
        if (btn) btn.disabled = false;
      }
    });
  });
});
