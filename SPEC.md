# SPEC.md

## 1. 시스템 목표

웹캠 또는 영상 파일을 입력으로 받아 사람과 물건을 탐지·추적하고, 시간 기반 관계 분석을 통해 방치물과 도난 의심 이벤트를 감지한다.

## 2. 대상 클래스

### 기본 클래스

```yaml
0: person
1: bag
2: laptop
3: cell_phone
```

### 선택 클래스

```yaml
4: wallet
```

`wallet`은 작은 물체라 탐지 난이도가 높으므로 최종 발표 안정성이 확보된 뒤 선택 기능으로 추가한다.

## 3. 입력

| 입력 | 설명 |
|---|---|
| Webcam | MacBook/Windows 기본 카메라 |
| Video file | mp4, mov, avi 등 |
| Sample video | 발표 fallback용 |
| Image folder | 데이터셋/자동 라벨링용 |

## 4. 출력

| 출력 | 설명 |
|---|---|
| OpenCV 화면 | 실시간 박스/ID/이벤트 표시 |
| CSV 로그 | 이벤트 기록 |
| Snapshot | 이벤트 순간 이미지 |
| Streamlit Dashboard | 이벤트/캡처/성능 요약 |
| Model metrics | mAP, precision, recall, FPS |

## 5. 상태 모델

### TrackedPerson

- `track_id`
- `bbox`
- `center`
- `first_seen`
- `last_seen`
- `visible`

### TrackedObject

- `track_id`
- `class_name`
- `bbox`
- `center`
- `first_seen`
- `last_seen`
- `owner_id`
- `status`
- `last_non_owner_near_id`
- `last_known_position`

### Event

- `timestamp`
- `event_type`
- `object_id`
- `object_class`
- `owner_id`
- `related_person_id`
- `confidence`
- `snapshot_path`

## 6. 이벤트 규칙

### owner_registered

조건:

```text
person A와 object B의 중심 거리가 owner_distance_ratio 이내
+ owner_min_seconds 이상 지속
+ B.owner_id가 아직 없음
```

결과:

```text
B.owner_id = A.id
owner_registered 이벤트 발생
```

### abandoned_object

조건:

```text
B.owner_id 존재
+ owner가 화면에서 사라짐
+ B는 화면에 계속 존재
+ abandoned_min_seconds 이상 지속
```

결과:

```text
B.status = abandoned
abandoned_object 이벤트 발생
```

### suspicious_approach

조건:

```text
B.status = abandoned
+ owner가 아닌 person C가 B 근처에 접근
+ suspicious_min_seconds 이상 지속
```

결과:

```text
suspicious_approach 이벤트 발생
```

### theft_suspected

조건 A:

```text
B.status = abandoned
+ owner가 아닌 person C가 최근 접근
+ B가 missing_grace_seconds 이상 탐지되지 않음
```

조건 B:

```text
B.status = abandoned
+ owner가 아닌 person C가 근처에 있음
+ B의 위치가 moved_distance_ratio 이상 크게 이동
```

결과:

```text
theft_suspected 이벤트 발생
```

## 7. 기본 threshold

```yaml
owner_distance_ratio: 0.15
owner_min_seconds: 3.0
abandoned_min_seconds: 5.0
suspicious_min_seconds: 1.5
missing_grace_seconds: 2.0
moved_distance_ratio: 0.20
event_cooldown_seconds: 3.0
```

## 8. 오탐 방지 규칙

- owner 등록 전에는 방치물 판단 금지
- 물건이 잠깐 가려졌다고 바로 제거 처리 금지
- 사람이 단순히 지나가면 도난 의심 금지
- 같은 이벤트는 cooldown 시간 내 중복 발생 금지
- `theft_suspected`만 사용하고 실제 도난 확정 금지

## 9. 설정 파일

### `configs/demo_mac.yaml`

```yaml
camera:
  source: 0
  width: 1280
  height: 720
  fps: 15

model:
  path: models/best_demo.pt
  device: auto
  imgsz: 640
  conf_default: 0.35
  iou: 0.5

classes:
  person: 0
  bag: 1
  laptop: 2
  cell_phone: 3

thresholds:
  owner_distance_ratio: 0.15
  owner_min_seconds: 3.0
  abandoned_min_seconds: 5.0
  suspicious_min_seconds: 1.5
  missing_grace_seconds: 2.0
  moved_distance_ratio: 0.20
  event_cooldown_seconds: 3.0

tracker:
  type: botsort
  fallback: bytetrack

paths:
  logs: data/logs/events.csv
  snapshots: data/snapshots
```
