# 트랙2: 국가 협력관행 등급과 분야별 케미 도구

기존 AidXray 구상은 폐기하고, 여러 공여국·수원국을 탐색하는 세계지도 기반 도구를 설계하고 있습니다. 현재는 웹사이트 제작 전 연구 단계입니다.

## 먼저 읽을 문서

- [다국가 연구·자료 범위·시연 설계](docs/multi-country-research.md)
- [초기 지표 설계와 평가보고서 검토](docs/research-initial.md): 이후 확장 문서가 우선합니다.
- [계산 설정](research/expansion/processed/methodology_v0.2.json)
- [자료 복합 활용 규칙](research/expansion/processed/source_reuse_matrix.json)
- [지도·상세 화면 데이터 계약](research/expansion/processed/data_contract.json)
- [출처 목록](research/source_registry.json)
- [수집·자료 검증 결과](research/expansion/processed/validation_summary.json)

## 현재 진척

공여국 10개·수원국 24개 범위에서 8개 공여국 소속 발행기관의 고유 IATI 활동 6,371개, 관계가 관측된 210개 국가쌍, GPEDC 765개 쌍·라운드, ATI 2024 기관 51개를 정리했습니다. 기관·파일 표본이며 국가 전체 원조사업의 전수목록은 아닙니다.

국가등급은 GPEDC 역할별 4영역 각 25%의 연구용 시험값입니다. 12등급 경계도 임시 규칙입니다. 케미는 정합성 30%·공동 이행 30%·성과 25%·지속성 15%의 제안이며, 현재 완성 점수는 산출하지 않았습니다. 실제 평가값과 예측·제안을 구분합니다.

시연 검토 경로는 호주 → 솔로몬제도 보건협력 → PNG → 트랙1 마누스 의약품 공급망입니다. PNG는 공통 정책과제에 따른 검토 후보이며 예측 케미 1위나 통계적 최근접 국가라는 뜻이 아닙니다.

## 데이터와 재현

`research/`는 기존 로컬 연구 패키지의 상대 폴더 구조를 유지합니다. 데이터 일부는 용량을 줄인 `.json.gz`이며 `python3 research/unpack.py`로 JSON을 복원할 수 있습니다. 복원 시 기존 파일을 덮어쓰지 않습니다.

`activity-index.json.gz`는 6,371개 활동 전체의 경량 색인입니다. 원래 `activities.json`의 설명·거래·문서 본문 전체를 포함하지 않습니다. `result_observations.json.gz`와 시연용 사업 근거는 별도로 포함했습니다.

대용량 원본 XML/XLSX/PDF, 전체 활동 상세 JSON, 원문 추출 텍스트, 제3자 레지스트리 메타데이터 원본은 로컬에 보관합니다. 원자료 주소·수집일·SHA256·실패 및 본문 확인 상태는 수집 기록과 `local-artifact-manifest.json.gz`에서 확인할 수 있습니다. 공개 원문 재배포 권한을 일괄 가정하지 않습니다.

수집 코드는 `research/scripts/`와 `research/expansion/scripts/`에 있습니다. 전체 재가공에는 수집 기록에 기재된 원자료가 필요하며 외부 API·다운로드 경로가 변경될 수 있습니다. 초기에 수집한 국가 배경자료 등 일부 선행 산출물도 다시 만들어야 합니다. 상세 수집 순서는 데이터 안내를 참고하세요.

- 초기: collect.py → collect_more.py → collect_final.py → collect_crs.py → prepare.py → build_design.py → finish_data.py → catalog.py
- 확장: fetch.py와 jobs1~4.json → normalize.py → finalize.py → document_decisions.py
- Python 3, 초기 XLSX/PDF 가공에는 openpyxl·pypdf가 필요합니다.

## 공개 범위와 다음 검증

기관 간 평가척도 연결, 케미 4영역 코딩·타당화, 전 세계 금액 총계, 추천 알고리즘 검증은 남아 있습니다. 원자료나 평가 결측을 0점으로 대체하지 않습니다. 새로운 웹사이트 구현은 아직 포함하지 않습니다.

이 작업은 저장소 소유자의 지시에 따라 다른 팀원의 사전 승인 없이 main에 직접 기록합니다. 기존 CONTRIBUTING.md의 일반 검토 규칙을 영구 변경하는 작업은 아닙니다.

## 2026-11-05 추가 작업

- [지표 v0.3: 자료 보완·통계 점검·등급 안정성](docs/indicator-optimization.md)
- [양방향 추천 자료와 경량 설계](docs/recommendation-design.md)
- [최신 계산 규칙](research/optimization/processed/methodology_v03.json)
- [추천 규칙](research/recommendations/processed/recommendation_rules.json)

2023년 공통 비교자료로 수원국 24개·공여국 10개 프로필을 준비했습니다. 추천은 첫 선택 국가를 고정하고 두 번째 선택 국가와 유사한 후보를 찾습니다. 미래 케미 추정값은 비워 두었습니다. 국가등급은 원자료 하위결측과 가중치 변화의 불확실성을 함께 제공합니다.

## 2026-11-06 추가 작업

- [케미 산식 연구와 실증 검증](docs/chemistry-methods.md): 과정 정합성 모형과 목표·실적 표준화 모형, 교차검증 및 채택·보류 판단.
- [사업·실적·기관 연결자료 수집 결과](docs/data-linkage.md): IATI 활동 8,077개, 공통 지표 후보 52개 및 PNG 사업 목표 변경 기록.
- [계산식 명세](research/chemistry-methods/processed/formula_specification.json), [모형 채택 판단](research/chemistry-methods/processed/model_adoption_decisions.json).
- [자료 준비 상태](research/data-linkage/processed/data_readiness.json), [수집 집계](research/data-linkage/processed/collection_summary.json), [원출처 목록](research/data-linkage/processed/source_manifest.json).

이 절의 검증 결과가 초기 케미 4영역 제안보다 우선합니다. 과정 정합성 값은 전 분야 조사 표본의 연구용 시험값입니다. 목표·실적 모형은 비교 기준보다 나은 검증 성능을 보이지 못해 공개 순위 채택을 보류했습니다. 새 연결자료도 아직 전 세계 분야별 케미 순위를 확정하지 않습니다.

오늘의 패키지는 `research/chemistry-methods/`와 `research/data-linkage/`에 있습니다. 각 폴더에서 `python3 unpack.py`로 큰 JSON을 복원할 수 있습니다. 원본·수업자료 본문은 로컬에 두고 출처·해시·가공 데이터·처리 코드를 기록했습니다. 상세한 재현 조건은 각 PACKAGE-NOTES.txt를 참고하세요.


## 2026-11-10 웹사이트 구현·확장

- 실행: [website/dist/index.html](website/dist/index.html). 저장소 전체를 내려받은 뒤 이 파일을 열 수 있습니다.
- 한·영 전환, 평면 SVG 국기, CONNECT 마우스 반응, 트랙1 People·Contact, 고정 세계지도와 접이식 국가 패널, 국가쌍 비교를 포함합니다.
- 최신 완전 국가등급 33개와 과거 참고등급 67개를 별도 버전으로 제공합니다. 기존 공표 입력값 평균의 72개 등급과 엄격한 완전자료 기준을 구분합니다.
- 최신 과정 정합성 추정치 230쌍과 과거 집계비율 참고값 273쌍을 별도 색상·시점·산식으로 제공합니다.
- 다자기관 관계 575쌍, UNICEF 활동 777개·실적 요소 3,215개는 별도 근거 목록에 포함했습니다. 원문 기초선·목표·실적과 출처를 확인할 수 있습니다.
- Behind the Numbers에 역할별 입력, 등급 경계, 결측·가중치 민감도, 계층형 베타이항 모형, 검증 결과·구간의 한계를 한·영으로 설명했습니다.
- 지도 데이터와 이미지가 모두 로컬 파일에 포함되어 있습니다. 외부 원문과 실제 이메일 발송에는 인터넷이 필요합니다.
- 검증: JavaScript 구문, 자료 범위·유일성·PNG 원자료 연도, 249개 국기, 상대 파일 링크·앵커, 모바일/데스크톱 주요 흐름 확인. 내장 브라우저의 file:// 제한으로 직접 파일 열기는 자동 확인하지 못했으며 정적 의존성 검사를 별도로 수행했습니다.

이번 기록은 저장소 소유자의 명시적인 직접 커밋 지시에 따른 변경이며, 기존 팀 검토 규칙 자체를 수정하지 않습니다.
