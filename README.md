# Webcam AI CCTV

웹캠 기반 AI CCTV 프로젝트. 사람과 물건을 탐지·추적하고, 방치물 및 도난 의심 이벤트를 감지한다.

## 핵심 기능

- 웹캠 실시간 객체 탐지
- 영상 파일 입력
- 객체 ID 추적
- owner 등록
- 방치물 감지
- 도난 의심 이벤트 감지
- CSV 로그 저장
- 캡처 저장
- Streamlit 대시보드
- 자동 라벨링 파이프라인
- YOLO 커스텀 학습
- MacBook 시연 최적화

## 설치

### macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

CUDA용 PyTorch는 환경에 맞게 별도 설치한다.

## 테스트

```bash
python -m pytest
python -m compileall src scripts tools
```

## 웹캠 실행

```bash
python scripts/run_webcam.py --config configs/demo_mac.yaml
```

## 영상 파일 실행

```bash
python scripts/run_video.py --source data/samples/final_demo.mp4 --config configs/demo_mac.yaml
```

## 대시보드

```bash
python scripts/run_dashboard.py
```

## 데이터 수집

```bash
python scripts/record_webcam.py --out data/raw/demo_bag_01.mp4 --width 1280 --height 720 --fps 15
python scripts/extract_frames.py --source data/raw/demo_bag_01.mp4 --out data/frames/demo_bag_01 --every-n 10
```

## 자동 라벨링

```bash
python scripts/auto_label_yolo.py --images data/frames --out data/autolabels --classes person bag laptop cell_phone
```

## 학습

RTX 4070 SUPER Windows 데스크탑 기준:

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11s.pt epochs=80 imgsz=640 batch=-1 device=0 project=runs/train name=ai_cctv_s_640
```

## 검증

```bash
yolo detect val data=data/datasets/ai_cctv.yaml model=models/best_demo.pt
python scripts/benchmark_model.py --model models/best_demo.pt --source 0 --imgsz 640
```

## 주의

이 시스템은 실제 도난을 확정하지 않는다. 출력은 반드시 `theft_suspected` 또는 `도난 의심`으로 표현한다. 얼굴 인식과 신원 식별은 하지 않는다.

## Readiness-first workflow

현재 단계에서는 실제 영상 촬영과 최종 데이터셋 수집을 나중에 진행한다.
먼저 모든 코드와 파이프라인을 준비한다.

### 지금 검증 가능한 명령

```bash
python -m pytest
python -m compileall src scripts tools
python scripts/record_webcam.py --help
python scripts/extract_frames.py --help
python scripts/auto_label_yolo.py --help
python scripts/check_dataset.py --help
python scripts/train_yolo.py --help
python scripts/validate_yolo.py --help
python scripts/benchmark_model.py --help
```

### 데이터가 준비된 뒤 실행할 명령

```bash
python scripts/extract_frames.py --source data/raw/demo_01.mp4 --out data/frames/demo_01 --every-n 10
python scripts/auto_label_yolo.py --images data/frames --out data/autolabels --classes person bag laptop cell_phone
streamlit run tools/label_review_app.py
python scripts/split_dataset.py --source data/reviewed --out data/datasets/ai_cctv --strategy by-video
python scripts/check_dataset.py --data data/datasets/ai_cctv.yaml
python scripts/train_yolo.py --data data/datasets/ai_cctv.yaml --model yolo11s.pt --epochs 80 --imgsz 640 --device cuda
python scripts/validate_yolo.py --model runs/train/ai_cctv_s_640/weights/best.pt --data data/datasets/ai_cctv.yaml
python scripts/benchmark_model.py --model models/best_demo.pt --source 0 --imgsz 640
```

### 환경 역할

- Windows Desktop + RTX 4070 SUPER: 기본 구현, 학습, 모델 실험
- MacBook: Windows 구현 이슈 발생 시 fallback 구현, 최종 시연, FPS 검증
