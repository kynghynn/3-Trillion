const locale = () => document.documentElement.lang;
const t = (en, ko) => locale() === 'ko' ? ko : en;
const originalAlt = new Map();
document.querySelectorAll('[data-alt-ko]').forEach(image => originalAlt.set(image, image.alt));
const teamGrid = document.querySelector('#people-grid');
async function copyText(text, status) {
  try {
    await navigator.clipboard.writeText(text);
    status.textContent = t('Copied.', '복사했습니다.');
  } catch {
    status.textContent = t('Select and copy the text below.', '아래 내용을 선택해 복사해 주세요.');
    const fallback = document.createElement('textarea');
    fallback.className = 'copy-fallback';
    fallback.value = text;
    fallback.readOnly = true;
    fallback.setAttribute('aria-label', t('Text to copy', '복사할 내용'));
    status.append(fallback);
    fallback.focus();
    fallback.select();
  }
}
document.querySelector('#copy-email')?.addEventListener('click', () => copyText('kyonghyeon29@snu.ac.kr', document.querySelector('#copy-status')));
const newsletter = document.querySelector('#newsletter-form');
const result = document.querySelector('#newsletter-result');
let draft = null;
let preferenceEdited = false;
const emailLanguage = document.querySelector('#newsletter-language');
emailLanguage?.addEventListener('change', () => { preferenceEdited = true; });
function resetDraft() {
  if (!result) return;
  result.hidden = true;
  draft = null;
  document.querySelector('#request-copy-status').textContent = '';
  document.querySelector('#send-request').href = 'mailto:kyonghyeon29@snu.ac.kr';
}
function updateRequestMode() {
  if (!newsletter) return;
  const unsubscribing = newsletter.elements.request.value === 'unsubscribe';
  const consent = document.querySelector('#newsletter-consent');
  consent.required = !unsubscribing;
  consent.closest('.consent').hidden = unsubscribing;
  resetDraft();
}
newsletter?.querySelectorAll('[name=request]').forEach(radio => radio.addEventListener('change', updateRequestMode));
newsletter?.addEventListener('input', resetDraft);
newsletter?.addEventListener('submit', event => {
  event.preventDefault();
  if (!newsletter.reportValidity()) return;
  const email = document.querySelector('#newsletter-email').value.trim();
  const subscribing = newsletter.elements.request.value === 'subscribe';
  const preferred = emailLanguage.value === 'ko' ? '한국어 / Korean' : 'English / 영어';
  const subject = `[3-Trillion] ${subscribing ? 'Mailing list subscription request / 구독 신청' : 'Mailing list unsubscribe request / 구독 해지'}`;
  const body = locale() === 'ko'
    ? `3-Trillion 팀에게,\n\n메일링리스트 ${subscribing ? '구독을 신청합니다' : '구독 해지를 요청합니다'}.\n\n이메일: ${email}\n${subscribing ? `수신 언어: ${preferred}\n\n프로젝트 소식 수신을 위해 위 이메일 주소를 팀에 제공하는 데 동의합니다.\n` : ''}\n요청 처리가 완료되면 알려주세요.\n감사합니다.`
    : `Hello 3-Trillion,\n\nPlease ${subscribing ? 'add me to' : 'remove me from'} your mailing list.\n\nEmail: ${email}\n${subscribing ? `Preferred language: ${preferred}\n\nI agree to share this email address with the team to receive project updates.\n` : ''}\nPlease let me know when my request has been processed.\nThank you.`;
  draft = { subject, body };
  document.querySelector('#send-request').href = `mailto:kyonghyeon29@snu.ac.kr?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  document.querySelector('#newsletter-status').textContent = t(
    'Your request is ready, but has not been sent. Open your email app and send it to complete the request. The team will process it manually.',
    '요청 메일을 준비했습니다. 아직 전송되지 않았습니다. 이메일 앱을 열고 직접 보내기를 완료해 주세요. 팀이 요청을 확인한 뒤 처리합니다.'
  );
  result.hidden = false;
});
document.querySelector('#copy-request')?.addEventListener('click', () => {
  if (!draft) return;
  copyText(`To: kyonghyeon29@snu.ac.kr\nSubject: ${draft.subject}\n\n${draft.body}`, document.querySelector('#request-copy-status'));
});
function updatePageLanguage() {
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
  if (emailLanguage && !preferenceEdited) emailLanguage.value = locale();
  document.querySelectorAll('.copy-status').forEach(node => { node.textContent = ''; });
  updateRequestMode();
}
document.addEventListener('site:language', updatePageLanguage);
updatePageLanguage();

// Local request export lets the mailing workflow be demonstrated without a network.
let requestDownloadUrl = null;
const saveRequest = document.querySelector('#save-request');
if (newsletter && saveRequest) {
  newsletter.addEventListener('submit', () => {
    if (!draft) return;
    if (requestDownloadUrl) URL.revokeObjectURL(requestDownloadUrl);
    const content = `To: kyonghyeon29@snu.ac.kr\nSubject: ${draft.subject}\n\n${draft.body}\n\nThis is a saved draft. It has not been sent. / 저장한 초안이며 아직 발송되지 않았습니다.\n`;
    requestDownloadUrl = URL.createObjectURL(new Blob([content], {type:'text/plain;charset=utf-8'}));
    saveRequest.href = requestDownloadUrl;
  });
}

// Each H keeps its gentle motion and responds independently to the nearby pointer.
const peopleSymbol = document.querySelector('.people-symbol');
if (peopleSymbol && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  peopleSymbol.classList.add('is-interactive');
  const letters = [...peopleSymbol.querySelectorAll('i')].map((node,index) => ({node,phase:index*1.5,energy:0,target:0,x:0,y:0}));
  letters.forEach(letter => {
    letter.node.addEventListener('pointermove', event => {
      const r = letter.node.getBoundingClientRect();
      letter.target=1; letter.x=(event.clientX-r.left)/r.width-.5; letter.y=(event.clientY-r.top)/r.height-.5;
    });
    letter.node.addEventListener('pointerleave',()=>{letter.target=0;});
    letter.node.addEventListener('pointercancel',()=>{letter.target=0;});
  });
  let visible=true, frame=null, last=null;
  function animate(time) {
    frame=null;
    if (!visible || document.hidden) {last=null;return;}
    const dt=Math.min((time-(last??time))/1000,.05);last=time;
    letters.forEach(letter=>{
      letter.energy+=(letter.target-letter.energy)*Math.min(1,dt*6);
      letter.phase+=dt*(.5+letter.energy*2.3);
      const e=letter.energy;
      const y=Math.sin(letter.phase)*(3+e*13)+letter.y*e*12;
      const rotate=Math.cos(letter.phase*.8)*(1+e*6)+letter.x*e*9;
      letter.node.style.transform=`translateY(${y.toFixed(2)}px) rotate(${rotate.toFixed(2)}deg)`;
      letter.node.querySelector('b').style.transform=`translateY(${(Math.sin(letter.phase)*(8+e*38)).toFixed(2)}%) rotate(${(rotate*1.3).toFixed(2)}deg)`;
    });
    frame=requestAnimationFrame(animate);
  }
  function resume(){if(visible&&!document.hidden&&frame===null)frame=requestAnimationFrame(animate);}
  new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;resume();}).observe(peopleSymbol);
  document.addEventListener('visibilitychange',resume);resume();
}
