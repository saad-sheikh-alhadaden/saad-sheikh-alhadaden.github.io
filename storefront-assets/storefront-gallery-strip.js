// Keep the product's own photo and option controls as the source of truth.
(() => {
  const initialized = new WeakSet();

  function photoOptions(screen, product) {
    const sources = product.collectionImages?.[screen.dataset.collectionView] || product.images;
    const finishControls = [...screen.querySelectorAll('button[data-color]')];
    const optionGroups = [...screen.querySelectorAll('fieldset[data-axis]')];
    const label = key => product.colorLabels?.[key] || key;

    if (screen.querySelector('[data-mixer-finish]')) {
      return Object.entries(javaMixFinishes).map(([finish, key]) => {
        const url = new URL(`/${screen.id}/`, document.baseURI);
        url.searchParams.set('color', finish);
        return {src: sources[key], label: label(key), href: url.href};
      });
    }

    if (optionGroups.length) {
      return Object.entries(sources).map(([key, src]) => {
        const values = key.split('|');
        const inputs = optionGroups.map((group, index) =>
          [...group.querySelectorAll('input')].find(input => input.value === values[index]));
        return {
          src: inputs.every(Boolean) ? src : null,
          label: label(key),
          select: () => inputs.forEach(input => { if (!input.checked) input.click(); }),
        };
      });
    }

    return finishControls.map(control => ({
      src: sources[control.dataset.color],
      label: control.getAttribute('aria-label') || label(control.dataset.color),
      select: () => control.click(),
      control,
    }));
  }

  function placeStrip(screen) {
    const product = products[screen.id];
    const info = screen.querySelector(':scope > .product-info');
    const image = screen.querySelector('.product-image img');
    if (!product?.images || !info || !image || initialized.has(screen)) return;
    initialized.add(screen);

    const gallery = [...info.querySelectorAll('.product-gallery, .velato-gallery')].find(strip =>
      strip.querySelector('[data-gallery-src]') && getComputedStyle(strip).display !== 'none');
    if (gallery) {
      gallery.classList.add('store-photo-strip');
      if (info.firstElementChild !== gallery) info.prepend(gallery);
      return;
    }

    const options = photoOptions(screen, product);
    const strip = document.createElement('div');
    strip.className = 'product-gallery store-photo-strip store-variant-photos';
    strip.setAttribute('role', 'group');
    strip.setAttribute('aria-label', 'صور المنتج');
    const records = new Map();
    const absolute = src => new URL(src, document.baseURI).href;

    // Shower-arm photos depend on both mounting and shape as well as finish.
    function photoFor(option) {
      if (!product.armPhotos) return option.src;
      const mount = screen.querySelector('[data-arm-mount][aria-pressed="true"]')?.dataset.armMount;
      const shape = screen.querySelector('[data-arm-shape][aria-pressed="true"]')?.dataset.armShape;
      return product.armPhotos[`${mount}/${shape}/${option.control.dataset.color}`]?.[0];
    }

    function refresh() {
      const current = absolute(image.getAttribute('src'));
      const candidates = new Map();
      for (const option of options) {
        const src = photoFor(option);
        if (src && !candidates.has(absolute(src))) candidates.set(absolute(src), option);
      }
      strip.hidden = candidates.size < 2;
      for (const [src, button] of records) {
        if (candidates.has(src)) continue;
        button.remove();
        records.delete(src);
      }
      for (const [src, option] of candidates) {
        let button = records.get(src);
        if (!button) {
          button = document.createElement(option.href ? 'a' : 'button');
          if (option.href) button.href = option.href;
          else {
            button.type = 'button';
            button.addEventListener('click', option.select);
          }
          button.setAttribute('aria-label', option.label);
          const thumbnail = document.createElement('img');
          thumbnail.src = src;
          thumbnail.alt = '';
          thumbnail.loading = 'lazy';
          button.append(thumbnail);
          strip.append(button);
          records.set(src, button);
        }
        if (option.href) button.setAttribute('aria-current', src === current ? 'true' : 'false');
        else button.setAttribute('aria-pressed', String(src === current));
      }
    }

    refresh();
    if (!strip.firstElementChild) return;
    info.prepend(strip);
    new MutationObserver(refresh).observe(image, {attributes: true, attributeFilter: ['src']});
  }

  for (const screen of document.querySelectorAll('section[id]:not([hidden])')) placeStrip(screen);
  const content = document.querySelector('main');
  if (!content) return;
  new MutationObserver(records => {
    for (const {target} of records) {
      if (target.matches('section[id]:not([hidden])')) placeStrip(target);
    }
  }).observe(content, {subtree: true, attributes: true, attributeFilter: ['hidden']});
})();
