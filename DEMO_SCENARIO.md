# DEMO_SCENARIO.md

## 1. 발표 장비

- MacBook
- 고정된 웹캠 각도
- 고정 조명
- 같은 가방/노트북/휴대폰
- `models/best_demo.pt`
- `configs/demo_mac.yaml`
- fallback 영상: `data/samples/final_demo.mp4`

## 2. 발표 전 preflight

카메라 화면만 먼저 확인한다. 이 단계는 YOLO 모델, tracker, dataset, CUDA가 없어도 실행된다.

```bash
python scripts/preview_camera.py --source 0 --width 1280 --height 720 --fps 15
```

예상 결과:

- OpenCV 창에 MacBook 데모 카메라 화면이 표시된다.
- 화면에 FPS와 frame size가 표시된다.
- preview 창에 포커스를 둔 상태에서 `q`를 누르면 종료된다.

발표 자산 검증:

```bash
python scripts/run_webcam.py --config configs/demo_mac.yaml --dry-run
python scripts/run_video.py --source data/samples/final_demo.mp4 --config configs/demo_mac.yaml --dry-run
python scripts/run_dashboard.py --dry-run
```

`models/best_demo.pt` 또는 `data/samples/final_demo.mp4`가 없으면 성공으로 말하지 말고,
출력된 missing asset 메시지를 readiness gap으로 설명한다.

## 3. 발표 금지 사항

발표 당일에는 하지 않는다.

```text
모델 학습
패키지 신규 설치
모델 다운로드
카메라 각도 급변경
처음 보는 물건 사용
조명 크게 변경
데이터셋 수정
```

표현 금지:

- 얼굴 인식 또는 사람 신원 식별을 한다고 말하지 않는다.
- 실제 도난을 확정한다고 말하지 않는다.
- 이벤트 이름은 `theft_suspected` 또는 도난 의심으로만 설명한다.
- 측정 전 mAP/FPS 수치를 말하지 않는다.

## 4. 시연 1: 기본 탐지

### 절차

1. `python scripts/run_webcam.py --config configs/demo_mac.yaml` 실행
2. 사람이 화면에 들어온다.
3. 가방/노트북/휴대폰을 보여준다.

### 기대 결과

- person 박스 표시
- bag/laptop/cell_phone 박스 표시
- track ID 표시

## 5. 시연 2: Owner 등록

### 절차

1. 사람이 가방을 내려놓는다.
2. 3초 이상 가방 근처에 머문다.

### 기대 결과

- `owner_registered`
- object label에 owner 표시

## 6. 시연 3: 방치물 감지

### 절차

1. owner가 화면 밖으로 나간다.
2. 가방만 화면에 남는다.
3. 5초 기다린다.

### 기대 결과

- `abandoned_object`
- 화면 경고 표시
- CSV 로그 저장
- snapshot 저장

## 7. 시연 4: 도난 의심

### 절차

1. 방치물 상태의 가방이 있다.
2. 다른 사람이 가방 근처에 접근한다.
3. 다른 사람이 가방을 들고 화면 밖으로 나간다.

### 기대 결과

- `suspicious_approach`
- `theft_suspected`
- CSV 로그 저장
- snapshot 저장

## 8. 시연 5: 대시보드

### 절차

```bash
python scripts/run_dashboard.py
```

### 기대 결과

- 최근 이벤트 목록 표시
- 이벤트 타입 표시
- snapshot path 표시
- 캡처 이미지 표시

## 9. Fallback

웹캠이나 조명이 실패하면 sample video로 전환한다.

```bash
python scripts/run_video.py --source data/samples/final_demo.mp4 --config configs/demo_mac.yaml
```

sample video가 없으면 다음 메시지가 나와야 한다.

```text
ERROR: Video source not found: data/samples/final_demo.mp4
```

이 경우 sample video가 아직 준비되지 않은 readiness gap이라고 설명한다.

## 10. 발표 설명 포인트

```text
이 프로젝트는 단순 객체 탐지가 아니라,
사람과 물건의 관계를 시간 기반으로 추론해
방치물과 도난 의심 이벤트를 판정하는 시스템이다.
```

## 11. 한계 설명

- 실제 도난 판정이 아니라 도난 의심 이벤트다.
- 얼굴 인식과 신원 식별은 하지 않는다.
- 시연 환경에 최적화된 모델이다.
- 조명/가림/물체 크기에 따라 정확도가 달라질 수 있다.
