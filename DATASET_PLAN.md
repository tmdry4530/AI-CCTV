# DATASET_PLAN.md

## 1. 데이터 전략

공개 데이터셋은 detector bootstrapping 용도로 사용한다. 최종 시연 정확도는 MacBook 웹캠으로 직접 찍은 데이터로 맞춘다.

```text
Public datasets = detector bootstrap
MacBook data = demo-domain adaptation
PETS-like video = event logic reference/fallback
```

## 2. 클래스

```yaml
0: person
1: bag
2: laptop
3: cell_phone
```

선택:

```yaml
4: wallet
```

`wallet`은 탐지 난이도가 높으므로 최종 프로젝트 안정성이 확보된 뒤에만 추가한다.

## 3. 공개 데이터셋 후보

| 데이터셋 | 용도 | 판단 |
|---|---|---|
| COCO pretrained | person, backpack, handbag, laptop, cell phone baseline | 필수 |
| Roboflow luggage/bag 계열 | bag/luggage 탐지 보강 | 추천 |
| Kaggle suitcase/luggage | luggage 이미지 보강 | 라이선스 확인 후 사용 |
| PETS 2006 | 방치물 이벤트 참고/영상 fallback | 추천 |
| Open Images V7 subset | 클래스 보강 | 필요 시 subset만 |

## 4. 직접 수집 데이터

MacBook 웹캠으로 직접 수집한다.

### 필수 장면

| 장면 | 목적 |
|---|---|
| 빈 공간 | 오탐 방지 |
| 사람만 있음 | 물건 오탐 방지 |
| 물건만 있음 | 물건 탐지 강화 |
| 사람 + 가방 | owner 등록 상황 |
| 사람 + 노트북 | laptop 탐지 |
| 사람 + 휴대폰 | cell_phone 탐지 |
| 사람이 물건을 가림 | occlusion 대응 |
| 사람이 물건을 들고 이동 | object removed/moved 상황 |
| 밝은 조명 | 조명 다양화 |
| 어두운 조명 | 조명 다양화 |
| 가까운 거리 | 큰 bbox 대응 |
| 먼 거리 | 작은 bbox 대응 |

## 5. 데이터 수집량

| 수준 | 이미지 수 |
|---|---:|
| MVP | 300~500 |
| 권장 | 1,000~1,500 |
| validation | 100~200 |
| test | 100+ |

## 6. Split 원칙

랜덤 split 금지. 같은 영상에서 추출한 거의 동일한 프레임이 train/val/test에 섞이면 성능이 과대평가된다.

권장:

```text
split by source video
split by scenario group
```

## 7. Label 품질 정책

| Split | 정책 |
|---|---|
| train | 자동 라벨 허용 + 일부 검수 |
| val | human-reviewed only |
| test | human-reviewed only |

## 8. 데이터 디렉토리 구조

```text
data/
├─ raw/
├─ frames/
├─ autolabels/
├─ reviewed/
├─ datasets/
│  └─ ai_cctv/
│     ├─ images/
│     │  ├─ train/
│     │  ├─ val/
│     │  └─ test/
│     └─ labels/
│        ├─ train/
│        ├─ val/
│        └─ test/
└─ samples/
```

## 9. YOLO dataset yaml

```yaml
path: data/datasets/ai_cctv
train: images/train
val: images/val
test: images/test

names:
  0: person
  1: bag
  2: laptop
  3: cell_phone
```
