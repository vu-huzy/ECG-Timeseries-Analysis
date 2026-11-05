# ECG Time Series Analysis with MIT-BIH

This project analyzes ECG signals from the **MIT-BIH Arrhythmia Database** following three main directions:

1. **Time series analysis / forecasting**: ECG preprocessing, HR/RR extraction, stationarity testing, and ARIMA/SARIMA comparison.
2. **Abnormality classification**: ECG windowing and classification of `Normal` / `Abnormal` beats using feature-based ML models and 1D CNN.
3. **ST-MEM fine-tuning**: a pretrained ST-MEM ViT-B encoder fine-tuned on MIT-BIH (see `notebooks/Classification/ST-MEM`).

Data is loaded using `wfdb`, primarily from PhysioNet (`pn_dir="mitdb"`). Some cells in the ARIMA/SARIMA notebook use a local path `DB_PATH` that needs adjustment on your machine if running that notebook.

A view-only **web demo** of all of the above lives in [`demo/`](demo) (see [Web demo](#web-demo-demo) below).

## Project Structure

```text
.
├── README.md
├── plan.md                    # working log of the demo: decisions, results, open issues
├── Final_Report_TS-3.pdf      # project report (numbers the ST-MEM results are compared with)
├── demo/                      # static web demo + scripts that generate its data
└── notebooks
    ├── 01_explore_data.ipynb
    ├── 02_EDA.ipynb
    ├── 03_preprocessing_data.ipynb
    ├── ARIMA and SARIMA model.ipynb
    └── Classification
        ├── sliding window.ipynb
        ├── CNN_model.ipynb
        └── ST-MEM
            └── mit-bih.py
```

## Web demo (`demo/`)

A static HTML + JavaScript demo (Plotly charts and a canvas ECG monitor). It has two pages:

- `demo/index.html`: seven sections (overview, signal exploration, preprocessing, HR/HRV, ARIMA/SARIMA forecast, Normal/Abnormal classification, ST-MEM).
- `demo/monitor.html`: a replay of recorded MIT-BIH excerpts, with a 9 s ECG sweep, HR/RR trends, illustrative rule flags and precomputed ST-MEM scores per 9 s window.

The website does not accept new ECG recordings or analyze a live patient. The replay trend reveals only HR/RR samples already played and ST-MEM scores for completed 9 s windows; playback stops at the end so the final window remains visible. Its RR short-long pattern is not a confirmed PVC diagnosis; a long RR interval is recorded only after the next beat arrives. Rolling RMSSD includes ectopic beats, so it is shown as RR variability rather than clinical HRV. The ST-MEM scores are uncalibrated research outputs (test F1 0.7777, specificity 0.4391), not medical alerts. Method-only STL and AIC charts remain available under **additional analysis** in the HR/RR and forecasting sections.

### 1. Just view it (no installation)

The generated data (`demo/data/*.js`) and Plotly (`demo/vendor/`) are committed, so nothing needs to be built:

```bash
git clone https://github.com/vu-huzy/ECG-Timeseries-Analysis
cd ECG-Timeseries-Analysis
python -m http.server 8765 --bind 127.0.0.1 --directory demo
```

Then open <http://localhost:8765/index.html> (monitor: <http://localhost:8765/monitor.html>). Double-clicking `demo/index.html` also works in Chrome/Edge because the pages use plain scripts, with no ES modules and no `fetch`. No internet connection is needed.

### 2. Rebuild the data on another machine, without retraining

The trained ST-MEM model is committed, so nothing has to be trained again:

- `demo/models/stmem_semi_finetune.pt` (about 11 KB): the weights that were trained, i.e. the two lead embeddings and the classifier head. In Semi-finetune the rest of the encoder is frozen, so the full model is these weights plus the original pretrained encoder (step 3 below).
- `demo/results/stmem_results.json`: test metrics, training curves, ROC and the per-window probabilities for every test/validation record. `build_monitor.py` and `build_data.py` read this file.

Use a fresh Python environment (developed with Python 3.12) and run everything from the repository root. On Windows, set `PYTHONIOENCODING=utf-8` first (`set PYTHONIOENCODING=utf-8` in cmd, `$env:PYTHONIOENCODING="utf-8"` in PowerShell); otherwise the Vietnamese log messages crash the default cp1252 console.

**Step 1: install dependencies** (PyTorch is not needed for this step)

```bash
pip install -r demo/requirements.txt
```

**Step 2: regenerate the demo data from the committed results**

```bash
python demo/build_monitor.py   # data for monitor.html   (about 10 s)
python demo/build_data.py      # data for index.html     (about 15 s after the first run)
```

`build_data.py` downloads MIT-BIH (48 records, about 90 MB) into `demo/.cache/mitdb/` on first use, from the PhysioNet S3 mirror `physionet-open.s3.amazonaws.com` (much faster than physionet.org), falling back to `wfdb`. Its first run also runs the ARIMA/SARIMA forecast for record 100, which takes a few minutes and is then cached. Flags: `--refresh-forecast`, `--skip-forecast`, `--records`. `demo/.cache/` is git-ignored and can be deleted at any time.

**Step 3 (optional): check the committed model against the pretrained encoder**

Needs PyTorch (install the build for your GPU from <https://pytorch.org/get-started/locally/>; RTX 50-series cards need a CUDA 12.8 build; the demo was developed with `torch 2.12.0.dev+cu128` on an RTX 5070) and the official pretrained encoder, which is not in git (340 MB). It comes from <https://github.com/vuno/ST-MEM> (link taken from `notebooks/Classification/ST-MEM/README.md`):
<https://drive.google.com/file/d/1E7J-A1HqWa2f08T6Sfk5uWk-_CFJhOYQ/view>

Save it exactly as `notebooks/Classification/ST-MEM/pretrain/st_mem_vit_base_encoder.pth` (from the command line: `pip install gdown`, then `gdown 1E7J-A1HqWa2f08T6Sfk5uWk-_CFJhOYQ -O notebooks/Classification/ST-MEM/pretrain/st_mem_vit_base_encoder.pth`). Expected file: 340,663,413 bytes, SHA-256 `6f63d370fd1a2ccf2fbddd681571adf985eeae3f652973f0071342a39b7793d6` (the copy used for the committed results). Then:

```bash
python demo/predict_stmem.py
```

It loads the encoder and `demo/models/stmem_semi_finetune.pt`, scores the test set (2,000 windows, threshold 0.5) and prints `KHỚP` (match) if the metrics equal the ones stored in `demo/results/stmem_results.json` (accuracy 0.7065, F1 0.7777, AUC 0.8165). The same file shows how to load the model in your own code (`load_trained_model()`). The first run builds and caches the windowed dataset in `demo/.cache/stmem/`.

**Step 4 (optional): retrain from scratch**

Same requirements as step 3 (a GPU is strongly recommended; it was only run on a GPU).

```bash
python demo/train_stmem.py     # about 7.5 min on an RTX 5070, overwrites demo/models and demo/results
python demo/build_monitor.py
python demo/build_data.py
```

`train_stmem.py` fine-tunes ST-MEM as described in the report: MIT-BIH read with WFDB, 2 leads, 9 s windows at 250 Hz, stride 4.5 s (15,200 / 2,000 / 2,000 train / val / test windows), pretrained encoder with only the two lead embeddings and the classifier head trained, threshold 0.5, seed 42. It also saves the per-window probabilities used by the monitor. Training can differ slightly between GPUs and PyTorch versions, so the numbers may not match the committed ones exactly.

### Notes on the results

- ST-MEM Semi-finetune reaches test F1 0.778 / AUC 0.817 with this setup, whereas `Final_Report_TS-3.pdf` (Table 5.3) reports F1 0.9695. Dataset, checkpoint and trainable parameters are the same as in the report, but the report does not give epochs, learning rate, batch size or seed, so the gap is not explained yet. Details are in `plan.md`, sections 9 and 10.
- The feature-based and 1D CNN numbers use different window-labeling rules, see "Labeling Notes" below.
- **Source of the classification numbers:** the feature-based models (Random Forest, Extra Trees, XGBoost) and the 1D CNN 4.5 s / 9 s rows follow `Final_Report_TS-3.pdf` (Tables 5.1 and 5.2, Figure 5.1). The sliding-window notebook on `main` was re-run later by a collaborator and no longer reproduces the report's 9 s numbers, so the report is the reference. The CNN 0.75 s row exists only in the notebook. The ARIMA/SARIMA tables are not in the report; they come from `ARIMA and SARIMA model.ipynb`, and the copied values were re-checked against the re-run notebook (same cells, same numbers). `demo/notebook_results.py` records the source of every number.
- The replay page presents recorded data and precomputed model outputs. It is not a real-time system and not a medical device.
- `demo/predict_stmem.py` re-scores the committed model (see step 3); `plan.md` is the full working log of this demo (design decisions, issues found, results, remaining work).

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
