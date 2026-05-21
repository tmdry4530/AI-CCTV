# READINESS_FIRST_PLAN.md

## 1. 목적

이 프로젝트는 데이터 수집과 영상 촬영이 아직 완료되지 않은 상태에서도 구현을 먼저 진행한다.
목표는 **데이터와 영상이 준비되는 즉시 자동 라벨링, 학습, 평가, 시연으로 넘어갈 수 있는 준비 완료 상태**를 만드는 것이다.

```text
지금 할 일 = 코드, 파이프라인, 문서, 테스트, 설정 준비
나중에 할 일 = 실제 영상 촬영, 라벨 검수, 학습 실행, 최종 시연 리허설
```

## 2. 구현 우선순위

### 지금 구현해야 하는 것

- 프로젝트 scaffold
- 순수 이벤트 로직
- mock sequence 기반 테스트
- detector/tracker adapter
- webcam/video runtime
- 데이터 수집 스크립트
- 프레임 추출 스크립트
- 자동 라벨링 스크립트
- 라벨 검수 UI
- dataset split/checker
- train/validate/benchmark 스크립트
- dashboard
- MacBook demo config
- Windows training config
- README와 실행 가이드

### 지금 하지 않는 것

- 실제 최종 영상 촬영
- 최종 dataset 확정
- 최종 model training 실행
- 최종 mAP 수치 확정
- 최종 demo video 촬영

위 항목은 데이터가 준비된 뒤 수행한다.

## 3. Data-ready 완료 기준

실제 데이터가 없어도 아래가 가능해야 한다.

```bash
python scripts/record_webcam.py --help
python scripts/extract_frames.py --help
python scripts/auto_label_yolo.py --help
python scripts/check_dataset.py --help
python scripts/train_yolo.py --help
python scripts/validate_yolo.py --help
python scripts/benchmark_model.py --help
python -m pytest
python -m compileall src scripts tools
```

## 4. 데이터가 들어온 뒤 실행 순서

```text
1. MacBook 또는 Windows에서 영상 촬영
2. extract_frames.py로 프레임 추출
3. auto_label_yolo.py로 1차 자동 라벨링
4. label_review_app.py로 val/test 우선 검수
5. split_dataset.py로 by-video split
6. check_dataset.py로 YOLO dataset 구조 검증
7. Windows RTX 4070 SUPER에서 train_yolo.py 실행
8. validate_yolo.py로 성능 측정
9. MacBook에서 benchmark_model.py 실행
10. run_webcam.py 또는 run_video.py로 시연 리허설
```

## 5. Windows/MacBook 역할 정정

### Windows Desktop + RTX 4070 SUPER

1순위 구현 및 학습 환경이다.

- 기본 개발
- 학습
- 모델 비교
- 데이터셋 점검
- 자동 라벨링
- 검증 스크립트 실행

### MacBook

Windows에서 구현이 막히거나 환경 문제가 있을 때의 대체 구현 환경이며, 최종 시연 환경이다.

- Windows 환경 이슈 발생 시 대체 개발
- 최종 시연
- MacBook 웹캠 권한/FPS 검증
- sample video fallback 실행
- 필요 시 데이터 수집

## 6. Codex 지시 원칙

Codex는 실제 데이터가 없다는 이유로 구현을 멈추면 안 된다.
대신 다음을 구현해야 한다.

- mock data
- sample config
- dry-run mode
- clear error messages
- `--help` 동작
- data directory scaffold
- dataset checker
- documented next commands

## 7. 금지사항

- 실제 데이터가 없다는 이유로 학습 파이프라인 구현을 생략하지 말 것
- 최종 mAP 수치를 임의로 작성하지 말 것
- sample video가 없는 상태에서 demo 통과를 주장하지 말 것
- MacBook 전용으로만 구현하지 말 것
- Windows path separator를 하드코딩하지 말 것
