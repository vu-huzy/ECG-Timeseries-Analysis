import os
import sys
import ast
import copy
import time
import warnings
import datetime

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from scipy.signal import resample as scipy_resample
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score
from tqdm import tqdm
import wfdb

warnings.filterwarnings('ignore')

# ========================================================================
# CẤU HÌNH
# ========================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRETRAINED_PATH = os.path.join(SCRIPT_DIR, 'pretrain', 'st_mem_vit_base_encoder.pth')

# Đường dẫn tới thư mục PTB-XL local (chứa ptbxl_database.csv, scp_statements.csv, records500/)
PTBXL_PATH = os.path.join(SCRIPT_DIR, 'data', 'ptb-xl-a-comprehensive-electrocardiographic-feature-dataset-1.0.1')

# Tín hiệu
FS_PTBXL = 500           # Sampling rate bản 500Hz
FS_TARGET = 250          # Resample xuống 250Hz (theo bài báo ST-MEM)
DURATION_SEC = 9.0       # Cắt 9 giây → 2250 samples
SEQ_LEN = int(DURATION_SEC * FS_TARGET)   # 2250
PATCH_SIZE = 75          # 2250 / 75 = 30 patches
NUM_LEADS = 12           # PTB-XL 12-lead

# 5 superclass
SUPERCLASSES = ['NORM', 'MI', 'STTC', 'CD', 'HYP']
NUM_CLASSES = len(SUPERCLASSES)

# Model ViT Base
EMBED_DIM = 768
DEPTH = 12
NUM_HEADS = 12
MLP_RATIO = 4

# Training chung
BATCH_SIZE = 64
NUM_EPOCHS = 50
WEIGHT_DECAY = 1e-4
PATIENCE = 10

# Learning rate
LR_SUPERVISED = 1e-3     # Supervised baseline: LR cao vì random init
LR_FINETUNE = 1e-4       # ST-MEM fine-tune: LR thấp để bảo toàn pretrained features

# Device
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Import models
sys.path.insert(0, SCRIPT_DIR)
from models.encoder.st_mem_vit import ST_MEM_ViT


# ========================================================================
# LOAD METADATA TỪ LOCAL
# ========================================================================

def get_metadata():
    """Load ptbxl_database.csv + scp_statements.csv từ thư mục local."""
    db_path = os.path.join(PTBXL_PATH, 'ptbxl_database.csv')
    scp_path = os.path.join(PTBXL_PATH, 'scp_statements.csv')

    meta = pd.read_csv(db_path, index_col='ecg_id')
    meta.scp_codes = meta.scp_codes.apply(ast.literal_eval)

    scp_df = pd.read_csv(scp_path, index_col=0)
    scp_df = scp_df[scp_df.diagnostic == 1.0]

    return meta, scp_df


# ========================================================================
# 1. ĐỌC PTB-XL METADATA & TẠO LABEL 5 SUPERCLASS
# ========================================================================

def build_labels(meta, scp_df):
    """
    Parse SCP codes → multi-label 5 superclass.
    Chỉ giữ records có ít nhất 1 superclass label.
    """
    def scp_to_superclass(scp_dict):
        classes = set()
        for code, conf in scp_dict.items():
            if conf >= 100.0 and code in scp_df.index:
                cls = scp_df.loc[code, 'diagnostic_class']
                if isinstance(cls, str) and cls in SUPERCLASSES:
                    classes.add(cls)
        return list(classes)

    meta['superclass'] = meta.scp_codes.apply(scp_to_superclass)
    for sc in SUPERCLASSES:
        meta[sc] = meta['superclass'].apply(lambda x: 1.0 if sc in x else 0.0)

    mask = meta[SUPERCLASSES].sum(axis=1) > 0
    meta = meta[mask].copy()

    print(f"  Records với label: {len(meta)}")
    for sc in SUPERCLASSES:
        n = int(meta[sc].sum())
        print(f"    {sc}: {n} ({100*n/len(meta):.1f}%)")

    return meta


# ========================================================================
# 2. LOAD WAVEFORM & PREPROCESSING
# ========================================================================

def load_waveforms(meta, fs_target=FS_TARGET, seq_len=SEQ_LEN):
    """
    Load waveforms 500Hz từ local, resample → fs_target, cắt → seq_len.
    Preprocessing theo bài báo ST-MEM:
      - Resample 500Hz → 250Hz
      - Z-score normalization per lead
      - Cắt/pad tới seq_len
    """
    n = len(meta)
    X = np.zeros((n, NUM_LEADS, seq_len), dtype=np.float32)
    valid_mask = np.ones(n, dtype=bool)

    for i, (idx, row) in enumerate(tqdm(meta.iterrows(), total=n,
                                         desc="  Loading waveforms")):
        fname_hr = row['filename_hr']
        record_path = os.path.join(PTBXL_PATH, fname_hr)

        try:
            record = wfdb.rdrecord(record_path)
            sig = record.p_signal  # (5000, 12)
        except Exception as e:
            print(f"    ⚠ Record {idx}: {e}")
            valid_mask[i] = False
            continue

        # Xử lý NaN
        sig = np.nan_to_num(sig, nan=0.0).astype(np.float32)
        sig = sig.T  # → (12, 5000)

        # Resample 500Hz → 250Hz
        if FS_PTBXL != fs_target:
            n_target = int(sig.shape[1] * fs_target / FS_PTBXL)
            sig_res = np.zeros((sig.shape[0], n_target), dtype=np.float32)
            for lead in range(sig.shape[0]):
                sig_res[lead] = scipy_resample(sig[lead], n_target)
            sig = sig_res

        # Cắt/pad tới seq_len
        if sig.shape[1] >= seq_len:
            sig = sig[:, :seq_len]
        else:
            sig = np.pad(sig, ((0, 0), (0, seq_len - sig.shape[1])))

        # Z-score normalization per lead
        for lead in range(sig.shape[0]):
            mu, sigma = sig[lead].mean(), sig[lead].std()
            sig[lead] = (sig[lead] - mu) / (sigma + 1e-8)

        X[i] = sig

    return X, valid_mask


# ========================================================================
# 3. CHIA TRAIN / VALID / TEST THEO strat_fold
# ========================================================================

def split_by_fold(meta, X, valid_mask):
    """
    strat_fold: Train = 1-8, Val = 9, Test = 10
    """
    meta_valid = meta.iloc[valid_mask]
    X_valid = X[valid_mask]
    y_all = meta_valid[SUPERCLASSES].values.astype(np.float32)
    folds = meta_valid['strat_fold'].values

    tr = np.isin(folds, list(range(1, 9)))
    va = folds == 9
    te = folds == 10

    X_tr, y_tr = X_valid[tr], y_all[tr]
    X_va, y_va = X_valid[va], y_all[va]
    X_te, y_te = X_valid[te], y_all[te]

    print(f"  Train: {len(X_tr)} | Val: {len(X_va)} | Test: {len(X_te)}")
    return X_tr, y_tr, X_va, y_va, X_te, y_te


# ========================================================================
# 4. PYTORCH DATASET & DATALOADER
# ========================================================================

class PTBXLDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.from_numpy(X).float()
        self.y = torch.from_numpy(y).float()

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def make_loaders(X_tr, y_tr, X_va, y_va, X_te, y_te):
    kw = dict(num_workers=0, pin_memory=True)
    train_ld = DataLoader(PTBXLDataset(X_tr, y_tr), batch_size=BATCH_SIZE,
                          shuffle=True, drop_last=True, **kw)
    val_ld = DataLoader(PTBXLDataset(X_va, y_va), batch_size=BATCH_SIZE,
                        shuffle=False, **kw)
    test_ld = DataLoader(PTBXLDataset(X_te, y_te), batch_size=BATCH_SIZE,
                         shuffle=False, **kw)
    return train_ld, val_ld, test_ld


# ========================================================================
# 5. MODEL
# ========================================================================

def build_model():
    """ST-MEM ViT Base cho PTB-XL: 12-lead, 5-class multi-label."""
    return ST_MEM_ViT(
        seq_len=SEQ_LEN, patch_size=PATCH_SIZE,
        num_leads=NUM_LEADS, num_classes=NUM_CLASSES,
        width=EMBED_DIM, depth=DEPTH,
        heads=NUM_HEADS, mlp_dim=MLP_RATIO * EMBED_DIM,
        qkv_bias=True,
    )


def load_pretrained_encoder(model, checkpoint_path):
    """
    Load pretrained encoder.  PTB-XL 12 leads → gần 100% weights khớp (trừ head).
    """
    if not os.path.exists(checkpoint_path):
        print(f"  ⚠ Checkpoint không tồn tại: {checkpoint_path}")
        return model, False

    ckpt = torch.load(checkpoint_path, map_location='cpu')
    sd = ckpt['model'] if 'model' in ckpt else ckpt

    model_sd = model.state_dict()
    loaded = skipped = 0
    skipped_keys = []

    for k, v in sd.items():
        if k in model_sd and v.shape == model_sd[k].shape:
            model_sd[k] = v
            loaded += 1
        else:
            skipped += 1
            skipped_keys.append(k)

    model.load_state_dict(model_sd)
    print(f"  Pretrained: loaded {loaded}, skipped {skipped} params")
    if skipped_keys:
        print(f"    Skipped: {skipped_keys}")
    return model, True


# ========================================================================
# 6. TRAINING & EVALUATION
# ========================================================================

def train_one_epoch(model, loader, criterion, optimizer, device, scaler=None):
    model.train()
    tot, n = 0.0, 0
    for X, y in loader:
        X, y = X.to(device), y.to(device)
        optimizer.zero_grad()
        if scaler is not None:
            with torch.cuda.amp.autocast():
                loss = criterion(model(X), y)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            loss = criterion(model(X), y)
            loss.backward()
            optimizer.step()
        tot += loss.item() * X.size(0)
        n += X.size(0)
    return tot / n


@torch.no_grad()
def evaluate_model(model, loader, criterion, device):
    model.eval()
    tot, n = 0.0, 0
    all_p, all_y = [], []
    for X, y in loader:
        X, y = X.to(device), y.to(device)
        logits = model(X)
        tot += criterion(logits, y).item() * X.size(0)
        n += X.size(0)
        all_p.append(torch.sigmoid(logits).cpu().numpy())
        all_y.append(y.cpu().numpy())
    probs = np.concatenate(all_p)
    labels = np.concatenate(all_y)

    # Per-class AUROC
    pc_auc = {}
    for i, sc in enumerate(SUPERCLASSES):
        try:
            pc_auc[sc] = roc_auc_score(labels[:, i], probs[:, i])
        except ValueError:
            pc_auc[sc] = 0.0

    valid = [v for v in pc_auc.values() if v > 0]
    macro_auc = np.mean(valid) if valid else 0.0

    # F1 (threshold 0.5)
    preds = (probs >= 0.5).astype(float)
    pc_f1 = {}
    for i, sc in enumerate(SUPERCLASSES):
        pc_f1[sc] = f1_score(labels[:, i], preds[:, i], zero_division=0)
    macro_f1 = np.mean(list(pc_f1.values()))

    return {
        'loss': tot / n,
        'macro_auc': macro_auc,
        'macro_f1': macro_f1,
        'per_class_auc': pc_auc,
        'per_class_f1': pc_f1,
    }


def run_training(model, train_ld, val_ld, test_ld, lr, device, tag):
    """Training loop đầy đủ cho 1 mô hình."""
    print(f"\n{'='*70}")
    print(f"  TRAINING: {tag}")
    print(f"  LR={lr}, Epochs={NUM_EPOCHS}, Batch={BATCH_SIZE}")
    print(f"{'='*70}")

    model = model.to(device)
    tot_p = sum(p.numel() for p in model.parameters())
    trn_p = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Params: {tot_p:,} total, {trn_p:,} trainable")

    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=lr, weight_decay=WEIGHT_DECAY
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS)
    scaler = torch.cuda.amp.GradScaler() if device.type == 'cuda' else None

    best_auc, best_st, pat = -1, None, 0
    t0 = time.time()

    for ep in range(1, NUM_EPOCHS + 1):
        tl = train_one_epoch(model, train_ld, criterion, optimizer, device, scaler)
        vm = evaluate_model(model, val_ld, criterion, device)
        scheduler.step()

        va = vm['macro_auc']
        mk = ""
        if va > best_auc:
            best_auc = va
            best_st = copy.deepcopy(model.state_dict())
            pat = 0
            mk = " ★"
        else:
            pat += 1

        if ep % 5 == 0 or ep == 1 or mk:
            el = str(datetime.timedelta(seconds=int(time.time() - t0)))
            print(f"  Ep {ep:3d}/{NUM_EPOCHS} | "
                  f"TrLoss {tl:.4f} | VaLoss {vm['loss']:.4f} | "
                  f"mAUC {va:.4f} | mF1 {vm['macro_f1']:.4f} | "
                  f"{el}{mk}")

        if pat >= PATIENCE:
            print(f"  → Early stopping at epoch {ep}")
            break

    if best_st:
        model.load_state_dict(best_st)
    print(f"  Best Val macro-AUROC: {best_auc:.4f}")

    # Test
    print(f"\n  --- Test Results ({tag}) ---")
    tm = evaluate_model(model, test_ld, criterion, device)
    print(f"  Macro AUROC : {tm['macro_auc']:.4f}")
    print(f"  Macro F1    : {tm['macro_f1']:.4f}")
    print(f"  Per-class AUROC:")
    for sc in SUPERCLASSES:
        print(f"    {sc:6s}: {tm['per_class_auc'][sc]:.4f}")
    print(f"  Per-class F1:")
    for sc in SUPERCLASSES:
        print(f"    {sc:6s}: {tm['per_class_f1'][sc]:.4f}")

    return tm


# ========================================================================
# 7. MAIN
# ========================================================================

def main():
    import gc

    print("=" * 70)
    print("  PTB-XL: Supervised Baseline  vs  ST-MEM Fine-tune")
    print("  (ST-MEM ViT Base, 12-lead, 5 superclass)")
    print("=" * 70)
    print(f"  Device     : {DEVICE}")
    print(f"  Pretrained : {PRETRAINED_PATH}")
    print(f"  seq_len    : {SEQ_LEN} ({DURATION_SEC}s @ {FS_TARGET}Hz)")
    print(f"  patch_size : {PATCH_SIZE} → {SEQ_LEN // PATCH_SIZE} patches")
    print(f"  Classes    : {SUPERCLASSES}")

    # ---- 1. Metadata & Labels ----
    print(f"\n--- Step 1: Đọc metadata & tạo labels ---")
    meta, scp_df = get_metadata()
    meta = build_labels(meta, scp_df)

    # ---- 2. Load waveforms ----
    print(f"\n--- Step 2: Load waveforms từ PhysioNet ---")
    print(f"  Resample {FS_PTBXL}Hz → {FS_TARGET}Hz, "
          f"cắt {DURATION_SEC}s, z-score per lead")
    X, valid_mask = load_waveforms(meta)
    print(f"  Shape: {X.shape}")

    # ---- 3. Split ----
    print(f"\n--- Step 3: Chia train/val/test theo strat_fold ---")
    X_tr, y_tr, X_va, y_va, X_te, y_te = split_by_fold(meta, X, valid_mask)
    del X; gc.collect()

    train_ld, val_ld, test_ld = make_loaders(X_tr, y_tr, X_va, y_va, X_te, y_te)

    # ---- 4a. Supervised (random init) ----
    print(f"\n--- Step 4a: Supervised Baseline (random init) ---")
    m_sup = build_model()
    res_sup = run_training(m_sup, train_ld, val_ld, test_ld,
                           lr=LR_SUPERVISED, device=DEVICE,
                           tag="Supervised (random init)")
    del m_sup
    if DEVICE.type == 'cuda':
        torch.cuda.empty_cache()
    gc.collect()

    # ---- 4b. ST-MEM fine-tune ----
    print(f"\n--- Step 4b: ST-MEM Fine-tune (pretrained encoder) ---")
    m_stm = build_model()
    m_stm, loaded = load_pretrained_encoder(m_stm, PRETRAINED_PATH)
    if not loaded:
        print("  ⚠ Pretrained không load được → train từ scratch!")
    res_stm = run_training(m_stm, train_ld, val_ld, test_ld,
                           lr=LR_FINETUNE, device=DEVICE,
                           tag="ST-MEM Fine-tune")
    del m_stm
    if DEVICE.type == 'cuda':
        torch.cuda.empty_cache()

    # ---- 5. Bảng so sánh ----
    print(f"\n{'='*70}")
    print(f"  BẢNG SO SÁNH KẾT QUẢ TRÊN TEST SET")
    print(f"{'='*70}")

    w1, w2, w3, w4 = 18, 16, 16, 18
    print(f"  {'Metric':<{w1}} {'Supervised':<{w2}} {'ST-MEM':<{w3}} {'Δ (ST-MEM−Sup)':<{w4}}")
    print(f"  {'-'*(w1+w2+w3+w4)}")

    for key, lab in [('macro_auc', 'Macro AUROC'),
                     ('macro_f1', 'Macro F1')]:
        vs = res_sup[key]
        vm = res_stm[key]
        d = vm - vs
        s = '+' if d >= 0 else ''
        print(f"  {lab:<{w1}} {vs:<{w2}.4f} {vm:<{w3}.4f} {s}{d:<{w4-1}.4f}")

    print(f"\n  Per-class AUROC:")
    print(f"  {'Class':<8} {'Supervised':<14} {'ST-MEM':<14} {'Δ':<14}")
    print(f"  {'-'*48}")
    for sc in SUPERCLASSES:
        vs = res_sup['per_class_auc'][sc]
        vm = res_stm['per_class_auc'][sc]
        d = vm - vs
        s = '+' if d >= 0 else ''
        print(f"  {sc:<8} {vs:<14.4f} {vm:<14.4f} {s}{d:<13.4f}")

    print(f"\n  Per-class F1:")
    print(f"  {'Class':<8} {'Supervised':<14} {'ST-MEM':<14} {'Δ':<14}")
    print(f"  {'-'*48}")
    for sc in SUPERCLASSES:
        vs = res_sup['per_class_f1'][sc]
        vm = res_stm['per_class_f1'][sc]
        d = vm - vs
        s = '+' if d >= 0 else ''
        print(f"  {sc:<8} {vs:<14.4f} {vm:<14.4f} {s}{d:<13.4f}")

    diff = res_stm['macro_auc'] - res_sup['macro_auc']
    if diff > 0:
        print(f"\n  ✅ ST-MEM fine-tune tốt hơn Supervised: {diff:+.4f} macro-AUROC")
    elif diff < 0:
        print(f"\n  ❌ Supervised tốt hơn ST-MEM: {-diff:+.4f} macro-AUROC")
    else:
        print(f"\n  ⚖️  Hai mô hình tương đương.")

    print(f"\n  Hoàn thành!")


if __name__ == '__main__':
    main()
