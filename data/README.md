# data directory

이 디렉토리는 실제 데이터가 들어오기 전에도 구조를 고정하기 위해 존재한다.

```text
raw/        촬영 원본 영상
frames/     추출된 이미지 프레임
autolabels/ 자동 생성된 YOLO labels
reviewed/   사람이 검수한 labels/images
datasets/   YOLO 학습용 dataset
logs/       이벤트 로그
snapshots/  이벤트 캡처
samples/    fallback demo video
```

원본 영상과 개인 데이터는 git에 커밋하지 않는다.
