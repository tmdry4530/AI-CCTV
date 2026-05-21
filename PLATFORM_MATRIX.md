# PLATFORM_MATRIX.md

## 1. 플랫폼 요약

| 플랫폼 | 역할 |
|---|---|
| Windows Desktop + RTX 4070 SUPER | 학습/실험/모델 비교 |
| MacBook | 데이터 수집/최종 시연/FPS 검증 |

## 2. Windows Desktop

### 하드웨어

- RTX 4070 SUPER
- CUDA 사용
- VRAM 12GB 기준

### 역할

- 공개 데이터셋 정리
- MacBook 수집 데이터 정리
- 자동 라벨링 실행
- 라벨 검수 보조
- YOLO 학습
- 모델별 mAP/precision/recall 비교
- 최종 후보 모델 생성

### 권장 명령

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11s.pt epochs=80 imgsz=640 batch=-1 device=0 project=runs/train name=ai_cctv_s_640
```

## 3. MacBook

### 역할

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

## 4. 크로스 플랫폼 규칙

- 경로는 `pathlib` 사용
- shell command는 Windows/macOS 차이를 고려
- 테스트는 GPU 없이 가능해야 함
- 학습만 CUDA 의존 허용
- MacBook 시연은 인터넷 없이 가능해야 함

## 5. 환경 설정 문서화 요구

README에는 반드시 다음을 분리해 작성한다.

- macOS setup
- Windows training setup
- CUDA 확인법
- MPS/CPU fallback
- common troubleshooting

## 6. 발표 전 MacBook 체크리스트

```text
모델 파일 존재: models/best_demo.pt
설정 파일 존재: configs/demo_mac.yaml
sample video 존재: data/samples/final_demo.mp4
웹캠 권한 허용
Streamlit 실행 가능
OpenCV 창 실행 가능
인터넷 없이 실행 가능
```
