document.documentElement.classList.add('js');
let language = 'en';
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const menu = document.querySelector('#menu');
const menuToggle = document.querySelector('.menu-toggle');
function closeMenu(restoreFocus = false) {
  menu.classList.remove('is-open');
  menu.inert = true;
  menuToggle.setAttribute('aria-expanded', 'false');
  document.body.style.overflow = '';
  if (restoreFocus) menuToggle.focus();
  scheduleAutoplay();
}
menuToggle.addEventListener('click', () => {
  const opening = menuToggle.getAttribute('aria-expanded') !== 'true';
  if (!opening) return closeMenu();
  menu.inert = false;
  menu.classList.add('is-open');
  menuToggle.setAttribute('aria-expanded', 'true');
  document.body.style.overflow = 'hidden';
  menu.querySelector('a').focus();
  scheduleAutoplay();
});
menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => closeMenu()));
document.querySelector('.header .brand').addEventListener('click', () => closeMenu());
document.addEventListener('keydown', event => {
  if (!menu.classList.contains('is-open')) return;
  if (event.key === 'Escape') closeMenu(true);
  if (event.key === 'Tab') {
    const links = [...menu.querySelectorAll('a')];
    if (event.shiftKey && document.activeElement === links[0]) { event.preventDefault(); menuToggle.focus(); }
    else if (event.shiftKey && document.activeElement === menuToggle) { event.preventDefault(); links.at(-1).focus(); }
    else if (!event.shiftKey && document.activeElement === links.at(-1)) { event.preventDefault(); menuToggle.focus(); }
    else if (!event.shiftKey && document.activeElement === menuToggle) { event.preventDefault(); links[0].focus(); }
  }
});
const observer = new IntersectionObserver(entries => entries.forEach(entry => {
  if (entry.isIntersecting) { entry.target.classList.add('visible'); observer.unobserve(entry.target); }
}), { threshold: .08 });
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

const chain = [
  { kicker:'01 / CONFIRM AVAILABILITY', title:'The journey starts<br>before the boat.', copy:'A delivery plan only works when medicines are available. First, confirm the designated supply pathway, allocated stock and the funding to keep it moving.', detail:'Supply responsibility & available stock' },
  { kicker:'02 / PREPARE IN LORENGAU', title:'One hub.<br>A clearer picture.', copy:'Connect facility orders with available stock at the Lorengau hub. Check quantities, packaging and dispatch records so each delivery starts with the right medicines.', detail:'Stock visibility & planned dispatch' },
  { kicker:'03 / CONNECT BY SEA', title:'A dependable<br>way across.', copy:'Use qualified transport suited to the route. Agree delivery windows, protect the cargo and prepare alternatives for weather disruption or vessel breakdown.', detail:'Safe transport & contingency planning' },
  { kicker:'04 / COMPLETE THE HANDOVER', title:'All the way<br>to the shelf.', copy:'Check medicines on arrival, confirm usable quantities and update facility records. Safe storage and the next stock report complete the connection back to the hub.', detail:'Verified receipt & a continuous feedback loop' }
];
const routeTabs = [...document.querySelectorAll('.route-node')];
let selectedStep = 0;
function selectStep(index, focus = false) {
  if (!routeTabs.length) return;
  selectedStep = (index + chain.length) % chain.length;
  const entry = language === 'ko' ? window.siteI18n.chain[selectedStep] : chain[selectedStep];
  routeTabs.forEach((tab, i) => { tab.setAttribute('aria-selected', String(i === selectedStep)); tab.tabIndex = i === selectedStep ? 0 : -1; });
  document.querySelector('#step-kicker').textContent = entry.kicker;
  document.querySelector('#step-title').innerHTML = entry.title;
  document.querySelector('#step-copy').textContent = entry.copy;
  document.querySelector('#step-detail strong').textContent = entry.detail;
  const panel = document.querySelector('#route-panel');
  panel.setAttribute('aria-labelledby', routeTabs[selectedStep].id);
  panel.classList.remove('changing'); void panel.offsetWidth; panel.classList.add('changing');
  if (focus) routeTabs[selectedStep].focus();
}
routeTabs.forEach((tab, i) => {
  tab.addEventListener('click', () => selectStep(i));
  tab.addEventListener('keydown', event => {
    if (!['ArrowRight','ArrowLeft','ArrowDown','ArrowUp','Home','End'].includes(event.key)) return;
    event.preventDefault();
    selectStep(event.key === 'Home' ? 0 : event.key === 'End' ? 3 : i + (['ArrowRight','ArrowDown'].includes(event.key) ? 1 : -1), true);
  });
});
document.querySelector('.next-step')?.addEventListener('click', () => selectStep(selectedStep + 1));

let currentSlide = 0;
let autoPaused = false, autoTimer = null;
const slideButtons = [...document.querySelectorAll('[data-slide]')];
const slides = [...document.querySelectorAll('.approach-slide')];
function showSlide(index) {
  if (!slides.length) return;
  currentSlide = (index + slides.length) % slides.length;
  document.querySelector('.gallery-track').style.transform = `translateX(-${currentSlide * 100}%)`;
  document.querySelector('#slide-number').textContent = String(currentSlide + 1).padStart(2, '0');
  slideButtons.forEach((button, i) => { button.classList.toggle('active', i === currentSlide); button.setAttribute('aria-pressed', String(i === currentSlide)); });
  slides.forEach((slide, i) => { slide.inert = i !== currentSlide; slide.setAttribute('aria-hidden', String(i !== currentSlide)); });
  scheduleAutoplay();
}
slideButtons.forEach((button, i) => button.addEventListener('click', () => showSlide(i)));
document.querySelector('#prev-slide')?.addEventListener('click', () => showSlide(currentSlide - 1));
document.querySelector('#next-slide')?.addEventListener('click', () => showSlide(currentSlide + 1));
let touchStart = null;
const gallery = document.querySelector('.approach-gallery');
gallery?.addEventListener('touchstart', event => { touchStart = {x:event.touches[0].clientX,y:event.touches[0].clientY}; }, { passive:true });
gallery?.addEventListener('touchend', event => {
  if (!touchStart) return;
  const dx = event.changedTouches[0].clientX - touchStart.x;
  const dy = event.changedTouches[0].clientY - touchStart.y;
  if (Math.abs(dx) > 55 && Math.abs(dx) > Math.abs(dy)) showSlide(currentSlide + (dx < 0 ? 1 : -1));
  touchStart = null;
}, { passive:true });
function scheduleAutoplay() {
  clearTimeout(autoTimer);
  const bounds = gallery?.getBoundingClientRect();
  const visible = bounds && bounds.bottom >= 82 && bounds.top <= window.innerHeight;
  const running = !!visible && !autoPaused && !document.hidden && !menu.classList.contains('is-open');
  gallery?.classList.toggle('is-playing', running);
  if (running) autoTimer = setTimeout(() => showSlide(currentSlide + 1), 3000);
}
function updateAutoplayLabel() {
  const button = document.querySelector('#toggle-autoplay');
  if (!button) return;
  button.setAttribute('aria-pressed', String(autoPaused));
  button.setAttribute('aria-label', language === 'ko' ? (autoPaused ? '자동 전환 재생' : '자동 전환 일시정지') : (autoPaused ? 'Resume automatic slides' : 'Pause automatic slides'));
  button.innerHTML = `<span aria-hidden="true">${autoPaused ? '▷' : 'Ⅱ'}</span>`;
}
if (gallery) {
  new IntersectionObserver(scheduleAutoplay, { threshold: [0, .01] }).observe(gallery);
  // Pointer hover and button focus do not suspend playback. Use the pause control.
  document.querySelector('#toggle-autoplay').addEventListener('click', () => { autoPaused = !autoPaused; updateAutoplayLabel(); scheduleAutoplay(); });
  document.addEventListener('visibilitychange', scheduleAutoplay);
}
showSlide(0);
updateAutoplayLabel();
let words = ['sea.', 'care.', 'people.', 'purpose.'];
let word = 0;
let rotating = document.querySelector('.rotating-word');
if (!reducedMotion && rotating) setInterval(() => {
  if (document.hidden || rotating.getBoundingClientRect().bottom < 0 || rotating.getBoundingClientRect().top > innerHeight) return;
  rotating.classList.add('out');
  setTimeout(() => { word = (word + 1) % words.length; rotating.textContent = words[word]; rotating.classList.remove('out'); }, 250);
}, 2900);
const dialog = document.querySelector('#brief-dialog');
let dialogTrigger;
function openBrief(event) { dialogTrigger = event.currentTarget; dialog.showModal(); document.body.style.overflow = 'hidden'; }
document.querySelector('#open-brief')?.addEventListener('click', openBrief);
document.querySelector('#open-source').addEventListener('click', openBrief);
document.querySelector('#close-brief').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => {
  const r = dialog.getBoundingClientRect();
  if (event.target === dialog && (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom)) dialog.close();
});
dialog.addEventListener('close', () => { document.body.style.overflow = ''; dialogTrigger?.focus(); });

const localizedNodes = window.siteI18n.copy.map(([selector, ko]) => {
  const node = document.querySelector(selector);
  if (!node) return null;
  return {node, en:node.innerHTML, ko};
}).filter(Boolean);
document.querySelectorAll('[data-ko]').forEach(node => localizedNodes.push({node, en:node.innerHTML, ko:node.dataset.ko}));
const localizedAttributes = window.siteI18n.attributes.map(([selector, attribute, ko]) => {
  const node = document.querySelector(selector);
  if (!node) return null;
  return {node, attribute, en:node.getAttribute(attribute), ko};
}).filter(Boolean);
function setLanguage(nextLanguage) {
  language = nextLanguage === 'ko' ? 'ko' : 'en';
  document.documentElement.lang = language;
  document.body.classList.toggle('is-ko', language === 'ko');
  localizedNodes.forEach(entry => { entry.node.innerHTML = entry[language]; });
  localizedAttributes.forEach(entry => { entry.node.setAttribute(entry.attribute, entry[language]); });
  document.querySelectorAll('[data-language]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.language === language)));
  if (routeTabs.length) document.querySelector('#step-detail').innerHTML = `${language === 'ko' ? '제안하는 핵심 과제' : 'Proposed focus'}<br><strong></strong>`;
  selectStep(selectedStep);
  words = language === 'ko' ? ['바다.', '돌봄.', '사람.', '내일.'] : ['sea.', 'care.', 'people.', 'purpose.'];
  word = 0;
  rotating = document.querySelector('.rotating-word');
  if (rotating) rotating.textContent = words[word];
  document.querySelector('#brief-dialog>.text-link').href = (document.body.dataset.fileRoot || '/') + (language === 'ko' ? 'project-note-ko.txt' : 'project-note.txt');
  document.title = language === 'ko' ? '3-Trillion — 필요한 약이, 필요한 곳에.' : '3-Trillion — Essential medicines. All the way.';
  document.querySelector('meta[name="description"]').content = language === 'ko' ? '3-Trillion이 제안하는 파푸아뉴기니 마누스주 외곽 보건소 필수의약품 공급망 개선 시범사업.' : '3-Trillion proposes a locally led essential medicines supply chain pilot for outer health facilities in Manus Province, Papua New Guinea.';
  const pageName = document.body.dataset.page;
  if(pageName === 'people') document.title = language === 'ko' ? '함께하는 사람들 — 3-Trillion' : 'People — 3-Trillion';
  if(pageName === 'contact') document.title = language === 'ko' ? '연락하기 — 3-Trillion' : 'Contact — 3-Trillion';
  updateAutoplayLabel();
  document.dispatchEvent(new CustomEvent('site:language', {detail:{language}}));
  try { localStorage.setItem('3trillion-language', language); } catch {}
}
document.querySelectorAll('[data-language]').forEach(button => button.addEventListener('click', () => setLanguage(button.dataset.language)));
let savedLanguage = 'en';
try { savedLanguage = localStorage.getItem('3trillion-language') || 'en'; } catch {}
setLanguage(savedLanguage);

// Keep the opening exactly one viewport tall, including the responsive header.
const siteHeader = document.querySelector('.header');
new ResizeObserver(() => document.documentElement.style.setProperty('--header-height', `${siteHeader.offsetHeight}px`)).observe(siteHeader);
const manusArt = document.querySelector('.manus-art');
if (manusArt && !reducedMotion) {
  manusArt.classList.add('is-interactive');
  const centers = [135, 423, 705, 984, 1265];
  const blocks = [...manusArt.querySelectorAll('.color-block')].map((node, index) => ({node, x:centers[index], phase:index * 1.8, energy:0}));
  let pointer = null, artVisible = true, frame = null, lastTime = null;
  const trackPointer = event => {
    const matrix = manusArt.getScreenCTM();
    if (!matrix) return;
    const point = new DOMPoint(event.clientX, event.clientY).matrixTransform(matrix.inverse());
    pointer = {x:point.x, y:point.y};
  };
  manusArt.addEventListener('pointermove', trackPointer);
  manusArt.addEventListener('pointerleave', () => { pointer = null; });
  manusArt.addEventListener('pointercancel', () => { pointer = null; });
  function animateArt(time) {
    frame = null;
    if (!artVisible || document.hidden) { lastTime = null; return; }
    const dt = Math.min((time - (lastTime ?? time)) / 1000, .05);
    lastTime = time;
    blocks.forEach(block => {
      const distance = pointer ? Math.hypot((pointer.x - block.x) / 200, (pointer.y - 220) / 330) : 2;
      const target = Math.max(0, 1 - distance);
      block.energy += (target - block.energy) * Math.min(1, dt * 7);
      block.phase += dt * (.48 + block.energy * 3.2);
      const wave = Math.sin(block.phase), energy = block.energy;
      const x = Math.cos(block.phase * .83) * energy * 35;
      const y = wave * (14 + energy * 76);
      const tilt = Math.sin(block.phase * .73) * energy * 12;
      block.node.setAttribute('transform', `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${tilt.toFixed(2)} ${block.x} 220)`);
    });
    frame = requestAnimationFrame(animateArt);
  }
  function resumeArt() {
    if (artVisible && !document.hidden && frame === null) frame = requestAnimationFrame(animateArt);
  }
  new IntersectionObserver(entries => { artVisible = entries[0].isIntersecting; resumeArt(); }).observe(manusArt);
  document.addEventListener('visibilitychange', resumeArt);
  resumeArt();
}
