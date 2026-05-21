# CODEX_EXECUTION_GUIDE.md

## 1. 기본 전략

이 프로젝트는 범위가 크다. Codex에게 한 번에 “전체 구현”을 시키지 않는다.

권장 순서:

```text
문서 생성
→ /plan
→ /goal
→ Phase별 구현
→ 테스트
→ 리뷰
→ 시연 안정화
```

## 2. 초기 세팅

```bash
mkdir webcam-ai-cctv
cd webcam-ai-cctv
git init
npm install -g @openai/codex oh-my-codex
omx setup --scope project
omx doctor
omx agents-init .
omx --high
```

## 3. 문서팩 복사

이 문서팩 전체를 레포 루트에 복사한다.

확인:

```bash
ls AGENTS.md PRD.md SPEC.md TEST_PLAN.md
ls .codex/goals/ai-cctv-complete.md
```

## 4. 계획 먼저 요청

```text
/plan
Read AGENTS.md, PRD.md, SPEC.md, TECH_SPEC.md, TEST_PLAN.md, DATASET_PLAN.md, AUTO_LABELING_PLAN.md, MODEL_PLAN.md, EVAL_PLAN.md, PLATFORM_MATRIX.md, and MODEL_EXPERIMENTS.md.

Propose a phased implementation plan.
Do not edit source code yet.

The plan must separate:
1. pure event logic
2. detector/tracker wrappers
3. webcam/video runtime
4. auto-labeling pipeline
5. dataset validation
6. YOLO training/validation
7. MacBook benchmark
8. Streamlit dashboard
9. demo hardening
```

## 5. 장기 구현 목표 설정

```text
/goal Complete .codex/goals/ai-cctv-complete.md exactly.
Use AGENTS.md, PRD.md, SPEC.md, TECH_SPEC.md, TEST_PLAN.md, DATASET_PLAN.md, AUTO_LABELING_PLAN.md, MODEL_PLAN.md, EVAL_PLAN.md, PLATFORM_MATRIX.md, and MODEL_EXPERIMENTS.md as source of truth.
Do not mark complete until tests pass and Mac/Windows setup instructions are documented.
Keep model training, runtime inference, event logic, auto-labeling, and dashboard separated.
```

## 6. 중간 확인 명령

Codex 세션 안에서:

```text
/status
/diff
/goal
```

터미널에서:

```bash
git status
python -m pytest
python -m compileall src scripts tools
```

## 7. 완료 전 리뷰

```text
/review
Review the current repository against AGENTS.md, PRD.md, SPEC.md, TEST_PLAN.md, and .codex/goals/ai-cctv-complete.md.

Focus on:
1. missing acceptance criteria
2. untested event logic
3. detector/event coupling problems
4. false positive risks
5. MacBook demo failure risks
6. dataset leakage risks
7. unclear README commands
8. privacy/safety issues

Return findings first, ordered by severity. Do not edit files.
```

## 8. 구현 중단 기준

다음 문제가 있으면 blind retry를 중단하고 원인 분석을 먼저 한다.

- 같은 테스트 실패가 2회 반복
- event_detector가 cv2/ultralytics에 의존
- 테스트가 실제 웹캠을 요구
- Windows 전용 경로가 들어감
- MacBook에서 실행 불가한 의존성 추가
- theft_detected처럼 확정 표현 사용
