# RISK_REGISTER.md

| ID | 리스크 | 원인 | 영향 | 대응 |
|---|---|---|---|---|
| R-001 | 작은 물체 탐지 실패 | cell_phone/wallet 크기 작음 | 이벤트 실패 | wallet 제외, imgsz 960 실험, 가까운 데이터 추가 |
| R-002 | MacBook FPS 낮음 | 모델 과중 | 시연 불안정 | small/nano 모델 사용, imgsz 640 유지 |
| R-003 | ID switch | tracking 한계 | owner 관계 깨짐 | ByteTrack/BoT-SORT 비교, threshold 조정 |
| R-004 | 방치물 오탐 | owner 등록 기준 약함 | 잘못된 경고 | owner_min_seconds 증가 |
| R-005 | 도난 의심 오탐 | 지나가는 사람 오인 | 발표 신뢰도 저하 | suspicious_min_seconds 증가, removed 조건 강화 |
| R-006 | 자동 라벨 품질 낮음 | pretrained 한계 | 학습 성능 저하 | val/test 수동 검수, active learning |
| R-007 | 데이터셋 leakage | 같은 영상 프레임이 train/val/test 섞임 | mAP 과대평가 | split by source video |
| R-008 | Windows/Mac 경로 오류 | separator hardcoding | 실행 실패 | pathlib 강제 |
| R-009 | CUDA 의존 | 학습 코드가 runtime에 CUDA 요구 | MacBook 실행 실패 | runtime은 cuda optional |
| R-010 | 발표 웹캠 실패 | 권한/조명/환경 문제 | 시연 실패 | sample video fallback 준비 |
| R-011 | 실제 도난 확정 표현 | 문구 실수 | 윤리/안전 문제 | theft_suspected만 사용 |
| R-012 | 모델 파일 누락 | 발표 전 복사 누락 | 실행 실패 | models/best_demo.pt 체크리스트 |

## 고위험 대응 원칙

- 웹캠 실패는 sample video로 즉시 전환한다.
- FPS가 낮으면 `yolo small 640` 또는 `nano 640`으로 전환한다.
- 도난 의심 오탐이 많으면 시연에서는 `missing_grace_seconds`와 `suspicious_min_seconds`를 늘린다.
- cell_phone이 불안정하면 발표 핵심 객체에서 제외하고 bag 중심으로 진행한다.

## R-READY-001: 실제 데이터 수집 전 과도한 완료 선언

- Risk: 데이터와 영상이 아직 없는데 Codex가 학습/시연까지 완료했다고 보고할 수 있음.
- Impact: 최종 단계에서 재작업 발생.
- Mitigation:
  - 데이터 준비 전 완료 기준과 데이터 준비 후 완료 기준을 분리한다.
  - mAP, FPS, demo success는 실제 측정 전에는 `pending`으로 둔다.
  - `READINESS_FIRST_PLAN.md`를 source of truth로 사용한다.

## R-PLATFORM-002: Windows 구현 실패 시 MacBook fallback 미비

- Risk: Windows 환경 문제로 구현이 막혔을 때 MacBook에서 이어받기 어렵다.
- Impact: 개발 일정 지연.
- Mitigation:
  - pathlib 사용.
  - OS별 setup 문서 분리.
  - GPU 없는 환경에서도 테스트 통과.
  - MacBook fallback setup을 README에 명시.
