for (const options of document.querySelectorAll(".options")) {
  const choices = [...options.querySelectorAll(":scope > button[data-color][aria-pressed]")];
  if (choices.length < 2) continue;

  const labelFor = choice => (choice.querySelector("bdi")?.textContent || choice.textContent).trim();
  const finishes = new Map();
  for (const choice of choices) {
    const label = labelFor(choice);
    const key = label.toLowerCase();
    if (!finishes.has(key)) {
      finishes.set(key, getComputedStyle(choice).getPropertyValue("--store-finish").trim());
    }
  }

  const picker = document.createElement("details");
  picker.className = "finish-picker";
  const summary = document.createElement("summary");
  summary.innerHTML = '<span class="finish-picker-copy"><strong>الألوان المتاحة <span class="finish-picker-count"></span></strong><span class="finish-picker-selected"><bdi></bdi></span></span><span class="finish-picker-palette" aria-hidden="true"></span>';
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
