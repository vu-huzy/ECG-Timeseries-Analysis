# ECG Time Series Analysis with MIT-BIH

This project analyzes ECG signals from the **MIT-BIH Arrhythmia Database** following two main directions:

1. **Time series analysis / forecasting**: ECG preprocessing, HR/RR extraction, stationarity testing, and ARIMA/SARIMA comparison.
2. **Abnormality classification**: ECG windowing and classification of `Normal` / `Abnormal` beats using feature-based ML models and 1D CNN.

Data is loaded using `wfdb`, primarily from PhysioNet (`pn_dir="mitdb"`). Some cells in the ARIMA/SARIMA notebook use a local path `DB_PATH` that needs adjustment on your machine if running that notebook.

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

| Notebook | Purpose |
| --- | --- |
| `notebooks/01_explore_data.ipynb` | Load MIT-BIH records, view metadata/lead info, plot raw ECG, detect R-peaks, extract beats around R-peak, and extract basic QRS features. |
| `notebooks/02_EDA.ipynb` | Signal EDA: quality check, baseline/powerline/noise analysis, filtering demo, RR/HR analysis, HRV metrics, STL decomposition, and label statistics. |
| `notebooks/03_preprocessing_data.ipynb` | Demonstrates ECG preprocessing pipeline: band-pass 0.5-40 Hz, baseline wander removal, notch 50/60 Hz, frequency spectrum comparison, and normalization. |
| `notebooks/ARIMA and SARIMA model.ipynb` | Extract HR/RR from filtered ECG, check stationarity with ADF, select ARIMA via ACF/PACF and grid search, rolling forecast HR/RR, tune SARIMA, and compare ARIMA vs SARIMA. |
| `notebooks/Classification/sliding window.ipynb` | Create sliding-window feature dataset and train `RandomForest`, `ExtraTrees`, `XGBoost`, soft-voting ensemble for normal/abnormal classification. |
| `notebooks/Classification/CNN_model.ipynb` | Create normalized raw ECG windows and train 1D CNN for binary classification `Normal` / `Abnormal`. |

## Installation

A separate Python environment is recommended.

```bash
pip install numpy pandas matplotlib seaborn scipy wfdb statsmodels scikit-learn imbalanced-learn xgboost tensorflow tqdm ipython
```

Or use the provided `requirements.txt`:
```bash
pip install -r requirements.txt
```

If running only EDA/preprocessing/ARIMA notebooks, `tensorflow`, `imbalanced-learn`, and `xgboost` are optional. For full classification pipelines, all packages are needed.

## Data Source

Project uses the **MIT-BIH Arrhythmia Database**:

- WFDB Python: <https://wfdb.readthedocs.io/>
- PhysioNet MIT-BIH: <https://physionet.org/content/mitdb/>

Most notebooks load data directly using:

```python
record = wfdb.rdrecord(record_id, pn_dir="mitdb")
ann = wfdb.rdann(record_id, "atr", pn_dir="mitdb")
```

The `ARIMA and SARIMA model.ipynb` notebook uses local data in some cells:

```python
DB_PATH = r"C:\Users\MY PC\Downloads\time series project\mitdb"
```

If running on a different machine, update `DB_PATH` to your local MIT-BIH directory, or modify the cell to use `pn_dir="mitdb"` like the other notebooks.

## Workflow

### 1. Explore Raw ECG

Notebook `01_explore_data.ipynb` performs:

- Load MIT-BIH records from groups `1xx` and `2xx`.
- View header info, sampling rate, lead names, and lead distribution.
- Plot raw ECG over time.
- Detect R-peaks using annotations or simple Pan-Tompkins-like algorithm.
- Extract beats around R-peak, build median beat template, and find anomalous beats via correlation.
- Extract QRS features such as Q amplitude, R amplitude, S amplitude, QRS duration, QR/RS slope.

### 2. EDA and Signal Quality

Notebook `02_EDA.ipynb` focuses on signal quality and temporal characteristics:

- Compute baseline metrics, powerline noise ratio 50/60 Hz, high-frequency noise ratio.
- Plot ECG with baseline estimate and Welch PSD.
- Remove baseline wander, notch powerline, band-pass 0.5-40 Hz.
- Compute RR intervals and HR per beat.
- Resample HR to 1 Hz for time series analysis.
- Compute HRV rolling metrics such as RMSSD.
- STL decomposition on HR series.
- Detect anomalous patterns like RR outliers, PVC-like beats, and irregular segments.
- Compute label statistics between record groups `1xx` and `2xx`.

### 3. Preprocessing

Notebook `03_preprocessing_data.ipynb` demonstrates each preprocessing step:

- Band-pass filter 0.5-40 Hz using Butterworth SOS.
- Remove baseline wander with two-stage median filtering.
- Automatically detect powerline noise at 50/60 Hz and notch additional harmonics if needed.
- Compare frequency spectrum before/after filtering using Welch PSD.
- Normalize using z-score or min-max scaling.

This pipeline forms the foundation for the forecasting and classification notebooks.

### 4. ARIMA/SARIMA Forecasting

Notebook `ARIMA and SARIMA model.ipynb` builds an HR/RR forecasting pipeline:

- Load ECG from local MIT-BIH data.
- Preprocess ECG using median baseline removal, band-pass, and notch filtering.
- Detect R-peaks, compute RR intervals, and HR.
- Resample HR/RR to uniform 1 Hz time series.
- Check stationarity using ADF test on records `1xx` and `2xx`.
- Use ACF/PACF to guide selection of `(p,d,q)` parameters.
- Grid search and fine-tune ARIMA using AIC/BIC.
- Rolling one-step forecast for HR and RR over the final 50 seconds.
- Tune SARIMA and compare ARIMA vs SARIMA using MAE, MSE, RMSE on records `2xx`.

Key metrics:

- `MAE`
- `MSE`
- `RMSE`

### 5. Sliding Window Classification

Notebook `notebooks/Classification/sliding window.ipynb` creates a feature dataset from ECG windows:

- Split records into `TRAIN_RECORDS`, `VAL_RECORDS`, `TEST_RECORDS` to avoid data leakage.
- Load records from local `notebooks/mitdb` if available, fallback to PhysioNet.
- Preprocess using band-pass, notch, detrend, and z-normalization.
- Create sliding windows with 4.5s and 9s configurations.
- Divide windows into 0.75s frames and extract frame-level features.
- Compute window-level features from R-peaks such as beat count, RR range, HR range, RMSSD.
- Assign labels based on the beat nearest to window center: `N` is normal, other valid symbols like `V`, `A`, `L`, `R` are abnormal.
- Train `RandomForest`, `ExtraTrees`, `XGBoost`, and soft-voting ensemble.
- Use `StandardScaler`, `SMOTE`, `SelectKBest` before training.
- Evaluate using accuracy, precision, recall, F1-score, and confusion matrix.

### 6. CNN Classification

Notebook `notebooks/Classification/CNN_model.ipynb` uses raw ECG windows instead of handcrafted features:

- Configure `FS = 360`, MIT-BIH record list, and train/validation/test split.
- Label mapping: `N` is normal; symbols in `DROP_SYMBOLS` are dropped; remaining symbols are abnormal.
- Segment ECG into windows of 0.75s, 4.5s, 9s without overlap.
- Assign window labels: a window is `Abnormal` if it contains at least one abnormal beat.
- Normalize each window using z-score.
- Build 1D CNN with multiple `Conv1D -> BatchNormalization -> MaxPooling` blocks, followed by `GlobalAveragePooling1D`, Dense, Dropout, and sigmoid output.
- Train using `class_weight`, `EarlyStopping`, `ReduceLROnPlateau`.
- Evaluate using accuracy, precision, recall, F1-score, and confusion matrix.

## Labeling Notes

The two classification notebooks use slightly different labeling rules:

- `sliding window.ipynb`: only considers `VALID_SYMBOLS = {"N", "V", "A", "L", "R"}` and labels based on the beat nearest to the window center.
- `CNN_model.ipynb`: `N` is normal, some metadata/noisy symbols are dropped, remaining symbols are abnormal; window label is abnormal if it contains at least one abnormal beat.

When comparing results between the two models, pay attention to these differences as they directly affect label distribution and problem difficulty.

## How to Run

1. Install dependencies.
2. Open the project with Jupyter Notebook or VS Code.
3. Run in recommended order:
   - `01_explore_data.ipynb`
   - `02_EDA.ipynb`
   - `03_preprocessing_data.ipynb`
   - `ARIMA and SARIMA model.ipynb` for forecasting
   - `Classification/sliding window.ipynb` for ML classification
   - `Classification/CNN_model.ipynb` for deep learning classification
4. For ARIMA/SARIMA notebook, verify `DB_PATH` before running cells that read local data.
5. For CNN notebook, preferably run on GPU as training over multiple window sizes can be time-consuming.

## Outputs

- ECG waveform plots before/after filtering.
- PSD plots and signal quality diagnostics.
- RR/HR time series, HRV metrics, and STL decomposition.
- ARIMA/SARIMA forecast plots and MAE/MSE/RMSE tables.
- Classification metric tables.
- Confusion matrices for abnormality detection models.
- Charts comparing window size and model performance.

## Important Notes

- MIT-BIH commonly uses a sampling rate of 360 Hz; code in this project defaults to this value in many places.
- Some notebooks load data from the internet via WFDB/PhysioNet, so network access is needed if you don't have local data.
- Cells with comments like "modify", "adjust", or placeholder `0` are customization/manual cells and don't always need to run in the main pipeline.
- Classification results depend heavily on record split, label mapping, window size, and class imbalance severity.
- This project is for learning and data analysis purposes only, not for medical diagnostic tools.
