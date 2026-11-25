for (const options of document.querySelectorAll(".options:not([data-package-options])")) {
  const choices = [...options.querySelectorAll(":scope > button[data-color][aria-pressed]")];
  if (!choices.length) continue;

  const labelFor = choice => (choice.querySelector("bdi")?.textContent || choice.textContent).trim();
  const finishes = new Map();
  for (const choice of choices) {
    const label = labelFor(choice);
    const key = label.toLowerCase();
    if (!finishes.has(key)) {
      finishes.set(key, getComputedStyle(choice).getPropertyValue("--store-finish").trim());
    }
  }

  const picker = document.createElement("div");
  picker.className = "finish-picker";
  const summary = document.createElement("div");
  summary.className = "finish-picker-summary";
  summary.innerHTML = `<span class="finish-picker-copy"><strong>${options.getAttribute('aria-label') === 'المقاس' ? 'المقاسات المتاحة' : 'الألوان المتاحة'} <span class="finish-picker-count"></span></strong><span class="finish-picker-selected"><bdi></bdi></span></span><span class="finish-picker-palette" aria-hidden="true"></span>`;
  summary.querySelector(".finish-picker-count").textContent = `(${finishes.size})`;
  const selected = summary.querySelector("bdi");
  const palette = summary.querySelector(".finish-picker-palette");
  for (const fill of [...finishes.values()].slice(0, 4)) {
    const dot = document.createElement("span");
    dot.className = "finish-picker-dot";
    if (fill) dot.style.background = fill;
    palette.append(dot);
  }
  if (finishes.size > 4) {
    const remaining = document.createElement("bdi");
    remaining.className = "finish-picker-more";
    remaining.textContent = `+${finishes.size - 4}`;
    palette.append(remaining);
  }

  const updateSelection = () => {
    const active = choices.find(choice => choice.getAttribute("aria-pressed") === "true");
    selected.textContent = active ? (active.getAttribute("aria-label") || labelFor(active)) : "";
  };
  updateSelection();
  new MutationObserver(updateSelection).observe(options, {
    attributes: true, subtree: true, attributeFilter: ["aria-pressed"],
  });

  options.before(picker);
  picker.append(summary, options);
}

const finishAliases = new Map(Object.entries({
  "رمادي": "gray", "رمادي فاتح": "light gray", "رمادي فحمي": "charcoal gray",
  "ذهبي": "gold", "ذهبي مفرش": "brushed gold", "روز غولد": "rose gold",
  "أبيض": "white", "ابيض": "white", "أسود": "black", "اسود": "black",
  "كروم": "chrome", "أخضر مفرش": "brushed green", "أخضر": "green",
  "charcoal grey": "charcoal gray", "grey": "gray", "ivory": "ivore",
}));
const fixedFinishes = new Set([
  "chrome", "black", "matt black", "matte black", "gold", "brushed gold",
  "rose gold", "brushed rose gold", "gray", "light gray", "charcoal gray",
  "white", "off-white", "ivore", "creamy", "greige", "green", "brushed green",
  "oil", "red", "bronze", "gunmetal", "brushed gunmetal gray", "walnut",
  "charcoal gray & walnut", "black & gold", "black oak", "champagne gold",
  "brushed champagne gold", "polished gold", "polished rose gold", "brushed nickel",
]);
for (const line of document.querySelectorAll(".product-info > p")) {
  if (line.closest(".product-info").querySelector(".finish-picker")) continue;
  const text = line.textContent.trim();
  const prefix = /^اللون(?:\s*[·:：]\s*|\s+)/u;
  const label = text.replace(prefix, "").trim();
  const name = label.split(" · ")[0].toLowerCase().replace(/[\u064b-\u0652]/gu, "");
  const finish = finishAliases.get(name) || name;
  if (!label || (!prefix.test(text) && !fixedFinishes.has(finish))) continue;

  const chip = document.createElement("span");
  chip.className = "fixed-finish-chip";
  chip.dataset.color = finish;
  const dot = document.createElement("span");
  dot.className = "finish-picker-dot";
  dot.setAttribute("aria-hidden", "true");
  const caption = document.createElement("bdi");
  caption.textContent = label;
  chip.append(dot, caption);
  line.classList.add("fixed-finish");
  line.setAttribute("aria-label", `اللون ${label}`);
  line.replaceChildren(chip);
}
