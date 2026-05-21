# DECISIONS.md

## ADR-001: Use YOLO instead of training a model from scratch

- Status: accepted
- Context: 학원 프로젝트 기간 안에 실시간 객체탐지 시스템과 이벤트 로직까지 구현해야 한다.
- Decision: pretrained YOLO를 기반으로 custom fine-tuning한다.
- Consequences: 모델 구조 설계보다 데이터셋/라벨링/평가/시연에 집중한다.

## ADR-002: Use auto-labeling instead of full manual labeling

- Status: accepted
- Context: 모든 라벨을 수작업으로 그리면 프로젝트 시간이 과도하게 소요된다.
- Decision: 자동 라벨링 + 일부 검수 방식을 사용한다.
- Consequences: validation/test는 human-reviewed only로 유지해야 한다.

## ADR-003: Use Windows RTX 4070 SUPER for training and MacBook for demo

- Status: accepted
- Context: 학습은 GPU가 필요하고, 발표는 MacBook으로 진행한다.
- Decision: Windows desktop은 학습/실험 장비, MacBook은 데이터 수집/최종 시연 장비로 분리한다.
- Consequences: 최종 모델은 반드시 MacBook에서 benchmark해야 한다.

## ADR-004: Use theft_suspected terminology only

- Status: accepted
- Context: 시스템은 실제 범죄를 확정할 수 없다.
- Decision: 이벤트명은 `THEFT_SUSPECTED`로 제한한다.
- Consequences: README, UI, 발표 자료에서 theft detected/도난 감지 표현을 쓰지 않는다.

## ADR-005: Event logic must be independent from YOLO/OpenCV

- Status: accepted
- Context: 모델이나 웹캠 없이도 핵심 로직을 테스트해야 한다.
- Decision: event_detector는 내부 dataclass만 입력으로 받는다.
- Consequences: detector/tracker wrapper가 YOLO 결과를 내부 형식으로 변환해야 한다.
