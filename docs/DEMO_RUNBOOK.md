# DEMO_RUNBOOK.md

## 목적

MacBook 최종 시연 절차를 고정한다.

## 1. 시연 전 준비

- `models/best_demo.pt` 존재 확인
- `configs/demo_mac.yaml` 존재 확인
- `data/samples/final_demo.mp4` fallback 존재 확인
- 웹캠 권한 허용
- 인터넷 없이 실행 가능 여부 확인

## 2. 웹캠 시연

```bash
python scripts/run_webcam.py --config configs/demo_mac.yaml
```

## 3. fallback 영상 시연

```bash
python scripts/run_video.py --source data/samples/final_demo.mp4 --config configs/demo_mac.yaml
```

## 4. 대시보드

```bash
streamlit run src/ai_cctv/app.py
```

## 5. 발표 당일 금지

- 새 모델 학습
- 새 패키지 설치
- 새 모델 다운로드
- 처음 보는 물건 사용
- 카메라 각도 변경
