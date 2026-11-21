const cartNotice = document.getElementById("cart-feedback");
let noticeTimer;

function dismissCartNotice() {
  window.clearTimeout(noticeTimer);
  cartNotice.replaceChildren();
}

window.addEventListener("hashchange", dismissCartNotice);
window.addEventListener("pagehide", dismissCartNotice);

function cartConfirmationFor(button) {
  let resetTimer;

  function clear() {
    window.clearTimeout(resetTimer);
    button.removeAttribute("data-cart-added");
    button.removeAttribute("aria-disabled");
  }

  function show(product, variant, quantity) {
    dismissCartNotice();
    button.dataset.cartAdded = "";
    button.setAttribute("aria-disabled", "true");
    const heading = document.createElement("strong");
    heading.className = "cart-notice-heading";
    heading.textContent = "أُضيف إلى السلة";
    const name = document.createElement("bdi");
    name.className = "cart-notice-product";
    name.textContent = product.name;
    const finish = document.createElement("bdi");
    finish.className = "cart-notice-finish";
    finish.textContent = itemColorLabel(product, variant);
    const price = document.createElement("div");
    price.className = "cart-notice-price";
    const amount = document.createElement("bdi");
    amount.dir = "ltr";
    amount.textContent = money(quantity * unitPrice(product, variant));
    const label = document.createElement("small");
    label.textContent = "السعر";
    if (quantity === 2) label.textContent = "إجمالي قطعتين";
    if (quantity > 2) label.textContent = `إجمالي ${quantity} ${quantity < 11 ? "قطع" : "قطعة"}`;
    price.append(label, amount);
    cartNotice.replaceChildren(heading, name, finish, price);
    resetTimer = window.setTimeout(clear, 900);
    noticeTimer = window.setTimeout(dismissCartNotice, 4500);
  }

  return { show, clear };
}
