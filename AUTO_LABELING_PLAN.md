# AUTO_LABELING_PLAN.md

## 1. 목표

라벨링 수작업을 최소화한다.

```text
수작업 박스 그리기 X
자동 라벨링 + 일부 검수 O
```

## 2. 전체 흐름

```text
MacBook 영상 수집
→ 프레임 추출
→ pretrained YOLO로 1차 자동 라벨링
→ 선택적으로 SAM/Roboflow/CVAT로 보강
→ 낮은 confidence/애매한 이미지 우선 검수
→ train/val/test 분리
→ YOLO 학습
```

## 3. 자동 라벨링 방식

### 1순위: Local YOLO auto-label

장점:

- 로컬 실행
- 빠름
- 데이터 업로드 없음
- Codex가 스크립트화하기 쉬움

단점:

- pretrained 모델이 못 잡는 객체는 라벨 누락
- 잘못된 class label 가능

### 2순위: CVAT automatic annotation

장점:

- 본격적인 annotation workflow
- 영상 기반 라벨링에 강함
- 수동 보정 UI 좋음

단점:

- 세팅 비용 존재

### 3순위: Roboflow Auto Label

장점:

- 편함
- 웹 UI 좋음
- augmentation/export 편함

단점:

- 클라우드 업로드 필요
- 무료 플랜 제약 가능

## 4. 검수 최소화 전략

전체를 검수하지 않는다. 우선순위를 둔다.

### 우선 검수 대상

- confidence 낮은 bbox
- bbox가 너무 작거나 큰 경우
- class가 헷갈리는 경우
- 한 이미지에 bbox가 과도하게 많은 경우
- cell_phone이 포함된 이미지
- validation/test 후보 이미지
- 최종 시연 장소와 유사한 이미지

## 5. Active learning selector

Codex가 구현해야 할 기능:

```text
images ranked by:
1. low confidence
2. class imbalance
3. small bounding boxes
4. high object count
5. near-duplicate groups
6. demo-scenario priority
```

## 6. Label review UI 요구사항

`tools/label_review_app.py`

필수:

- 이미지 표시
- bbox overlay 표시
- class/confidence 표시
- accept/reject 버튼
- 이미지 단위 accepted/rejected 상태 저장
- label file 누락 표시
- validation/test 후보 표시

선택:

- bbox 수정
- class 변경
- keyboard shortcut

MVP에서는 bbox 직접 수정보다 accepted/rejected 우선.

## 7. 수동 검수 범위

| 항목 | 최소 검수량 |
|---|---:|
| validation | 100~200장 |
| test | 100장 이상 |
| train | confidence 낮은 것 중심 |
| final demo scenes | 전부 검수 권장 |

## 8. 금지 사항

- 자동 라벨을 100% 신뢰하지 않는다.
- validation/test에 미검수 자동 라벨을 넣지 않는다.
- 같은 영상에서 추출한 near-duplicate를 train/val/test에 섞지 않는다.
- 라벨 오류가 많은 데이터를 그대로 학습하지 않는다.
