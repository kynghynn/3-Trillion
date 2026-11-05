# optimization

수집 원자료 주소·상태는 jobs 및 manifest, 분석 결과는 processed, 재현 코드는 scripts에 있습니다.

50KB를 넘는 JSON은 gzip으로 보존했습니다. python3 unpack.py로 복원할 수 있습니다. 원래 연구 패키지의 구조를 유지하며, 스크립트는 기존 research/의 선행 자료를 사용합니다. optimization의 finalize.py는 로컬 PDF 추출 텍스트도 필요합니다. recommendations의 prepare.py는 전체 IATI 활동 상세 JSON이 필요하며 경량 색인만으로 대체할 수 없습니다. 전체 상세 JSON은 기존 수집·정규화 코드로 생성합니다.

이번 커밋은 자료 및 설계 준비이며 웹사이트나 검증된 케미 예측 구현이 아닙니다.
