# AidXray 저장소 운영 규칙

## 1. 기본 원칙

1. 모든 팀원은 자신의 GitHub 계정으로 작업한다.
2. `main`에는 현재 기준으로 가장 신뢰할 수 있는 파일만 둔다.
3. 파일명으로 수정 이력을 관리하지 않는다.
4. 한 파일의 최신본은 원칙적으로 하나만 유지한다.
5. 중요한 변경은 커밋 메시지에 무엇을 변경했는지 기록한다.
6. 공개 저장소에는 개인정보, 비밀번호, API 키, 비공개 설문 응답을 올리지 않는다.
7. 각 팀원이 자신의 작업을 직접 올려 기여 기록을 남긴다.

---

## 2. 파일명 규칙

### 기본 형식

파일명은 다음 규칙을 따른다.

- 영문 소문자 사용
- 단어 사이는 하이픈 `-` 사용
- 띄어쓰기 사용 금지
- 한글 파일명은 가급적 사용하지 않음
- 괄호, 특수문자 사용 금지
- 파일명을 보고 내용을 짐작할 수 있도록 작성

좋은 예:

```text
project-proposal.md
aidxray-methodology.md
country-analysis-nepal.md
aid-effectiveness-indicators.csv
user-guide.pdf
```

피해야 할 예:

```text
사업계획서 최종.pdf
사업계획서_진짜최종_수정2.pdf
new document.docx
자료(최종).pdf
김철수작업물.md
```

### 날짜가 필요한 파일

회의록, 조사 기록, 주간 보고처럼 시간 순서가 중요한 자료에만 날짜를 붙인다.

날짜 형식은 항상 `YYYY-MM-DD`로 통일한다.

```text
2026-09-22-team-meeting.md
2026-10-03-user-interview.md
2026-11-15-progress-report.pdf
```

다음 형식은 사용하지 않는다.

```text
9월22일회의록.md
0922회의.md
22-09-26-meeting.md
```

### 사람 이름 사용 금지

담당자를 표시하기 위해 파일명에 이름을 넣지 않는다.

```text
kyonghyeon-report.md       # 사용하지 않음
project-background.md      # 권장
```

작성자는 GitHub 기록으로 확인할 수 있다. 설문·인터뷰 자료에서도 실명 대신 익명 코드를 사용한다.

```text
interview-p01.md
interview-p02.md
```

---

## 3. 문서 형식 규칙

### Markdown `.md`

GitHub에서 계속 수정하고 공동 관리할 문서에 사용한다.

사용 대상:

- 프로젝트 소개
- 연구 계획
- 방법론 설명
- 회의록
- 조사 기록
- 사용 설명서
- 참고문헌 목록

예:

```text
README.md
project-overview.md
aidxray-methodology.md
2026-09-22-team-meeting.md
```

### PDF `.pdf`

형식과 페이지 구성이 확정된 제출·배포 문서에 사용한다.

사용 대상:

- 수업 제출본
- 공식 계획서
- 중간·최종 보고서
- 외부 공개용 보고서

Markdown 또는 Google Docs에서 작업한 후 확정된 시점에 PDF로 내보낸다.

### Word `.docx`

교수님이나 조교님이 요구하거나 Word 원본 보존이 필요한 경우에만 사용한다. 기본 협업 형식으로는 사용하지 않는다.

### 데이터 파일

- 표 형태의 공개 데이터: `.csv`
- 복잡한 수식이나 여러 시트가 필요한 원본: `.xlsx`
- 프로그램에서 사용하는 구조화 데이터: `.json`

CSV는 가능하면 UTF-8 형식으로 저장한다.

### 웹 결과물

```text
.html
.css
.js
```

이미지는 다음 형식을 우선 사용한다.

```text
.svg  # 로고, 아이콘, 도표
.png  # 화면 캡처, 투명 이미지
.jpg  # 사진
.webp # 웹용 압축 이미지
```

---

## 4. 버전 표기 규칙

### 작업 중인 파일

일상적인 수정에는 버전 번호를 파일명에 넣지 않는다.

```text
aidxray-methodology.md
```

이 파일을 수정하고 다시 저장하면 GitHub가 이전 버전을 자동으로 기록한다.

다음처럼 파일을 계속 복제하지 않는다.

```text
aidxray-methodology-v2.md
aidxray-methodology-new.md
aidxray-methodology-final.md
aidxray-methodology-final-final.md
```

### 공식 버전

중간 발표, 최종 제출, 공개 배포처럼 중요한 시점에만 버전을 부여한다.

버전은 `v주버전.부버전.수정버전` 형식을 사용한다.

```text
v0.1.0
v0.2.0
v0.2.1
v1.0.0
```

각 숫자의 의미는 다음과 같다.

- 첫 번째 숫자: 핵심 구조나 방법론이 크게 달라짐
- 두 번째 숫자: 새로운 기능·지표·분석 요소가 추가됨
- 세 번째 숫자: 오탈자, 오류, 표현 등 작은 부분을 수정함

AidXray 적용 예:

```text
v0.1.0  최초 아이디어와 기본 구조
v0.2.0  평가 요소와 정보 구조 추가
v0.3.0  첫 번째 작동 프로토타입
v0.9.0  수업 최종 발표 직전 시험판
v1.0.0  최초 공식 공개본
v1.1.0  새로운 지표나 시각화 기능 추가
v1.1.1  계산 오류나 문서 오탈자 수정
v2.0.0  평가 방법론을 근본적으로 변경
```

공식 공개 전 시험판은 다음과 같이 표시할 수 있다.

```text
v1.0.0-beta.1
v1.0.0-rc.1
```

- `beta`: 기능은 있으나 충분한 검증이 필요함
- `rc`: 공식 공개 직전의 후보 버전

### PDF 파일의 버전

공식적으로 내보낸 PDF에는 버전을 붙인다.

```text
aidxray-project-proposal-v0.2.0.pdf
aidxray-final-report-v1.0.0.pdf
aidxray-user-guide-v1.0.0.pdf
```

초안 Markdown에는 버전을 붙이지 않고, 확정된 PDF와 GitHub Release에만 붙인다.

---

## 5. GitHub Release 규칙

일상적인 수정마다 Release를 만들지 않는다. 다음과 같은 중요한 시점에만 만든다.

- 중간 발표본 공개
- 작동 가능한 프로토타입 완성
- 최종 보고서 제출
- 외부 공개 가능한 공식 버전 완성
- 방법론의 중요한 개정

Release 제목과 Tag는 동일하게 작성한다.

```text
Tag: v0.3.0
Title: AidXray v0.3.0
```

Release 설명에는 다음 내용을 적는다.

```markdown
## 주요 변경 사항

- 국가별 원조 환경 정보 구조 추가
- 사업 위험요인 분류 개선
- 결과 화면의 설명 문구 수정

## 포함된 결과물

- AidXray 프로토타입
- 방법론 설명서
- 사용 예시

## 알려진 한계

- 일부 지표는 아직 시험 단계임
- 데이터가 없는 국가에서는 결과가 제한될 수 있음
```

---

## 6. 폴더 구조

팀의 두 트랙과 통합 결과물을 구분하기 위해 다음 구조를 사용한다.

```text
README.md
CONTRIBUTING.md
LICENSE
docs/
  project-overview.md
  meetings/
  references/
track-1-aid-project/
  README.md
  reports/
  data/
  assets/
track-2-aidxray/
  README.md
  docs/
  data/
  src/
  tests/
  assets/
integration/
  README.md
  reports/
  site/
deliverables/
  interim/
  final/
```

각 폴더의 용도는 다음과 같다.

### `README.md`

저장소의 첫 화면이자 전체 프로젝트의 목차이다.

포함할 내용:

- 프로젝트 이름과 한 줄 소개
- 프로젝트의 목적
- 두 트랙에 대한 설명
- 주요 결과물 링크
- 현재 버전
- 사용 방법
- 라이선스

### `docs/`

팀 전체에 적용되는 문서를 저장한다.

```text
docs/
  project-overview.md
  meetings/
    2026-09-22-team-meeting.md
  references/
    bibliography.md
```

### `track-1-aid-project/`

특정 국가에 적용할 개발협력 사업안을 저장한다.

```text
track-1-aid-project/
  README.md
  reports/
  data/
  assets/
```

### `track-2-aidxray/`

AidXray 도구와 방법론을 저장한다.

```text
track-2-aidxray/
  README.md
  docs/
    methodology.md
    indicator-definitions.md
    user-guide.md
  data/
  src/
  tests/
  assets/
```

### `integration/`

첫 번째 트랙의 사업안에 AidXray를 적용한 통합 결과물을 저장한다.

```text
integration/
  README.md
  reports/
  site/
```

### `deliverables/`

교수님·조교님에게 제출할 확정 결과물만 저장한다.

```text
deliverables/
  interim/
    aidxray-interim-report-v0.5.0.pdf
  final/
    aidxray-final-report-v1.0.0.pdf
```

작업 중인 초안은 이 폴더에 넣지 않는다.

---

## 7. 커밋 메시지 규칙

커밋 메시지는 다음 형식을 사용한다.

```text
종류: 변경 내용
```

종류는 다음 중 하나를 선택한다.

- `docs`: 문서 추가 또는 수정
- `feat`: 새로운 기능 추가
- `fix`: 오류 수정
- `data`: 데이터 추가 또는 수정
- `design`: 화면이나 디자인 수정
- `test`: 시험·검증 자료 추가
- `chore`: 폴더 정리 등 기타 관리 작업

예:

```text
docs: add AidXray project background
docs: revise indicator definitions
feat: add country comparison page
fix: correct aid score calculation
data: add Nepal development indicators
design: update dashboard color scheme
chore: reorganize report folders
```

한 커밋에는 가능한 한 하나의 목적만 담는다.

좋은 예:

```text
docs: add methodology limitations
```

피해야 할 예:

```text
update
수정
파일 올림
여러가지 변경
final version
```

---

## 8. 브랜치 이름 규칙

작은 문서 수정은 초기에는 `main`에서 직접 작업해도 된다. 다만 웹 도구, 핵심 방법론, 데이터처럼 중요한 작업은 별도의 브랜치에서 진행한다.

브랜치 이름은 다음 형식을 사용한다.

```text
작업종류/짧은-설명
```

예:

```text
docs/methodology
feat/country-comparison
fix/score-calculation
data/nepal-indicators
design/dashboard-layout
```

사람 이름을 브랜치명으로 사용하지 않는다.

```text
kyonghyeon-branch       # 사용하지 않음
feat/risk-dashboard     # 권장
```

작업이 끝나면 Pull Request를 만들고, 최소 한 명의 팀원이 확인한 후 `main`에 합친다.

---

## 9. 문서 수정 충돌 방지 규칙

1. 작업을 시작하기 전에 팀 채팅에 수정할 파일을 알린다.
2. 두 명이 같은 파일을 동시에 대규모로 수정하지 않는다.
3. 큰 보고서는 장별로 Markdown 파일을 분리할 수 있다.
4. 작업이 끝나면 오래 미루지 말고 바로 업로드한다.
5. 다른 사람의 작업을 덮어쓰지 않는다.
6. 충돌이 발생하면 양쪽 내용을 확인한 후 합친다.

큰 보고서를 나누는 예:

```text
reports/
  01-executive-summary.md
  02-background.md
  03-methodology.md
  04-application-case.md
  05-expected-impact.md
  06-limitations.md
```

---

## 10. 데이터 관리 규칙

데이터는 다음과 같이 구분한다.

```text
data/
  raw/
  processed/
  sample/
  README.md
```

- `raw/`: 원본 데이터
- `processed/`: 분석을 위해 정리한 데이터
- `sample/`: 도구 시연용 소규모 데이터
- `README.md`: 출처, 수집일, 변수 설명, 이용 조건

원본 데이터는 특별한 이유 없이 직접 수정하지 않는다. 정제한 결과는 `processed`에 별도로 저장한다.

외부 데이터 파일명은 출처와 연도를 포함한다.

```text
world-bank-2025-development-indicators.csv
oecd-2024-aid-disbursements.csv
```

각 데이터의 `README.md`에는 다음 정보를 기록한다.

- 자료명
- 제공 기관
- 원본 주소
- 내려받은 날짜
- 이용 조건 또는 라이선스
- 데이터에 가한 변경
- 개인정보 포함 여부

---

## 11. 절대 올리지 않는 자료

다음 자료는 저장소에 올리지 않는다.

- 비밀번호
- API 키
- 개인 이메일과 전화번호
- 실명이 포함된 설문·인터뷰 원본
- 공개 동의를 받지 않은 사진
- 저작권상 재배포할 수 없는 문서
- 출처를 확인할 수 없는 데이터
- 대용량 임시 파일
- 자동으로 생성되는 불필요한 시스템 파일

민감한 데이터가 필요한 경우 공개 저장소 밖에서 별도로 관리하고, 저장소에는 익명화된 자료나 예시 데이터만 올린다.

---

## 12. 팀의 표준 작업 순서

1. 맡은 작업과 관련된 기존 파일을 확인한다.
2. 중요한 작업이라면 새 브랜치를 만든다.
3. 파일명과 폴더 위치가 규칙에 맞는지 확인한다.
4. 하나의 명확한 작업 단위로 수정한다.
5. 변경 내용을 설명하는 커밋 메시지를 작성한다.
6. 중요한 변경은 Pull Request로 팀원 검토를 받는다.
7. 검토가 끝나면 `main`에 합친다.
8. 공식 발표나 제출 시점에만 버전 Tag와 Release를 만든다.
9. 공식 PDF는 `deliverables` 폴더와 해당 Release에 올린다.
