# Webcam AI CCTV

웹캠/영상 파일에서 사람과 물건을 탐지·추적하고, 시간 기반 관계 규칙으로 `abandoned_object` 및 `theft_suspected` 이벤트를 기록하는 AI CCTV 데모 프로젝트입니다. 이 시스템은 실제 도난을 확정하지 않으며 얼굴 인식이나 신원 식별을 하지 않습니다.

## 구현 범위

- 입력: webcam, video file, sample video fallback
- 탐지/추적: Ultralytics YOLO wrapper + tracker wrapper
- 이벤트: owner 등록, abandoned object, suspicious approach, theft_suspected
- 출력: OpenCV overlay, CSV/SQLite logging, snapshot 저장, Streamlit dashboard
- 데이터/모델: frame extraction, local auto-labeling, review candidate selection, dataset checker, YOLO train/validate, FPS benchmark
- 플랫폼: MacBook demo without CUDA, Windows RTX 4070 SUPER training support

## 설치 — macOS / MacBook demo

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

MacBook에서는 CUDA가 없어도 동작해야 합니다. 런타임 device는 `configs/demo_mac.yaml`의 `model.device: auto`를 사용하며, 코드가 `cuda -> mps -> cpu` 순서로 사용 가능한 장치를 선택합니다.

최종 발표 전 로컬에 다음 파일을 준비합니다.

```text
models/best_demo.pt
data/samples/final_demo.mp4
configs/demo_mac.yaml
```

## 설치 — Windows RTX 4070 SUPER training

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

CUDA용 PyTorch는 PC의 CUDA 버전에 맞춰 PyTorch 공식 설치 명령으로 별도 설치하세요. CUDA 확인:

```powershell
python - <<'PY'
import torch
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no cuda')
PY
```

## 필수 검증

```bash
python -m pytest
python -m compileall src scripts tools
python scripts/check_dataset.py --help
python scripts/train_yolo.py --help
python scripts/validate_yolo.py --help
python scripts/benchmark_model.py --help
```

데이터셋 scaffold 검증:

```bash
python scripts/check_dataset.py --data data/datasets/ai_cctv.yaml --allow-empty
```

## 실행 — webcam / video / dashboard

웹캠:

```bash
python scripts/run_webcam.py --config configs/demo_mac.yaml
```

웹캠 실패 시 sample video fallback:

```bash
python scripts/run_webcam.py --config configs/demo_mac.yaml --fallback-video data/samples/final_demo.mp4
```

영상 파일:

```bash
python scripts/run_video.py --source data/samples/final_demo.mp4 --config configs/demo_mac.yaml
```

대시보드:

```bash
python scripts/run_dashboard.py
```

Dry-run smoke checks:

```bash
python scripts/run_webcam.py --config configs/demo_mac.yaml --dry-run
python scripts/run_video.py --source data/samples/final_demo.mp4 --config configs/demo_mac.yaml --dry-run
python scripts/run_dashboard.py --dry-run
```

## 데이터 수집 / 자동 라벨링

웹캠 녹화:

```bash
python scripts/record_webcam.py --out data/raw/demo_bag_01.mp4 --width 1280 --height 720 --fps 15 --seconds 30
```

프레임 추출:

```bash
python scripts/extract_frames.py --source data/raw/demo_bag_01.mp4 --out data/frames/demo_bag_01 --every-n 10
```

Local YOLO auto-labeling:

```bash
python scripts/auto_label_yolo.py --images data/frames --out data/autolabels --classes person bag laptop cell_phone
```

검수 후보 랭킹:

```bash
python tools/select_review_candidates.py --images data/frames --labels data/autolabels/labels --metadata data/autolabels/metadata.jsonl --out data/review_candidates.csv
```

Label review UI:

```bash
streamlit run tools/label_review_app.py -- --images data/frames --labels data/autolabels/labels --state data/review_state.json
```

Dataset split/check:

```bash
python scripts/split_dataset.py --images data/frames --labels data/autolabels/labels --out data/datasets/ai_cctv
python scripts/check_dataset.py --data data/datasets/ai_cctv.yaml
```

Validation/test labels must be human-reviewed before reporting metrics.

## YOLO training / validation

빠른 데이터셋 검증:

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11n.pt epochs=30 imgsz=640 batch=-1 device=0 project=runs/train name=ai_cctv_n_quick
```

기본 최종 후보:

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11s.pt epochs=80 imgsz=640 batch=-1 device=0 project=runs/train name=ai_cctv_s_640
```

작은 물체 개선 후보:

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11s.pt epochs=80 imgsz=960 batch=-1 device=0 project=runs/train name=ai_cctv_s_960
```

정확도 상한 확인:

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11m.pt epochs=100 imgsz=640 batch=-1 device=0 project=runs/train name=ai_cctv_m_640
```

Python wrapper도 제공합니다.

```bash
python scripts/train_yolo.py --data data/datasets/ai_cctv.yaml --model yolo11s.pt --epochs 80 --imgsz 640 --device auto
python scripts/validate_yolo.py --model runs/train/ai_cctv_s_640/weights/best.pt --data data/datasets/ai_cctv.yaml
```

## MacBook benchmark / final model policy

```bash
python scripts/benchmark_model.py --model models/best_demo.pt --source 0 --imgsz 640 --device auto
python scripts/benchmark_model.py --model models/best_demo.pt --source data/samples/final_demo.mp4 --imgsz 640 --device auto
```

목표:

- MacBook FPS >= 10
- demo success >= 4/5
- mAP50 >= 0.70
- person recall >= 0.85
- main object recall >= 0.65

최종 모델은 mAP만으로 선택하지 말고 `MODEL_EXPERIMENTS.md`에 MacBook FPS와 5회 demo success를 함께 기록한 뒤 `models/best_demo.pt`로 고정합니다.

## Demo scenario

1. Owner가 물건 근처에 3초 이상 머무르면 `owner_registered`.
2. Owner가 사라지고 물건만 5초 이상 남으면 `abandoned_object`.
3. Non-owner가 abandoned object 근처에 1.5초 이상 있으면 `suspicious_approach`.
4. Non-owner 접근 이후 물건이 grace time 이후 사라지거나 크게 이동하면 `theft_suspected`.
5. 단순 지나감과 짧은 occlusion은 `theft_suspected`를 발생시키면 안 됩니다.

## Troubleshooting

- Webcam permission denied on macOS: System Settings에서 Terminal/Python/IDE 카메라 권한을 허용합니다.
- FPS too low: `imgsz=640`, YOLO nano/small, video fallback, 낮은 해상도를 사용합니다.
- Model download fails offline: 발표 전 `models/best_demo.pt`를 로컬에 배치합니다.
- Dataset metrics look too high: 같은 source video의 near-duplicate가 train/val/test에 섞였는지 확인합니다.
- False `theft_suspected`: `suspicious_min_seconds`를 늘리고 `missing_grace_seconds`/`moved_distance_ratio`를 보수적으로 조정합니다.

## Safety / privacy

- 얼굴 인식 없음
- 실제 사람 신원 식별 없음
- 클라우드 업로드 default 없음
- 실제 도난 확정 표현 없음
- 이벤트 이름은 `theft_suspected`만 사용
