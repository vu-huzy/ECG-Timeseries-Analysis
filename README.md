# ECG Time Series Analysis with MIT-BIH

Dự án này phân tích tín hiệu ECG từ **MIT-BIH Arrhythmia Database** bằng hai hướng chính:

1. **Time series analysis / forecasting**: tiền xử lý ECG, trích xuất HR/RR, kiểm tra tính dừng và so sánh ARIMA/SARIMA.
2. **Abnormality classification**: tạo cửa sổ ECG và phân loại `Normal` / `Abnormal` bằng feature-based ML models và 1D CNN.

Dữ liệu được đọc bằng `wfdb`, chủ yếu từ PhysioNet (`pn_dir="mitdb"`). Một số cell trong notebook ARIMA/SARIMA dùng đường dẫn local `DB_PATH`, cần chỉnh lại theo máy của bạn nếu chạy notebook đó.

## Project Structure

```text
.
├── README.md
└── notebooks
    ├── 01_explore_data.ipynb
    ├── 02_EDA.ipynb
    ├── 03_preprocessing_data.ipynb
    ├── ARIMA and SARIMA model.ipynb
    └── Classification
        ├── sliding window.ipynb
        └── CNN_model.ipynb
```

## Main Notebooks

| Notebook | Mục đích chính |
| --- | --- |
| `notebooks/01_explore_data.ipynb` | Load MIT-BIH records, xem metadata/lead, plot ECG raw, detect R-peak, cắt beat quanh R-peak và trích xuất QRS features cơ bản. |
| `notebooks/02_EDA.ipynb` | EDA tín hiệu: quality check, baseline/powerline/noise, filtering demo, RR/HR analysis, HRV metrics, STL decomposition và thống kê label. |
| `notebooks/03_preprocessing_data.ipynb` | Minh họa pipeline tiền xử lý ECG: band-pass 0.5-40 Hz, khử baseline wander, notch 50/60 Hz, so sánh phổ tần số và chuẩn hóa. |
| `notebooks/ARIMA and SARIMA model.ipynb` | Trích xuất HR/RR từ ECG đã lọc, kiểm tra stationarity bằng ADF, chọn ARIMA qua ACF/PACF và grid search, rolling forecast HR/RR, tune SARIMA và so sánh ARIMA vs SARIMA. |
| `notebooks/Classification/sliding window.ipynb` | Tạo sliding-window feature dataset và huấn luyện `RandomForest`, `ExtraTrees`, `XGBoost`, soft-voting ensemble cho phân loại normal/abnormal. |
| `notebooks/Classification/CNN_model.ipynb` | Tạo raw ECG windows đã chuẩn hóa và huấn luyện 1D CNN cho binary classification `Normal` / `Abnormal`. |

## Installation

Khuyến nghị dùng Python environment riêng.

```bash
pip install numpy pandas matplotlib seaborn scipy wfdb statsmodels scikit-learn imbalanced-learn xgboost tensorflow tqdm ipython
```

Nếu chỉ chạy các notebook EDA/preprocessing/ARIMA thì `tensorflow`, `imbalanced-learn`, `xgboost` không bắt buộc. Nếu chạy classification đầy đủ thì cần đủ các package trên.

## Data Source

Project dùng **MIT-BIH Arrhythmia Database**:

- WFDB Python: <https://wfdb.readthedocs.io/>
- PhysioNet MIT-BIH: <https://physionet.org/content/mitdb/>

Phần lớn notebook đọc dữ liệu trực tiếp bằng:

```python
record = wfdb.rdrecord(record_id, pn_dir="mitdb")
ann = wfdb.rdann(record_id, "atr", pn_dir="mitdb")
```

Notebook `ARIMA and SARIMA model.ipynb` có một số cell dùng dữ liệu local:

```python
DB_PATH = r"C:\Users\MY PC\Downloads\time series project\mitdb"
```

Nếu chạy trên máy khác, đổi `DB_PATH` sang thư mục MIT-BIH local của bạn, hoặc sửa cell để dùng `pn_dir="mitdb"` giống các notebook còn lại.

## Workflow

### 1. Explore Raw ECG

Notebook `01_explore_data.ipynb` thực hiện:

- Load các record MIT-BIH nhóm `1xx` và `2xx`.
- Xem thông tin header, sampling rate, lead names và phân bố lead.
- Plot raw ECG theo thời gian.
- Detect R-peaks bằng annotation hoặc thuật toán kiểu Pan-Tompkins đơn giản.
- Cắt beat quanh R-peak, dựng median beat template và tìm beat khác thường bằng correlation.
- Trích xuất QRS features như Q amplitude, R amplitude, S amplitude, QRS duration, QR/RS slope.

### 2. EDA and Signal Quality

Notebook `02_EDA.ipynb` tập trung vào chất lượng tín hiệu và đặc trưng thời gian:

- Tính baseline metrics, powerline noise ratio 50/60 Hz, high-frequency noise ratio.
- Plot ECG với baseline estimate và PSD Welch.
- Loại baseline wander, notch powerline, band-pass 0.5-40 Hz.
- Tính RR interval và HR theo beat.
- Resample HR về 1 Hz để phân tích time series.
- Tính HRV rolling metrics như RMSSD.
- STL decomposition trên HR series.
- Detect các pattern bất thường như RR outlier, PVC-like beat và irregular segment.
- Thống kê annotation labels giữa record nhóm `1xx` và `2xx`.

### 3. Preprocessing

Notebook `03_preprocessing_data.ipynb` minh họa từng bước tiền xử lý:

- Band-pass filter 0.5-40 Hz bằng Butterworth SOS.
- Khử baseline wander bằng median filter hai tầng.
- Tự động detect nhiễu điện lưới 50/60 Hz và notch thêm harmonic nếu cần.
- So sánh phổ trước/sau lọc bằng Welch PSD.
- Chuẩn hóa bằng z-score hoặc min-max.

Pipeline này là nền tảng cho các notebook forecasting và classification.

### 4. ARIMA/SARIMA Forecasting

Notebook `ARIMA and SARIMA model.ipynb` xây dựng pipeline dự báo HR/RR:

- Load ECG từ MIT-BIH local.
- Tiền xử lý ECG bằng median baseline removal, band-pass và notch.
- Detect R-peaks, tính RR intervals và HR.
- Resample HR/RR về chuỗi đều 1 Hz.
- Kiểm tra tính dừng bằng ADF trên record `1xx` và `2xx`.
- Dùng ACF/PACF để định hướng chọn `(p,d,q)`.
- Grid search và fine-tuning ARIMA bằng AIC/BIC.
- Rolling one-step forecast cho HR và RR trong 50 giây cuối.
- Tune SARIMA và so sánh ARIMA/SARIMA bằng MAE, MSE, RMSE trên các record `2xx`.

Metric chính:

- `MAE`
- `MSE`
- `RMSE`

### 5. Sliding Window Classification

Notebook `notebooks/Classification/sliding window.ipynb` tạo feature dataset từ ECG windows:

- Chia record cố định thành `TRAIN_RECORDS`, `VAL_RECORDS`, `TEST_RECORDS` để tránh leakage.
- Load record từ local `notebooks/mitdb` nếu có, nếu không fallback sang PhysioNet.
- Tiền xử lý bằng band-pass, notch, detrend và z-normalization.
- Tạo sliding windows với cấu hình 4.5s và 9s.
- Chia window thành frame 0.75s và trích xuất frame-level features.
- Tính window-level features từ R-peaks như beat count, RR range, HR range, RMSSD.
- Gán nhãn theo beat gần tâm window: `N` là normal, các symbol hợp lệ khác như `V`, `A`, `L`, `R` là abnormal.
- Train `RandomForest`, `ExtraTrees`, `XGBoost` và soft-voting ensemble.
- Dùng `StandardScaler`, `SMOTE`, `SelectKBest` trước khi train.
- Đánh giá bằng accuracy, precision, recall, F1-score và confusion matrix.

### 6. CNN Classification

Notebook `notebooks/Classification/CNN_model.ipynb` dùng raw ECG windows thay vì handcrafted features:

- Cấu hình `FS = 360`, danh sách record MIT-BIH và split train/validation/test.
- Mapping nhãn: `N` là normal; các symbol trong `DROP_SYMBOLS` bị bỏ; các symbol còn lại là abnormal.
- Cắt ECG thành windows `0.75s`, `4.5s`, `9s` không overlap.
- Gán nhãn window: chỉ cần một beat abnormal trong window thì toàn bộ window là `Abnormal`.
- Chuẩn hóa từng window bằng z-score.
- Build 1D CNN gồm nhiều block `Conv1D -> BatchNormalization -> MaxPooling`, sau đó `GlobalAveragePooling1D`, Dense, Dropout và sigmoid output.
- Train với `class_weight`, `EarlyStopping`, `ReduceLROnPlateau`.
- Đánh giá bằng accuracy, precision, recall, F1-score và confusion matrix.

## Labeling Notes

Hai notebook classification dùng quy tắc nhãn hơi khác nhau:

- `sliding window.ipynb`: chỉ xét `VALID_SYMBOLS = {"N", "V", "A", "L", "R"}` và gán nhãn theo beat gần tâm window.
- `CNN_model.ipynb`: `N` là normal, một số symbol metadata/noisy bị drop, các symbol còn lại được xem là abnormal; nhãn window là abnormal nếu window chứa ít nhất một beat abnormal.

Khi so sánh kết quả giữa hai mô hình, cần chú ý khác biệt này vì nó ảnh hưởng trực tiếp đến phân bố nhãn và độ khó của bài toán.

## How to Run

1. Cài dependencies.
2. Mở project bằng Jupyter Notebook hoặc VS Code.
3. Chạy theo thứ tự khuyến nghị:
   - `01_explore_data.ipynb`
   - `02_EDA.ipynb`
   - `03_preprocessing_data.ipynb`
   - `ARIMA and SARIMA model.ipynb` nếu cần forecasting
   - `Classification/sliding window.ipynb` nếu cần ML classification
   - `Classification/CNN_model.ipynb` nếu cần deep learning classification
4. Với notebook ARIMA/SARIMA, kiểm tra lại `DB_PATH` trước khi chạy các cell đọc local data.
5. Với notebook CNN, nên chạy trên GPU nếu có vì training qua nhiều window size có thể mất thời gian.

## Outputs


- ECG waveform plots trước/sau lọc.
- PSD plots và signal quality diagnostics.
- RR/HR time series, HRV metrics và STL decomposition.
- ARIMA/SARIMA forecast plots và bảng MAE/MSE/RMSE.
- Classification metric tables.
- Confusion matrices cho các mô hình abnormality detection.
- Biểu đồ so sánh window size và model performance.

## Important Notes

- MIT-BIH có sampling rate phổ biến là 360 Hz; code trong project mặc định theo giá trị này ở nhiều nơi.
- Một số notebook tải dữ liệu từ internet thông qua WFDB/PhysioNet, nên cần network nếu chưa có data local.
- Các cell có comment `thay`, `đổi`, hoặc placeholder `0` là cell tùy chỉnh/thủ công, không phải luôn cần chạy trong pipeline chính.
- Kết quả classification phụ thuộc mạnh vào split record, label mapping, window size và mức mất cân bằng lớp.
- Nội dung này phục vụ mục đích học tập/phân tích dữ liệu, không dùng như công cụ chẩn đoán y tế.
