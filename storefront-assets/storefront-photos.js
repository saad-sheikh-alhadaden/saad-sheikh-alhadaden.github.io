// Restrict image menus and dragging while leaving links, text and swipe controls usable.
(() => {
  let imageLink;
  document.addEventListener("pointerdown", event => {
    imageLink = event.target instanceof HTMLImageElement ? event.target.closest("a") : null;
  }, true);

  document.addEventListener("contextmenu", event => {
    if (event.target instanceof HTMLImageElement) event.preventDefault();
  }, true);

  document.addEventListener("dragstart", event => {
    if (event.target instanceof HTMLImageElement || event.target === imageLink) event.preventDefault();
  }, true);
})();
