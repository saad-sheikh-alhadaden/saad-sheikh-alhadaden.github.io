function createJavaGallery() {
  const main = document.querySelector('.app > main');
  const header = document.querySelector('.app > .top');
  const footer = document.querySelector('.app > .nav');
  const selector = document.createElement('nav');
  selector.className = 'java-gallery-selector';
  selector.setAttribute('aria-label', 'خلاطات الطقم');
  selector.hidden = true;

  const grip = document.createElement('button');
  grip.type = 'button';
  grip.className = 'java-gallery-grip';
  grip.dir = 'ltr';
  grip.textContent = 'JAVA MIX · ' + javaMixFinishes[javaMixFinish];
  const thumbnails = document.createElement('div');
  thumbnails.className = 'java-gallery-thumbnails';
  const models = screens.filter(screen => javaMixModelIds.has(screen.id));
  for (const screen of models) screen.classList.add('java-gallery-model');
  for (const choice of models[0].querySelectorAll('[data-mixer-choice]')) {
    const model = choice.dataset.mixerChoice;
    const link = document.createElement('a');
    const url = new URL(location.href);
    url.hash = model;
    link.href = url.href;
    link.setAttribute('aria-label', choice.textContent.trim());
    const image = new Image(790, 988);
    image.src = products[model].images[javaMixFinishes[javaMixFinish]];
    image.alt = '';
    image.draggable = false;
    link.append(image);
    thumbnails.append(link);
  }
  selector.append(grip, thumbnails);
  main.prepend(selector);

  let offset = 0;
  let travel = 0;
  function place(value) {
    offset = Math.min(travel, Math.max(0, value));
    selector.style.setProperty('--rail-offset', offset + 'px');
    selector.toggleAttribute('data-floating', offset > 8);
    grip.setAttribute('aria-label', offset > travel / 2 ? 'رفع شريط الصور' : 'تنزيل شريط الصور');
  }
  function measure() {
    if (selector.hidden) return;
    const top = header.offsetHeight;
    const height = window.visualViewport?.height ?? document.documentElement.clientHeight;
    travel = Math.max(0, height - top - footer.offsetHeight - selector.offsetHeight - 8);
    selector.style.setProperty('--rail-header', top + 'px');
    selector.style.setProperty('--rail-height', selector.offsetHeight + 'px');
    place(offset);
  }
  const resize = new ResizeObserver(measure);
  for (const element of [header, footer, selector]) resize.observe(element);
  window.visualViewport?.addEventListener('resize', measure);
  window.addEventListener('resize', measure);

  let drag = null;
  let suppressClick = false;
  selector.addEventListener('pointerdown', event => {
    if (!event.isPrimary || event.button !== 0) return;
    suppressClick = false;
    drag = { id: event.pointerId, x: event.clientX, y: event.clientY,
      offset, moving: false };
  });
  selector.addEventListener('pointermove', event => {
    if (!drag || drag.id !== event.pointerId) return;
    const dx = event.clientX - drag.x;
    const dy = event.clientY - drag.y;
    if (!drag.moving) {
      if (Math.max(Math.abs(dx), Math.abs(dy)) < 6) return;
      suppressClick = true;
      if (Math.abs(dx) > Math.abs(dy)) {
        drag = null;
        return;
      }
      drag.moving = true;
      selector.setPointerCapture(event.pointerId);
    }
    place(drag.offset + dy);
  });
  function endDrag(event) {
    if (drag?.id === event.pointerId) drag = null;
  }
  window.addEventListener('pointerup', endDrag);
  window.addEventListener('pointercancel', endDrag);
  selector.addEventListener('click', event => {
    if (suppressClick && event.detail !== 0) {
      event.preventDefault();
      event.stopImmediatePropagation();
      suppressClick = false;
    }
  }, true);
  grip.addEventListener('click', () => place(offset > travel / 2 ? 0 : travel));

  return function selectModel(id) {
    selector.hidden = !javaMixModelIds.has(id);
    if (selector.hidden) return;
    measure();
    for (const link of thumbnails.children) {
      if (link.hash !== '#' + id) {
        link.removeAttribute('aria-current');
        continue;
      }
      link.setAttribute('aria-current', 'true');
    }
  };
}
