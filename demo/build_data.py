"""
Tạo dữ liệu cho demo web (demo/index.html).

Chạy (từ thư mục gốc của repo):
    python demo/build_data.py
    python demo/build_data.py --refresh-forecast   # chạy lại ARIMA/SARIMA (mất vài phút)
    python demo/build_data.py --skip-forecast      # bỏ qua phần dự báo

Kết quả: demo/data/demo_data.js  →  window.DEMO_DATA = {...}
(dùng file .js thay vì .json để mở index.html trực tiếp bằng double-click vẫn chạy)

Dữ liệu MIT-BIH được tải từ PhysioNet một lần vào demo/.cache/mitdb.
Các hàm xử lý chép từ notebook, giữ nguyên tham số; nguồn ghi ở từng hàm.
Kết quả cần train lâu (phân loại, grid search...) lấy từ demo/notebook_results.py.
"""

import argparse
import datetime
import json
import sys
import time
import warnings
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import wfdb
from scipy.ndimage import median_filter
from scipy.signal import butter, filtfilt, iirnotch, medfilt, sosfiltfilt, welch
from statsmodels.tsa.seasonal import STL

DEMO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO_DIR))
import notebook_results as NR  # noqa: E402

CACHE_DIR = DEMO_DIR / ".cache"
MITDB_DIR = CACHE_DIR / "mitdb"
FORECAST_CACHE = CACHE_DIR / "forecast_100.json"
OUT_FILE = DEMO_DIR / "data" / "demo_data.js"

warnings.filterwarnings("ignore")

# ========================================================================
# CẤU HÌNH
# ========================================================================

ALL_RECORDS = [
    "100", "101", "102", "103", "104", "105", "106", "107", "108", "109",
    "111", "112", "113", "114", "115", "116", "117", "118", "119", "121",
    "122", "123", "124", "200", "201", "202", "203", "205", "207", "208",
    "209", "210", "212", "213", "214", "215", "217", "219", "220", "221",
    "222", "223", "228", "230", "231", "232", "233", "234",
]

# Record tiêu biểu để xem tín hiệu, tiền xử lý và HRV
SHOWCASE = {
    "100": "Gần như toàn nhịp bình thường, vài beat nhĩ sớm (A)",
    "109": "Block nhánh trái — beat L",
    "119": "Ngoại tâm thu thất (V) dạng nhịp đôi/nhịp ba",
    "203": "Nhiều nhiễu, PVC đa dạng, rung/cuồng nhĩ",
    "208": "PVC kèm beat hỗn hợp (F)",
    "232": "Nhịp chậm, nhiều beat nhĩ sớm (A), có khoảng ngưng dài",
}
FORECAST_RECORD = "100"
EXAMPLE_RECORD = "106"   # record test dùng để minh hoạ 2 quy tắc gán nhãn

SEGMENT_SECONDS = 30
MAINS_HZ = 60.0

# Annotation là beat thật (giống notebook ARIMA, cell 20)
BEAT_SYMBOLS = {"N", "L", "R", "A", "a", "J", "S", "V", "F", "e", "j", "E", "/", "f", "Q"}

# Quy ước nhãn của notebook phân loại
NORMAL_SYMBOLS = {"N"}
DROP_SYMBOLS = {"+", "x", '"', "Q", "~"}

SPLIT = {r: "test" for r in NR.CLASSIFICATION["split"]["test"]}
SPLIT.update({r: "val" for r in NR.CLASSIFICATION["split"]["val"]})

SYMBOL_INFO = {
    "N": ("Normal beat", "Nhịp bình thường"),
    "L": ("Left bundle branch block beat", "Block nhánh trái"),
    "R": ("Right bundle branch block beat", "Block nhánh phải"),
    "V": ("Premature ventricular contraction", "Ngoại tâm thu thất"),
    "/": ("Paced beat", "Nhịp tạo nhịp"),
    "A": ("Atrial premature beat", "Ngoại tâm thu nhĩ"),
    "a": ("Aberrated atrial premature beat", "Ngoại tâm thu nhĩ dẫn truyền lệch"),
    "f": ("Fusion of paced and normal beat", "Hỗn hợp tạo nhịp + bình thường"),
    "F": ("Fusion of ventricular and normal beat", "Hỗn hợp thất + bình thường"),
    "j": ("Nodal (junctional) escape beat", "Nhịp thoát bộ nối"),
    "J": ("Nodal (junctional) premature beat", "Ngoại tâm thu bộ nối"),
    "E": ("Ventricular escape beat", "Nhịp thoát thất"),
    "e": ("Atrial escape beat", "Nhịp thoát nhĩ"),
    "S": ("Supraventricular premature beat", "Ngoại tâm thu trên thất"),
    "Q": ("Unclassifiable beat", "Beat không phân loại được"),
    "!": ("Ventricular flutter wave", "Sóng cuồng thất"),
    "+": ("Rhythm change", "Đổi nhịp (ghi chú nhịp)"),
    "~": ("Signal quality change", "Thay đổi chất lượng tín hiệu"),
    '"': ("Comment annotation", "Ghi chú"),
    "x": ("Non-conducted P-wave", "Sóng P không dẫn"),
    "|": ("Isolated QRS-like artifact", "Nhiễu giống QRS"),
    "[": ("Start of ventricular flutter/fibrillation", "Bắt đầu cuồng/rung thất"),
    "]": ("End of ventricular flutter/fibrillation", "Kết thúc cuồng/rung thất"),
}

RHYTHM_INFO = {
    "(N": "Nhịp xoang", "(AFIB": "Rung nhĩ", "(AFL": "Cuồng nhĩ", "(B": "Nhịp đôi thất",
    "(T": "Nhịp ba thất", "(VT": "Nhanh thất", "(SVTA": "Nhanh nhĩ kịch phát",
    "(SBR": "Nhịp xoang chậm", "(BII": "Block nhĩ thất độ II", "(IVR": "Nhịp tự thất",
    "(NOD": "Nhịp bộ nối", "(P": "Nhịp tạo nhịp", "(PREX": "Tiền kích thích (WPW)",
    "(VFL": "Cuồng thất", "(AB": "Nhịp đôi nhĩ", "(PSVT": "Nhanh trên thất kịch phát",
}


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def ints(x, scale=1000):
    """Mảng float → list int (đã nhân scale) để file JSON gọn hơn."""
    return [int(v) for v in np.round(np.asarray(x, dtype=float) * scale)]


def rounded(x, nd=2):
    out = []
    for v in np.asarray(x, dtype=float):
        out.append(None if not np.isfinite(v) else round(float(v), nd))
    return out


# ========================================================================
# TẢI DỮ LIỆU
# ========================================================================

# Mirror chính thức của PhysioNet trên AWS (Open Data), nhanh hơn physionet.org nhiều
S3_MIRROR = "https://physionet-open.s3.amazonaws.com/mitdb/1.0.0/"


def _download(fname):
    import urllib.request

    dest = MITDB_DIR / fname
    tmp = dest.with_name(dest.name + ".part")
    try:
        urllib.request.urlretrieve(S3_MIRROR + fname, tmp)
        tmp.replace(dest)
    except Exception as e:
        if tmp.exists():
            tmp.unlink()
        log(f"  S3 lỗi với {fname} ({e}), tải từ physionet.org ...")
        wfdb.dl_files("mitdb", str(MITDB_DIR), [fname])


def ensure_downloads(full_records):
    """Header + annotation của 48 record, tín hiệu (.dat) của các record cần dùng."""
    MITDB_DIR.mkdir(parents=True, exist_ok=True)
    files = []
    for r in ALL_RECORDS:
        for ext in ("hea", "atr"):
            if not (MITDB_DIR / f"{r}.{ext}").exists():
                files.append(f"{r}.{ext}")
    for r in sorted(full_records):
        if not (MITDB_DIR / f"{r}.dat").exists():
            files.append(f"{r}.dat")
    if not files:
        log("Dữ liệu MIT-BIH đã có trong cache.")
        return
    log(f"Tải {len(files)} file MIT-BIH vào {MITDB_DIR} ...")
    for fname in files:
        _download(fname)


def read_record(rec):
    record = wfdb.rdrecord(str(MITDB_DIR / rec))
    ann = wfdb.rdann(str(MITDB_DIR / rec), "atr")
    return record, ann


def read_ann(rec):
    return wfdb.rdann(str(MITDB_DIR / rec), "atr")


# ========================================================================
# TIỀN XỬ LÝ  (03_preprocessing_data.ipynb)
# ========================================================================

def bandpass_sos(x, fs, low=0.5, high=40.0, order=4):
    # 03_preprocessing_data.ipynb — CELL 1
    sos = butter(order, [low, high], btype="bandpass", fs=fs, output="sos")
    return sosfiltfilt(sos, x)


def _odd(n):
    n = int(n)
    if n < 3:
        n = 3
    return n if n % 2 == 1 else n + 1


def remove_baseline_median(x, fs, w1_s=0.2, w2_s=0.6):
    # 03_preprocessing_data.ipynb — CELL 3. Notebook dùng scipy.signal.medfilt;
    # ở đây dùng ndimage.median_filter (cùng kết quả, chỉ khác ở mép, nhanh hơn).
    k1 = _odd(round(w1_s * fs))
    k2 = _odd(round(w2_s * fs))
    baseline = median_filter(median_filter(x, size=k1, mode="nearest"), size=k2, mode="nearest")
    return x - baseline, baseline


def notch_harmonics(x, fs, mains_hz=MAINS_HZ, Q=30.0, n_harmonics=6):
    # 03_preprocessing_data.ipynb — CELL 5
    y = np.asarray(x, dtype=np.float64).copy()
    used = []
    for k in range(1, n_harmonics + 1):
        f0 = mains_hz * k
        if f0 >= fs / 2.0:
            break
        b, a = iirnotch(w0=f0, Q=Q, fs=fs)
        y = filtfilt(b, a, y)
        used.append(f0)
    return y, used


def zscore(x, eps=1e-12):
    x = np.asarray(x, dtype=float)
    return (x - x.mean()) / (x.std() + eps)


# ========================================================================
# CHẤT LƯỢNG TÍN HIỆU  (02_EDA.ipynb — cell 7, 8, 9)
# ========================================================================

_trapezoid = getattr(np, "trapezoid", None) or np.trapz  # numpy < 2.0 chưa có trapezoid


def psd_band_power(f, pxx, f1, f2):
    m = (f >= f1) & (f <= f2)
    return float(_trapezoid(pxx[m], f[m])) if np.any(m) else 0.0


def qc_metrics(ecg, beat_samples, fs):
    b, a = butter(2, 0.5 / (fs / 2), btype="low")
    baseline = filtfilt(b, a, ecg)
    f, pxx = welch(ecg, fs=fs, nperseg=min(len(ecg), 4096))
    p_0_40 = psd_band_power(f, pxx, 0.0, 40.0) + 1e-12
    rr = np.diff(beat_samples) / fs
    bad = (rr < 0.3) | (rr > 2.5)
    return {
        "baseline_std": round(float(np.std(baseline)), 4),
        "baseline_ptp": round(float(np.ptp(baseline)), 4),
        "powerline_50_ratio": round(psd_band_power(f, pxx, 49.0, 51.0) / p_0_40, 6),
        "powerline_60_ratio": round(psd_band_power(f, pxx, 59.0, 61.0) / p_0_40, 6),
        "hf_noise_ratio_20_40": round(psd_band_power(f, pxx, 20.0, 40.0) / p_0_40, 4),
        "amp_std": round(float(np.std(ecg)), 4),
        "amp_min": round(float(np.min(ecg)), 3),
        "amp_max": round(float(np.max(ecg)), 3),
        "rr_min": round(float(rr.min()), 3) if len(rr) else None,
        "rr_max": round(float(rr.max()), 3) if len(rr) else None,
        "bad_rr_pct": round(float(100.0 * bad.mean()), 3) if len(rr) else None,
    }


def psd_db(x, fs, fmax=180.0):
    x = np.asarray(x, dtype=float)
    f, p = welch(x - x.mean(), fs=fs, nperseg=min(len(x), 4096))
    m = f <= fmax
    return f[m], 10 * np.log10(p[m] + 1e-20)


# ========================================================================
# HR / HRV  (02_EDA.ipynb — cell 20–32)
# ========================================================================

def hr_analysis(beat_samples, beat_symbols, fs, duration_s):
    r_t = beat_samples / fs
    rr = np.diff(r_t)
    hr = 60.0 / rr
    t_beat = r_t[1:]

    rr_s = pd.Series(rr)
    rmssd = np.sqrt(rr_s.diff().pow(2).rolling(20).mean()).values
    sdnn = rr_s.rolling(20).std().values

    med_rr = float(np.median(rr))
    rr_outlier = (rr < 0.5 * med_rr) | (rr > 1.8 * med_rr)
    pvc_like = np.zeros(len(rr), dtype=bool)
    for i in range(len(rr) - 1):
        if rr[i] < 0.8 * med_rr and rr[i + 1] > 1.2 * med_rr:
            pvc_like[i] = True
    rmssd_thr = float(np.nanpercentile(rmssd, 90))

    # Nội suy HR về lưới đều 1 Hz
    t_grid = np.arange(np.ceil(t_beat[0]), np.floor(min(t_beat[-1], duration_s)) + 1, 1.0)
    hr_1hz = np.interp(t_grid, t_beat, hr)

    res = STL(hr_1hz, period=60, robust=True).fit()
    resid = np.asarray(res.resid)
    resid_thr = float(np.nanpercentile(np.abs(resid), 99))

    return {
        "beat_t_ms": ints(t_beat, 1000),
        "beat_symbols": "".join(beat_symbols[1:]),
        "rr_ms": ints(rr, 1000),
        "rmssd_ms": [None if not np.isfinite(v) else int(round(v * 1000)) for v in rmssd],
        "sdnn_ms": [None if not np.isfinite(v) else int(round(v * 1000)) for v in sdnn],
        "rmssd_threshold_ms": round(rmssd_thr * 1000, 1),
        "median_rr_ms": round(med_rr * 1000, 1),
        "rr_outlier_idx": np.where(rr_outlier)[0].tolist(),
        "pvc_like_idx": np.where(pvc_like)[0].tolist(),
        "hr_1hz_t0": float(t_grid[0]),
        "hr_1hz": rounded(hr_1hz, 1),
        "stl": {
            "period": 60,
            "trend": rounded(res.trend, 2),
            "seasonal": rounded(res.seasonal, 2),
            "resid": rounded(resid, 2),
            "resid_threshold": round(resid_thr, 2),
            "resid_spike_idx": np.where(np.abs(resid) > resid_thr)[0].tolist(),
        },
        "summary": {
            "mean_hr": round(float(np.mean(hr_1hz)), 1),
            "min_hr": round(float(np.min(hr_1hz)), 1),
            "max_hr": round(float(np.max(hr_1hz)), 1),
            "tachy_seconds": int(np.sum(hr_1hz > 120)),
            "brady_seconds": int(np.sum(hr_1hz < 50)),
            "rr_outliers": int(rr_outlier.sum()),
            "pvc_like": int(pvc_like.sum()),
            "irregular_beats": int(np.nansum(rmssd > rmssd_thr)),
            "resid_spikes": int(np.sum(np.abs(resid) > resid_thr)),
        },
    }


# ========================================================================
# RECORD TIÊU BIỂU
# ========================================================================

def choose_segment(beat_samples, beat_symbols, fs, n, seconds):
    """Chọn đoạn có nhiều loại beat bất thường nhất, vẫn còn beat bình thường để so sánh."""
    win = int(seconds * fs)
    best_score, best_start = -1, int(10 * fs)
    for start in range(int(10 * fs), n - win - int(10 * fs), int(5 * fs)):
        m = (beat_samples >= start) & (beat_samples < start + win)
        syms = beat_symbols[m]
        abn = syms[syms != "N"]
        score = 100 * len(set(abn)) + min(len(abn), int(np.sum(syms == "N")))
        if score > best_score:
            best_score, best_start = score, start
    return best_start


def mean_beats(signal, beat_samples, beat_symbols, fs, pre_ms=200, post_ms=400, min_count=5):
    # 01_explore_data.ipynb — cell 27 (mean beat morphology theo nhãn)
    left = int(pre_ms * fs / 1000)
    right = int(post_ms * fs / 1000)
    out = {}
    for sym, cnt in Counter(beat_symbols).most_common():
        if cnt < min_count:
            continue
        segs = [signal[s - left:s + right] for s, b in zip(beat_samples, beat_symbols)
                if b == sym and s - left >= 0 and s + right <= len(signal)]
        if len(segs) < min_count:
            continue
        segs = np.asarray(segs)
        out[sym] = {"n": len(segs), "mean": ints(segs.mean(axis=0)), "std": ints(segs.std(axis=0))}
    return {"pre_ms": pre_ms, "post_ms": post_ms, "scale": 1000, "labels": out}


def build_showcase_record(rec, desc):
    t0 = time.time()
    record, ann = read_record(rec)
    fs = float(record.fs)
    raw = record.p_signal[:, 0].astype(np.float64)
    n = len(raw)

    samples = np.asarray(ann.sample)
    symbols = np.asarray(ann.symbol)
    is_beat = np.isin(symbols, list(BEAT_SYMBOLS))
    beat_samples = samples[is_beat]
    beat_symbols = symbols[is_beat]

    # Pipeline như 03_preprocessing_data.ipynb: band-pass → baseline → notch → z-score
    bp = bandpass_sos(raw, fs)
    bl_removed, baseline = remove_baseline_median(bp, fs)
    notched, notch_used = notch_harmonics(bl_removed, fs)
    z = zscore(notched)

    start = choose_segment(beat_samples, beat_symbols, fs, n, SEGMENT_SECONDS)
    end = start + int(SEGMENT_SECONDS * fs)
    sl = slice(start, end)

    m = (samples >= start) & (samples < end)
    seg_ann = []
    for s, sym, aux in zip(samples[m], symbols[m], np.asarray(ann.aux_note, dtype=object)[m]):
        item = [int(s - start), str(sym)]
        aux = (aux or "").strip("\x00").strip()
        if aux:
            item.append(aux)
        seg_ann.append(item)

    rhythms = Counter(a.strip("\x00").strip() for a, s in zip(ann.aux_note, ann.symbol) if s == "+" and a)

    f, raw_db = psd_db(raw, fs)
    _, final_db = psd_db(notched, fs)

    data = {
        "id": rec,
        "description": desc,
        "fs": fs,
        "n_samples": n,
        "duration_s": round(n / fs, 2),
        "lead": record.sig_name[0],
        "leads": list(record.sig_name),
        "split": SPLIT.get(rec, "train"),
        "symbol_counts": dict(Counter(symbols.tolist()).most_common()),
        "rhythms": dict(rhythms.most_common()),
        "segment": {
            "start_sample": int(start),
            "start_s": round(start / fs, 2),
            "seconds": SEGMENT_SECONDS,
            "scale": 1000,
            "raw": ints(raw[sl]),
            "bandpass": ints(bp[sl]),
            "baseline": ints(baseline[sl]),
            "baseline_removed": ints(bl_removed[sl]),
            "notch": ints(notched[sl]),
            "zscore": ints(z[sl]),
            "annotations": seg_ann,
        },
        "preprocessing": {
            "bandpass_hz": [0.5, 40.0],
            "baseline_windows_s": [0.2, 0.6],
            "notch_hz": notch_used,
        },
        "psd": {"f": rounded(f, 3), "raw_db": rounded(raw_db, 1), "final_db": rounded(final_db, 1)},
        "qc": qc_metrics(raw, beat_samples, fs),
        "mean_beats": mean_beats(notched, beat_samples, beat_symbols, fs),
        "hr": hr_analysis(beat_samples, beat_symbols, fs, n / fs),
    }
    log(f"  record {rec}: đoạn {data['segment']['start_s']}s–{data['segment']['start_s'] + SEGMENT_SECONDS}s, "
        f"{len(beat_samples)} beat, {time.time() - t0:.1f}s")
    return data


# ========================================================================
# TỔNG QUAN 48 RECORD  (02_EDA.ipynb — cell 35, CNN_model.ipynb — cell 12, 15)
# ========================================================================

def map_label(symbol):
    if symbol in NORMAL_SYMBOLS:
        return 0
    if symbol in DROP_SYMBOLS:
        return None
    return 1


def build_dataset_overview():
    rows = []
    c_1xx, c_2xx = Counter(), Counter()
    for rec in ALL_RECORDS:
        ann = read_ann(rec)
        hdr = wfdb.rdheader(str(MITDB_DIR / rec))
        cnt = Counter(ann.symbol)
        (c_1xx if rec.startswith("1") else c_2xx).update(cnt)
        n_beats = sum(v for k, v in cnt.items() if k in BEAT_SYMBOLS)
        rows.append({
            "id": rec,
            "leads": list(hdr.sig_name),
            "split": SPLIT.get(rec, "train"),
            "n_annotations": int(sum(cnt.values())),
            "n_beats": int(n_beats),
            "n_normal": int(cnt.get("N", 0)),
            "counts": dict(cnt.most_common()),
        })
    total = c_1xx + c_2xx
    labels = []
    for sym, cnt in total.most_common():
        mapped = map_label(sym)
        labels.append({
            "symbol": sym,
            "name_en": SYMBOL_INFO.get(sym, ("", ""))[0],
            "name_vi": SYMBOL_INFO.get(sym, ("", ""))[1],
            "count_1xx": int(c_1xx.get(sym, 0)),
            "count_2xx": int(c_2xx.get(sym, 0)),
            "count": int(cnt),
            "is_beat": sym in BEAT_SYMBOLS,
            "mapped_to": "dropped" if mapped is None else ("normal" if mapped == 0 else "abnormal"),
        })
    lead_counter = Counter(l for r in rows for l in set(r["leads"]))
    return {
        "n_records": len(ALL_RECORDS),
        "fs": 360,
        "duration_min": 30,
        "n_annotations": int(sum(total.values())),
        "n_beats": int(sum(v for k, v in total.items() if k in BEAT_SYMBOLS)),
        "lead_counts": dict(lead_counter.most_common()),
        "labels": labels,
        "records": rows,
    }


# ========================================================================
# MINH HOẠ 2 QUY TẮC GÁN NHÃN  (sliding window.ipynb — cell 9, CNN_model.ipynb — cell 18)
# ========================================================================

def cnn_preprocess(signal, fs=360):
    # CNN_model.ipynb — cell 8: band-pass 0.5–40 Hz (ba) + notch 60 Hz
    nyq = 0.5 * fs
    b, a = butter(4, [0.5 / nyq, 40.0 / nyq], btype="band")
    y = filtfilt(b, a, signal)
    bn, an = iirnotch(MAINS_HZ / nyq, 30.0)
    return filtfilt(bn, an, y)


def label_center_beat(samples, symbols, start, end):
    m = (samples >= start) & (samples < end)
    loc_s, loc_y = samples[m], symbols[m]
    keep = [i for i, s in enumerate(loc_y) if s not in DROP_SYMBOLS]
    if not keep:
        return None, None
    loc_s, loc_y = loc_s[keep], loc_y[keep]
    center = start + (end - start) // 2
    i = int(np.argmin(np.abs(loc_s - center)))
    return (0 if loc_y[i] in NORMAL_SYMBOLS else 1), int(loc_s[i] - start)


def label_any_abnormal(samples, symbols, start, end):
    m = (samples >= start) & (samples < end)
    mapped = [map_label(s) for s in symbols[m]]
    mapped = [v for v in mapped if v is not None]
    if not mapped:
        return None
    return 1 if any(v == 1 for v in mapped) else 0


def build_label_examples(rec=EXAMPLE_RECORD, window_s=4.5):
    record, ann = read_record(rec)
    fs = int(record.fs)
    sig = cnn_preprocess(record.p_signal[:, 0].astype(float), fs)
    samples, symbols = np.asarray(ann.sample), np.asarray(ann.symbol)
    win = int(window_s * fs)

    counts = {"center_beat": Counter(), "any_abnormal": Counter(), "both": Counter()}
    picked = {}
    for start in range(0, len(sig) - win + 1, win):
        end = start + win
        c, c_pos = label_center_beat(samples, symbols, start, end)
        a = label_any_abnormal(samples, symbols, start, end)
        if c is not None:
            counts["center_beat"][c] += 1
        if a is not None:
            counts["any_abnormal"][a] += 1
        if c is None or a is None:
            continue
        key = f"{c}{a}"
        counts["both"][key] += 1
        if start < 10 * fs:  # bỏ vài giây đầu record khi chọn ví dụ
            continue
        m = (samples >= start) & (samples < end)
        n_abn = sum(1 for s in symbols[m] if map_label(s) == 1)
        # Ưu tiên: Normal/Normal sạch; Abnormal/Abnormal nhiều beat bất thường;
        # Normal/Abnormal chỉ đúng 1 beat bất thường nằm xa tâm
        score = {"00": -start, "11": n_abn, "01": -abs(n_abn - 1) * 1e6 - start}.get(key)
        if score is None:
            continue
        if key not in picked or score > picked[key]["score"]:
            seg = sig[start:end]
            picked[key] = {
                "score": score,
                "start_s": round(start / fs, 2),
                "center_label": c,
                "any_label": a,
                "center_beat_offset": c_pos,
                "signal": ints((seg - seg.mean()) / (seg.std() + 1e-8)),
                "annotations": [[int(s - start), str(y)] for s, y in zip(samples[m], symbols[m])],
            }

    examples = []
    for key, title in [("00", "Cả hai quy tắc: Normal"),
                       ("11", "Cả hai quy tắc: Abnormal"),
                       ("01", "Hai quy tắc cho nhãn khác nhau")]:
        if key in picked:
            ex = dict(picked[key])
            ex.pop("score")
            ex["title"] = title
            examples.append(ex)
    log(f"  ví dụ gán nhãn record {rec}: {dict(counts['both'])}")
    return {
        "record": rec,
        "window_s": window_s,
        "fs": fs,
        "scale": 1000,
        "counts": {k: {str(kk): vv for kk, vv in v.items()} for k, v in counts.items()},
        "examples": examples,
    }


# ========================================================================
# DỰ BÁO HR RECORD 100  (ARIMA and SARIMA model.ipynb — cell 15, 20)
# ========================================================================

def hampel(x, window=10, n_sigmas=3.0):
    x = np.asarray(x, dtype=float).copy()
    n, k = len(x), 1.4826
    y = x.copy()
    for i in range(n):
        lo, hi = max(0, i - window), min(n, i + window + 1)
        w = x[lo:hi]
        med = np.nanmedian(w)
        mad = k * np.nanmedian(np.abs(w - med))
        if not np.isfinite(mad) or mad < 1e-9:
            continue
        if np.abs(x[i] - med) > n_sigmas * mad:
            y[i] = med
    return y


def hr_series_arima(record):
    """Cell 15: baseline median → band-pass → notch → XQRS → RR/HR + Hampel → 1 Hz."""
    from wfdb import processing

    fs = record.fs
    ecg = record.p_signal[:, 0].astype(float)
    w1 = int(max(3, (0.2 * fs) // 2 * 2 + 1))
    w2 = int(max(3, (0.6 * fs) // 2 * 2 + 1))
    x_detr = ecg - medfilt(medfilt(ecg, kernel_size=w1), kernel_size=w2)
    nyq = 0.5 * fs
    b, a = butter(4, [0.5 / nyq, 40.0 / nyq], btype="band")
    x_bp = filtfilt(b, a, x_detr)
    bn, an = iirnotch(60.0 / (fs / 2), 30.0)
    x_clean = filtfilt(bn, an, x_bp)

    rpeaks = np.asarray(processing.xqrs_detect(sig=x_clean, fs=fs, verbose=False), dtype=int)
    rr = np.clip(np.diff(rpeaks) / fs, 0.25, 2.5)
    rr = hampel(rr, window=10, n_sigmas=3.0)
    hr = hampel(np.clip(60.0 / rr, 30, 220), window=10, n_sigmas=3.0)
    t_hr = rpeaks[1:] / fs

    t_end = int(np.floor((len(ecg) - 1) / fs))
    t_grid = np.arange(0, t_end + 1, 1.0)
    mask = np.isfinite(hr) & np.isfinite(t_hr)
    return t_grid, np.interp(t_grid, t_hr[mask], hr[mask])


def hr_series_sarima(ann, fs):
    """Cell 20: HR từ annotation beat, RR trong [0.25, 2.5] s → 1 Hz."""
    sym = np.asarray(ann.symbol)
    r = np.asarray(ann.sample)[np.isin(sym, list(BEAT_SYMBOLS))]
    rr = np.diff(r) / fs
    t_hr = r[1:] / fs
    hr = 60.0 / rr
    ok = (rr >= 0.25) & (rr <= 2.5)
    t_hr, hr = t_hr[ok], hr[ok]
    idx = np.arange(int(np.floor(t_hr.min())), int(np.ceil(t_hr.max())) + 1)
    return idx.astype(float), np.interp(idx, t_hr, hr)


def metrics(y, p):
    e = np.asarray(y) - np.asarray(p)
    return {"mae": round(float(np.mean(np.abs(e))), 4),
            "mse": round(float(np.mean(e ** 2)), 4),
            "rmse": round(float(np.sqrt(np.mean(e ** 2))), 4)}


def build_forecast(H=50, W=100):
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    record, ann = read_record(FORECAST_RECORD)
    rep = NR.FORECAST["record_100_reported"]

    # ARIMA(7,0,4) rolling one-step: fit lại ở mỗi bước
    t0 = time.time()
    t_grid, y = hr_series_arima(record)
    order = tuple(rep["arima"]["order"])
    hist = list(y[:-H])
    preds = []
    for i, actual in enumerate(y[-H:]):
        try:
            res = ARIMA(np.asarray(hist), order=order).fit()
            preds.append(float(res.get_forecast(steps=1).predicted_mean[0]))
        except Exception:
            preds.append(hist[-1])
        hist.append(actual)
        if (i + 1) % 10 == 0:
            log(f"    ARIMA{order}: {i + 1}/{H} bước ({time.time() - t0:.0f}s)")
    arima = {
        "order": list(order),
        "hr_source": "R-peak phát hiện bằng XQRS trên ECG đã lọc, RR/HR qua Hampel filter",
        "mode": "Rolling one-step: fit lại mô hình ở mỗi bước rồi thêm giá trị thật",
        "t": rounded(t_grid[-W:], 0),
        "actual": rounded(y[-W:], 2),
        "pred": rounded(preds, 2),
        "n_train": int(len(y) - H),
        **metrics(y[-H:], preds),
        "reported": {"mae": rep["arima"]["mae"], "rmse": rep["arima"]["rmse"]},
    }
    log(f"  ARIMA{order}: MAE {arima['mae']} / RMSE {arima['rmse']} "
        f"(notebook {rep['arima']['mae']} / {rep['arima']['rmse']})")

    # SARIMA(3,1,3)(0,0,1,12): fit một lần, sau đó append giá trị thật (refit=False)
    t0 = time.time()
    t_idx, s = hr_series_sarima(ann, record.fs)
    s_order = tuple(rep["sarima"]["order"])
    s_seasonal = tuple(rep["sarima"]["seasonal_order"])
    train, test = s[:-H], s[-H:]
    res = SARIMAX(train, order=s_order, seasonal_order=s_seasonal,
                  enforce_stationarity=False, enforce_invertibility=False).fit(disp=False, maxiter=100)
    s_preds = []
    for actual in test:
        s_preds.append(float(res.forecast(steps=1)[0]))
        res = res.append([float(actual)], refit=False)
    sarima = {
        "order": list(s_order),
        "seasonal_order": list(s_seasonal),
        "hr_source": "R-peak lấy từ annotation beat của MIT-BIH",
        "mode": "Rolling one-step: fit một lần trên train, sau đó cập nhật bằng giá trị thật (không fit lại)",
        "t": rounded(t_idx[-W:], 0),
        "actual": rounded(s[-W:], 2),
        "pred": rounded(s_preds, 2),
        "n_train": int(len(train)),
        **metrics(test, s_preds),
        "reported": {"mae": rep["sarima"]["mae"], "rmse": rep["sarima"]["rmse"]},
    }
    log(f"  SARIMA{s_order}x{s_seasonal}: MAE {sarima['mae']} / RMSE {sarima['rmse']} "
        f"(notebook {rep['sarima']['mae']} / {rep['sarima']['rmse']}) — {time.time() - t0:.0f}s")

    return {"record": FORECAST_RECORD, "horizon_s": H, "plot_window_s": W,
            "arima": arima, "sarima": sarima}


def load_or_build_forecast(refresh):
    if FORECAST_CACHE.exists() and not refresh:
        log(f"Dự báo: dùng cache {FORECAST_CACHE.name} (thêm --refresh-forecast để chạy lại)")
        return json.loads(FORECAST_CACHE.read_text(encoding="utf-8"))
    log("Dự báo HR record 100 (ARIMA rolling fit lại 50 lần, có thể mất vài phút)...")
    data = build_forecast()
    FORECAST_CACHE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


# ========================================================================
# ST-MEM: fine-tune lại theo Final_Report_TS-3.pdf bằng demo/train_stmem.py
# (MIT-BIH qua WFDB, checkpoint pretrained có sẵn, Linear probe + Semi-finetune, ngưỡng 0.5)
# ========================================================================

STMEM_RESULTS = DEMO_DIR / "results" / "stmem_results.json"
EXP_NAME = {1: "Linear probe (đóng băng encoder, chỉ train head)",
            2: "Semi-finetune (train lead embedding + head)"}


def build_stmem():
    out = {k: v for k, v in NR.STMEM.items() if k != "experiments"}
    out["experiments"] = [e for e in NR.STMEM["experiments"] if e["dataset"].startswith("MIT-BIH")]
    out["status_text"] = "Chưa có kết quả (chạy python demo/train_stmem.py)."
    if not STMEM_RESULTS.exists():
        return out
    res = json.loads(STMEM_RESULTS.read_text(encoding="utf-8"))
    thr = res["threshold"]
    per_record = []
    for rec, d in res["predictions"].items():
        pairs = [(p >= thr, l) for p, l in zip(d["probs"], d["labels"]) if l is not None]
        per_record.append({
            "record": rec,
            "split": SPLIT.get(rec, "train"),
            "windows": len(pairs),
            "truth_abnormal": int(sum(l for _, l in pairs)),
            "pred_abnormal": int(sum(int(p) for p, _ in pairs)),
            "accuracy": round(float(np.mean([int(p) == l for p, l in pairs])), 4) if pairs else None,
        })
    report = {int(k): v for k, v in (res.get("report_table_5_3") or {}).items()}
    out.update({
        "status": "done_mitbih",
        "status_text": "Đã fine-tune lại trên MIT-BIH theo report (demo/train_stmem.py, seed 42).",
        "results": {
            "generated_at": res["generated_at"],
            "device": res["device"],
            "config": res["config"],
            "split": res["split"],
            "chosen_experiment": res["chosen_experiment"],
            "threshold": thr,
            "roc_test": res.get("roc_test"),
            "experiments": [dict({k: e.get(k) for k in ("experiment", "trainable_params", "best_epoch", "epochs_run",
                                                          "train_seconds", "val", "test", "history")},
                                 name=EXP_NAME[e["experiment"]], report=report.get(e["experiment"]))
                            for e in res["experiments"]],
            "per_record": per_record,
        },
    })
    return out


# ========================================================================
# MAIN
# ========================================================================

def main():
    ap = argparse.ArgumentParser(description="Tạo demo/data/demo_data.js cho demo web ECG")
    ap.add_argument("--records", default=",".join(SHOWCASE),
                    help="Danh sách record tiêu biểu, cách nhau bởi dấu phẩy")
    ap.add_argument("--skip-forecast", action="store_true", help="Bỏ qua phần ARIMA/SARIMA")
    ap.add_argument("--refresh-forecast", action="store_true", help="Chạy lại ARIMA/SARIMA, bỏ cache")
    args = ap.parse_args()

    showcase = [r.strip() for r in args.records.split(",") if r.strip()]
    t_start = time.time()
    ensure_downloads(set(showcase) | {FORECAST_RECORD, EXAMPLE_RECORD})

    log("Tổng quan 48 record...")
    dataset = build_dataset_overview()

    log("Record tiêu biểu...")
    records = [build_showcase_record(r, SHOWCASE.get(r, "")) for r in showcase]

    log("Ví dụ quy tắc gán nhãn...")
    label_examples = build_label_examples()

    forecast = None if args.skip_forecast else load_or_build_forecast(args.refresh_forecast)

    data = {
        "meta": {
            "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "generator": "demo/build_data.py",
            "source": "MIT-BIH Arrhythmia Database (PhysioNet)",
        },
        "symbols": {k: {"en": v[0], "vi": v[1]} for k, v in SYMBOL_INFO.items()},
        "rhythms": RHYTHM_INFO,
        "dataset": dataset,
        "records": records,
        "label_examples": label_examples,
        "forecast": {
            "record_100": forecast,
            "grid_search": NR.FORECAST["grid_search"],
            "compare_2xx": NR.FORECAST["compare_2xx"],
        },
        "classification": NR.CLASSIFICATION,
        "stmem": build_stmem(),
    }

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    OUT_FILE.write_text("window.DEMO_DATA = " + payload + ";\n", encoding="utf-8")

    log(f"Đã ghi {OUT_FILE} ({OUT_FILE.stat().st_size / 1e6:.2f} MB) trong {time.time() - t_start:.0f}s")
    for key in ("dataset", "records", "label_examples", "forecast", "classification", "stmem"):
        size = len(json.dumps(data[key], ensure_ascii=False, separators=(",", ":"))) / 1e6
        print(f"    {key:<15} {size:.2f} MB")


if __name__ == "__main__":
    main()
