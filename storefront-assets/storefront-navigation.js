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

  const cardSelector = "a.mixer-product, a.concealed-accessory-card";
  const positionKey = "saad-collection-position";

  // Preserve the card's position within the viewport, including partially visible cards.
  // History is per entry (browser Back). Session storage bridges the explicit return link.
  document.addEventListener("click", event => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const card = event.target.closest(cardSelector);
    const section = card?.closest("main > section.panel");
    if (!section || section.hidden || card.origin !== location.origin) return;
    const position = {
      section: section.id,
      href: card.pathname + card.search,
      top: card.getBoundingClientRect().top,
      band: new URL(card.href).searchParams.get("band"),
    };
    try { history.replaceState({...history.state, collectionPosition: position}, ""); } catch {}
    try { sessionStorage.setItem(positionKey, JSON.stringify(position)); } catch {}
  });

  function pagerLink(nav, href, direction) {
    if (!href) return;
    const link = document.createElement("a");
    link.rel = direction;
    link.href = href;
    link.textContent = direction === "prev" ? "الموديل السابق" : "الموديل التالي";
    nav.append(link);
  }

  function returnDestination(link) {
    const target = new URL(link.href, location.origin);
    target.searchParams.delete("from");
    return target.href;
  }

  function updateNavigation() {
    const section = screen();
    if (!section) return;
    const model = section.id;
    returnLink.textContent = "رجوع";
    if (model === "kitchen" && query.get("view") === "all") {
      returnLink.href = "/kitchen-mixers/";
    }
    if (!Object.hasOwn(products, model)) return;

    const from = query.get("from");
    const sourcePart = [...section.querySelectorAll("[data-set-return]")]
      .find(link => link.dataset.setReturn === from);
    if (sourcePart) {
      sourcePart.href = returnDestination(sourcePart);
      sourcePart.hidden = false;
      returnLink.href = sourcePart.href;
      returnLink.textContent = "للقطعة";
      returnLink.setAttribute("aria-label", sourcePart.firstElementChild.textContent);
      return;
    }
    if (from === "set") {
      const setLink = section.querySelector("[data-related-set]");
      if (setLink) {
        returnLink.href = returnDestination(setLink);
        returnLink.textContent = "للطقم";
        returnLink.setAttribute("aria-label", setLink.firstElementChild.textContent);
        return;
      }
    }

    const product = products[model];
    const group = Object.hasOwn(product.collectionImages || {}, from) ? from : product.category || "mixers";
    const filtered = group === "cabinet-luxury" && bandButton;
    const collection = document.getElementById(filtered ? "washbasins" : group);
    if (!collection || !productPath(collection.id)) return;
    if (filtered) bandButton.click();
    const cards = Array.from(collection.querySelectorAll("a.mixer-product"));
    const path = productPath(model);
    const target = new URL(productPath(collection.id), location.origin);
    target.searchParams.set("model", model);
    const kitchenGrid = group === "kitchen" && query.get("view") === "all";
    if (kitchenGrid) target.searchParams.set("view", "all");
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
        if (kitchenGrid) url.searchParams.set("view", "all");
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
    for (const card of filter.querySelectorAll("a.mixer-product")) {
      const url = new URL(card.href);
      url.searchParams.set("band", band);
      card.href = url.href;
    }
  }
  filter?.addEventListener("click", linkFilteredCards);

  function restoreCard() {
    const section = screen();
    const model = query.get("model");
    if (!section?.classList.contains("panel")) return;

    const entry = history.state?.collectionPosition;
    const returningInHistory = entry?.section === section.id;
    if (!returningInHistory && (!model || !Object.hasOwn(products, model))) return;
    let position = returningInHistory ? entry : null;
    if (!position) {
      try { position = JSON.parse(sessionStorage.getItem(positionKey)); } catch {}
    }
    const band = returningInHistory ? position.band : selectedBand;
    if (section.id === "washbasins" && band) {
      Array.from(filter?.querySelectorAll("[data-vanity-band]") || [])
        .find(button => button.dataset.vanityBand === band)?.click();
    }

    const cards = Array.from(section.querySelectorAll(cardSelector));
    const card = returningInHistory
      ? cards.find(link => link.pathname + link.search === position.href)
      : cards.find(link => section.id === "java-mix"
          ? new URL(link.href).searchParams.get("color") === query.get("color")
          : link.pathname === productPath(model));
    if (!card) return;
    card.focus({preventScroll: true});
    if (position?.section === section.id && position.href === card.pathname + card.search
        && Number.isFinite(position.top) && position.top < window.innerHeight
        && position.top + card.getBoundingClientRect().height > 0) {
      window.scrollBy({top: card.getBoundingClientRect().top - position.top, behavior: "instant"});
    } else {
      card.scrollIntoView({block: "center", behavior: "instant"});
    }
  }

  updateNavigation();
  window.addEventListener("pageshow", () => requestAnimationFrame(restoreCard));
  window.addEventListener("hashchange", () => {
    updateNavigation();
    requestAnimationFrame(restoreCard);
  });
})();
