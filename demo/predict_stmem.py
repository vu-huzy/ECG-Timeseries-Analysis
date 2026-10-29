"""
Dùng lại model ST-MEM Semi-finetune đã train, KHÔNG train lại.

Model = encoder ST-MEM ViT-B pretrained (đóng băng, file checkpoint gốc 340 MB, không nằm trong git)
      + phần đã train, được commit sẵn ở demo/models/stmem_semi_finetune.pt (~11 KB):
        2 lead embedding (MIT-BIH có 2 lead) và classifier head.

Chạy từ thư mục gốc repo:
    python demo/predict_stmem.py

Script nạp checkpoint + trọng số đã train, chấm lại tập test (record 102–106, stride 4.5 s, ngưỡng 0.5)
và so với số đã lưu trong demo/results/stmem_results.json. Cần: checkpoint pretrained
(xem README), dữ liệu MIT-BIH (tự tải vào demo/.cache/mitdb ở lần chạy đầu).
Dùng trong code khác: `model = load_trained_model()`, đầu vào (B, 2, 2250) @ 250 Hz đã lọc như mit-bih.py,
đầu ra là logit, sigmoid(logit) ≥ 0.5 là Abnormal.
"""
import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

DEMO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO_DIR))
import train_stmem as T  # noqa: E402

WEIGHTS_FILE = T.WEIGHTS_FILE
RESULTS_FILE = T.OUT_FILE


def load_trained_model(device=None):
    """Encoder pretrained (đóng băng) + lead embedding và head đã train."""
    T.use_local_mitdb()
    mod = T.load_mitbih_module()
    device = device or mod.DEVICE
    if not Path(mod.PRETRAINED_PATH).exists():
        raise FileNotFoundError(
            f"Thiếu checkpoint pretrained: {mod.PRETRAINED_PATH}\n"
            "Tải theo hướng dẫn trong README (mục Web demo, bước b).")
    model = mod.build_model()
    model, _ = mod.load_pretrained_weights(model, mod.PRETRAINED_PATH)
    trained = torch.load(WEIGHTS_FILE, map_location="cpu", weights_only=True)
    res = model.load_state_dict(trained, strict=False)
    assert not res.unexpected_keys, res.unexpected_keys
    return model.to(device).eval(), mod, device


def main():
    BD = T.BD
    BD.ensure_downloads(set(BD.ALL_RECORDS))
    model, mod, device = load_trained_model()
    X_tr, y_tr, X_va, y_va, X_te, y_te = T.build_or_load_datasets(mod)
    print(f"Tập test: {X_te.shape[0]} cửa sổ ({int((y_te == 0).sum())} Normal / {int((y_te == 1).sum())} Abnormal)")

    loader = DataLoader(mod.ECGDataset(X_te, y_te), batch_size=mod.BATCH_SIZE, shuffle=False)
    m = T.to_py(mod.evaluate(model, loader, nn.BCEWithLogitsLoss(), device))
    print("Chấm lại bằng trọng số đã commit:", {k: m[k] for k in ("accuracy", "precision", "recall", "f1", "auc")})

    saved = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    ref = next(e for e in saved["experiments"] if e["experiment"] == saved["chosen_experiment"])["test"]
    print("Đã lưu trong results/stmem_results.json:", {k: ref[k] for k in ("accuracy", "precision", "recall", "f1", "auc")})
    ok = all(abs(m[k] - ref[k]) < 5e-3 for k in ("accuracy", "f1", "auc"))
    print("KHỚP" if ok else "LỆCH: kiểm tra checkpoint pretrained và dữ liệu")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
