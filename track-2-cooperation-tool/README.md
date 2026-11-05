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
