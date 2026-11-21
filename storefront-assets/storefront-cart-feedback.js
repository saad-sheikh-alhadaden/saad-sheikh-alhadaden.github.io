function cartConfirmationFor(button) {
  let resetTimer;

  function clear() {
    window.clearTimeout(resetTimer);
    button.removeAttribute("data-cart-added");
    button.removeAttribute("aria-disabled");
  }

  function show(productName, quantity) {
    button.dataset.cartAdded = `✓ تمت الإضافة (${quantity})`;
    button.setAttribute("aria-disabled", "true");
    const total = document.getElementById("cart-count").textContent;
    document.getElementById("cart-feedback").textContent =
      `أُضيف إلى السلة: ${productName}، الكمية ${quantity}. عدد القطع في السلة ${total}.`;
    resetTimer = window.setTimeout(clear, 1800);
  }

  return { show, clear };
}
