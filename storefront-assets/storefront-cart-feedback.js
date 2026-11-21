const cartNotice = document.getElementById("cart-feedback");
let noticeTimer;

function dismissCartNotice() {
  window.clearTimeout(noticeTimer);
  cartNotice.replaceChildren();
}

function scheduleCartNoticeDismissal() {
  window.clearTimeout(noticeTimer);
  noticeTimer = window.setTimeout(dismissCartNotice, 4500);
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
    const action = document.createElement("span");
    action.className = "cart-notice-action";
    action.textContent = "عرض السلة";
    heading.append(action);
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
    const link = document.createElement("a");
    link.className = "cart-notice-link";
    link.href = location.pathname + location.search + "#cart";
    link.append(heading, name, finish, price);
    link.addEventListener("focus", () => window.clearTimeout(noticeTimer));
    link.addEventListener("blur", scheduleCartNoticeDismissal);
    cartNotice.replaceChildren(link);
    resetTimer = window.setTimeout(clear, 900);
    scheduleCartNoticeDismissal();
  }

  return { show, clear };
}
