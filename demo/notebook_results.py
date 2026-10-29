"""
Kết quả đã có sẵn trong output của các notebook và trong Final_Report_TS-3.pdf, chép lại để demo hiển thị.

Nguồn chuẩn của các mô hình đặc trưng thủ công (sliding window) và CNN 4.5 s / 9 s là report
(Bảng 5.1, 5.2, Hình 5.1); notebook sliding window trên main đã được chạy lại và không còn khớp.
Phần ARIMA/SARIMA không có trong report nên vẫn lấy từ output notebook.

Đây là những phần cần train/grid-search rất lâu (phân loại, chọn bậc ARIMA,
so sánh ARIMA/SARIMA trên 25 record 2xx) nên demo KHÔNG chạy lại mà lấy đúng
con số notebook đã in ra. Mỗi mục ghi rõ notebook + ô (cell index, đếm từ 0).
"""

# ----------------------------------------------------------------------
# Phân loại Normal / Abnormal
# ----------------------------------------------------------------------
# Confusion matrix theo thứ tự sklearn: [[TN, FP], [FN, TP]]

CLASSIFICATION = {
    "split": {
        "test": ["102", "103", "104", "105", "106"],
        "val": ["200", "208", "232", "233", "234"],
        "train": "38 record còn lại",
    },
    "label_rules": {
        "center_beat": {
            "name": "Beat gần tâm cửa sổ",
            "used_by": "Sliding window (Random Forest, Extra Trees, XGBoost)",
            "rule": "Nhãn của cửa sổ = nhãn của beat hợp lệ gần tâm cửa sổ nhất (N → Normal, còn lại → Abnormal).",
        },
        "any_abnormal": {
            "name": "Có ít nhất 1 beat bất thường",
            "used_by": "1D CNN, ST-MEM",
            "rule": "Cửa sổ là Abnormal nếu chứa ít nhất một beat bất thường; chỉ toàn beat N thì là Normal.",
        },
    },
    "normal_symbols": ["N"],
    "drop_symbols": ["+", "x", '"', "Q", "~"],
    "models": [
        {
            # Final_Report_TS-3.pdf, Bảng 5.1 (số của report) + Hình 5.1 (confusion matrix 4.5s XGBoost).
            # Bảng 5.1 là kết quả tốt nhất của từng cửa sổ; notebook hiện tại (đã chạy lại) cho cùng số ở 4.5s.
            "id": "ml_4.5s",
            "family": "ml",
            "name": "XGBoost",
            "window": "4.5s",
            "window_seconds": 4.5,
            "label_rule": "center_beat",
            "source": "Final_Report_TS-3.pdf — Bảng 5.1, Hình 5.1",
            "train_samples": 15238, "val_samples": 2004, "test_samples": 2004,
            "test_normal": 1150, "test_abnormal": 854,
            "accuracy": 0.6282, "precision": 0.5945, "recall": 0.4016,
            "f1": 0.4794, "auc": None, "specificity": 0.7965,
            "confusion_matrix": [[916, 234], [511, 343]],
        },
        {
            # Final_Report_TS-3.pdf, Bảng 5.1 + Hình 5.1 (confusion matrix 9s Extra Trees).
            # Số này khớp Bảng 5.5 của report (mô hình sliding window tốt nhất).
            "id": "ml_9s",
            "family": "ml",
            "name": "Extra Trees",
            "window": "9s",
            "window_seconds": 9.0,
            "label_rule": "center_beat",
            "source": "Final_Report_TS-3.pdf — Bảng 5.1, 5.5, Hình 5.1",
            "train_samples": 15200, "val_samples": 2000, "test_samples": 2000,
            "test_normal": 1143, "test_abnormal": 857,
            "accuracy": 0.7300, "precision": 0.6590, "recall": 0.7666,
            "f1": 0.7087, "auc": None, "specificity": 0.7025,
            "confusion_matrix": [[803, 340], [200, 657]],
        },
        {
            # CNN_model.ipynb, cell 35 (cấu hình 0.75s) + cell 37 (bảng tổng hợp)
            "id": "cnn_0.75s",
            "family": "cnn",
            "name": "1D CNN",
            "window": "0.75s",
            "window_seconds": 0.75,
            "label_rule": "any_abnormal",
            "source": "notebooks/Classification/CNN_model.ipynb — cell 35, 37",
            "train_samples": 79043, "val_samples": 11114, "test_samples": 10736,
            "test_normal": 6040, "test_abnormal": 4696,
            "accuracy": 0.8986, "precision": 0.8493, "recall": 0.9338,
            "f1": 0.8895, "auc": None, "specificity": 0.8712,
            "confusion_matrix": [[5262, 778], [311, 4385]],
        },
        {
            "id": "cnn_4.5s",
            "family": "cnn",
            "name": "1D CNN",
            "window": "4.5s",
            "window_seconds": 4.5,
            "label_rule": "any_abnormal",
            "source": "notebooks/Classification/CNN_model.ipynb — cell 35, 37",
            "train_samples": 15238, "val_samples": 2004, "test_samples": 2004,
            "test_normal": 954, "test_abnormal": 1050,
            "accuracy": 0.9376, "precision": 0.9409, "recall": 0.9400,
            "f1": 0.9404, "auc": None, "specificity": 0.9350,
            "confusion_matrix": [[892, 62], [63, 987]],
        },
        {
            "id": "cnn_9s",
            "family": "cnn",
            "name": "1D CNN",
            "window": "9s",
            "window_seconds": 9.0,
            "label_rule": "any_abnormal",
            "source": "notebooks/Classification/CNN_model.ipynb — cell 35, 37",
            "train_samples": 7600, "val_samples": 1000, "test_samples": 1000,
            "test_normal": 439, "test_abnormal": 561,
            "accuracy": 0.9380, "precision": 0.9354, "recall": 0.9554,
            "f1": 0.9453, "auc": None, "specificity": 0.9157,
            "confusion_matrix": [[402, 37], [25, 536]],
        },
    ],
    # Bảng 5.1 của report: cả ba mô hình đặc trưng thủ công ở hai cửa sổ.
    # Report chỉ in confusion matrix của XGBoost 4.5s và Extra Trees 9s (Hình 5.1); bốn ma trận còn lại
    # suy ra từ recall + precision + số cửa sổ mỗi lớp, và khớp lại cả bốn chỉ số (accuracy, precision, recall, F1)
    # của Bảng 5.1 (sai lệch < 0.0006). Test: 4.5s có 1150 N / 854 A, 9s có 1143 N / 857 A (tổng ma trận của Hình 5.1).
    "ml_all": [
        {"model": "Random Forest", "window": "4.5s", "accuracy": 0.5883, "precision": 0.5271, "recall": 0.3302, "f1": 0.4060,
         "confusion_matrix": [[897, 253], [572, 282]], "cm_source": "suy ra"},
        {"model": "Extra Trees", "window": "4.5s", "accuracy": 0.5953, "precision": 0.5464, "recall": 0.2963, "f1": 0.3842,
         "confusion_matrix": [[940, 210], [601, 253]], "cm_source": "suy ra"},
        {"model": "XGBoost", "window": "4.5s", "accuracy": 0.6282, "precision": 0.5945, "recall": 0.4016, "f1": 0.4794,
         "confusion_matrix": [[916, 234], [511, 343]], "cm_source": "Hình 5.1"},
        {"model": "Random Forest", "window": "9s", "accuracy": 0.7385, "precision": 0.6811, "recall": 0.7328, "f1": 0.7060,
         "confusion_matrix": [[849, 294], [229, 628]], "cm_source": "suy ra"},
        {"model": "Extra Trees", "window": "9s", "accuracy": 0.7300, "precision": 0.6590, "recall": 0.7666, "f1": 0.7087,
         "confusion_matrix": [[803, 340], [200, 657]], "cm_source": "Hình 5.1"},
        {"model": "XGBoost", "window": "9s", "accuracy": 0.6660, "precision": 0.6103, "recall": 0.6103, "f1": 0.6103,
         "confusion_matrix": [[809, 334], [334, 523]], "cm_source": "suy ra"},
    ],
    "methods": {
        "ml": {
            "title": "Đặc trưng thủ công + mô hình cây",
            "steps": [
                "Median filter → high-pass 0.3 Hz → band-pass 0.5–45 Hz → notch 60/120/180 Hz → detrend",
                "Chuẩn hoá robust (MAD + IQR) cho từng cửa sổ",
                "Chia cửa sổ thành 6 frame × 0.75 s, mỗi frame 13 đặc trưng thống kê/hình dạng",
                "Đặc trưng RR/HR của cửa sổ (NeuroKit2): số beat, mean/median RR, HR range, RMSSD (cửa sổ 9 s)",
                "StandardScaler → SMOTE → SelectKBest (k = 25)",
                "Ba mô hình huấn luyện riêng: Random Forest, Extra Trees, XGBoost (report không dùng bỏ phiếu mềm); đặc trưng 86 (4.5 s) hoặc 165 (9 s) trước khi chọn lọc",
            ],
        },
        "cnn": {
            "title": "1D CNN trên tín hiệu thô",
            "steps": [
                "Band-pass 0.5–40 Hz + notch 60 Hz",
                "Cắt cửa sổ không chồng lấn 0.75 s / 4.5 s / 9 s, z-score từng cửa sổ",
                "4 khối Conv1D (32→64→128→256) + BatchNorm + MaxPooling",
                "GlobalAveragePooling → Dense 128 → Dropout 0.4 → Dense 64 → Dropout 0.3 → sigmoid",
                "class_weight cân bằng, EarlyStopping (patience 5), ReduceLROnPlateau, tối đa 15 epoch",
                "192,385 tham số",
            ],
        },
    },
}

# ----------------------------------------------------------------------
# ARIMA / SARIMA
# ----------------------------------------------------------------------

FORECAST = {
    # ARIMA and SARIMA model.ipynb, cell 11: grid search p,q ∈ [0..8], d chọn
    # bằng ADF (d = 0 phổ biến nhất), fit trên HR 1 Hz 60 s đầu của 17 record 2xx.
    "grid_search": {
        "source": "notebooks/ARIMA and SARIMA model.ipynb — cell 11",
        "note": "HR 1 Hz, 60 s đầu mỗi record, 17 record 2xx tải được; xếp theo AIC trung bình.",
        "best_order": [3, 0, 2],
        "test_1xx_avg_aic": 251.87,
        "test_1xx_std_aic": 89.90,
        "top": [
            {"order": [3, 0, 2], "avg_aic": 360.434, "std_aic": 135.337, "avg_bic": 375.210},
            {"order": [2, 0, 3], "avg_aic": 360.543, "std_aic": 133.508, "avg_bic": 375.319},
            {"order": [2, 0, 2], "avg_aic": 361.454, "std_aic": 133.073, "avg_bic": 374.119},
            {"order": [4, 0, 2], "avg_aic": 361.845, "std_aic": 134.857, "avg_bic": 378.732},
            {"order": [5, 0, 5], "avg_aic": 361.873, "std_aic": 136.805, "avg_bic": 387.203},
            {"order": [3, 0, 3], "avg_aic": 361.932, "std_aic": 133.747, "avg_bic": 378.819},
            {"order": [4, 0, 5], "avg_aic": 362.389, "std_aic": 135.097, "avg_bic": 385.609},
            {"order": [5, 0, 2], "avg_aic": 362.389, "std_aic": 134.981, "avg_bic": 381.387},
            {"order": [6, 0, 5], "avg_aic": 362.462, "std_aic": 137.043, "avg_bic": 389.904},
            {"order": [5, 0, 4], "avg_aic": 362.644, "std_aic": 135.391, "avg_bic": 385.864},
        ],
    },
    # Kết quả rolling one-step của record 100 như notebook đã in; build_data.py
    # chạy lại và so khớp với các số này.
    "record_100_reported": {
        "arima": {"order": [7, 0, 4], "mae": 1.1808, "rmse": 1.4630,
                  "source": "notebooks/ARIMA and SARIMA model.ipynb — cell 15"},
        "sarima": {"order": [3, 1, 3], "seasonal_order": [0, 0, 1, 12],
                   "mae": 2.0553, "mse": 5.8474, "rmse": 2.4181,
                   "source": "notebooks/ARIMA and SARIMA model.ipynb — cell 20, 22"},
    },
    # ARIMA and SARIMA model.ipynb, cell 24: dự báo nhiều bước 50 s cuối của
    # 300 s đầu mỗi record 2xx (không cập nhật dần như rolling 1-step).
    "compare_2xx": {
        "source": "notebooks/ARIMA and SARIMA model.ipynb — cell 24",
        "arima_order": [7, 0, 4],
        "sarima_order": [7, 0, 4],
        "sarima_seasonal_order": [1, 0, 1, 10],
        "horizon_s": 50,
        "duration_s": 300,
        "mode": "Dự báo 50 bước một lần (multi-step), dự báo bị kẹp trong khoảng phân vị 1–99% của tập train",
        "mean": {
            "ARIMA": {"mae": 7.962726, "mse": 366.809568, "rmse": 9.861457},
            "SARIMA": {"mae": 13.307283, "mse": 781.949512, "rmse": 15.907537},
        },
        # record, ARIMA MAE, MSE, RMSE, SARIMA MAE, MSE, RMSE
        "per_record": [
            ["200", 6.599133, 80.959591, 8.997755, 6.195963, 67.770340, 8.232274],
            ["201", 13.021375, 294.106822, 17.149543, 24.515332, 993.343628, 31.517354],
            ["202", 0.987878, 1.493369, 1.222035, 3.004226, 11.650363, 3.413263],
            ["203", 26.277844, 906.027715, 30.100294, 61.620523, 5130.723255, 71.629067],
            ["205", 3.631500, 19.658415, 4.433781, 3.642584, 19.807608, 4.450574],
            ["207", 66.214061, 7015.836268, 83.760589, 89.125920, 10471.110638, 102.328445],
            ["208", 5.451815, 40.120411, 6.334067, 14.035171, 237.345726, 15.406029],
            ["209", 12.498022, 167.141685, 12.928329, 11.562738, 199.104772, 14.110449],
            ["210", 6.796371, 73.582603, 8.578030, 6.333427, 69.071554, 8.310930],
            ["212", 2.881419, 13.461042, 3.668929, 11.925674, 166.439889, 12.901158],
            ["213", 1.358900, 2.863183, 1.692094, 1.356603, 3.001594, 1.732511],
            ["214", 3.565563, 20.554061, 4.533659, 3.502515, 22.537197, 4.747336],
            ["215", 3.560046, 20.027169, 4.475173, 9.228524, 107.363411, 10.361632],
            ["217", 1.416170, 3.207976, 1.791082, 2.375607, 8.013670, 2.830843],
            ["219", 9.364195, 144.352227, 12.014667, 9.296529, 144.597098, 12.024853],
            ["220", 1.255298, 2.583958, 1.607469, 1.448312, 2.651958, 1.628483],
            ["221", 11.275797, 204.513444, 14.300820, 9.552319, 140.402430, 11.849153],
            ["222", 2.309186, 8.831607, 2.971802, 2.698297, 10.784798, 3.284022],
            ["223", 2.017533, 5.683574, 2.384025, 1.409044, 3.562522, 1.887464],
            ["228", 2.484468, 10.815770, 3.288734, 27.997088, 915.420749, 30.255921],
            ["230", 7.324868, 104.214503, 10.208550, 9.190600, 171.151645, 13.082494],
            ["231", 3.385973, 15.672119, 3.958803, 2.080136, 7.054629, 2.656055],
            ["232", 0.978116, 1.348069, 1.161064, 0.620651, 0.892652, 0.944803],
            ["233", 2.827581, 9.753316, 3.123030, 17.533216, 636.696076, 25.232837],
            ["234", 1.585041, 3.430304, 1.852108, 2.431066, 8.239587, 2.870468],
        ],
    },
}

# ----------------------------------------------------------------------
# ST-MEM (chưa có kết quả)
# ----------------------------------------------------------------------

STMEM = {
    "status": "in_progress",
    "status_text": "Đã có code fine-tune, chưa có kết quả được lưu lại.",
    "paper": "Na et al., ICLR 2024 — Guiding Masked Representation Learning to Capture Spatio-Temporal Relationship of Electrocardiogram",
    "encoder": "ViT-B (768 chiều, 12 tầng, 12 head), pretrained ST-MEM",
    "input": "9 s @ 250 Hz = 2250 mẫu, patch 75 → 30 patch mỗi lead",
    "experiments": [
        {
            "dataset": "MIT-BIH (2 lead), nhị phân Normal/Abnormal",
            "script": "notebooks/Classification/ST-MEM/mit-bih.py",
            "runs": [
                "Thử nghiệm 1: đóng băng encoder, chỉ train classifier head",
                "Thử nghiệm 2: train thêm lead embeddings + classifier head",
            ],
        },
        {
            "dataset": "PTB-XL (12 lead), 5 siêu lớp NORM / MI / STTC / CD / HYP",
            "script": "notebooks/Classification/ST-MEM/compare_ptbxl_supervised_vs_stmem.py",
            "runs": [
                "Supervised baseline: ViT-B khởi tạo ngẫu nhiên",
                "ST-MEM fine-tune: encoder pretrained",
            ],
            "blocker": "Thư mục dữ liệu hiện có là PTB-XL+ (features), thiếu ptbxl_database.csv và records500/ mà script cần.",
        },
    ],
}
