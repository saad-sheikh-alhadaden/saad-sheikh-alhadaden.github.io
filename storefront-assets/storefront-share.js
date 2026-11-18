const shareButton = document.querySelector("[data-share-page]");
const shareDialog = document.querySelector("[data-share-dialog]");
const shareInput = shareDialog.querySelector("[data-share-link]");
const shareStatus = shareDialog.querySelector("[data-share-status]");
const shareOptions = JSON.parse(shareButton.dataset.sharePages);
const shareFinishes = new Set(["chrome", "black", "gray", "gold", "brushed-gold", "rose-gold", "black-chrome", "black-rose-gold"]);

function currentSharePage() {
  const current = document.querySelector("main > section[id]:not([hidden])")?.id;
  const page = Object.hasOwn(shareOptions, current) ? shareOptions[current] : shareOptions.home;
  const url = new URL(page.path, location.origin);
  const color = new URLSearchParams(location.search).get("color");
  if (page.path.startsWith("/java-mix-") && shareFinishes.has(color)) {
    url.searchParams.set("color", color);
  }
  return { title: page.title, url: url.href, label: page.label };
}

function updateShareLabel() {
  const { label } = currentSharePage();
  shareButton.setAttribute("aria-label", label);
  shareButton.title = label;
}

async function shareCurrentPage() {
  const { title, url, label } = currentSharePage();
  if (typeof navigator.share === "function") {
    try {
      await navigator.share({ title, url });
      return;
    } catch (error) {
      if (error?.name === "AbortError") return;
    }
  }
  shareDialog.querySelector("h2").textContent = label;
  shareInput.value = url;
  shareStatus.textContent = "";
  const whatsapp = shareDialog.querySelector("[data-share-whatsapp]");
  whatsapp.href = "https://wa.me/?text=" + encodeURIComponent(title + "\n" + url);
  shareDialog.showModal();
}

shareButton.addEventListener("click", shareCurrentPage);
shareDialog.querySelector("[data-share-copy]").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(shareInput.value);
    shareStatus.textContent = "تم نسخ الرابط.";
  } catch {
    shareInput.focus();
    shareInput.select();
    shareStatus.textContent = "تم تحديد الرابط. انسخه من قائمة النسخ على جهازك.";
  }
});
window.addEventListener("hashchange", updateShareLabel);
updateShareLabel();
