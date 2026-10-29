"""
Tạo dữ liệu cho màn hình theo dõi (demo/monitor.html).

Chạy sau train_stmem.py (nếu chưa có kết quả ST-MEM thì màn hình chỉ có cảnh báo theo luật):
    python demo/build_monitor.py

Kết quả: demo/data/monitor_data.js  →  window.MONITOR_DATA = {...}

Mỗi record lấy một đoạn ~5 phút, căn theo lưới cửa sổ 9 s của ST-MEM:
  - Tín hiệu lead 0 đã lọc như mit-bih.py (band-pass 0.5–40 Hz + notch 60 Hz), resample 250 Hz
  - R-peak phát hiện bằng NeuroKit2 (ecg_clean + ecg_peaks), không dùng nhãn chuyên gia.
    XQRS (notebook ARIMA) bỏ sót nhiều PVC (208: Se 0.92) → báo ngưng nhịp/nhịp chậm giả;
    NeuroKit2 đạt Se/PPV ≈ 0.997/0.999 trên 208, 0.998 trên 106
  - Sự kiện theo luật nhịp (dựa trên 02_EDA, chỉ dùng các beat đã qua → chạy được thời gian thực)
  - Xác suất bất thường của ST-MEM cho từng cửa sổ 9 s (tính trước bởi train_stmem.py)
  - Nhãn chuyên gia chỉ để đối chiếu
"""

import argparse
import datetime
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.signal import resample

DEMO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO_DIR))
import build_data as BD  # noqa: E402

STMEM_FILE = BD.CACHE_DIR / "stmem_results.json"
OUT_FILE = DEMO_DIR / "data" / "monitor_data.js"

FS = 250                  # tần số của ST-MEM
WINDOW_S = 9.0            # cửa sổ ST-MEM
EXCERPT_WINDOWS = 34      # 34 × 9 s = 306 s

MONITOR_RECORDS = {
    "103": "Nhịp xoang gần như bình thường",
    "106": "Nhiều ngoại tâm thu thất (V), có đoạn nhịp đôi",
    "105": "Nhiễu rất nhiều, thỉnh thoảng có PVC",
    "208": "PVC dày kèm beat hỗn hợp (F)",
    "232": "Nhịp chậm, nhiều beat nhĩ sớm, có khoảng ngưng dài",
}

# Ngưỡng luật nhịp (02_EDA.ipynb — cell 32, chuyển sang dạng chạy theo từng beat)
RULES = {
    "warmup_beats": 8,
    "median_window": 32,       # số RR gần nhất để lấy trung vị
    "hr_window": 4,            # HR hiển thị = 60 / trung bình 4 RR gần nhất
    "state_window": 8,         # luật nhanh/chậm dùng 60 / trung vị 8 RR gần nhất (một khoảng ngưng lẻ không kéo HR xuống)
    "tachy_on": 120, "tachy_off": 110,
    "brady_on": 50, "brady_off": 55,
    "pause_s": 2.0, "pause_ratio": 1.8,
    "pvc_short": 0.8, "pvc_long": 1.2,
    "rmssd_window": 20, "rmssd_on": 0.12, "rmssd_off": 0.08,
    "persist_on": 3,           # trạng thái (nhanh/chậm/không đều) bật khi điều kiện đúng ≥3 beat liên tiếp
    "persist_off": 5,          # và tắt khi điều kiện tắt đúng ≥5 beat liên tiếp → không nhấp nháy
}

RULE_INFO = [
    {"type": "pvc", "severity": "warning", "title": "Beat sớm kiểu PVC",
     "rule": "RR ngắn hơn 80% trung vị rồi tới khoảng bù dài hơn 120% (02_EDA: pvc_like)"},
    {"type": "pause", "severity": "critical", "title": "Ngưng nhịp",
     "rule": "Một khoảng RR dài hơn 2 s và hơn 1.8 lần trung vị (02_EDA: RR outlier)"},
    {"type": "tachy", "severity": "serious", "title": "Nhịp nhanh",
     "rule": "HR (trung vị 8 RR gần nhất) > 120 bpm trong ≥3 beat liên tiếp; tắt khi < 110 bpm ≥5 beat (02_EDA: tachy)"},
    {"type": "brady", "severity": "serious", "title": "Nhịp chậm",
     "rule": "HR (trung vị 8 RR gần nhất) < 50 bpm trong ≥3 beat liên tiếp; tắt khi > 55 bpm ≥5 beat (02_EDA: brady)"},
    {"type": "irregular", "severity": "warning", "title": "Nhịp không đều",
     "rule": "RMSSD của 20 khoảng RR gần nhất > 120 ms trong ≥3 beat; tắt khi < 80 ms ≥5 beat (02_EDA: irregular)"},
    {"type": "stmem", "severity": "serious", "title": "ST-MEM: đoạn 9 s bất thường",
     "rule": "Xác suất Abnormal của ST-MEM Semi-finetune ≥ 0.5 (như report), báo khi đã thu đủ 9 s"},
]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def map_label(sym):
    if sym in BD.NORMAL_SYMBOLS:
        return 0
    if sym in BD.DROP_SYMBOLS:
        return None
    return 1


def detect_beats(raw360, fs360):
    import neurokit2 as nk
    clean = nk.ecg_clean(raw360, sampling_rate=fs360)
    _, info = nk.ecg_peaks(clean, sampling_rate=fs360)
    return np.unique(np.asarray(info["ECG_R_Peaks"], dtype=int))


def rule_events(beat_t):
    """Chạy luật trên từng beat theo thứ tự thời gian, chỉ dùng dữ liệu quá khứ."""
    R = RULES
    rr = np.diff(beat_t)
    hr_disp = np.full(len(beat_t), np.nan)
    pvc_beats = []
    events = []
    state = {"tachy": False, "brady": False, "irregular": False}
    streak = {"tachy": 0, "brady": 0, "irregular": 0}

    def update_state(key, t, cond_on, cond_off, value):
        """Bật/tắt trạng thái có trễ: cần persist_on beat liên tiếp để bật, persist_off để tắt."""
        if not state[key]:
            streak[key] = streak[key] + 1 if cond_on else 0
            if streak[key] >= R["persist_on"]:
                state[key], streak[key] = True, 0
                events.append({"t": t, "type": key, "value": value})
        else:
            streak[key] = streak[key] + 1 if cond_off else 0
            if streak[key] >= R["persist_off"]:
                state[key], streak[key] = False, 0
                events.append({"t": t, "type": key + "_end", "value": value})

    for j in range(len(rr)):
        t = float(beat_t[j + 1])
        lo = max(0, j - R["hr_window"] + 1)
        hr = 60.0 / float(np.mean(rr[lo:j + 1]))
        hr_disp[j + 1] = hr
        if j < R["warmup_beats"]:
            continue
        med = float(np.median(rr[max(0, j - R["median_window"]):j]))
        r = float(rr[j])
        is_pause = r > max(R["pause_s"], R["pause_ratio"] * med)
        if is_pause:
            events.append({"t": t, "type": "pause", "value": round(r, 2)})
        elif rr[j - 1] < R["pvc_short"] * med and r > R["pvc_long"] * med:
            pvc_beats.append(j)  # beat j (kết thúc khoảng RR ngắn) là beat sớm
            events.append({"t": t, "type": "pvc", "value": round(60.0 / float(rr[j - 1]))})

        hr_s = 60.0 / float(np.median(rr[max(0, j - R["state_window"] + 1):j + 1]))
        update_state("tachy", t, hr_s > R["tachy_on"], hr_s < R["tachy_off"], round(hr_s))
        update_state("brady", t, hr_s < R["brady_on"], hr_s > R["brady_off"], round(hr_s))

        if j >= R["rmssd_window"]:
            seg = rr[j - R["rmssd_window"] + 1:j + 1]
            rmssd = float(np.sqrt(np.mean(np.diff(seg) ** 2)))
            update_state("irregular", t, rmssd > R["rmssd_on"], rmssd < R["rmssd_off"], round(rmssd * 1000))
    return hr_disp, pvc_beats, events


def window_truth(ann_250, symbols, n_win, win):
    labels, counts = [], []
    for k in range(n_win):
        m = (ann_250 >= k * win) & (ann_250 < (k + 1) * win)
        syms = [s for s, keep in zip(symbols, m) if keep]
        mapped = [v for v in (map_label(s) for s in syms) if v is not None]
        labels.append(None if not mapped else int(any(v == 1 for v in mapped)))
        counts.append(dict(Counter(s for s in syms if map_label(s) is not None).most_common()))
    return labels, counts


def choose_excerpt(labels, long_rr_per_win, n_win):
    """Chọn đoạn có cả cửa sổ bình thường lẫn bất thường, nhiều lần chuyển trạng thái."""
    best, best_k = -1, 1
    for k0 in range(1, n_win - EXCERPT_WINDOWS):
        lab = [l for l in labels[k0:k0 + EXCERPT_WINDOWS] if l is not None]
        n_abn = sum(lab)
        n_norm = len(lab) - n_abn
        switches = sum(1 for a, b in zip(lab, lab[1:]) if a != b)
        score = switches + 0.5 * min(n_abn, n_norm) + 2 * sum(long_rr_per_win[k0:k0 + EXCERPT_WINDOWS])
        if score > best:
            best, best_k = score, k0
    return best_k


def build_record(rec, desc, stmem):
    t0 = time.time()
    record, ann = BD.read_record(rec)
    fs360 = int(record.fs)
    sig360 = BD.cnn_preprocess(record.p_signal[:, 0].astype(float), fs360)  # = preprocess_ecg của mit-bih.py
    sig = resample(sig360, int(len(sig360) * FS / fs360))
    win = int(WINDOW_S * FS)
    n_win = len(sig) // win

    beats360 = detect_beats(record.p_signal[:, 0].astype(float), fs360)
    beat_t = beats360 / fs360
    hr_disp, pvc_beats, events = rule_events(beat_t)

    ann_samples = np.asarray(ann.sample)
    symbols = np.asarray(ann.symbol)
    ann_250 = (ann_samples * FS / fs360).astype(int)
    labels, counts = window_truth(ann_250, symbols, n_win, win)

    rr = np.diff(beat_t)
    long_rr = np.zeros(n_win)
    for j, r in enumerate(rr):
        k = int(beat_t[j + 1] * FS) // win
        if r > 2.0 and k < n_win:
            long_rr[k] += 1

    probs = None
    thr = stmem["threshold"] if stmem else 0.5
    if stmem and rec in stmem["predictions"]:
        probs = stmem["predictions"][rec]["probs"][:n_win]

    k0 = choose_excerpt(labels, long_rr, n_win)
    s0, s1 = k0 * win, (k0 + EXCERPT_WINDOWS) * win
    t_start, t_end = s0 / FS, s1 / FS

    in_ex = (beat_t >= t_start) & (beat_t < t_end)
    beat_idx = np.where(in_ex)[0]
    pvc_set = set(pvc_beats)
    beats = []
    for i in beat_idx:
        hr = hr_disp[i]
        beats.append([int(round((beat_t[i] - t_start) * FS)),
                      None if not np.isfinite(hr) else int(round(hr)),
                      1 if i in pvc_set else 0])

    m = (ann_250 >= s0) & (ann_250 < s1)
    annotations = [[int(a - s0), str(s)] for a, s in zip(ann_250[m], symbols[m])]

    ev = []
    for e in events:
        if t_start <= e["t"] < t_end:
            ev.append({"t": round(e["t"] - t_start, 3), "type": e["type"], "value": e["value"]})
    windows = []
    for k in range(k0, k0 + EXCERPT_WINDOWS):
        p = None if probs is None else probs[k]
        windows.append({"p": p, "truth": labels[k], "counts": counts[k]})
        if p is not None and p >= thr:
            ev.append({"t": round((k - k0 + 1) * WINDOW_S, 3), "type": "stmem", "value": round(p, 3),
                       "window": k - k0})
    ev.sort(key=lambda e: e["t"])

    seg = sig[s0:s1]
    lo, hi = np.percentile(seg, [0.2, 99.8])
    summary = Counter(e["type"] for e in ev)
    log(f"  {rec}: đoạn {t_start:.0f}–{t_end:.0f}s, {len(beats)} beat phát hiện, "
        f"{sum(1 for a in annotations if a[1] in BD.BEAT_SYMBOLS)} beat chuyên gia, sự kiện {dict(summary)} "
        f"({time.time() - t0:.0f}s)")

    rhythms = Counter((a or "").strip("\x00").strip() for a, s in zip(ann.aux_note, ann.symbol) if s == "+" and a)
    return {
        "id": rec,
        "description": desc,
        "split": BD.SPLIT.get(rec, "train"),
        "lead": record.sig_name[0],
        "fs": FS,
        "start_s": round(t_start, 3),
        "duration_s": round(t_end - t_start, 3),
        "scale": 1000,
        "signal": BD.ints(seg),
        "y_range": [round(float(lo), 3), round(float(hi), 3)],
        "beats": beats,
        "annotations": annotations,
        "windows": windows,
        "events": ev,
        "rhythms": dict(rhythms.most_common()),
    }


def main():
    ap = argparse.ArgumentParser(description="Tạo demo/data/monitor_data.js")
    ap.add_argument("--records", default=",".join(MONITOR_RECORDS))
    args = ap.parse_args()
    recs = [r.strip() for r in args.records.split(",") if r.strip()]

    BD.ensure_downloads(set(recs))
    stmem = None
    if STMEM_FILE.exists():
        stmem = json.loads(STMEM_FILE.read_text(encoding="utf-8"))
        log(f"Dùng dự đoán ST-MEM từ {STMEM_FILE.name} (thử nghiệm {stmem['chosen_experiment']})")
    else:
        log("Chưa có kết quả ST-MEM (chạy demo/train_stmem.py trước) — chỉ có cảnh báo theo luật.")

    records = [build_record(r, MONITOR_RECORDS.get(r, ""), stmem) for r in recs]

    model = None
    if stmem:
        chosen = next(e for e in stmem["experiments"] if e["experiment"] == stmem["chosen_experiment"])
        model = {
            "name": "ST-MEM ViT-B Semi-finetune",
            "experiment": stmem["chosen_experiment"],
            "experiment_text": {1: "đóng băng encoder, chỉ train classifier head",
                                2: "train lead embeddings + classifier head"}[stmem["chosen_experiment"]],
            "threshold": stmem["threshold"],
            "window_s": WINDOW_S,
            "test": (stmem.get("calibration") or {}).get("test_chosen", chosen["test"]),
            "threshold_method": (stmem.get("calibration") or {}).get("method", "mặc định 0.5"),
            "generated_at": stmem["generated_at"],
        }

    data = {
        "meta": {
            "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "generator": "demo/build_monitor.py",
            "fs": FS,
            "window_s": WINDOW_S,
        },
        "symbols": {k: {"en": v[0], "vi": v[1]} for k, v in BD.SYMBOL_INFO.items()},
        "rhythms": BD.RHYTHM_INFO,
        "rules": RULE_INFO,
        "rule_params": RULES,
        "model": model,
        "records": records,
    }
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text("window.MONITOR_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
                        encoding="utf-8")
    log(f"Đã ghi {OUT_FILE} ({OUT_FILE.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
