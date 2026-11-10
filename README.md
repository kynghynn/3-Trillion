# 3-Trillion

Team 3-Trillion research project for International Political Economy of Development and Cooperation at SNU.

서울대학교 「개발과 협력의 국제정치경제」 수업의 개발협력 사업 및 개발협력 분석 도구 연구 프로젝트입니다.

## 주요 작업물

- [트랙2 웹사이트](track-2-cooperation-tool/website/dist/index.html): 세계지도·국가 비교·한영 전환·최신/과거 자료·방법론·추가 근거 탐색.

- [트랙2 도구 설계·지표·자료 준비](track-2-cooperation-tool/): 국가 협력관행 등급과 분야별 케미 연구, 자료 보완·통계 점검·양방향 추천 데이터 준비.
- [팀 홈페이지 전체 소스](site/): 2026년 11월 10일 갱신한 Project · People · Contact, 한국어/영어 전환과 지역 개념도, 사업 필요성·성과지표·협력 역할 소개.
- [마누스주 필수의약품 공급망 사업기획서](track-1-aid-project/docs/project-proposal.md): 2026년 10월 20일 작성한 공개자료 조사 및 실행설계 초안.
- [3주차 개인 아이디어](docs/ideas/week-03/): 초기 구상 기록을 보존합니다.
- [저장소 운영 규칙](CONTRIBUTING.md)
- [GitHub Pages 배포 안내](docs/github-pages.md)

## 프로젝트 구성

트랙 1은 파푸아뉴기니 마누스주의 필수의약품 공급망 개선 사업안입니다. 트랙 2는 기존 AidXray 구상을 폐기하고 국가 협력관행 등급과 국가쌍·분야별 케미 도구를 설계하는 연구입니다. 트랙2 세계지도 웹사이트를 구현했습니다. 최신 정합성 모형과 과거 서술형 참고값을 구분해 탐색하며, 미래 성공확률이나 인과적 케미를 검증한 도구는 아닙니다. 현재 홈페이지는 트랙 1 기획을 소개하며 통합 분석이 완료됐다는 의미는 아닙니다.

## 홈페이지 실행

저장소 전체를 내려받아 루트의 `index.html` 또는 `site/index.html`을 엽니다. 별도 설치·빌드·서버·API 키가 필요하지 않습니다. HTML, CSS, JavaScript, SVG와 프로젝트 노트가 모두 포함돼 있습니다. 폴더 구조를 유지해 주세요.

로컬 서버를 사용하려면 저장소 루트에서 `python3 -m http.server 8000`을 실행한 뒤 `http://localhost:8000/`을 엽니다.

[오프라인 전달용 ZIP](downloads/3-trillion-track1-offline.zip)을 내려받아 전체 압축을 해제한 뒤 `index.html`을 열 수도 있습니다. 재생성: `python3 scripts/package-offline.py /tmp/3-trillion-offline`. 기획서 전문은 사이트의 프로젝트 노트에서 내려받을 수 있습니다.

## 현재 상태와 공개용 변경

- 사업은 사전타당성 기획 단계이며 현지 협약, 재원, 시행이 확정되지 않았습니다.
- 공식 GitHub Tag/Release는 아직 부여하지 않았습니다. 기획서 본문의 v1.0은 기존 문서의 표기이며 저장소 공식 릴리스가 아닙니다.
- 사용자에게 사용 허가를 확인한 팀원 사진·소속·이메일을 People에 반영했습니다. Contact의 구독·해지 양식은 요청 초안 작성·복사·저장과 이메일 앱 연결을 제공하며, 자동 발송·등록하지 않습니다.
- 사용자에게 교수님 사진·정보 사용 허가를 확인한 뒤 공식 프로필 출처와 함께 반영했습니다.
- 중요한 변경은 별도 브랜치와 Pull Request를 사용하고 팀원 1명 이상 검토 후 main에 합칩니다.

## 라이선스

팀의 코드·문서 라이선스는 아직 결정하지 않았습니다. 공개 저장소라는 사실만으로 재배포 허가가 부여되지는 않습니다. 외부 자료의 권리는 각 권리자에게 있으며 기획서의 참고문헌과 원문 이용 조건을 확인해 주세요.
