# TROUBLESHOOTING.md

## Dataset yaml missing

Run data collection and split first, or inspect the scaffold:

```bash
python scripts/split_dataset.py --help
python scripts/check_dataset.py --help
```

The repository includes an empty dataset scaffold, but real training requires real reviewed images
and labels.

## `models/best_demo.pt` missing

This is expected before final training. Runtime and benchmark commands should fail clearly until a
real selected model is copied into `models/best_demo.pt`. Do not report final FPS or demo success
until the model exists and has been measured on MacBook.

Expected runtime dry-run symptom:

```text
ERROR: Model file not found: models/best_demo.pt
```

Fix only after training/selection: copy the selected local model to `models/best_demo.pt`, then rerun:

```bash
python scripts/run_webcam.py --config configs/demo_mac.yaml --dry-run
```

## Sample video missing

The fallback demo video is expected at `data/samples/final_demo.mp4`.

Expected clear error:

```text
ERROR: Video source not found: data/samples/final_demo.mp4
```

Do not claim sample-video fallback readiness until the file exists and this command reaches the next
validation step:

```bash
python scripts/run_video.py --source data/samples/final_demo.mp4 --config configs/demo_mac.yaml --dry-run
```

## CUDA not available on Windows

- Confirm NVIDIA driver and CUDA-compatible PyTorch installation.
- Run training with `--device cpu` only for smoke testing; final training should use RTX 4070 SUPER
  CUDA when available.

## MacBook runtime is slow

- Try the YOLO nano or small 640 model.
- Keep `imgsz=640` before testing 960.
- Use sample video fallback if webcam lighting or permissions fail.

## OpenCV camera does not open

- Try `--source 0`, `--source 1`, etc.
- Check OS camera permissions.
- On macOS, grant camera access to the terminal app you are using (`Terminal`, `iTerm`, VS Code, or
  the Python launcher) in **System Settings → Privacy & Security → Camera**, restart the terminal,
  and try again.
- Use the preview command before running the model pipeline:

```bash
python scripts/preview_camera.py --source 0 --width 1280 --height 720 --fps 15
```

- On demo day, keep `data/samples/final_demo.mp4` ready and use `scripts/run_video.py` as fallback.

## Dashboard dry-run

Use this to verify the Streamlit command without launching a browser:

```bash
python scripts/run_dashboard.py --dry-run
```

Expected output includes `streamlit run src/ai_cctv/app.py` or the absolute path to that module.

## Auto-label quality is poor

- Prioritize review of validation/test candidates.
- Add more MacBook demo-domain data.
- Do not place unreviewed auto labels into validation/test.

## False `theft_suspected`

- Confirm owner was registered first.
- Increase `suspicious_min_seconds` or `missing_grace_seconds`.
- Check tracker ID switches and object occlusion.
