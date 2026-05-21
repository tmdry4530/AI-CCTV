# models directory

Expected model artifacts after training:

```text
best_demo.pt   selected final MacBook demo model
best_s_640.pt  YOLO small 640 candidate
best_s_960.pt  YOLO small 960 candidate
```

Large model files are ignored by default. Keep this README in git and copy actual weights locally
only after training/selection.

Final model selection must be based on measured MacBook demo performance, not mAP alone:

1. MacBook FPS >= 10;
2. demo scenario success >= 4/5;
3. person recall >= 0.85;
4. main object recall >= 0.65;
5. false `theft_suspected` is acceptably low.

Do not claim that `best_demo.pt` is validated until `scripts/validate_yolo.py` and
`scripts/benchmark_model.py` have been run with real artifacts.
