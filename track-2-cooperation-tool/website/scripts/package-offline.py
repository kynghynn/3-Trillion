from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,shutil,zipfile,sys
site=Path(__file__).resolve().parents[1];src=site/'dist';dest=Path(sys.argv[1]).resolve();dest.mkdir(parents=True,exist_ok=True)
class Links(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  for key in ['src','href']:
   if key in a:self.refs.append(a[key])
parsers={}
for p in src.rglob('*.html'):
 h=Links();h.feed(p.read_text());assert len(h.ids)==len(set(h.ids)),p;parsers[p.resolve()]=h
for p,h in parsers.items():
 for ref in h.refs:
  u=urlsplit(ref)
  if u.scheme or u.netloc:continue
  assert not u.path.startswith('/'),(p,ref)
  target=(p.parent/unquote(u.path)).resolve() if u.path else p
  assert target.is_file(),(p,ref)
  if u.fragment and target in parsers:assert unquote(u.fragment) in parsers[target].ids,(p,ref)
d=json.load(open(src/'assets/data.json'))
assert len(d['gradeRegistry'])==100 and sum(g['version']=='v03' for g in d['gradeRegistry'])==33
assert len(d['chemistryRegistry'])==1078
assert sum(x['partner_type']=='Bilateral' for x in d['chemistryRegistry'])==503
assert len(d['activities'])==777 and len(d['observations'])==3215
for c in d['countries']:assert (src/'assets/flags'/(c['iso2'].lower()+'.svg')).exists(),c['iso2']
for n in ['app.js','language.js','methods.js','evidence.js']:
 s=(src/n).read_text();assert 'fetch(' not in s and 'XMLHttpRequest' not in s
readme='''3-Trillion Track 2 — 2026.11.10

ZIP 전체를 압축 해제하고 3-Trillion-track2 폴더의 index.html을 브라우저로 여세요.
폴더 전체를 함께 보관하세요. 서버, 설치, ChatGPT 로그인은 필요하지 않습니다.
지도·패널·국가 비교·최신/과거 전환·검색·한영 전환·SVG 국기·CONNECT 반응·People·Contact·수식 설명·근거 목록은 로컬 파일로 제공됩니다.
외부 원문 링크와 실제 이메일 발송에는 인터넷 또는 이메일 앱이 필요합니다.
Contact의 메일링 기능은 요청 초안을 작성하며 자동 발송/등록하지 않습니다.

자료: 최신 완전 국가등급 33 + 과거 참고 67. 최신 모형 230쌍 + 과거 참고 273쌍.
다자기관 관계 575쌍, UNICEF 활동 777개, 실적 요소 3215개는 별도 근거로 제공합니다.
최신과 과거 점수는 서로 다른 산식/시점이며 지도 버전을 구분합니다.

English: unzip the whole archive, then open index.html. Keep all files together.
No server, installation or ChatGPT login is needed. Original online sources and actual email sending require connectivity.
Testing note: interactive checks used local HTTP preview. The embedded test browser prohibits file:// navigation; local link/dependency checks passed separately.
'''
(src/'READ-ME.txt').write_text(readme)
folder=dest/'3-Trillion-track2';shutil.copytree(src,folder,dirs_exist_ok=True)
archive=dest/'3-Trillion-track2-offline.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(folder.rglob('*')):
  if p.is_file() and not p.name.startswith('.'):z.write(p,p.relative_to(dest))
print('Validated relative file links, anchors, data counts, all 249 SVG flags, and no runtime data fetches.')
print(archive)
