# DATA_COLLECTION_RUNBOOK.md

## 목적

영상 촬영이 가능한 시점에 바로 데이터 수집을 시작하기 위한 절차다.

## 1. 촬영 전 체크

- 카메라 각도 고정
- 조명 고정
- 시연에 쓸 물건 고정
- 파일명에 scenario와 번호 포함

## 2. 권장 파일명

```text
data/raw/mac_bag_owner_leave_01.mp4
data/raw/mac_bag_theft_suspected_01.mp4
data/raw/mac_laptop_owner_leave_01.mp4
data/raw/mac_empty_scene_01.mp4
```

## 3. 촬영 명령

```bash
python scripts/record_webcam.py --out data/raw/mac_bag_owner_leave_01.mp4 --width 1280 --height 720 --fps 15
```

## 4. 프레임 추출

```bash
python scripts/extract_frames.py --source data/raw/mac_bag_owner_leave_01.mp4 --out data/frames/mac_bag_owner_leave_01 --every-n 10
```

## 5. 주의

같은 영상에서 추출한 유사 프레임을 train/val/test에 무작위로 섞지 않는다.
