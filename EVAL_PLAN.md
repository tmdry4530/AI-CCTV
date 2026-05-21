# EVAL_PLAN.md

## 1. 평가 범위

평가는 세 층으로 나눈다.

```text
Detection metrics
Runtime metrics
Event metrics
```

객체 탐지 mAP만 높아도 이벤트가 잘못 나오면 실패다. 반대로 이벤트 로직이 좋아도 물건 탐지가 안 되면 실패다.

## 2. Detection metrics

| 지표 | 설명 | 목표 |
|---|---|---:|
| mAP50 | IoU 0.5 기준 평균 정밀도 | >= 0.70 |
| mAP50-95 | 더 엄격한 평균 정밀도 | 참고 |
| precision | 예측 중 맞은 비율 | class별 확인 |
| recall | 실제 객체를 잡은 비율 | 중요 |
| person recall | 사람 탐지 재현율 | >= 0.85 |
| main object recall | bag/laptop/cell_phone 재현율 | >= 0.65 |

## 3. Runtime metrics

| 지표 | 목표 |
|---|---:|
| MacBook FPS | >= 10 |
| Windows FPS | 참고 |
| 평균 inference time | 낮을수록 좋음 |
| tracker ID switch | 낮을수록 좋음 |

## 4. Event metrics

| 지표 | 목표 |
|---|---:|
| abandoned success | 4/5 이상 |
| theft_suspected success | 4/5 이상 |
| false abandoned | 낮을수록 좋음 |
| false theft_suspected | 매우 낮아야 함 |
| event delay | 시연상 자연스러운 수준 |

## 5. 평가 데이터 정책

- validation/test는 human-reviewed labels만 사용한다.
- MacBook demo와 유사한 장면을 반드시 포함한다.
- 같은 source video의 near-duplicate가 train/val/test에 섞이면 안 된다.

## 6. 검증 명령

```bash
yolo detect val data=data/datasets/ai_cctv.yaml model=models/best_demo.pt
python scripts/benchmark_model.py --model models/best_demo.pt --source 0 --imgsz 640
python scripts/run_video.py --source data/samples/final_demo.mp4 --config configs/demo_mac.yaml
```

## 7. 합격 기준

### 최소 합격

```text
mAP50 >= 0.70
person recall >= 0.85
main object recall >= 0.65
MacBook FPS >= 10
demo success >= 4/5
```

### 발표용 우수

```text
mAP50 >= 0.80
person recall >= 0.90
main object recall >= 0.75
MacBook FPS >= 15
demo success >= 5/5
```

## 8. 실패 시 조치

| 실패 | 조치 |
|---|---|
| person recall 낮음 | 데이터셋 라벨/클래스 매핑 확인 |
| bag recall 낮음 | bag 데이터 추가, 공개 luggage 데이터 보강 |
| cell_phone recall 낮음 | 가까운 장면 추가, imgsz 960 실험 |
| MacBook FPS 낮음 | nano/small 640으로 낮춤 |
| theft_suspected 오탐 | suspicious_min_seconds 증가, removed 조건 강화 |
| abandoned 오탐 | owner_min_seconds 증가 |
