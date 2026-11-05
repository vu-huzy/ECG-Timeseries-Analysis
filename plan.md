# Kế hoạch demo web — ECG Time Series Analysis

Mục tiêu: một **trang web tĩnh, chỉ để xem**, trình bày lại toàn bộ dự án (dữ liệu → tiền xử lý → HR/HRV → dự báo → phân loại) bằng biểu đồ tương tác (zoom, chọn record, bật/tắt lớp lọc). Không có backend, không chạy model trực tiếp trên web.

---

## 1. Dự án hiện có gì

| Phần | Nguồn | Kết quả chính đã có trong notebook |
| --- | --- | --- |
| Khám phá dữ liệu | `01_explore_data.ipynb` | 48 record MIT-BIH, 360 Hz, 2 lead (MLII có ở 46/48 record); R-peak, beat template, đặc trưng QRS (QRS ≈ 78 ms ở record 101) |
| EDA & chất lượng tín hiệu | `02_EDA.ipynb` | Baseline, nhiễu 50/60 Hz, PSD, RR/HR, RMSSD/SDNN, STL của HR, cờ bất thường (tachy/brady/PVC-like), phân bố nhãn 1xx/2xx (N chiếm 66.6%) |
| Tiền xử lý | `03_preprocessing_data.ipynb` | Band-pass 0.5–40 Hz → khử baseline (median 2 tầng) → notch 60 Hz + hài 120 Hz → z-score (record 203) |
| Dự báo HR | `ARIMA and SARIMA model.ipynb` | Grid search chọn ARIMA(3,0,2) theo AIC; rolling 1-step 50 s cuối record 100: **ARIMA(7,0,4) MAE 1.18 / RMSE 1.46 bpm**, **SARIMA(3,1,3)(0,0,1,12) MAE 2.06 / RMSE 2.42 bpm**; trên 2xx (dự báo nhiều bước): ARIMA MAE 7.96 vs SARIMA 13.31 |
| Phân loại ML | `Classification/sliding window.ipynb` | Ensemble RF + ET + XGB (soft voting): 4.5 s **F1 0.437**, AUC 0.734; 9 s F1 0.393, AUC 0.731 |
| Phân loại CNN | `Classification/CNN_model.ipynb` | 1D CNN: 0.75 s F1 0.890; 4.5 s F1 0.940; **9 s F1 0.945** (acc 0.938) |
| ST-MEM | `Classification/ST-MEM/mit-bih.py`, `compare_ptbxl_supervised_vs_stmem.py` | Code fine-tune ViT-B pretrained (MIT-BIH 2 lead, PTB-XL 12 lead). **Chưa có kết quả nào được lưu** |

---

## 2. Những điểm ảnh hưởng tới demo (phát hiện khi đọc code)

1. **Không có model nào được lưu ra file** (CNN chỉ giữ trong RAM, cache của sliding window không có trong repo). Vì vậy demo hiển thị **kết quả đã tính sẵn**, không dự đoán trực tiếp. Muốn có phần "xem dự đoán từng cửa sổ" thì cần train lại CNN một lần và lưu dự đoán (bước 4, tuỳ chọn).
2. **Hai pipeline phân loại gán nhãn khác nhau**: sliding window lấy nhãn của beat gần tâm cửa sổ nhất; CNN coi cả cửa sổ là bất thường nếu có ít nhất 1 beat bất thường. Hai bài toán khác nhau nên F1 0.44 và 0.94 **không so sánh trực tiếp được**. Demo sẽ ghi rõ điều này và minh hoạ bằng vài cửa sổ mẫu.
3. **"RR" có hai nghĩa**: trong notebook ARIMA, RR là *nhịp thở* (respiratory rate, tách từ ECG), còn ở các notebook khác RR là *khoảng R-R*. Ô số 2 của notebook ARIMA in ra nhịp thở 64.1 lần/phút, con số này không hợp lý về sinh lý. Demo sẽ đặt tên rõ cho từng đại lượng và chỉ dự báo HR.
4. **Bậc ARIMA không đồng nhất**: grid search chọn (3,0,2), nhưng biểu đồ dự báo dùng (7,0,4); SARIMA cho record 100 dùng (3,1,3)(0,0,1,12), còn bảng so sánh 2xx lại dùng (7,0,4)(1,0,1,10). Mỗi biểu đồ trong demo sẽ ghi đúng bậc đã dùng.
5. **HR trong EDA bị lẫn annotation không phải beat** (`+`, `~`, ...) nên nhịp đầu tiên ra 284 bpm. Demo chỉ dùng annotation là beat thật để tính RR/HR.
6. **ST-MEM với PTB-XL chưa chạy được bằng dữ liệu hiện có**: thư mục `ptb-xl-a-comprehensive-electrocardiographic-feature-dataset-1.0.1` là bộ **PTB-XL+** (chỉ có features, fiducial points, median beats). Bộ này thiếu `ptbxl_database.csv`, `scp_statements.csv` và `records500/` mà script cần.
7. Notebook ARIMA dùng đường dẫn cứng `DB_PATH = C:\Users\MY PC\...`. Script của demo sẽ tự tải dữ liệu qua `wfdb` và cache lại.

---

## 3. Demo có những gì

Một trang duy nhất, thanh điều hướng chia các mục:

**0. Đầu trang**: tên dự án, một câu mô tả, ghi chú "chỉ phục vụ học tập, không dùng để chẩn đoán".

**1. Tổng quan**
- Bài toán, dữ liệu (MIT-BIH: 48 record × 30 phút, 360 Hz, 2 lead).
- 3–4 ô số nổi bật: CNN 9 s F1 0.945 · ARIMA MAE 1.18 bpm · 48 record · ~110k annotation.
- Sơ đồ pipeline: tín hiệu thô → lọc → R-peak/HR → (dự báo | phân loại).

**2. Khám phá tín hiệu**
- Chọn record (6 record tiêu biểu, xem bảng dưới) → ECG 30 s, các beat đánh dấu màu theo nhãn (N, V, A, L, R, F, ...), có zoom và thanh trượt.
- Phân bố nhãn toàn bộ 48 record (so sánh 1xx với 2xx).
- Hình dạng beat trung bình theo từng nhãn của record đang chọn (mean ± std).

| Record | Lý do chọn |
| --- | --- |
| 100 | Gần như toàn nhịp bình thường, vài beat A |
| 109 | Block nhánh trái (beat L) |
| 119 | Ngoại tâm thu thất (V) dạng nhịp đôi |
| 203 | Nhiều nhiễu, PVC đa dạng: hợp để minh hoạ tiền xử lý |
| 208 | PVC + beat hỗn hợp (F) |
| 232 | Nhịp chậm, nhiều beat A, có khoảng ngưng dài |

**3. Tiền xử lý**
- Cùng đoạn 30 s, bật/tắt từng tầng: thô → band-pass → khử baseline → notch → z-score.
- PSD (Welch) trước và sau lọc, có vạch 0.5 / 40 / 60 Hz.
- Bảng chỉ số chất lượng: baseline std, tỉ lệ nhiễu 50/60 Hz, nhiễu cao tần 20–40 Hz, % RR bất thường.

**4. Nhịp tim & HRV** (toàn bộ 30 phút của record đang chọn)
- HR theo thời gian (1 Hz) với ngưỡng tachy 120 / brady 50.
- Chuỗi RR có đánh dấu outlier và PVC-like.
- RMSSD cuộn (cửa sổ 20 beat).
- STL: observed / trend / seasonal / residual.

**5. Dự báo HR (ARIMA / SARIMA)**
- Record 100: 100 s cuối gồm HR thật, dự báo ARIMA(7,0,4) và SARIMA(3,1,3)(0,0,1,12) rolling 1-step cho 50 s cuối, kèm ô MAE/RMSE.
- Top mô hình theo AIC từ grid search.
- Bảng + biểu đồ so sánh ARIMA và SARIMA theo từng record 2xx, kèm số lần thắng.

**6. Phân loại Normal / Abnormal**
- Hai thẻ phương pháp: đặc trưng thủ công + ensemble cây, và 1D CNN trên tín hiệu thô.
- Bảng kết quả 5 cấu hình (ML 4.5 s, 9 s; CNN 0.75 s, 4.5 s, 9 s) và biểu đồ metric theo độ dài cửa sổ.
- Confusion matrix (dạng heatmap).
- Khung giải thích quy tắc gán nhãn, với vài cửa sổ mẫu và nhãn theo cả hai quy tắc.

**7. ST-MEM (đang thực hiện)**: mô tả cách làm (ViT-B pretrained, 2250 mẫu, 30 patch, 2 thử nghiệm freeze/unfreeze) và trạng thái "chưa có kết quả".

**8. Cuối trang**: nguồn dữ liệu (PhysioNet), cách tạo lại dữ liệu demo.

---

## 4. Kiến trúc

```text
demo/
├── build_data.py         # tải MIT-BIH, tính toán, xuất dữ liệu cho web
├── notebook_results.py   # các kết quả đã có trong notebook (metric, confusion matrix...), ghi rõ nguồn từng ô
├── data/demo_data.js     # window.DEMO_DATA = {...}  (file sinh ra)
├── index.html
├── app.js
├── style.css
└── .cache/               # dữ liệu MIT-BIH tải về (không commit)
```

- **Python tính sẵn mọi thứ** → xuất ra `demo_data.js` dạng `window.DEMO_DATA = {...}`. Dùng file `.js` thay cho `.json` để mở `index.html` trực tiếp bằng double-click vẫn chạy (`fetch` JSON qua `file://` sẽ bị chặn).
- Phần tính toán dùng lại đúng các hàm và tham số trong notebook (bộ lọc, R-peak, HR, STL, ARIMA/SARIMA).
- Những kết quả cần train lâu (phân loại, grid search, bảng 2xx) được **chép từ output notebook** vào `notebook_results.py`, ghi rõ nguồn notebook + ô, không train lại.
- Front-end: HTML + JS thuần + Plotly.js (CDN, cố định phiên bản), không cần build. Có giao diện sáng/tối và hiển thị được trên điện thoại.
- Mục tiêu dung lượng dữ liệu < 5 MB (tín hiệu làm tròn 3 chữ số thập phân, chỉ lưu đoạn 30 s cho mỗi record).

---

## 5. Các bước thực hiện

**Bước 1: Script xuất dữ liệu** (`demo/build_data.py`, `demo/notebook_results.py`)
- Tải 6 record tiêu biểu + annotation của 48 record vào `demo/.cache/`.
- Tính: đoạn 30 s qua từng tầng lọc, beat trong đoạn, beat trung bình theo nhãn, PSD, chỉ số chất lượng, HR/RR/RMSSD/STL/cờ bất thường, phân bố nhãn 48 record.
- Chạy lại dự báo ARIMA(7,0,4) và SARIMA cho record 100 (có cache vì mất vài phút).
- Chép kết quả notebook (phân loại, grid search, bảng 2xx, ST-MEM) có ghi nguồn.
- Xong khi: chạy `python demo/build_data.py` ra được `demo/data/demo_data.js`, dung lượng < 5 MB, MAE/RMSE ARIMA khớp notebook (≈ 1.18 / 1.46).
- ✅ **Đã xong**: `demo_data.js` nặng 2.48 MB, chạy mất ~3 phút (lần đầu thêm thời gian tải dữ liệu). Chạy lại dự báo: ARIMA MAE 1.178 / RMSE 1.465 (notebook 1.181 / 1.463); SARIMA MAE 2.137 / RMSE 2.517 (notebook 2.055 / 2.418). Chuỗi HR giống hệt (1806 điểm, train 1756), phần lệch đến từ bộ tối ưu SARIMAX không hội tụ (notebook cũng đã cảnh báo ConvergenceWarning). Demo hiển thị cả số chạy lại lẫn số notebook. Dữ liệu tải từ mirror S3 của PhysioNet vì physionet.org chỉ đạt khoảng 6 KB/s.

**Bước 2: Khung trang**: `index.html`, thanh điều hướng, bố cục, giao diện sáng/tối, nạp dữ liệu.
- ✅ **Đã xong**: `index.html` + `style.css` + `app.js` (JS thuần, không cần build). Đã có: thanh trên cùng (điều hướng tự đánh dấu mục đang xem, chọn record, nút theme Tự động/Sáng/Tối có ghi nhớ), 4 ô số ở mục Tổng quan, 6 thẻ chọn record, biểu đồ ECG mẫu (lưới kiểu giấy ECG, nhãn beat có màu + chữ, nút 5–10 s / 30 s, nút xem dạng bảng). Các mục còn lại đang để khung chờ bước 3.
- Khác kế hoạch: Plotly **lưu sẵn trong `demo/vendor/`** (bản cartesian 2.35.2, 1.36 MB) thay vì tải từ CDN, để mở demo khi không có mạng vẫn chạy.
- Cách mở: double-click `demo/index.html` (Chrome/Edge), hoặc chạy `python -m http.server 8765 --directory demo` rồi vào `http://localhost:8765`. Cấu hình xem trước của app Claude nằm ở `.claude/launch.json`.
- Đã kiểm tra: không lỗi console, sáng/tối, đổi record, bảng, màn hình 375 px không cuộn ngang. Bảng màu đã chạy bộ kiểm định CVD/độ tương phản: qua ở cả hai chế độ. Ba màu sáng có tương phản thấp nên luôn kèm nhãn chữ và có dạng bảng.

**Bước 3: Dựng từng mục 1 → 7** theo phần 3 ở trên.

**Bước 4 (tuỳ chọn): Xem dự đoán CNN theo từng cửa sổ**: thêm vào notebook CNN đoạn lưu model + xác suất trên tập test, train lại một lần (cần GPU), rồi demo hiện các cửa sổ test được đoán đúng/sai.

**Bước 5: Kiểm tra & chia sẻ**: chạy thử trên Chrome/Edge, màn hình điện thoại, sáng/tối; chia sẻ bằng file zip hoặc GitHub Pages.

---

**Bước 3: ✅ Đã xong** (19/10/2026), xem mục 8 ở cuối file.

---

## 5b. YÊU CẦU MỚI: màn hình theo dõi nhịp tim (ưu tiên trước bước 3) — ✅ đã xong, xem mục 8

Yêu cầu: một trang **chạy sóng ECG như máy monitor thật**, HR cập nhật theo nhịp, **cảnh báo khi có bất thường**.
Đã chốt: cảnh báo = **luật nhịp (02_EDA) + mô hình ST-MEM** (dự đoán tính trước, không cần real-time); không dùng CNN. Vị trí: trang riêng `demo/monitor.html` (bạn không chọn, mình chọn theo đề xuất), trang demo có nút mở.

### Đã làm
- `demo/train_stmem.py`: dùng lại hàm của `mit-bih.py` (2 thử nghiệm), đọc MIT-BIH từ cache local, seed 42, lưu model tốt nhất (theo val AUC) và **xác suất Abnormal cho từng cửa sổ 9 s** của record test 102–106 + val 200/208/232/233/234 → `demo/.cache/stmem_results.json`.
  - Đã tải đủ 48 record vào `demo/.cache/mitdb/`; dataset đã cache ở `demo/.cache/stmem/dataset.npz` (train 7600, val 1000, test 1000: 439 Normal / 561 Abnormal, khớp phân bố của CNN 9 s).
  - GPU: RTX 5070 qua PyTorch (TensorFlow trên Windows không thấy GPU). Thử nghiệm 1 ~10 s/epoch.
  - **Đã DỪNG theo yêu cầu** khi thử nghiệm 1 tới epoch ~10 (val AUC ~0.78). Chưa có `stmem_results.json`. Log dở: `demo/.cache/stmem_train_partial.log`. Chạy lại: `python demo/train_stmem.py` (dùng lại dataset cache).
- `demo/build_monitor.py`: xuất `demo/data/monitor_data.js` cho 5 record (103, 106, 105 thuộc test; 208, 232 thuộc val), mỗi record một đoạn 306 s (34 cửa sổ 9 s), tín hiệu 250 Hz đã lọc như mit-bih.py, R-peak tự phát hiện, HR từng nhịp, sự kiện theo luật (PVC-like, ngưng nhịp, nhịp nhanh/chậm, không đều), xác suất ST-MEM + nhãn chuyên gia từng cửa sổ. Đã chạy thử khi chưa có ST-MEM (1.65 MB).

### Vấn đề tìm thấy, cần sửa tiếp
1. **Bộ phát hiện R-peak**: XQRS bỏ sót PVC (Se 0.922 ở 208, 0.956 ở 106) → sinh cảnh báo ngưng/nhịp chậm giả. So sánh với nhãn chuyên gia (sai số ±150 ms):

   | Record | XQRS | GQRS | Pan-Tompkins (nb 01) | NeuroKit2 |
   | --- | --- | --- | --- | --- |
   | 103 | 0.999 / 1.000 | 1.000 / 1.000 | 0.997 / 1.000 | 1.000 / 1.000 |
   | 106 | 0.956 / 0.999 | 1.000 / 0.997 | 0.855 / 0.999 | 0.998 / 0.996 |
   | 105 | 0.998 / 0.987 | 0.997 / 0.970 | 0.996 / 0.983 | 0.990 / 0.994 |
   | 208 | 0.922 / 0.998 | 0.995 / 0.998 | 0.926 / 0.999 | 0.997 / 0.999 |
   | 232 | 0.999 / 0.999 | 0.999 / 0.986 | 0.996 / 1.000 | 1.000 / 0.965 |

   (Se / PPV.) Đề xuất: đổi sang **NeuroKit2** (đã dùng trong notebook sliding window) hoặc GQRS trong `detect_beats()` của `build_monitor.py`.
2. **Cảnh báo nhịp chậm/nhanh/không đều bật-tắt liên tục** (232: 24 lần) → thêm điều kiện duy trì: bật khi điều kiện đúng ≥ 3 beat liên tiếp, tắt khi điều kiện tắt đúng ≥ 5 beat.

### Còn lại
1. Sửa 2 vấn đề trên, chạy lại `train_stmem.py` (~10–20 phút GPU) rồi `build_monitor.py`.
2. Viết `monitor.html` / `monitor.js` / `monitor.css`: nền tối kiểu monitor bệnh viện; sóng ECG quét trên canvas (~8 s/màn hình); HR lớn + tim nhấp nháy theo nhịp (tuỳ chọn tiếng bíp); ô ST-MEM cho cửa sổ 9 s đã hoàn tất (điểm mô hình + nhãn chuyên gia để đối chiếu); băng dấu hiệu + nhật ký sự kiện (gộp sự kiện cùng loại trong 10 s); dải thời gian chỉ hiện điểm của cửa sổ đã hoàn tất, bấm để tua; chọn record, phát/tạm dừng, tốc độ 1×/2×/4×.
3. Thêm nút "Mở màn hình theo dõi" ở trang demo; cập nhật mục 07 ST-MEM bằng kết quả test thật (đọc `stmem_results.json` trong `build_data.py`).
4. Kiểm tra trình duyệt (`.claude/launch.json`, cấu hình `ecg-demo`, cổng 8765), rồi quay lại bước 3.

---

## 6. Ngoài phạm vi

- Tải ECG lên, dự đoán thời gian thực, backend, đăng nhập.
- Train lại các model (trừ bước 4 tuỳ chọn).
- Sửa notebook gốc (trừ bước 4).

## 7. Câu hỏi còn mở (đang dùng mặc định trong ngoặc)

1. Ngôn ngữ giao diện? (tiếng Việt, giữ thuật ngữ chuyên môn tiếng Anh)
2. Có đưa ST-MEM vào demo không? (có: đã fine-tune lại trên MIT-BIH, mục 07 có kết quả thật; PTB-XL vẫn thiếu dữ liệu)
3. Có làm bước 4 không? (để sau)
4. Chia sẻ demo thế nào? (mở file local; GitHub Pages nếu cần)

---

## 8. TỔNG HỢP PHIÊN TỰ ĐỘNG (19/10/2026), để bạn kiểm tra lại

Bạn giao: tự làm hết các việc còn lại rồi ghi tổng hợp vào đây. Giữa chừng bạn nhắn thêm: *"chỉ cần sử dụng cửa sổ 9 giây… hình trái tim thì không phù hợp… phải thường là ECG, HR/RR là các biểu đồ cần xem"*. Màn hình theo dõi đã được làm lại theo yêu cầu này.

### 8.1 Cách mở

```bash
python -m http.server 8765 --bind 127.0.0.1 --directory demo
```
- Trang chính: http://localhost:8765/index.html
- Màn hình theo dõi: http://localhost:8765/monitor.html. Mở từ nút "Mở màn hình theo dõi" ở đầu trang chính, hoặc mục "Theo dõi ↗" trên thanh điều hướng.
- Double-click `demo/index.html` hoặc `demo/monitor.html` cũng chạy được, vì không dùng ES module và không cần fetch.

### 8.2 Thứ tự chạy lại toàn bộ dữ liệu

| Lệnh | Thời gian | Tạo ra |
| --- | --- | --- |
| `python demo/train_stmem.py` | ~7 phút (RTX 5070) | `demo/.cache/stmem_results.json`, `demo/.cache/stmem/exp{1,2}_trainable.pt` |
| `python demo/calibrate_stmem.py` | ~10 s | chọn ngưỡng trên val, ghi thêm vào `stmem_results.json` |
| `python demo/build_monitor.py` | ~10 s | `demo/data/monitor_data.js` (1.65 MB) |
| `python demo/build_data.py` | ~15 s (khi đã có cache) | `demo/data/demo_data.js` (2.49 MB) |

Trên Windows nên đặt `PYTHONIOENCODING=utf-8`. Nếu không, `print` tiếng Việt ra console cp1252 sẽ lỗi `UnicodeEncodeError`; lần chạy đầu của `train_stmem.py` đã chết vì lỗi này.

### 8.3 Màn hình theo dõi: `monitor.html` + `monitor.js` + `monitor.css`

Bố cục tham khảo màn hình monitor đầu giường và phần mềm Holter: nền đen, sóng ECG bên trái, số liệu lớn màu xanh bên phải, các biểu đồ xu hướng xếp chồng chung trục thời gian, có tachogram RR và nhật ký sự kiện. Thay đổi so với kế hoạch ở 5b:
- **Sóng ECG quét đúng 9 s mỗi màn**, bằng 1 cửa sổ ST-MEM, trên mọi kích thước màn hình (kế hoạch cũ: 8 s). Lưới giấy ECG 0.2 s × 0.5 mV. Beat sớm do luật phát hiện được ghi "PVC" phía trên. Khoảng ngưng có vạch đỏ kèm "Ngưng x.xx s". Nhãn chuyên gia ở đáy, tắt được.
- **Bỏ hình trái tim lớn.** Cột số liệu gồm: HR (bpm, chữ xanh lớn, chuyển đỏ khi có cảnh báo nhanh/chậm hoặc mất nhịp > 2 s, có chấm nhỏ nháy theo nhịp), RR (ms), số PVC, số lần ngưng, RMSSD (20 RR), và ô ST-MEM cho cửa sổ 9 s vừa thu xong (xác suất, thanh ngưỡng, nhãn chuyên gia, khớp/lệch).
- **Biểu đồ xu hướng** (canvas, chung trục 0–306 s, bấm để tua):
  1. HR theo từng nhịp, có vạch ngưỡng 120/50 và nền cam ở đoạn đang cảnh báo nhanh/chậm.
  2. RR tachogram: chấm xanh là RR thường, vàng là beat sớm, đỏ là RR > 2 s; nền vàng ở đoạn "không đều".
  3. ST-MEM: cột xác suất mỗi 9 s, vạch ngưỡng, gạch đỏ dưới cột cho cửa sổ chuyên gia gán bất thường.

  Chỉ vẽ HR/RR đã phát và điểm ST-MEM của cửa sổ 9 s đã hoàn tất. Ô trắng mờ đánh dấu phần đã phát của cửa sổ 9 s đang hiện trên màn ECG.
- **Poincaré RR** (RRₙ → RRₙ₊₁, 60 s gần nhất): nhịp đôi hiện thành 2 cụm, ngưng nhịp hiện thành điểm xa.
- **Băng cảnh báo** (`role=alert`) hiện cảnh báo nặng nhất đang có, kèm "+N cảnh báo khác". Mức critical thì nhấp nháy, tắt khi người dùng bật giảm chuyển động. **Nhật ký** gộp các sự kiện cùng loại trong 10 s thành "×N".
- Điều khiển: chọn record, phát/dừng (phím cách), tốc độ 1×/2×/4×, ← → để tua 9 s, tiếng bíp (mặc định tắt). Phát dừng ở cuối để hiện cửa sổ cuối; bấm Phát để xem lại. Nhớ record, tốc độ và lựa chọn nhãn bằng localStorage.
- 5 record: 103 (gần bình thường), 106 (PVC, nhịp đôi), 105 (nhiễu) thuộc tập test; 208 (PVC + F), 232 (nhịp chậm, ngưng dài) thuộc tập val. Mỗi record phát một đoạn 306 s (34 cửa sổ).

**Sửa trong `build_monitor.py`** (2 vấn đề ghi ở 5b):
1. R-peak đổi từ XQRS sang **NeuroKit2** (`ecg_clean` + `ecg_peaks` trên tín hiệu thô 360 Hz). Số beat phát hiện so với chuyên gia trong đoạn phát: 103 358/358, 106 325/324, 105 426/426, 208 503/509, 232 286/280.
2. **Cảnh báo trạng thái có điều kiện duy trì:** bật khi điều kiện đúng ≥ 3 beat liên tiếp, tắt khi điều kiện tắt đúng ≥ 5 beat. Thêm một thay đổi mình tự quyết: luật nhanh/chậm dùng **trung vị 8 RR** thay cho trung bình 4 RR. Lý do: ở 232, các khoảng ngưng 2–5 s kéo trung bình 4 RR xuống < 50 bpm dù giữa các khoảng ngưng HR ≈ 80. Kết quả trên 232: cảnh báo nhịp chậm giảm từ 19 lần xuống 2 lần; 34 khoảng ngưng vẫn được báo riêng. HR hiển thị vẫn là trung bình 4 RR.

Số sự kiện trong đoạn phát (luật + ST-MEM):

| Record | PVC | Ngưng | Nhanh | Chậm | Không đều | ST-MEM |
| --- | --- | --- | --- | --- | --- | --- |
| 103 | 0 | 0 | 0 | 0 | 0 | 15 |
| 106 | 45 | 0 | 0 | 0 | 2 | 5 |
| 105 | 12 | 0 | 0 | 0 | 7 | 28 |
| 208 | 5 | 2 | 1 | 0 | 4 | 17 |
| 232 | 1 | 34 | 0 | 2 | 0 | 4 |

### 8.4 ST-MEM: đã chạy thật

- `train_stmem.py` chạy hết 2 thử nghiệm của `mit-bih.py` (seed 42, GPU RTX 5070, tổng 402 s):

  | Thử nghiệm | Epoch tốt nhất / chạy | Val AUC | Test acc | Test F1 | Test AUC |
  | --- | --- | --- | --- | --- | --- |
  | 1 · đóng băng encoder, train head | 12 / 22 | 0.781 | 0.681 | 0.757 | 0.779 |
  | 2 · train lead emb + head | 1 / 11 | 0.780 | 0.699 | 0.751 | 0.757 |

  Thử nghiệm 1 được chọn vì val AUC cao hơn.
- **Ngưỡng (mình tự quyết):** ở ngưỡng 0.5, model báo bất thường 58% cửa sổ bình thường của tập test (specificity 0.42). Trên màn hình theo dõi, record 103 (gần như bình thường) báo động giả 19/34 cửa sổ. Script mới `demo/calibrate_stmem.py` chọn ngưỡng bằng **Youden J trên tập val** (record 200, 208, 232, 233, 234) và không dùng test để chọn. Ngưỡng chọn được: **0.619**.

  | | Ngưỡng | Acc | Precision | Recall | Specificity | F1 |
  | --- | --- | --- | --- | --- | --- | --- |
  | Test @0.5 | 0.500 | 0.681 | 0.661 | 0.888 | 0.417 | 0.757 |
  | Test @chọn | 0.619 | 0.703 | 0.718 | 0.775 | 0.611 | 0.746 |

  Màn hình theo dõi và mục 07 dùng ngưỡng 0.619. Record 103 vẫn còn 15/34 cảnh báo ST-MEM: model này yếu thật, mình không che đi.
- **Nhận xét:** ST-MEM (F1 0.746, AUC 0.779) **kém xa 1D CNN 9 s** (F1 0.945) dù cùng tập test và cùng quy tắc nhãn. Accuracy theo cửa sổ ở 232 chỉ 0.165, vì record này nhiều beat A mà model không bắt được; ở 105 (nhiễu) là 0.395. Nguyên nhân có thể là encoder được pretrain trên ECG 12 lead 250 Hz, còn ở đây chỉ dùng 2 lead MIT-BIH và mới train head. Muốn cải thiện thì cần fine-tune toàn bộ encoder (thử nghiệm 3, chưa có trong `mit-bih.py`).
- PTB-XL vẫn chưa chạy được, vì thiếu `ptbxl_database.csv` và `records500/`.

### 8.5 Trang chính: các mục 01–07 đã có nội dung

- **01 Tổng quan:** 4 ô số; sơ đồ quy trình 2 nhánh (dự báo, phân loại), bấm vào từng bước để tới mục tương ứng; danh sách "Điểm chính" (CNN và ensemble khác quy tắc nhãn; ST-MEM so với CNN; ARIMA thắng 15/25 record; hai quy tắc nhãn lệch nhau 115/401 cửa sổ ở 106; 68.5% beat là N); link sang màn hình theo dõi.
- **02 Tín hiệu:** ECG 30 s (đã có từ trước), thẻ thông tin record với số beat theo loại, beat trung bình ± std theo nhãn, phân bố 23 loại nhãn trên 48 record (log, tô màu Normal/Abnormal/bỏ qua), % beat bất thường của 48 record tô màu theo tập train/val/test.
- **03 Tiền xử lý:** nút chọn tầng (thô / band-pass / khử baseline, kèm đường baseline ước lượng / notch / z-score), PSD trước và sau lọc với vạch 0.5/40/60 Hz, bảng chỉ số chất lượng 6 record (tô cột đang chọn).
- **04 Nhịp tim & HRV:** 7 ô số; HR 1 Hz với ngưỡng 120/50; RR theo loại beat (khoanh beat kiểu PVC và RR outlier); RMSSD cuộn với ngưỡng; STL 4 tầng có chấm đột biến.
- **05 Dự báo:** 4 ô MAE/RMSE (kèm số trong notebook); ARIMA và SARIMA trên record 100; top 10 AIC (chấm ± std); dumbbell ARIMA vs SARIMA trên 25 record 2xx (MAE/RMSE, trục log).
- **06 Phân loại:** 2 thẻ phương pháp; bảng 6 cấu hình (thêm hàng ST-MEM); biểu đồ metric theo độ dài cửa sổ (F1/Recall/Precision/Specificity); 6 confusion matrix; 2 quy tắc nhãn kèm 3 cửa sổ ví dụ.
- **07 ST-MEM:** cách làm và cấu hình; 5 ô số; bảng 2 thử nghiệm; đường loss; ROC test có 2 điểm làm việc; bảng chọn ngưỡng kèm 2 confusion matrix; độ chính xác theo record.
- `build_data.py` có thêm `build_stmem()`: đọc `stmem_results.json` nếu có, còn không thì dùng mô tả cũ trong `notebook_results.py`.
- Sửa thêm lỗi: biểu đồ vẽ khi khung chứa chưa gắn vào trang bị Plotly lấy độ rộng mặc định 700 px, làm trang tràn ngang. Giờ `plot()` chờ tới lúc phần tử đã nằm trong trang mới vẽ.

### 8.6 Đã kiểm tra

- Trên trình duyệt (server `ecg-demo`), cả hai trang không lỗi console. Trang chính có đủ 21 biểu đồ, không có biểu đồ nào rộng hơn khung chứa.
- Giao diện tối và sáng; màn hình 375 px và desktop: không cuộn ngang. Trên điện thoại, sơ đồ quy trình xếp dọc.
- Màn hình theo dõi: đổi record, tua bằng cách bấm biểu đồ, băng cảnh báo, nhật ký "×N", ô ST-MEM khớp/lệch.
- **Chưa kiểm tra:** chạy lâu nhiều vòng lặp, tiếng bíp (khung xem ẩn không phát âm thanh), trình duyệt Firefox/Safari, mở bằng `file://`.

### 8.7 Việc còn lại / gợi ý

1. **Chưa commit gì.** Các file mới: `demo/` (trừ `.cache/`, đã có trong `.gitignore`), `plan.md`, `.claude/launch.json`. Thư mục PTB-XL+ trong `notebooks/.../ST-MEM/data/` rất nặng, không nên commit.
2. Nếu muốn ST-MEM tốt hơn: thêm thử nghiệm fine-tune toàn bộ encoder (lr nhỏ, ~1e-5), hoặc thử tăng số lead đầu vào.
3. Bước 4 cũ (lưu dự đoán CNN theo cửa sổ) vẫn để sau. Nếu làm, màn hình theo dõi có thể hiện CNN song song với ST-MEM để so sánh.
4. Muốn chia sẻ: GitHub Pages phục vụ thẳng thư mục `demo/`, vì mọi thư viện đã nằm trong `demo/vendor/`.
5. Hạn chế đã biết của luật PVC (02_EDA: RR ngắn < 80% trung vị, sau đó RR dài > 120%): ở 208, PVC xuất hiện dày (nhịp đôi/nhịp ba) nên trung vị RR bị kéo theo, luật chỉ bắt được 5 lần trong đoạn phát. Nhãn chuyên gia (chữ V ở đáy màn ECG) và ST-MEM bù một phần. Nếu cần sửa thì nên dùng trung vị của các RR "dài" (ví dụ 8 RR lớn nhất trong 32 RR gần nhất) làm mốc.


## 9. KIỂM TRA LẠI THEO REPORT (3:20 sáng 19/10/2026)

Phiên tự động, không có người xem. Không commit, không push, không xoá file của bạn.

### 9.1 Report (`Final_Report_TS-3.pdf`, 39 trang) nói gì
- **Dataset MIT-BIH** (360 Hz, 2 lead). Lọc 0.5–40 Hz + notch, resample **250 Hz**, cửa sổ **9 s = 2250 mẫu** (và 4.5 s). Nhãn: `N` = Normal; `+ x " Q ~` bỏ; còn lại = Abnormal. Chia theo record: test 102–106, val 200/208/232/233/234, còn lại train.
- **Bảng 3.1: 9 s có 15.200 train / 2.000 val / 2.000 test cửa sổ** (4.5 s: 15.238 / 2.004 / 2.004).
- **Pretrain:** dùng checkpoint ST-MEM ViT-B có sẵn (patch 75, 30 patch/lead, mask 0.75 chỉ ở pretrain). Không tự pretrain.
- **Fine-tune:** bỏ decoder, thêm head sigmoid + BCE, ngưỡng 0.5. Hai chiến lược: *Linear probe* (đóng băng encoder, chỉ train head) và *Semi-finetune* (train **lead embedding + head**, còn lại đóng băng). Report không ghi epoch, lr, batch.
- **Kết quả công bố (test, 9 s):**

  | | Acc | Precision | Recall | F1 |
  | --- | --- | --- | --- | --- |
  | Linear probe (Bảng 5.3) | 0.5392 | 0.6776 | 0.8398 | 0.7500 |
  | Semi-finetune (Bảng 5.3) | 0.9672 | 0.9722 | 0.9669 | **0.9695** |
  | 1D CNN 9 s (Bảng 5.2) | 0.9354 | 0.9354 | 0.9554 | 0.9453 |
  | Extra Trees 9 s (Bảng 5.1) | 0.7300 | 0.6590 | 0.7666 | 0.7087 |

- **PTB-XL (Bảng 5.4):** 12 lead, ViT-B; Supervised (random init) acc 0.787 / F1 0.604; ST-MEM linear probe 0.726 / 0.508; ST-MEM finetune 0.825 / 0.655. Report không nói rõ 5 lớp hay cách chia; mình dùng đúng `compare_ptbxl_supervised_vs_stmem.py` (5 superclass, strat_fold).

### 9.2 Các điểm lệch tìm thấy
1. **Stride cửa sổ (lệch dữ liệu):** `mit-bih.py` dùng stride 9 s (không chồng lấn) → 7.600 / 1.000 / 1.000 cửa sổ. Report có 15.200 / 2.000 / 2.000, đúng gấp đôi, tức **stride 4.5 s (chồng 50%)**. Phiên trước chạy theo stride 9 s nên tập val/test khác (test 439 N / 561 A thay vì 879 / 1121). Đã xác nhận: stride 4.5 s cho ra đúng 15.200 / 2.000 / 2.000.
2. **Semi-finetune không tái hiện được 0.97 với đúng mô tả.** Train chỉ 2 lead embedding + head (2.305 tham số trên ~85 triệu) chỉ đạt F1 ≈ 0.78 (AUC 0.82). Linear probe thì khớp report (F1 0.756 vs 0.750). Chỉ **fine-tune cả encoder** mới lên F1 0.9625, rất sát 0.9695 của report. Khả năng cao con số 0.9695 trong report đến từ bản có nhiều tham số được train hơn mô tả (hoặc code khác); mình không có code đó nên không khẳng định được. Cần bạn xác nhận.
3. **Ngưỡng:** phiên trước tự chọn ngưỡng 0.619 (Youden trên val) cho demo; report dùng 0.5. Kết quả mới đều ở 0.5.
4. **Dataset PTB-XL sai/thiếu:** thư mục trong repo là PTB-XL+ (chỉ features). Chưa từng có waveform thật → mục PTB-XL của demo trống. Đã tải đúng PTB-XL 1.0.3.
5. **Checkpoint pretrain:** load đúng. MIT-BIH (2 lead): loaded 156, skipped 10 (lead_embeddings.2–11, vì model 2 lead chỉ có 2 embedding; hợp lý, 2 embedding đầu được giữ nguyên). PTB-XL (12 lead): loaded 166, skipped 0.
6. Màn hình theo dõi (`monitor.html`) vẫn dùng model *đóng băng encoder, stride 9 s* cũ (yếu, AUC 0.78). Chưa đổi (xem 9.6).

### 9.3 Đã tải gì
- PTB-XL 1.0.3 từ mirror S3 `https://physionet-open.s3.amazonaws.com/ptb-xl/1.0.3/`: `ptbxl_database.csv`, `scp_statements.csv`, `records500/` (21.799 record, 43.598 file `.dat/.hea`, **2.629 MB**, 0 lỗi) → `demo/.cache/ptbxl/`. Script: `demo/download_ptbxl.py`. Thư mục PTB-XL+ cũ giữ nguyên.
- Cache mảng đã xử lý: `demo/.cache/ptbxl_arrays.npz` (1,9 GB) và `demo/.cache/stmem/dataset_stride45.npz`. Xoá được nếu cần chỗ.

### 9.4 Đã chạy lại gì
**MIT-BIH, `demo/train_stmem_v2.py`** (dùng hàm của `mit-bih.py`; 9 s @ 250 Hz, 2 lead, stride 4.5 s; train 15.200 (7.649 N / 7.551 A), val 2.000 (425 / 1.575), test 2.000 (879 / 1.121); seed 42; ngưỡng 0.5; early stop theo val loss). Test:

| Cách fine-tune | Tham số train | Acc | Precision | Recall | F1 | AUC |
| --- | --- | --- | --- | --- | --- | --- |
| Linear probe (chạy lại) | 769 | 0.672 | 0.648 | 0.908 | 0.756 | 0.771 |
| Semi-finetune: lead emb + head (chạy lại) | 2.305 | 0.711 | 0.684 | 0.902 | 0.778 | 0.824 |
| **Full fine-tune cả encoder, lr 1e-4 (thêm)** | 85.143.703 | 0.958 | 0.963 | 0.962 | **0.9625** | 0.993 |
| *Report: linear probe* | | 0.539 | 0.678 | 0.840 | 0.750 | |
| *Report: semi-finetune* | | 0.967 | 0.972 | 0.967 | 0.9695 | |
| *Cũ (mục 8.4): stride 9 s, ngưỡng 0.5, đóng băng* | | 0.681 | 0.661 | 0.888 | 0.757 | 0.779 |

Số tham số train đọc từ `stmem_results_v2.json` / log (`demo/.cache/stmem_v2.log`). Full fine-tune: best epoch 2 (dừng sớm), AdamW lr 1e-4 encoder / 1e-3 head, tối đa 15 epoch.

**PTB-XL, `demo/run_ptbxl.py`** (bọc `compare_ptbxl_supervised_vs_stmem.py`; 5 superclass multi-label, 12 lead, 9 s @ 250 Hz, strat_fold 1–8 / 9 / 10 → 13.801 / 1.709 / 1.711 record; **chỉ tối đa 8 epoch, patience 3, batch 32**, bản gốc là 50 epoch/batch 64 nên chưa hội tụ hẳn). Test, ngưỡng 0.5; Acc tính theo từng nhãn, F1 macro:

| Mô hình | Acc | F1 macro | AUROC macro | Acc report | F1 report |
| --- | --- | --- | --- | --- | --- |
| Supervised (random init, lr 1e-4) | 0.861 | 0.540 | 0.863 | 0.787 | 0.604 |
| ST-MEM Linear Probe | 0.870 | 0.583 | 0.894 | 0.726 | 0.508 |
| ST-MEM Finetune (cả model, lr 1e-4) | 0.898 | 0.707 | 0.937 | 0.825 | 0.655 |

Thứ tự Supervised < Linear probe < Finetune khác thứ tự report (ở report Linear probe thấp nhất); finetune tốt nhất giống report. Cách tính accuracy của report không rõ nên số acc không so trực tiếp được. Lưu ý: lần chạy supervised đầu với lr 1e-3 (mặc định của script) bị **loss NaN do fp16** (macro-AUC 0.763, F1 0.208, lưu ở `ptbxl_results_lr1e-3_sup_nan.json`); đã chạy lại với lr 1e-4. Train 1 seed, không có khoảng tin cậy.

### 9.5 File đã sửa / thêm
- Thêm: `demo/download_ptbxl.py`, `demo/train_stmem_v2.py`, `demo/run_ptbxl.py`.
- Sửa: `demo/build_data.py` (thêm `build_report_rerun()`, đọc `stmem_results_v2.json` + `ptbxl_results.json` + số của report vào `D.stmem.report_rerun`), `demo/app.js` (mục 07 thêm 2 thẻ: "Chạy lại theo report" và "PTB-XL 5 lớp").
- Đã chạy lại `python demo/build_data.py` (ghi `demo/data/demo_data.js`, forecast dùng cache). `node --check demo/app.js` ok.
- Kết quả thô: `demo/.cache/stmem_results_v2.json`, `ptbxl_results.json`; log `stmem_v2.log`, `ptbxl_run2.log`, `ptbxl_run3.log`.
- Không sửa `notebooks/Classification/ST-MEM/*`, không động vào `stmem_results.json` cũ.

### 9.6 Chưa làm được
- **Chưa kiểm tra trình duyệt:** việc mở preview server `ecg-demo` bị từ chối trong phiên tự động, nên chưa xem thẻ mới, chưa kiểm tra console và cuộn ngang ở 375 px. Chỉ có kiểm tra cú pháp JS. Bạn nên mở `demo/index.html` mục 07 xem.
- **Màn hình theo dõi chưa đổi** sang model full fine-tune (không lưu trọng số, chỉ lưu số liệu). Muốn thì thêm lưu trọng số + dự đoán cho các record test/val vào `train_stmem_v2.py` rồi sửa `build_monitor.py`.
- **Chưa giải thích được** vì sao report đạt 0.9695 với "semi-finetune"; cần bạn xem lại code/notebook gốc của report (số tham số thực sự được train).
- PTB-XL chưa chạy đủ 50 epoch như script gốc (giới hạn thời gian, ~1,5 giờ GPU cho 8 epoch × 3 mô hình).
- Kết quả MIT-BIH là 1 seed (42), chưa lặp lại.

---

## 10. CHỐT LẠI ST-MEM THEO YÊU CẦU (19/10/2026, sáng)

Bạn chốt:
- **Dữ liệu là MIT-BIH đọc bằng WFDB**, không dùng PTB-XL. Phần PTB-XL ở mục 9 là thừa: tác vụ 3:20 tự đi tải vì đề bài tôi viết cho nó nhấn quá mạnh vào PTB-XL.
- **Dùng checkpoint pretrained có sẵn** (ST-MEM của bài báo Na et al., ICLR 2024), chỉ fine-tune, không tự pretrain.
- **Giữ đúng Semi-finetune như report** (train lead embedding + head), dù F1 thấp hơn report.
- **Không chạy Linear probe**, chỉ chạy Semi-finetune để dùng luôn.

### Đã làm
- `demo/train_stmem.py` viết lại theo report:
  - MIT-BIH qua WFDB (file giống hệt `pn_dir='mitdb'`, đọc từ cache `demo/.cache/mitdb`), 2 lead, 9 s @ 250 Hz.
  - Cửa sổ trượt **stride 4.5 s**, ra 15.200 / 2.000 / 2.000 cửa sổ, đúng Bảng 3.1 của report. `mit-bih.py` để stride 9 s nên chỉ ra một nửa số cửa sổ.
  - Checkpoint `pretrain/st_mem_vit_base_encoder.pth`: load 156 key. Bỏ qua `lead_embeddings.2–11`, vì model 2 lead chỉ có 2 lead embedding.
  - **Chỉ chạy Semi-finetune** (thử nghiệm 2 của `mit-bih.py`): 2.305 tham số được train (head 769 + 2 lead embedding × 768), 85.141.398 tham số đóng băng.
  - Ngưỡng **0.5** như report. Không còn bước tự chọn ngưỡng; đã xoá `demo/calibrate_stmem.py`.
- Kết quả cũ (stride 9 s) được giữ ở `demo/.cache/stmem_results_stride9_old.json`.
- Đã chạy lại `build_monitor.py` và `build_data.py`. Mục 07 của trang chính đã bỏ hết PTB-XL và Linear probe, chỉ còn Semi-finetune so với report. Màn hình theo dõi dùng model này.
- Đã kiểm tra trên trình duyệt: không lỗi console, không cuộn ngang, đủ 21 biểu đồ, màn hình theo dõi hiện "ST-MEM ViT-B Semi-finetune · ngưỡng 0.50".

### Kết quả Semi-finetune (tập test, record 102–106, ngưỡng 0.5, seed 42)

| | Accuracy | Precision | Recall | F1 | AUC |
| --- | --- | --- | --- | --- | --- |
| Chạy lại (best epoch 6/16, 440 s) | 0.7065 | 0.6757 | 0.9161 | 0.7777 | 0.8165 |
| Report, Bảng 5.3 | 0.9672 | 0.9722 | 0.9669 | 0.9695 | — |

Confusion matrix của lần chạy lại: Normal thật 386 đúng / 493 sai; Abnormal thật 1.027 đúng / 94 sai.

Model bắt được hầu hết cửa sổ bất thường (recall 0.92), nhưng báo nhầm hơn một nửa số cửa sổ bình thường (specificity 0.44). Accuracy theo record (cửa sổ 9 s không chồng lấn): 102 0.965, 103 0.690, 104 0.950, 105 0.335, 106 0.650, 200 0.790, 208 0.930, 232 0.530, 233 0.940, 234 0.620.

**Vẫn còn lệch so với report:** cùng dữ liệu, cùng checkpoint, cùng tham số được train, nhưng F1 chỉ 0.778 so với 0.9695 trong report. Report không ghi epoch, learning rate, batch hay seed, và repo không còn log của lần chạy gốc. Nếu bạn còn notebook hoặc log Kaggle/Colab của lần chạy ra 0.9695, gửi tôi để so từng bước.

### Dọn dẹp
- Theo yêu cầu, đã xoá: `demo/.cache/ptbxl/` (2,6 GB), `demo/.cache/ptbxl_arrays.npz` (1,8 GB), `demo/download_ptbxl.py`, `demo/run_ptbxl.py`, `demo/train_stmem_v2.py`. `demo/.cache` còn 585 MB.
- Vẫn còn vài file log/kết quả nhỏ của mục 9 trong `demo/.cache/` (`ptbxl_*.json`, `ptbxl_*.log`, `stmem_results_v2.json`, `stmem_v2.log`). Demo không đọc các file này.
- Chưa commit gì.

### Cập nhật khi đưa lên git
- Trọng số đã train (`demo/models/stmem_semi_finetune.pt`, ~11 KB: 2 lead embedding + head) và kết quả (`demo/results/stmem_results.json`) được commit, nên máy khác không phải train lại. `demo/predict_stmem.py` nạp lại và chấm test: ra đúng accuracy 0.7065, F1 0.7777, AUC 0.8165. `train_stmem.py` giờ ghi vào hai thư mục này thay vì `demo/.cache/`.
- **Số liệu ML (sliding window): đã chuyển sang report PDF (bạn chọn).** Sau `git pull --rebase` (10 commit của hoang3003) notebook `sliding window.ipynb` đã chạy lại và không còn khớp báo cáo (ở notebook mới, kết quả 9 s trùng hệt 4.5 s). `demo/notebook_results.py` giờ lấy theo `Final_Report_TS-3.pdf`:
  - Hai dòng tốt nhất mỗi cửa sổ: XGBoost 4.5 s (F1 0.4794) và Extra Trees 9 s (F1 0.7087), kèm confusion matrix từ Hình 5.1 (4.5 s: 916/234/511/343; 9 s: 803/340/200/657). Thêm thẻ "cả sáu cấu hình" của Bảng 5.1; bốn ma trận còn lại suy từ recall + precision + số lớp và khớp lại cả bốn chỉ số của report (sai lệch < 0.0006).
  - Bỏ dòng "Ensemble RF+ET+XGB" (F1 0.437 / 0.393): report không có kết quả bỏ phiếu mềm. Mô tả phương pháp ML cũng sửa theo (ba mô hình riêng, 86/165 đặc trưng).
  - CNN 4.5 s / 9 s khớp Bảng 5.2. Riêng accuracy CNN 9 s: ma trận cho 0.938, report ghi 0.9354 (trùng precision, có vẻ là gõ nhầm); demo giữ 0.938 và ghi chú. Dòng CNN 0.75 s chỉ có trong notebook.
  - ARIMA/SARIMA không có trong report. Đã kiểm lại: các số chép (grid search 360.434, MAE 1.1808 / 2.0553, bảng 2xx 7.962726 / 13.307283) vẫn có đúng trong notebook chạy lại, cùng ô.

### Rà soát logic web (30/10/2026)

- Trang chính ưu tiên tín hiệu ECG, RR/HR, dự báo và phân loại. Đồ thị STL và AIC vẫn giữ trong mục "Phân tích thêm"; không dùng chúng làm bằng chứng về tình trạng tim.
- Trang `monitor.html` được gọi là **phát lại bản ghi**. Tín hiệu và điểm ST-MEM đều có sẵn, không phải phân tích bệnh nhân trực tiếp.
- Quy tắc RR ngắn–dài chỉ gợi ý nhịp sớm, không xác nhận PVC. Quy tắc RR dài được ghi nhận khi nhịp kế tiếp xuất hiện, không phải cảnh báo ngưng tim tức thời.
- RMSSD ở trang web tính trên mọi RR, gồm cả beat ngoại tâm thu. Vì vậy giao diện mô tả là biến thiên RR, không trình bày như HRV lâm sàng. Ngưỡng phân vị 90 trên biểu đồ là của chính record đó.
- Điểm ST-MEM dùng ngưỡng thử nghiệm 0.5, chưa hiệu chỉnh xác suất. Tập test có F1 0.7777 và specificity 0.4391; giao diện dùng từ "gắn cờ" và hiển thị giới hạn này thay vì báo động y tế.
- Đồ thị phát lại giờ chỉ vẽ HR/RR đã đến và điểm ST-MEM của cửa sổ 9 s đã hoàn tất; không làm mờ dữ liệu tương lai nữa. Trục y điều chỉnh theo dữ liệu đã phát. Khi hết đoạn, trang dừng ở cuối để thấy cửa sổ cuối cùng; bấm Phát để xem lại từ đầu.
