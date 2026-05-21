# TEST_PLAN.md

## 1. 목표

모델 추론과 무관하게 핵심 이벤트 로직을 검증하고, 최종 시스템이 MacBook에서 시연 가능한지 확인한다.

## 2. Unit tests

| 테스트 | 내용 |
|---|---|
| geometry center | bbox 중심점 계산 |
| distance | 사람-물건 거리 계산 |
| near threshold | 화면 비율 기반 근접 판정 |
| owner assignment | 3초 이상 근접 시 owner 등록 |
| abandoned | owner 사라짐 + 물건 남음 판정 |
| suspicious approach | 타인 접근 판정 |
| theft suspected | 타인 접근 후 물건 사라짐 판정 |
| occlusion grace | 잠깐 가려짐은 removed 처리하지 않음 |
| cooldown | 중복 이벤트 방지 |
| logger | CSV 저장 형식 검증 |
| dataset checker | YOLO label 구조 검증 |

## 3. Mock sequence tests

### Sequence A: 정상 보유

```text
T0: person1 + bag1 등장
T1-T4: person1이 bag1 근처 유지
T5: person1과 bag1 모두 화면에 있음
Expected: OWNER_REGISTERED only, no abandoned
```

### Sequence B: 방치물

```text
T0: person1 + bag1 등장
T1-T4: owner 등록
T5: person1 사라짐, bag1 남음
T10: bag1 계속 남음
Expected: ABANDONED_OBJECT
```

### Sequence C: 도난 의심

```text
T0-T10: bag1 abandoned 상태
T11-T13: person2가 bag1 근처 접근
T14-T17: bag1 사라짐
Expected: SUSPICIOUS_APPROACH, THEFT_SUSPECTED
```

### Sequence D: 단순 지나감

```text
T0-T10: bag1 abandoned 상태
T11: person2가 잠깐 지나감
T12: person2 멀어짐, bag1 그대로 있음
Expected: no THEFT_SUSPECTED
```

### Sequence E: 잠깐 가려짐

```text
T0-T10: bag1 abandoned 상태
T11: bag1 미탐지
T12: bag1 다시 탐지
Expected: no OBJECT_REMOVED, no THEFT_SUSPECTED
```

## 4. Integration tests

- detector output → internal dataclass 변환
- tracker output → event detector 입력 변환
- event → logger → CSV row
- event → snapshot path 생성
- dashboard가 CSV 로그를 읽을 수 있는지 확인

## 5. Manual tests

| 시나리오 | 기대 결과 |
|---|---|
| 가방 놓고 근처에 계속 있음 | 방치물 없음 |
| 가방 놓고 나감 | 방치물 발생 |
| 타인이 가방 접근 후 가져감 | 도난 의심 발생 |
| 사람이 그냥 지나감 | 도난 의심 없음 |
| 웹캠 실패 시 sample video 실행 | fallback 성공 |

## 6. 필수 검증 명령

```bash
python -m pytest
python -m compileall src scripts tools
python scripts/check_dataset.py --help
python scripts/train_yolo.py --help
python scripts/benchmark_model.py --help
```

## 7. Release gate

- unit tests 통과
- mock sequence tests 통과
- MacBook에서 run_webcam 실행 가능
- sample video fallback 실행 가능
- README 실행법 명확
- final demo scenario 문서화
