"""Validate and package only the static deliverable files, with no host dependency."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import shutil,sys,zipfile,hashlib
source=Path(__file__).resolve().parents[1]/'site'
destination=Path(sys.argv[1]).resolve()
output=destination/'3-Trillion-track1'
output.mkdir(parents=True,exist_ok=True)
files=[p for p in sorted(source.rglob('*')) if p.is_file() and not any(part.startswith('.') for part in p.relative_to(source).parts) and not p.name.startswith('qa-') and not p.name.startswith('person-') and p.name not in ['project-note.txt','project-note-ko.txt']]
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        for k in ['href','src']:
            if k in a:self.links.append(a[k])
parsers={}
for p in files:
    if p.suffix=='.html':
        h=Links();h.feed(p.read_text());assert len(h.ids)==len(set(h.ids)),f'Duplicate id: {p}';parsers[p.resolve()]=h
for page,h in parsers.items():
    for link in h.links:
        u=urlsplit(link)
        if u.scheme or u.netloc:continue
        assert not u.path.startswith('/'),f'Host-dependent path: {link}'
        target=(page.parent/unquote(u.path)).resolve() if u.path else page
        assert target.exists(),f'Missing file: {link}'
        assert target.is_file(),f'Directory navigation cannot open from disk: {link}'
        if u.fragment and target in parsers:assert unquote(u.fragment) in parsers[target].ids,f'Missing anchor: {link}'
for p in files:
    target=output/p.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
readme='''3-Trillion · Track 1 / 파일형 웹사이트

시작하기
1. ZIP 전체를 압축 해제하세요.
2. 3-Trillion-track1 폴더 안의 index.html을 Chrome, Edge 또는 Safari로 여세요.
3. index.html만 옮기지 말고 폴더 전체를 함께 전달하세요.
ChatGPT 계정, 웹서버, 별도 프로그램 설치는 필요하지 않습니다.

인터넷 없이 시연 가능한 기능
- Project / People / Contact 페이지 이동과 한·영 전환
- MANUS와 People의 H 마우스 반응
- 네 단계 공급망 설명과 키보드 조작
- 3초 갤러리 자동 전환 및 일시정지
- 사업 필요성·지역 개념도·성과지표·협력 역할
- 팀원 사진·소속·이메일 표시
- 프로젝트 노트 열기와 한국어 사업기획서 전문 다운로드
- 메일링리스트 신청/해지 요청 초안 작성·복사·파일 저장

실제 이메일 발송, GitHub, 외부 출처 링크에는 인터넷과 해당 앱이 필요합니다.
메일링리스트 폼은 요청을 준비하는 기능이며, 자동 등록하거나 메일을 보내지 않습니다.
브라우저가 클립보드 복사를 허용하지 않으면 표시되는 텍스트를 직접 복사하세요.
운영체제의 동작 줄이기 설정에 따라 장식 애니메이션은 줄어들 수 있습니다.

사업기획서
원본: documents/project-proposal-ko.md (2026-10-20 v1.0, 원문 그대로)
웹사이트는 기획 단계의 제안을 소개합니다. 실제 사업 실적이나 확정 계약이 아닙니다.
배송은 월 2회 방문 검토안이며 실제 노선·빈도는 현지 검증 후 결정합니다.

English
Unzip the whole folder, then open index.html in Chrome, Edge or Safari.
No login, server, installation or internet is needed for the on-page demonstration.
Keep the entire folder together. External links and actual email sending need internet.
The mailing form only prepares a draft; it does not send mail or register subscribers.
The complete original Korean proposal is included in documents/project-proposal-ko.md.
'''
(output/'READ-ME.txt').write_text(readme)
archive=destination/'3-Trillion-track1-offline.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(output/p.relative_to(source),Path(output.name)/p.relative_to(source))
    z.write(output/'READ-ME.txt',Path(output.name)/'READ-ME.txt')
print(archive)
print(f'{len(files)+1} files; all local files, anchors and relative navigation validated.')
print('Proposal SHA-256:',hashlib.sha256((output/'documents/project-proposal-ko.md').read_bytes()).hexdigest())
