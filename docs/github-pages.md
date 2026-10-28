# GitHub Pages 배포

이 저장소는 빌드 없는 정적 HTML/CSS/JavaScript 사이트입니다. 루트 `index.html`이 `site/index.html`로 연결하고 사이트 내부는 상대 경로를 사용합니다.

## 팀원 검토 후 최초 배포

1. 홈페이지·기획서 Pull Request를 팀원 1명 이상이 검토한 뒤 `main`에 합칩니다.
2. 저장소 **Settings → Pages → Build and deployment**로 이동합니다.
3. **Source: Deploy from a branch**, **Branch: main**, **Folder: /(root)**를 선택하고 **Save**를 누릅니다.
4. Actions의 `pages build and deployment` 작업이 성공하면 Pages 화면의 방문 링크를 확인합니다.

예상 주소: https://kynghynn.github.io/3-Trillion/ — Pages를 활성화하고 첫 배포가 성공해야 사용할 수 있습니다.

이 업로드 작업에서는 Pages를 켜지 않습니다. 향후 위 설정만으로 배포할 수 있으며 `.nojekyll`은 Jekyll 변환 없이 파일을 제공하도록 합니다. 별도의 의존성 설치나 빌드 명령은 없습니다.

## 수정과 점검

사이트의 최신 소스는 `site/` 한 곳에서 관리합니다. `site/index.html`, `site/people/index.html`, `site/contact/index.html`이 페이지이며 `styles.css`, `app.js`, `i18n.js`, `pages.js`, `assets/`가 구성 요소입니다. Java가 아닌 JavaScript를 사용합니다.

메뉴 이동, 한·영 전환, 운영 방식 자동 갤러리, People 그리드·리스트, 프로젝트 노트 내려받기, 모바일 화면을 확인합니다. 외부 GitHub·공식 프로필 링크는 인터넷이 필요합니다. 메일링리스트는 팀 공용 이메일 확보 전까지 신청을 받지 않습니다.

[GitHub 공식 배포 소스 설정 안내](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
