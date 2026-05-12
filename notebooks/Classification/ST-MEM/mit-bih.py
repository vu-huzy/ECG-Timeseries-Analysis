"""
Áp dụng thuật toán ST-MEM (Spatio-Temporal Masked Electrocardiogram Modeling)
lên dataset MIT-BIH Arrhythmia để phân loại ECG nhị phân (Normal / Abnormal).

Pipeline:
  1. Load data MIT-BIH từ wfdb (PhysioNet)
  2. Preprocessing: bandpass 0.5-40Hz, notch 60Hz (giống ARIMA notebook)
  3. Resample 360Hz → 250Hz (cho khớp với ST-MEM paper)
  4. Tạo sliding windows 9s không trùng nhau, gán nhãn binary (giống CNN model)
  5. Hai thử nghiệm:
     - Thử nghiệm 1: Freeze encoder, chỉ train classifier head
     - Thử nghiệm 2: Train lead embeddings + classifier head
  6. Đầu ra sigmoid dự đoán 2 nhãn (Normal=0, Abnormal=1)

Usage:
  cd ST-MEM
  python mit-bih.py
"""

import os
import sys
import gc
import warnings
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from scipy.signal import butter, filtfilt, iirnotch, resample
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
from sklearn.utils.class_weight import compute_class_weight
from collections import Counter
from tqdm import tqdm

warnings.filterwarnings('ignore')

# Add current directory to path for model imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models.encoder.st_mem_vit import ST_MEM_ViT

# ========================================================================
# CONFIGURATION
# ========================================================================
FS_ORIGINAL = 360        # MIT-BIH original sampling rate
FS_TARGET = 250          # ST-MEM target sampling rate (paper standard)
WINDOW_SECONDS = 9.0     # Window duration in seconds
STRIDE_SECONDS = 9.0     # Non-overlapping stride
SEQ_LEN = int(WINDOW_SECONDS * FS_TARGET)  # 2250 samples (matches ST-MEM default)
PATCH_SIZE = 75           # ST-MEM default patch size (2250 / 75 = 30 patches)
NUM_LEADS = 2             # MIT-BIH has 2 leads (MLII + V5)
NUM_CLASSES = 1           # Binary classification with sigmoid

# Model: ST-MEM ViT Base
EMBED_DIM = 768
DEPTH = 12
NUM_HEADS = 12
MLP_RATIO = 4

# Training
BATCH_SIZE = 32
NUM_EPOCHS = 50
LR_CLASSIFIER = 1e-3
LR_LEAD_EMB = 1e-4
WEIGHT_DECAY = 1e-4
PATIENCE = 10

# Pre-trained checkpoint
PRETRAINED_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'pretrain', 'st_mem_vit_base_encoder.pth'
)

# Data
NORMAL_SYMBOLS = {'N'}
DROP_SYMBOLS = {'+', 'x', '"', 'Q', '~'}

ALL_RECORDS = [
    '100', '101', '102', '103', '104', '105', '106', '107', '108', '109',
    '111', '112', '113', '114', '115', '116', '117', '118', '119', '121',
    '122', '123', '124', '200', '201', '202', '203', '205', '207', '208',
    '209', '210', '212', '213', '214', '215', '217', '219', '220', '221',
    '222', '223', '228', '230', '231', '232', '233', '234'
]
TEST_RECORDS = ['102', '103', '104', '105', '106']
VAL_RECORDS = ['200', '208', '232', '233', '234']
TRAIN_RECORDS = [r for r in ALL_RECORDS if r not in TEST_RECORDS + VAL_RECORDS]

# Device
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ========================================================================
# PREPROCESSING FUNCTIONS (giống ARIMA notebook)
# ========================================================================

def bandpass_filter(signal, fs=360, lowcut=0.5, highcut=40.0, order=4):
    """Band-pass filter 0.5-40 Hz (Butterworth)."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)


def notch_filter(signal, fs=360, notch_freq=60.0, quality_factor=30.0):
    """Notch filter to remove power-line noise."""
    nyq = 0.5 * fs
    w0 = notch_freq / nyq
    b, a = iirnotch(w0, quality_factor)
    return filtfilt(b, a, signal)


def preprocess_ecg(signal, fs=360, use_notch=True, notch_freq=60.0):
    """Full preprocessing: bandpass → notch (giống ARIMA notebook)."""
    filtered = bandpass_filter(signal, fs=fs, lowcut=0.5, highcut=40.0, order=4)
    if use_notch:
        filtered = notch_filter(filtered, fs=fs, notch_freq=notch_freq, quality_factor=30.0)
    return filtered


def resample_signal(signal, fs_original, fs_target):
    """Resample tín hiệu từ fs_original sang fs_target."""
    num_samples_target = int(len(signal) * fs_target / fs_original)
    return resample(signal, num_samples_target)


# ========================================================================
# LABEL MAPPING (giống CNN model)
# ========================================================================

def map_label(symbol):
    """Map annotation symbol to binary label: 0=Normal, 1=Abnormal, None=drop."""
    if symbol in NORMAL_SYMBOLS:
        return 0
    if symbol in DROP_SYMBOLS:
        return None
    return 1


# ========================================================================
# DATA LOADING & SLIDING WINDOW
# ========================================================================

def load_and_process_record(record_name):
    """
    Load 1 record MIT-BIH, preprocess, resample, trả về signal 2-lead và annotations.
    """
    import wfdb

    record = wfdb.rdrecord(record_name, pn_dir='mitdb')
    ann = wfdb.rdann(record_name, 'atr', pn_dir='mitdb')
    fs = record.fs  # 360 Hz

    # Lấy cả 2 leads
    signals = []
    for lead_idx in range(min(2, record.p_signal.shape[1])):
        raw = record.p_signal[:, lead_idx].astype(float)
        # Preprocess giống ARIMA notebook
        cleaned = preprocess_ecg(raw, fs=fs, use_notch=True, notch_freq=60.0)
        # Resample 360 → 250 Hz
        resampled = resample_signal(cleaned, fs, FS_TARGET)
        signals.append(resampled)

    # Nếu chỉ có 1 lead, duplicate
    if len(signals) == 1:
        signals.append(signals[0].copy())

    # Stack thành (2, length)
    signal_2lead = np.stack(signals, axis=0)

    # Resample annotation positions
    ann_samples_resampled = (ann.sample * FS_TARGET / fs).astype(int)

    return signal_2lead, ann_samples_resampled, ann.symbol


def create_windows_for_record(record_name, window_samples, stride_samples):
    """
    Tạo non-overlapping sliding windows cho 1 record.
    Trả về danh sách (window_data, label) pairs.
    """
    signal_2lead, ann_samples, ann_symbols = load_and_process_record(record_name)
    total_samples = signal_2lead.shape[1]

    windows = []
    labels = []

    start = 0
    while start + window_samples <= total_samples:
        end = start + window_samples

        # Lấy window từ cả 2 leads: shape (2, window_samples)
        window_data = signal_2lead[:, start:end]

        # Tìm annotations trong window
        mask = (ann_samples >= start) & (ann_samples < end)
        window_symbols = [ann_symbols[i] for i in range(len(ann_symbols)) if mask[i]]

        # Map labels
        mapped = [map_label(s) for s in window_symbols]
        mapped = [m for m in mapped if m is not None]

        if len(mapped) == 0:
            # Không có annotation hợp lệ → skip window
            start += stride_samples
            continue

        # Nếu có bất kỳ abnormal nào → label = 1
        label = 1 if any(m == 1 for m in mapped) else 0

        windows.append(window_data)
        labels.append(label)
        start += stride_samples

    return windows, labels


def build_dataset_split(record_list):
    """Build dataset cho 1 split (train/val/test)."""
    window_samples = int(WINDOW_SECONDS * FS_TARGET)
    stride_samples = int(STRIDE_SECONDS * FS_TARGET)

    all_windows = []
    all_labels = []

    for rec in tqdm(record_list, desc="Loading records"):
        try:
            windows, labels = create_windows_for_record(rec, window_samples, stride_samples)
            all_windows.extend(windows)
            all_labels.extend(labels)
        except Exception as e:
            print(f"  Lỗi record {rec}: {e}")
            continue

    if len(all_windows) == 0:
        return np.array([]), np.array([])

    X = np.stack(all_windows, axis=0)  # (N, 2, seq_len)
    y = np.array(all_labels, dtype=np.float32)  # (N,)
    return X, y


# ========================================================================
# PYTORCH DATASET
# ========================================================================

class ECGDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.from_numpy(X).float()
        self.y = torch.from_numpy(y).float().unsqueeze(1)  # (N, 1) for BCEWithLogitsLoss

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


# ========================================================================
# MODEL BUILDING
# ========================================================================

def build_model(num_leads=NUM_LEADS, num_classes=NUM_CLASSES,
                seq_len=SEQ_LEN, patch_size=PATCH_SIZE):
    """Build ST-MEM ViT Base model cho MIT-BIH (2 leads)."""
    model = ST_MEM_ViT(
        seq_len=seq_len,
        patch_size=patch_size,
        num_leads=num_leads,
        num_classes=num_classes,
        width=EMBED_DIM,
        depth=DEPTH,
        heads=NUM_HEADS,
        mlp_dim=MLP_RATIO * EMBED_DIM,
        qkv_bias=True,
    )
    return model


def load_pretrained_weights(model, checkpoint_path):
    """
    Load pre-trained encoder weights.
    Xử lý mismatch giữa 12-lead pretrained và 2-lead target.
    Chỉ load các weights tương thích (transformer blocks, pos_embedding, etc.)
    Skip lead_embeddings và head vì shape khác.
    """
    if not os.path.exists(checkpoint_path):
        print(f"[WARNING] Checkpoint không tồn tại: {checkpoint_path}")
        print("  → Sẽ train từ scratch (random init).")
        return model, False

    print(f"Loading pre-trained checkpoint: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location='cpu')

    # Checkpoint có thể chứa 'model' key (ST-MEM format)
    if 'model' in checkpoint:
        state_dict = checkpoint['model']
    else:
        state_dict = checkpoint

    model_state = model.state_dict()

    # Filter: chỉ load weights có shape khớp
    loaded_keys = []
    skipped_keys = []
    for k, v in state_dict.items():
        if k in model_state:
            if v.shape == model_state[k].shape:
                model_state[k] = v
                loaded_keys.append(k)
            else:
                skipped_keys.append(f"{k} (pretrained: {v.shape} vs model: {model_state[k].shape})")
        else:
            skipped_keys.append(f"{k} (not in model)")

    model.load_state_dict(model_state)

    print(f"  Loaded {len(loaded_keys)} params, skipped {len(skipped_keys)} params.")
    if skipped_keys:
        print(f"  Skipped keys (first 10):")
        for sk in skipped_keys[:10]:
            print(f"    - {sk}")
        if len(skipped_keys) > 10:
            print(f"    ... and {len(skipped_keys) - 10} more")

    return model, True


def setup_experiment(model, experiment_type):
    """
    Thiết lập parameters cho mỗi thử nghiệm.

    experiment_type:
      1 → Freeze encoder, chỉ train classifier head
      2 → Train lead embeddings + classifier head
    """
    # Freeze tất cả
    for param in model.parameters():
        param.requires_grad = False

    if experiment_type == 1:
        # Thử nghiệm 1: Chỉ unfreeze classifier head
        for param in model.head.parameters():
            param.requires_grad = True
        trainable_desc = "classifier head only"

    elif experiment_type == 2:
        # Thử nghiệm 2: Unfreeze lead embeddings + classifier head
        for param in model.head.parameters():
            param.requires_grad = True
        for param in model.lead_embeddings.parameters():
            param.requires_grad = True
        trainable_desc = "lead embeddings + classifier head"

    # Count params
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    frozen_params = total_params - trainable_params

    print(f"  Experiment {experiment_type}: {trainable_desc}")
    print(f"  Total params: {total_params:,}")
    print(f"  Trainable:    {trainable_params:,}")
    print(f"  Frozen:       {frozen_params:,}")

    return model


# ========================================================================
# TRAINING LOOP
# ========================================================================

def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    total_loss = 0
    total_samples = 0

    for batch_X, batch_y in dataloader:
        batch_X = batch_X.to(device)
        batch_y = batch_y.to(device)

        optimizer.zero_grad()
        logits = model(batch_X)  # (B, 1)
        loss = criterion(logits, batch_y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * batch_X.size(0)
        total_samples += batch_X.size(0)

    return total_loss / total_samples


@torch.no_grad()
def evaluate(model, dataloader, criterion, device):
    model.eval()
    total_loss = 0
    total_samples = 0
    all_preds = []
    all_probs = []
    all_labels = []

    for batch_X, batch_y in dataloader:
        batch_X = batch_X.to(device)
        batch_y = batch_y.to(device)

        logits = model(batch_X)  # (B, 1)
        loss = criterion(logits, batch_y)

        probs = torch.sigmoid(logits)  # Sigmoid output
        preds = (probs >= 0.5).float()

        total_loss += loss.item() * batch_X.size(0)
        total_samples += batch_X.size(0)
        all_probs.append(probs.cpu().numpy())
        all_preds.append(preds.cpu().numpy())
        all_labels.append(batch_y.cpu().numpy())

    avg_loss = total_loss / total_samples
    all_probs = np.concatenate(all_probs, axis=0).squeeze()
    all_preds = np.concatenate(all_preds, axis=0).squeeze()
    all_labels = np.concatenate(all_labels, axis=0).squeeze()

    metrics = compute_metrics(all_labels, all_preds, all_probs)
    metrics['loss'] = avg_loss
    return metrics


def compute_metrics(y_true, y_pred, y_prob):
    """Compute classification metrics."""
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    try:
        auc = roc_auc_score(y_true, y_prob)
    except ValueError:
        auc = 0.0

    return {
        'accuracy': acc,
        'precision': prec,
        'recall': rec,
        'f1': f1,
        'auc_roc': auc,
        'y_true': y_true,
        'y_pred': y_pred,
    }


def run_experiment(experiment_type, train_loader, val_loader, test_loader,
                   class_weights, device):
    """Chạy 1 thử nghiệm hoàn chỉnh."""
    print(f"\n{'='*70}")
    print(f"  THỬ NGHIỆM {experiment_type}")
    print(f"{'='*70}")

    # Build model
    model = build_model()

    # Load pre-trained weights
    model, loaded = load_pretrained_weights(model, PRETRAINED_PATH)

    # Setup experiment (freeze/unfreeze)
    model = setup_experiment(model, experiment_type)
    model = model.to(device)

    # Loss function with class weights
    pos_weight = torch.tensor([class_weights[1] / class_weights[0]]).to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    # Optimizer: different LR for different param groups
    param_groups = []
    # Classifier head
    head_params = [p for n, p in model.named_parameters()
                   if p.requires_grad and 'head' in n]
    if head_params:
        param_groups.append({'params': head_params, 'lr': LR_CLASSIFIER})

    # Lead embeddings (only for experiment 2)
    lead_params = [p for n, p in model.named_parameters()
                   if p.requires_grad and 'lead' in n]
    if lead_params:
        param_groups.append({'params': lead_params, 'lr': LR_LEAD_EMB})

    if not param_groups:
        print("[ERROR] Không có parameters nào để train!")
        return None

    optimizer = torch.optim.AdamW(param_groups, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS)

    # Training loop with early stopping
    best_val_loss = float('inf')
    best_model_state = None
    patience_counter = 0

    for epoch in range(1, NUM_EPOCHS + 1):
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_metrics = evaluate(model, val_loader, criterion, device)
        val_loss = val_metrics['loss']

        scheduler.step()

        if epoch % 5 == 0 or epoch == 1:
            print(f"  Epoch {epoch:3d}/{NUM_EPOCHS} | "
                  f"Train Loss: {train_loss:.4f} | "
                  f"Val Loss: {val_loss:.4f} | "
                  f"Val F1: {val_metrics['f1']:.4f} | "
                  f"Val AUC: {val_metrics['auc_roc']:.4f}")

        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_state = {k: v.clone() for k, v in model.state_dict().items()}
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                print(f"  Early stopping at epoch {epoch}")
                break

    # Load best model
    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    # Evaluate on test set
    print(f"\n  --- Kết quả trên Test Set ---")
    test_metrics = evaluate(model, test_loader, criterion, device)

    print(f"  Loss:      {test_metrics['loss']:.4f}")
    print(f"  Accuracy:  {test_metrics['accuracy']:.4f}")
    print(f"  Precision: {test_metrics['precision']:.4f}")
    print(f"  Recall:    {test_metrics['recall']:.4f}")
    print(f"  F1-Score:  {test_metrics['f1']:.4f}")
    print(f"  AUC-ROC:   {test_metrics['auc_roc']:.4f}")

    # Classification report
    print(f"\n  Classification Report:")
    print(classification_report(
        test_metrics['y_true'], test_metrics['y_pred'],
        target_names=['Normal', 'Abnormal'], zero_division=0
    ))

    # Confusion matrix
    cm = confusion_matrix(test_metrics['y_true'], test_metrics['y_pred'])
    print(f"  Confusion Matrix:")
    print(f"    {cm}")

    return test_metrics


# ========================================================================
# MAIN
# ========================================================================

def main():
    print("=" * 70)
    print("  ST-MEM ViT Base - MIT-BIH Arrhythmia Classification")
    print("=" * 70)
    print(f"Device: {DEVICE}")
    print(f"Window: {WINDOW_SECONDS}s = {SEQ_LEN} samples (at {FS_TARGET}Hz)")
    print(f"Patch size: {PATCH_SIZE} → {SEQ_LEN // PATCH_SIZE} patches")
    print(f"Num leads: {NUM_LEADS}")
    print(f"Model: ViT Base (d={EMBED_DIM}, L={DEPTH}, H={NUM_HEADS})")
    print(f"Pre-trained: {PRETRAINED_PATH}")

    # Step 1: Load & process data
    print(f"\n--- Step 1: Loading & Processing Data ---")
    print(f"  Resample: {FS_ORIGINAL}Hz → {FS_TARGET}Hz")
    print(f"  Window: {WINDOW_SECONDS}s, Stride: {STRIDE_SECONDS}s (non-overlapping)")

    print(f"\n  Building TRAIN set ({len(TRAIN_RECORDS)} records)...")
    X_train, y_train = build_dataset_split(TRAIN_RECORDS)
    print(f"    → {len(X_train)} windows, shape: {X_train.shape if len(X_train) > 0 else 'empty'}")

    print(f"\n  Building VAL set ({len(VAL_RECORDS)} records)...")
    X_val, y_val = build_dataset_split(VAL_RECORDS)
    print(f"    → {len(X_val)} windows, shape: {X_val.shape if len(X_val) > 0 else 'empty'}")

    print(f"\n  Building TEST set ({len(TEST_RECORDS)} records)...")
    X_test, y_test = build_dataset_split(TEST_RECORDS)
    print(f"    → {len(X_test)} windows, shape: {X_test.shape if len(X_test) > 0 else 'empty'}")

    # Print label distribution
    for name, y in [('TRAIN', y_train), ('VAL', y_val), ('TEST', y_test)]:
        if len(y) > 0:
            n_normal = int((y == 0).sum())
            n_abnormal = int((y == 1).sum())
            print(f"  {name}: Normal={n_normal}, Abnormal={n_abnormal}, "
                  f"Total={len(y)}, Abnormal%={100*n_abnormal/len(y):.1f}%")

    # Compute class weights for imbalanced data
    classes = np.array([0, 1])
    cw = compute_class_weight('balanced', classes=classes, y=y_train)
    class_weights = {0: cw[0], 1: cw[1]}
    print(f"\n  Class weights: {class_weights}")

    # Step 2: Create dataloaders
    print(f"\n--- Step 2: Creating DataLoaders ---")
    train_dataset = ECGDataset(X_train, y_train)
    val_dataset = ECGDataset(X_val, y_val)
    test_dataset = ECGDataset(X_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=0, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False,
                            num_workers=0, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False,
                             num_workers=0, pin_memory=True)

    # Step 3: Run experiments
    print(f"\n--- Step 3: Running Experiments ---")

    # Thử nghiệm 1: Freeze encoder, chỉ train classifier head
    results_exp1 = run_experiment(
        experiment_type=1,
        train_loader=train_loader,
        val_loader=val_loader,
        test_loader=test_loader,
        class_weights=class_weights,
        device=DEVICE,
    )

    # Thử nghiệm 2: Train lead embeddings + classifier head
    results_exp2 = run_experiment(
        experiment_type=2,
        train_loader=train_loader,
        val_loader=val_loader,
        test_loader=test_loader,
        class_weights=class_weights,
        device=DEVICE,
    )

    # Step 4: So sánh kết quả
    print(f"\n{'='*70}")
    print(f"  SO SÁNH KẾT QUẢ 2 THỬ NGHIỆM")
    print(f"{'='*70}")
    print(f"{'Metric':<15} {'Exp 1 (Freeze Enc)':<22} {'Exp 2 (+Lead Emb)':<22}")
    print(f"{'-'*59}")
    for metric in ['accuracy', 'precision', 'recall', 'f1', 'auc_roc']:
        v1 = results_exp1[metric] if results_exp1 else 0
        v2 = results_exp2[metric] if results_exp2 else 0
        print(f"{metric:<15} {v1:<22.4f} {v2:<22.4f}")

    print(f"\n  Hoàn thành!")


if __name__ == '__main__':
    main()
