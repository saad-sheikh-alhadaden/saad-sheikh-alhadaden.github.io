(() => {
  const home = document.getElementById("home");
  const hero = home.querySelector(".top-ten-entry + a.hero");
  const photo = hero.querySelector("img");
  const models = [
    { path: "shower-ferrari", name: "Ferrari", title: "شاور فيراري الذكي",
      image: "/assets/shower-ferrari-brushed-gold-1.webp", alt: "شاور فيراري الذكي بالذهبي المصقول" },
    { path: "cabinet-v20", name: "V20", title: "مغسلة بخزانة معلّقة",
      image: "/assets/cabinet-v20-black-gold-90x50.webp", alt: "مغسلة V20 بخزانة سوداء مخدّدة وشريط ذهبي" },
    { path: "st-307840", name: "S.T 307840", title: "خلاط مغسلة جداري",
      image: "/assets/st307840-gray-01.webp", alt: "خلاط المغسلة الجداري S.T 307840 باللون الرمادي" },
    { path: "cobra-plus-2027", name: "COBRA Plus", title: "خلاط مغسلة كوبرا بلس",
      image: "/assets/cobra-finish-1.webp", alt: photo.alt }
  ];
  const visitKey = "saad-home-cover";
  const awayKey = "saad-home-away-at";
  const visitBreak = 30 * 60 * 1000;
  let selected;

  function showCover() {
    const screen = location.hash.slice(1) || document.documentElement.dataset.screen || "home";
    if (screen !== "home") return;
    if (!selected) {
      let previous;
      try { previous = localStorage.getItem(visitKey); } catch {}
      const lastIndex = models.findIndex(model => model.path === previous);
      selected = models[(lastIndex + 1) % models.length];
      try { sessionStorage.setItem(visitKey, selected.path); } catch {}
      try { localStorage.setItem(visitKey, selected.path); } catch {}
    }
    if (hero.dataset.featured === selected.path) return;
    hero.dataset.featured = selected.path;
    hero.href = "/" + selected.path + "/";
    photo.alt = selected.alt;
    photo.src = selected.image;
    hero.querySelector(".hero-copy bdi").textContent = selected.name;
    hero.querySelector(".hero-product-name").textContent = selected.title;
    hero.querySelector(".more").firstChild.textContent = "تفاصيل الموديل ";
  }

  function resume() {
    try {
      const awayAt = Number(sessionStorage.getItem(awayKey));
      if (awayAt && Date.now() - awayAt >= visitBreak) sessionStorage.removeItem(visitKey);
      sessionStorage.removeItem(awayKey);
      const current = sessionStorage.getItem(visitKey);
      selected = models.find(model => model.path === current);
    } catch {}
    showCover();
  }

  function rememberDeparture() {
    try { sessionStorage.setItem(awayKey, String(Date.now())); } catch {}
  }
  if (!document.hidden) resume();
  window.addEventListener("hashchange", showCover);
  window.addEventListener("pagehide", rememberDeparture);
  window.addEventListener("pageshow", event => { if (event.persisted) resume(); });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) rememberDeparture();
    else resume();
  });
})();
