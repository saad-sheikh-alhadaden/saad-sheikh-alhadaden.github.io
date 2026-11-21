// The cart uses the same option key as the photo and unit-price summary.
function bindAccessoryOptions(screen, product, select) {
  const groups = [...screen.querySelectorAll("fieldset[data-axis]")];
  const query = new URLSearchParams(location.search);
  const onProductPage = location.pathname.replaceAll("/", "") === screen.id;
  const collection = query.get("from");
  const collectionImages = onProductPage && Object.hasOwn(product.collectionImages || {}, collection)
    ? product.collectionImages[collection] : undefined;
  if (collectionImages) screen.dataset.collectionView = collection;
  if (onProductPage) {
    for (const group of groups) {
      const match = [...group.querySelectorAll("input")].find(input => input.value === query.get(group.dataset.axis));
      if (match) match.checked = true;
    }
  }
  const image = screen.querySelector(".product-image img");
  const price = screen.querySelector("[data-unit-price]");
  const summary = screen.querySelector("[data-family-summary]");

  function update() {
    const values = groups.map(group => group.querySelector("input:checked").value);
    const key = values.length ? values.join("|") : product.defaultColor;
    const label = product.colorLabels[key];
    const src = collectionImages?.[key] ?? product.images[key];
    if (image.getAttribute("src") !== src) image.src = src;
    image.alt = product.name + " · " + label;
    summary.textContent = label;
    price.textContent = product.prices[key] === null ? "السعر قيد التحديث" : money(product.prices[key]);

    for (const input of screen.querySelectorAll('[data-axis="package"] input')) {
      const optionKey = [values[0], input.value].join("|");
      input.parentElement.querySelector("[data-option-price]").textContent = money(product.prices[optionKey]);
    }
    for (const input of screen.querySelectorAll('[data-axis="size"] input')) {
      const optionKey = [values[0], values[1], input.value].join("|");
      input.parentElement.querySelector("[data-option-label]").textContent = product.colorLabels[optionKey].split(" · ").at(-1);
    }
    select(key);
  }

  for (const group of groups) group.addEventListener("change", update);
  update();
}

function prepareFlushPlateView(screen, product, image, choices) {
  const collection = new URLSearchParams(location.search).get("from");
  if (location.pathname.replaceAll("/", "") !== screen.id || !Object.hasOwn(product.collectionImages, collection)) {
    return product.images;
  }
  screen.dataset.collectionView = collection;
  const images = product.collectionImages[collection];
  image.src = images[product.defaultColor];
  for (const choice of choices) choice.querySelector("img").src = images[choice.dataset.color];
  const warranty = screen.querySelector(".velato-warranty");
  if (warranty) warranty.hidden = true;
  return images;
}

function migrateAccessoryCart(items, families) {
  const result = [];
  for (const item of items) {
    const family = families.find(([, product]) => item && Object.hasOwn(product.legacyOptions, item.product));
    if (!family) { result.push(item); continue; }
    const [slug, product] = family;
    const variant = product.legacyOptions[item.product][item.color];
    if (variant && Number.isSafeInteger(item.qty) && item.qty > 0) {
      const existing = result.find(row => row?.product === slug && row.color === variant);
      if (existing) existing.qty += item.qty;
      else result.push({...item, product: slug, color: variant});
    }
  }
  return result;
}
