# PLATFORM_MATRIX.md

## 1. 플랫폼 요약

| 플랫폼 | 역할 | 우선순위 |
|---|---|---:|
| Windows Desktop + RTX 4070 SUPER | 1순위 개발, 학습, 실험, 모델 비교 | 1 |
| MacBook | Windows 구현이 막힐 때의 대체 개발 환경, 최종 시연/FPS 검증 | 2 |

## 2. Windows Desktop

### 하드웨어

- RTX 4070 SUPER
- CUDA 사용
- VRAM 12GB 기준

### 역할

Windows 데스크탑은 기본 개발 및 학습 환경이다.

- 일반 구현 작업
- 공개 데이터셋 정리
- 자동 라벨링 실행
- 라벨 검수 보조
- YOLO 학습
- 모델별 mAP/precision/recall 비교
- 최종 후보 모델 생성
- 학습/평가 스크립트 검증

### 권장 명령

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11s.pt epochs=80 imgsz=640 batch=-1 device=0 project=runs/train name=ai_cctv_s_640
```

## 3. MacBook

### 역할

MacBook은 Windows 환경에서 구현이 막히거나 호환성 문제가 생길 때의 대체 개발 환경이며, 최종 시연 환경이다.

- Windows 환경 이슈 발생 시 대체 구현
- 실제 시연 환경 영상 수집
- MacBook 웹캠 기반 데이터 확보
- 최종 모델 추론
- FPS 측정
- Streamlit dashboard 실행
- 발표 리허설
- sample video fallback 실행

### Device policy

```text
cuda unavailable
mps if available
cpu fallback
```

## 4. 데이터/영상 준비 상태 정책

현재 단계에서는 실제 영상 촬영과 최종 데이터셋이 아직 준비되지 않았다고 가정한다.
따라서 구현 목표는 다음이다.

```text
데이터가 없어도 코드와 파이프라인은 완성
데이터가 들어오면 즉시 자동 라벨링/학습/평가/시연 가능
```

## 5. 크로스 플랫폼 규칙

- 경로는 `pathlib` 사용
- shell command는 Windows/macOS 차이를 고려
- 테스트는 GPU 없이 가능해야 함
- 학습만 CUDA 의존 허용
- MacBook 시연은 인터넷 없이 가능해야 함
- 모든 스크립트는 `--help`가 동작해야 함
- 데이터가 없을 때는 명확한 에러 메시지 또는 dry-run 결과를 제공해야 함

## 6. README 문서화 요구

README에는 반드시 다음을 분리해 작성한다.

- Windows development setup
- Windows RTX 4070 SUPER training setup
- MacBook fallback development setup
- MacBook demo setup
- CUDA 확인법
- MPS/CPU fallback
- 데이터가 아직 없을 때 실행 가능한 준비 명령
- 데이터가 준비된 뒤 실행할 학습/시연 명령
- common troubleshooting

## 7. 발표 전 MacBook 체크리스트

```text
모델 파일 존재: models/best_demo.pt
설정 파일 존재: configs/demo_mac.yaml
sample video 존재: data/samples/final_demo.mp4
웹캠 권한 허용
Streamlit 실행 가능
OpenCV 창 실행 가능
인터넷 없이 실행 가능
```
