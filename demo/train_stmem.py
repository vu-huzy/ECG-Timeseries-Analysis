"""
Fine-tune ST-MEM trên MIT-BIH và lưu kết quả cho demo (màn hình theo dõi + mục 07).

Làm đúng theo Final_Report_TS-3.pdf (mục 3.3, 4.3, Bảng 3.1 và 5.3), dùng lại nguyên các hàm,
cấu hình và hai thử nghiệm của notebooks/Classification/ST-MEM/mit-bih.py:
  - Dữ liệu: MIT-BIH đọc bằng WFDB (file giống hệt pn_dir='mitdb', lấy từ cache local
    demo/.cache/mitdb), 2 lead, 9 s @ 250 Hz; cửa sổ trượt stride 4.5 s
    → 15.200 / 2.000 / 2.000 cửa sổ như Bảng 3.1 (mit-bih.py để stride 9 s → chỉ một nửa)
  - Encoder: checkpoint ST-MEM ViT-B pretrained có sẵn (pretrain/st_mem_vit_base_encoder.pth),
    không tự pretrain
  - Chỉ chạy Semi-finetune (thử nghiệm 2 của mit-bih.py): train lead embeddings + classifier head,
    phần còn lại của encoder đóng băng. Linear probe (thử nghiệm 1) không chạy.
  - Ngưỡng 0.5; model này dùng cho demo và màn hình theo dõi
Khác mit-bih.py: stride, cố định seed, lưu model và dự đoán từng cửa sổ 9 s
(không chồng lấn) của các record test/val cho màn hình theo dõi.

Chạy (cần GPU để nhanh; CPU vẫn chạy được nhưng rất lâu):
    python demo/train_stmem.py
Kết quả: demo/results/stmem_results.json, trọng số đã train: demo/models/stmem_semi_finetune.pt (build_monitor.py đọc file này).
"""

import importlib.util
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import wfdb
from torch.utils.data import DataLoader

DEMO_DIR = Path(__file__).resolve().parent
REPO_DIR = DEMO_DIR.parent
STMEM_DIR = REPO_DIR / "notebooks" / "Classification" / "ST-MEM"
sys.path.insert(0, str(DEMO_DIR))
import build_data as BD  # noqa: E402

CACHE = BD.CACHE_DIR / "stmem"
# Kết quả và trọng số đã train được commit vào git (nhỏ) để máy khác không phải train lại
OUT_FILE = DEMO_DIR / "results" / "stmem_results.json"
WEIGHTS_FILE = DEMO_DIR / "models" / "stmem_semi_finetune.pt"
SEED = 42
STRIDE_SECONDS = 4.5      # report Bảng 3.1: 15.200 / 2.000 / 2.000 cửa sổ 9 s
CHOSEN_EXPERIMENT = 2     # report chọn Semi-finetune (Bảng 5.3, 5.5)
THRESHOLD = 0.5

# Final_Report_TS-3.pdf — Bảng 5.3 (tập test)
REPORT_TABLE_5_3 = {
    1: {"accuracy": 0.5392, "precision": 0.6776, "recall": 0.8398, "f1": 0.7500},
    2: {"accuracy": 0.9672, "precision": 0.9722, "recall": 0.9669, "f1": 0.9695},
}

# Record dự đoán cho màn hình theo dõi: toàn bộ test + validation
PREDICT_RECORDS = ["102", "103", "104", "105", "106", "200", "208", "232", "233", "234"]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_mitbih_module():
    """Import mit-bih.py (tên file có dấu gạch ngang nên phải nạp bằng importlib)."""
    sys.path.insert(0, str(STMEM_DIR))
    spec = importlib.util.spec_from_file_location("stmem_mitbih", STMEM_DIR / "mit-bih.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def use_local_mitdb():
    """mit-bih.py gọi wfdb.rdrecord(name, pn_dir='mitdb'); chuyển sang đọc file local."""
    rdrecord, rdann = wfdb.rdrecord, wfdb.rdann

    def rdrecord_local(record_name, pn_dir=None, **kw):
        return rdrecord(str(BD.MITDB_DIR / record_name), **kw)

    def rdann_local(record_name, extension, pn_dir=None, **kw):
        return rdann(str(BD.MITDB_DIR / record_name), extension, **kw)

    wfdb.rdrecord = rdrecord_local
    wfdb.rdann = rdann_local


def set_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def build_or_load_datasets(mod):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / "dataset_stride45.npz"
    mod.STRIDE_SECONDS = STRIDE_SECONDS
    if f.exists():
        log(f"Dùng dataset đã cache: {f}")
        d = np.load(f)
        return d["X_train"], d["y_train"], d["X_val"], d["y_val"], d["X_test"], d["y_test"]
    out = []
    for name, recs in [("train", mod.TRAIN_RECORDS), ("val", mod.VAL_RECORDS), ("test", mod.TEST_RECORDS)]:
        t0 = time.time()
        X, y = mod.build_dataset_split(recs)
        log(f"  {name}: {X.shape}, Normal={int((y == 0).sum())}, Abnormal={int((y == 1).sum())} ({time.time() - t0:.0f}s)")
        out += [X.astype(np.float32), y.astype(np.float32)]
    np.savez(f, X_train=out[0], y_train=out[1], X_val=out[2], y_val=out[3], X_test=out[4], y_test=out[5])
    return out


def to_py(metrics):
    cm = None
    if "y_true" in metrics:
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(metrics["y_true"], metrics["y_pred"], labels=[0, 1]).tolist()
    return {
        "loss": round(float(metrics["loss"]), 4),
        "accuracy": round(float(metrics["accuracy"]), 4),
        "precision": round(float(metrics["precision"]), 4),
        "recall": round(float(metrics["recall"]), 4),
        "f1": round(float(metrics["f1"]), 4),
        "auc": round(float(metrics["auc_roc"]), 4),
        "specificity": round(cm[0][0] / max(1, cm[0][0] + cm[0][1]), 4) if cm else None,
        "confusion_matrix": cm,
    }


def train_experiment(mod, exp_type, loaders, class_weights, device):
    """Giống mod.run_experiment nhưng trả về model tốt nhất và lịch sử train."""
    train_loader, val_loader, test_loader = loaders
    set_seed()
    model = mod.build_model()
    model, loaded = mod.load_pretrained_weights(model, mod.PRETRAINED_PATH)
    model = mod.setup_experiment(model, exp_type).to(device)

    pos_weight = torch.tensor([class_weights[1] / class_weights[0]], dtype=torch.float32).to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    groups = []
    head = [p for n, p in model.named_parameters() if p.requires_grad and "head" in n]
    lead = [p for n, p in model.named_parameters() if p.requires_grad and "lead" in n]
    if head:
        groups.append({"params": head, "lr": mod.LR_CLASSIFIER})
    if lead:
        groups.append({"params": lead, "lr": mod.LR_LEAD_EMB})
    optimizer = torch.optim.AdamW(groups, weight_decay=mod.WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=mod.NUM_EPOCHS)

    best_val_loss, best_state, best_epoch, patience = float("inf"), None, 0, 0
    history = []
    t0 = time.time()
    for epoch in range(1, mod.NUM_EPOCHS + 1):
        train_loss = mod.train_one_epoch(model, train_loader, criterion, optimizer, device)
        vm = mod.evaluate(model, val_loader, criterion, device)
        scheduler.step()
        history.append({"epoch": epoch, "train_loss": round(train_loss, 4), "val_loss": round(vm["loss"], 4),
                        "val_f1": round(float(vm["f1"]), 4), "val_auc": round(float(vm["auc_roc"]), 4)})
        log(f"  Exp {exp_type} | epoch {epoch:2d} | train {train_loss:.4f} | val {vm['loss']:.4f} "
            f"| val F1 {vm['f1']:.4f} | val AUC {vm['auc_roc']:.4f} | {time.time() - t0:.0f}s")
        if vm["loss"] < best_val_loss:
            best_val_loss, best_epoch, patience = vm["loss"], epoch, 0
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            patience += 1
            if patience >= mod.PATIENCE:
                log(f"  Early stopping ở epoch {epoch}")
                break

    model.load_state_dict(best_state)
    val_m = to_py(mod.evaluate(model, val_loader, criterion, device))
    test_m = to_py(mod.evaluate(model, test_loader, criterion, device))
    log(f"  Exp {exp_type}: best epoch {best_epoch} | val AUC {val_m['auc']} | "
        f"test acc {test_m['accuracy']} F1 {test_m['f1']} AUC {test_m['auc']} ({time.time() - t0:.0f}s)")

    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    trainable = {k: v.cpu() for k, v in model.state_dict().items() if "head" in k or "lead" in k}
    WEIGHTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    torch.save(trainable, WEIGHTS_FILE)
    return model, {
        "experiment": exp_type,
        "pretrained_loaded": bool(loaded),
        "trainable_params": n_trainable,
        "best_epoch": best_epoch,
        "epochs_run": len(history),
        "train_seconds": round(time.time() - t0),
        "val": val_m,
        "test": test_m,
        "history": history,
    }


@torch.no_grad()
def test_roc(model, X, y, device, n_points=120):
    """Đường ROC trên tập test (rút gọn ~120 điểm) cho mục 07."""
    from sklearn.metrics import roc_curve
    model.eval()
    probs = []
    for i in range(0, len(X), 64):
        probs.append(torch.sigmoid(model(torch.from_numpy(X[i:i + 64]).to(device))).cpu().numpy().ravel())
    fpr, tpr, _ = roc_curve(y.astype(int), np.concatenate(probs))
    idx = np.unique(np.linspace(0, len(fpr) - 1, min(len(fpr), n_points)).astype(int))
    return {"fpr": [round(float(v), 4) for v in fpr[idx]], "tpr": [round(float(v), 4) for v in tpr[idx]]}


@torch.no_grad()
def predict_records(mod, model, device):
    """Xác suất Abnormal cho mọi cửa sổ 9 s (không chồng lấn) của từng record."""
    model.eval()
    win = int(mod.WINDOW_SECONDS * mod.FS_TARGET)
    out = {}
    for rec in PREDICT_RECORDS:
        sig, ann_samples, ann_symbols = mod.load_and_process_record(rec)
        n_win = sig.shape[1] // win
        X = np.stack([sig[:, i * win:(i + 1) * win] for i in range(n_win)]).astype(np.float32)
        probs = []
        for i in range(0, n_win, 64):
            logits = model(torch.from_numpy(X[i:i + 64]).to(device))
            probs.append(torch.sigmoid(logits).cpu().numpy().ravel())
        probs = np.concatenate(probs)
        labels = []
        for i in range(n_win):
            m = (ann_samples >= i * win) & (ann_samples < (i + 1) * win)
            mapped = [mod.map_label(s) for s, keep in zip(ann_symbols, m) if keep]
            mapped = [v for v in mapped if v is not None]
            labels.append(None if not mapped else int(any(v == 1 for v in mapped)))
        out[rec] = {"probs": [round(float(p), 4) for p in probs], "labels": labels}
        valid = [(p >= THRESHOLD, l) for p, l in zip(probs, labels) if l is not None]
        acc = np.mean([int(p) == l for p, l in valid]) if valid else float("nan")
        log(f"  {rec}: {n_win} cửa sổ, accuracy so với nhãn = {acc:.3f}")
    return out


def main():
    t_start = time.time()
    BD.ensure_downloads(set(BD.ALL_RECORDS))
    use_local_mitdb()
    mod = load_mitbih_module()
    device = mod.DEVICE
    log(f"Device: {device}" + (f" ({torch.cuda.get_device_name(0)})" if device.type == "cuda" else ""))

    log("Tạo dataset (bandpass + notch, resample 250 Hz, cửa sổ 9 s, 2 lead)...")
    X_tr, y_tr, X_va, y_va, X_te, y_te = build_or_load_datasets(mod)

    from sklearn.utils.class_weight import compute_class_weight
    cw = compute_class_weight("balanced", classes=np.array([0, 1]), y=y_tr)
    class_weights = {0: float(cw[0]), 1: float(cw[1])}

    set_seed()
    kw = dict(num_workers=0, pin_memory=True)
    g = torch.Generator().manual_seed(SEED)
    loaders = (
        DataLoader(mod.ECGDataset(X_tr, y_tr), batch_size=mod.BATCH_SIZE, shuffle=True, generator=g, **kw),
        DataLoader(mod.ECGDataset(X_va, y_va), batch_size=mod.BATCH_SIZE, shuffle=False, **kw),
        DataLoader(mod.ECGDataset(X_te, y_te), batch_size=mod.BATCH_SIZE, shuffle=False, **kw),
    )

    results, models = [], {}
    for exp in (CHOSEN_EXPERIMENT,):
        log(f"Thử nghiệm {exp}...")
        model, res = train_experiment(mod, exp, loaders, class_weights, device)
        results.append(res)
        models[exp] = model

    best = next(r for r in results if r["experiment"] == CHOSEN_EXPERIMENT)
    log(f"Dùng thử nghiệm {CHOSEN_EXPERIMENT} (Semi-finetune, như report) cho màn hình theo dõi")
    roc_test = test_roc(models[CHOSEN_EXPERIMENT], X_te, y_te, device)
    predictions = predict_records(mod, models[CHOSEN_EXPERIMENT], device)

    dist = lambda y: {"normal": int((y == 0).sum()), "abnormal": int((y == 1).sum())}  # noqa: E731
    data = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source": "notebooks/Classification/ST-MEM/mit-bih.py (chạy lại qua demo/train_stmem.py)",
        "device": torch.cuda.get_device_name(0) if device.type == "cuda" else str(device),
        "seed": SEED,
        "config": {
            "fs": mod.FS_TARGET, "window_s": mod.WINDOW_SECONDS, "seq_len": mod.SEQ_LEN,
            "patch_size": mod.PATCH_SIZE, "num_leads": mod.NUM_LEADS, "batch_size": mod.BATCH_SIZE,
            "max_epochs": mod.NUM_EPOCHS, "patience": mod.PATIENCE, "stride_s": STRIDE_SECONDS,
            "lr_head": mod.LR_CLASSIFIER, "lr_lead_emb": mod.LR_LEAD_EMB,
        },
        "split": {"train": dist(y_tr), "val": dist(y_va), "test": dist(y_te)},
        "experiments": results,
        "chosen_experiment": best["experiment"],
        "threshold": THRESHOLD,
        "report_table_5_3": REPORT_TABLE_5_3,
        "roc_test": roc_test,
        "predictions": predictions,
    }
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    log(f"Đã ghi {OUT_FILE} — tổng thời gian {time.time() - t_start:.0f}s")


if __name__ == "__main__":
    main()
