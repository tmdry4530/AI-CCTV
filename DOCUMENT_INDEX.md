# Webcam AI CCTV 문서팩 인덱스

## 목적

이 문서팩은 Codex/OMX를 사용해 **웹캠 기반 AI CCTV: 방치물·도난 의심 감지 시스템**을 완성하기 위한 실행 문서 묶음이다.

핵심 방향은 다음과 같다.

```text
웹캠 입력
→ 객체 탐지
→ 객체 추적
→ 사람-물건 관계 추론
→ 방치물/도난 의심 이벤트 판단
→ 로그/캡처/대시보드
→ 자동 라벨링
→ 커스텀 YOLO 학습
→ MacBook 시연 최적화
```

## 포함 파일

| 파일 | 용도 |
|---|---|
| `PRD.md` | 제품 요구사항 문서 |
| `SPEC.md` | 기능/비기능 명세 |
| `TECH_SPEC.md` | 기술 설계서 |
| `ARCHITECTURE.md` | 시스템 아키텍처 |
| `AGENTS.md` | Codex/OMX 작업 규칙 |
| `.codex/goals/ai-cctv-complete.md` | `/goal` 실행 계약 |
| `CODEX_EXECUTION_GUIDE.md` | Codex 실행 순서 |
| `CODEX_PROMPTS.md` | 바로 붙여넣는 프롬프트 |
| `IMPLEMENTATION_PLAN.md` | Phase별 구현 계획 |
| `TEST_PLAN.md` | 테스트 계획 |
| `DATASET_PLAN.md` | 데이터셋 수집/구성 계획 |
| `AUTO_LABELING_PLAN.md` | 자동 라벨링 전략 |
| `MODEL_PLAN.md` | 모델 학습 전략 |
| `MODEL_EXPERIMENTS.md` | 실험표/결과 기록지 |
| `EVAL_PLAN.md` | 평가 지표/기준 |
| `PLATFORM_MATRIX.md` | MacBook/Windows/RTX 4070 SUPER 운영 전략 |
| `DEMO_SCENARIO.md` | 발표 시연 시나리오 |
| `ACCEPTANCE_CHECKLIST.md` | 최종 완료 체크리스트 |
| `RISK_REGISTER.md` | 리스크와 대응 |
| `TASKS.json` | Codex 작업 단위 JSON |
| `PROGRESS.md` | 진행 기록 템플릿 |
| `DECISIONS.md` | 의사결정 기록 템플릿 |
| `README.md` | 레포 README 초안 |

## 사용 순서

```text
1. 이 문서팩을 새 레포 루트에 복사
2. Codex/OMX 실행
3. AGENTS.md 확인
4. /plan으로 구현 계획 검토
5. /goal로 장기 구현 시작
6. Phase별 구현/검증
7. Windows RTX 4070 SUPER로 학습
8. MacBook으로 최종 시연 검증
```

- `READINESS_FIRST_PLAN.md`: 데이터/영상 준비 전 구현 완료 기준과 후속 실행 절차
- `docs/DATA_COLLECTION_RUNBOOK.md`: 추후 영상 촬영 절차
- `docs/TRAINING_RUNBOOK.md`: 데이터 준비 후 RTX 4070 SUPER 학습 절차
- `docs/DEMO_RUNBOOK.md`: MacBook 최종 시연 절차
