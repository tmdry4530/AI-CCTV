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
- On demo day, keep `data/samples/final_demo.mp4` ready and use `scripts/run_video.py` as fallback.

## Auto-label quality is poor

- Prioritize review of validation/test candidates.
- Add more MacBook demo-domain data.
- Do not place unreviewed auto labels into validation/test.

## False `theft_suspected`

- Confirm owner was registered first.
- Increase `suspicious_min_seconds` or `missing_grace_seconds`.
- Check tracker ID switches and object occlusion.
