function bindCatalogFavorite(id, product, screen) {
  const button = screen?.querySelector("[data-save]");
  const link = document.querySelector(`[data-saved="${id}"]`);
  let favorite = false;
  try {
    const stored = localStorage.getItem(product.favoriteKey);
    favorite = stored === "1" || (stored === null && Object.keys(product.legacyOptions || {})
      .some(old => localStorage.getItem("saad-saved-" + old) === "1"));
  } catch {}

  function render() {
    if (button) {
      button.textContent = favorite ? "♥" : "♡";
      button.setAttribute("aria-pressed", String(favorite));
      button.setAttribute("aria-label", `${favorite ? "إزالة من" : "إضافة إلى"} المفضّلة · ${product.name}`);
    }
    link.hidden = !favorite;
    saved.hidden = !saved.querySelector("a:not([hidden])");
    emptySaved.hidden = !saved.hidden;
  }
  button?.addEventListener("click", () => {
    favorite = !favorite;
    try { localStorage.setItem(product.favoriteKey, favorite ? "1" : "0"); } catch {}
    render();
  });
  render();
}

function openLinkedProduct(id) {
  if (!Object.hasOwn(products, id) || document.getElementById(id)) return false;
  const routes = JSON.parse(document.querySelector("[data-share-pages]").dataset.sharePages);
  const target = new URL(routes[id].path, location.origin);
  target.search = location.search;
  location.replace(target.href);
  return true;
}

function setScreenVisibility(screen, visible) {
  screen.hidden = !visible;
  const heading = screen.querySelector("[data-screen-heading]");
  const tag = visible ? "H1" : "H2";
  if (!heading || heading.tagName === tag) return;
  const replacement = document.createElement(tag);
  for (const attr of heading.attributes) replacement.setAttribute(attr.name, attr.value);
  replacement.append(...heading.childNodes);
  heading.replaceWith(replacement);
}
