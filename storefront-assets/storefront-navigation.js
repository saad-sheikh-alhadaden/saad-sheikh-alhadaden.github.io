(() => {
  const returnLink = document.getElementById("back");
  const query = new URLSearchParams(location.search);
  const selectedBand = query.get("band");
  const bandButton = Array.from(document.querySelectorAll("[data-vanity-band]"))
    .find(button => button.dataset.vanityBand === selectedBand);
  const screen = () => document.querySelector("main > section[id]:not([hidden])");

  function productPath(id) {
    return shareOptions[id]?.path;
  }

  function cardsIn(section) {
    return Array.from(section.querySelectorAll("a.mixer-product"));
  }

  function pagerLink(nav, href, direction) {
    if (!href) return;
    const link = document.createElement("a");
    link.rel = direction;
    link.href = href;
    link.textContent = direction === "prev" ? "الموديل السابق" : "الموديل التالي";
    nav.append(link);
  }

  function updateNavigation() {
    const section = screen();
    if (!section) return;
    const model = section.id;
    returnLink.textContent = "رجوع";
    if (!Object.hasOwn(products, model)) return;

    const group = products[model].category || "mixers";
    const filtered = group === "cabinet-luxury" && bandButton;
    const collection = document.getElementById(filtered ? "washbasins" : group);
    if (!collection || !productPath(collection.id)) return;
    if (filtered) bandButton.click();
    const cards = cardsIn(collection);
    const path = productPath(model);
    const target = new URL(productPath(collection.id), location.origin);
    target.searchParams.set("model", model);
    if (filtered) target.searchParams.set("band", selectedBand);
    if (group === "java-mix") target.searchParams.set("color", javaMixFinish);
    returnLink.href = target.href;
    returnLink.textContent = "للموديلات";
    returnLink.setAttribute("aria-label", "الرجوع لقائمة الموديلات");

    const info = section.querySelector(".product-info");
    if (!info || info.querySelector(".model-pager")) return;
    const nav = document.createElement("nav");
    nav.className = "model-pager";
    nav.setAttribute("aria-label", "تصفّح موديلات المجموعة");
    if (group === "java-mix") {
      pagerLink(nav, section.querySelector('[data-mixer-step="previous"]')?.href, "prev");
      pagerLink(nav, section.querySelector('[data-mixer-step="next"]')?.href, "next");
    } else {
      const index = cards.findIndex(card => card.pathname === path);
      if (index < 0) return;
      for (const [offset, direction] of [[-1, "prev"], [1, "next"]]) {
        const card = cards[index + offset];
        if (!card) continue;
        const url = new URL(card.href);
        if (filtered) url.searchParams.set("band", selectedBand);
        pagerLink(nav, url.href, direction);
      }
    }
    if (nav.childElementCount) info.append(nav);
  }

  // The size filter recreates its cards whenever the shopper chooses a band.
  const filter = document.querySelector("[data-vanity-filter]");
  function linkFilteredCards() {
    const band = filter.querySelector('[aria-pressed="true"]')?.dataset.vanityBand;
    if (!band) return;
    for (const card of cardsIn(filter)) {
      const url = new URL(card.href);
      url.searchParams.set("band", band);
      card.href = url.href;
    }
  }
  filter?.addEventListener("click", linkFilteredCards);

  function restoreCard() {
    const section = screen();
    const model = query.get("model");
    if (!model || !Object.hasOwn(products, model) || !section?.classList.contains("panel")) return;
    if (section.id === "washbasins" && bandButton) bandButton.click();
    const cards = cardsIn(section);
    const card = section.id === "java-mix"
      ? cards.find(link => new URL(link.href).searchParams.get("color") === query.get("color"))
      : cards.find(link => link.pathname === productPath(model));
    if (card) {
      card.focus({preventScroll: true});
      card.scrollIntoView({block: "center"});
    }
  }

  updateNavigation();
  requestAnimationFrame(restoreCard);
  window.addEventListener("hashchange", updateNavigation);
})();
