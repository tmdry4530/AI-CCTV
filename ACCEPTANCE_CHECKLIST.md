# ACCEPTANCE_CHECKLIST.md

## 1. 코드 구조

- [ ] `src/ai_cctv` 패키지가 존재한다.
- [ ] detector/tracker/event_detector가 분리되어 있다.
- [ ] `event_detector.py`가 `cv2`를 import하지 않는다.
- [ ] `event_detector.py`가 `ultralytics`를 import하지 않는다.
- [ ] 모든 경로 처리는 `pathlib` 기반이다.

## 2. Runtime

- [ ] 웹캠 실행 가능
- [ ] 영상 파일 실행 가능
- [ ] `q`로 안전 종료 가능
- [ ] 박스/ID/상태 표시 가능
- [ ] MacBook demo config 존재
- [ ] sample video fallback 존재

## 3. Event logic

- [ ] owner 등록 가능
- [ ] abandoned event 가능
- [ ] suspicious approach 가능
- [ ] theft_suspected 가능
- [ ] occlusion grace 처리 가능
- [ ] 중복 이벤트 방지 가능
- [ ] 지나가는 사람 오탐 방지 가능

## 4. Logging/Dashboard

- [ ] CSV 로그 저장
- [ ] snapshot 저장
- [ ] Streamlit dashboard 실행
- [ ] 최근 이벤트 조회
- [ ] 캡처 이미지 확인

## 5. Dataset pipeline

- [ ] webcam recording script
- [ ] frame extraction script
- [ ] auto-label script
- [ ] label review UI
- [ ] split by source video
- [ ] dataset checker
- [ ] YOLO yaml 생성/검증

## 6. Model pipeline

- [ ] train script
- [ ] validate script
- [ ] benchmark script
- [ ] RTX 4070 SUPER 학습 명령 문서화
- [ ] MacBook benchmark 문서화
- [ ] `models/best_demo.pt` 배치 가능

## 7. Tests

- [ ] `python -m pytest` 통과
- [ ] `python -m compileall src scripts tools` 통과
- [ ] owner assignment test 존재
- [ ] abandoned detection test 존재
- [ ] theft_suspected test 존재
- [ ] dataset checker test 존재

## 8. Docs

- [ ] README 완성
- [ ] Mac setup 작성
- [ ] Windows training setup 작성
- [ ] demo scenario 작성
- [ ] troubleshooting 작성
- [ ] known limitations 작성

## 9. Final demo

- [ ] MacBook에서 FPS 10 이상
- [ ] demo success 4/5 이상
- [ ] fallback video 실행 가능
- [ ] 발표 당일 인터넷 없이 실행 가능

## 10. Safety

- [ ] face recognition 없음
- [ ] identity recognition 없음
- [ ] theft 확정 표현 없음
- [ ] cloud upload default 없음
