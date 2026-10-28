const locale = () => document.documentElement.lang;
const t = (en, ko) => locale() === 'ko' ? ko : en;
const originalAlt = new Map();
document.querySelectorAll('[data-alt-ko]').forEach(image => originalAlt.set(image, image.alt));
const teamGrid = document.querySelector('#people-grid');
document.querySelectorAll('[data-view]').forEach(button => {
  button.addEventListener('click', () => {
    const list = button.dataset.view === 'list';
    teamGrid.classList.toggle('list-view', list);
    document.querySelectorAll('[data-view]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  });
});
function updatePageLanguage() {
  document.querySelectorAll('[data-view]').forEach(button => {
    const label = button.dataset.view === 'grid' ? t('Grid view', '그리드 보기') : t('List view', '리스트 보기');
    button.setAttribute('aria-label', label);
    button.title = label;
  });
  if (teamGrid) {
    const nameKey = locale() === 'ko' ? 'nameKo' : 'nameEn';
    [...teamGrid.querySelectorAll('.person-card')]
      .sort((a, b) => a.dataset[nameKey].localeCompare(b.dataset[nameKey], locale()))
      .forEach((card, index) => {
        card.querySelector('.person-number').textContent = String(index + 1).padStart(2, '0');
        teamGrid.append(card);
      });
  }
  originalAlt.forEach((en, image) => { image.alt = locale() === 'ko' ? image.dataset.altKo : en; });
  document.querySelectorAll('.copy-status').forEach(node => { node.textContent = ''; });
}
document.addEventListener('site:language', updatePageLanguage);
updatePageLanguage();
