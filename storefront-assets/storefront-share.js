const shareButton = document.querySelector("[data-share-page]");
const shareDialog = document.querySelector("[data-share-dialog]");
const shareInput = shareDialog.querySelector("[data-share-link]");
const shareStatus = shareDialog.querySelector("[data-share-status]");
const shareOptions = JSON.parse(shareButton.dataset.sharePages);
const shareFinishes = new Set(["chrome", "black", "gray", "gold", "brushed-gold", "rose-gold", "black-chrome", "black-rose-gold"]);

function currentSharePage() {
  const screen = document.querySelector("main > section[id]:not([hidden])");
  const current = screen?.id;
  if (screen?.dataset.javaFinish) {
    const url = new URL(shareOptions["java-mix"].path, location.origin);
    url.searchParams.set("color", screen.dataset.javaFinish);
    return { title: screen.querySelector("h1").innerText, url: url.href, label: "مشاركة المجموعة" };
  }
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

const nativeShare = shareDialog.querySelector("[data-share-native]");
const manualShare = shareDialog.querySelector("[data-share-manual]");
const shareImage = shareDialog.querySelector("[data-share-image]");
const shareName = shareDialog.querySelector("[data-share-name]");

function shareCurrentPage() {
  const { title, url, label } = currentSharePage();
  const screen = document.querySelector("main > section[id]:not([hidden])");
  const isProduct = label === "مشاركة المنتج";
  const productImage = isProduct ? screen?.querySelector(".product-image img") : null;
  const modelName = isProduct ? screen?.querySelector("h1")?.textContent : null;
  shareName.textContent = modelName?.trim() || title.split("|")[0].trim();
  shareImage.hidden = !productImage;
  if (productImage) shareImage.src = productImage.currentSrc || productImage.src;

  shareDialog.querySelector("h2").textContent = label;
  shareInput.value = url;
  shareStatus.textContent = "";
  manualShare.hidden = true;
  nativeShare.hidden = typeof navigator.share !== "function";
  const whatsapp = shareDialog.querySelector("[data-share-whatsapp]");
  whatsapp.href = "https://wa.me/?text=" + encodeURIComponent(title + "\n" + url);
  shareDialog.showModal();
}

nativeShare.addEventListener("click", async () => {
  const { title, url } = currentSharePage();
  try {
    await navigator.share({ title, url });
  } catch (error) {
    if (error?.name !== "AbortError") {
      shareStatus.textContent = "جرّب نسخ الرابط أو مشاركته عبر واتساب.";
    }
  }
});

shareButton.addEventListener("click", shareCurrentPage);
shareDialog.querySelector("[data-share-copy]").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(shareInput.value);
    shareStatus.textContent = "تم نسخ الرابط.";
  } catch {
    manualShare.hidden = false;
    shareInput.focus();
    shareInput.select();
    shareStatus.textContent = "تم تحديد الرابط. انسخه من قائمة النسخ على جهازك.";
  }
});
window.addEventListener("hashchange", updateShareLabel);
updateShareLabel();
