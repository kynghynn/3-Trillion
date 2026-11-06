케미 산식 연구 — 2026-11-06
먼저 케미_산식_연구와_실증검증.txt를 읽으세요.

핵심 파일
processed/formula_specification.json: 실제 구현한 두 모형의 식과 적용범위.
processed/process_scores.json: 전 분야 조사 표본의 정합성 시험값. 분야별 효과성 점수 아님.
processed/target_standardized_scores.json: 채택 보류된 연구 실험값. 공개 순위에 사용 금지.
processed/model_adoption_decisions.json: 채택·보류 근거.
processed/process_cross_validation.json, target_nested_validation.json: 검증 결과.
processed/required_data_schema.json: 추가 수집에 필요한 필드.
processed/data_inventory.json: 데이터 수와 분야 연결 주의사항.
figures/model_validation.png: 검증 그림.

재현 순서
Python 환경에 requirements-lock.txt의 라이브러리를 준비한다.
scripts/prepare.py → process_model.py → target_model.py → diagnostics.py → summarize.py
기존 outputs/track2_research_20261104 원자료와 가공자료가 선행 입력이다.
수업 PDF 추출은 조사기록이며 공유 시 원저작물 재배포를 별도 확인한다.
.venv/는 로컬 작업 환경이며 데이터·웹사이트 배포물에 포함하지 않는다.
이번 턴은 연구와 계산까지 수행했으며 웹사이트는 만들지 않았다.
