# Kế hoạch quản lý chất lượng dự án ECG

**Bản điều chỉnh:** 12/11/2026. **Lịch tham chiếu:** 27 ngày làm việc, 01/10–06/11/2026. Kế hoạch này dùng cùng 16 gói WBS, 5 điểm kiểm tra tích hợp và 6 thành viên với `ECG_Project_WBS_Revised.md` và báo cáo quản lý dự án. Các kiểm tra dưới đây là tiêu chí/bằng chứng cần có; không được đọc như kết quả đã kiểm thử nếu chưa có biên bản.

## 1. Mục tiêu chất lượng

Sản phẩm là tài liệu nghiên cứu và bản trình diễn giáo dục trên ECG MIT-BIH đã ghi. Nó phải đúng phạm vi, mở được từ bản phát hành, truy nguồn được số liệu và không tạo ấn tượng rằng đang đo hoặc cảnh báo y tế trực tiếp. Các chỉ số của mô hình phải đi cùng nhãn, chia tập và cấu hình thí nghiệm. Khác biệt F1 ST-MEM trong báo cáo nghiên cứu (0,9695) và kết quả chạy lại (0,7777) phải được nêu như hai nguồn riêng, chưa kết luận nguyên nhân.

## 2. Trách nhiệm và thời điểm

| Thành viên (vai trò) | Trách nhiệm chất lượng | Ngày LV liên quan |
|---|---|---:|
| Trần Tuấn Anh (DATA) | Kiểm tra nguồn MIT-BIH, lead, nhãn, xử lý tín hiệu và quy tắc chia tập | 4–9, 23–25 |
| Vũ Quốc Huy (ML) | Kiểm tra chuỗi HR, tham số ARIMA/SARIMA, metric và điều kiện so sánh mô hình đặc trưng | 10–13, 19–25 |
| Nguyễn Quang Huy (DL) | Kiểm tra CNN/ST-MEM, split, cấu hình và tệp kết quả; hỗ trợ đối chiếu điểm hiển thị | 10–22, 23–25 |
| Mai Tuấn Mạnh (WEB) | Tự kiểm chức năng và nguồn dữ liệu hai trang trước khi giao QA | 14–22 |
| Hoàng Thị Ngọc Hân (QA) | Dẫn dắt tiêu chí kiểm tra, thử độc lập, ghi lỗi và thử lại; chịu trách nhiệm gói 5.1 | 1–9, 14–25 |
| Nguyễn Tuấn Anh (PM) | Chốt phạm vi/tiêu chí; xử lý ngoại lệ và ra quyết định nghiệm thu nội bộ | 1–3, 21–27 |

QA thực hiện kiểm tra độc lập với người phát triển gói. Chủ gói cung cấp dữ liệu, sửa lỗi và minh chứng; PM quyết định chấp nhận sau khi xem biên bản, không tự thay QA đánh dấu pass.

## 3. Ma trận tiêu chí nghiệm thu

| ID | Gói WBS | Tiêu chí và cách kiểm tra | Bằng chứng tối thiểu |
|---|---|---|---|
| QC1 | 2.1–2.2 | Danh mục record/lead/nhãn đúng nguồn; mô tả lọc, chuẩn hóa, window và split đủ để lặp lại. | Notebook, đặc tả và mẫu đối chiếu. |
| QC2 | 3.1 | Các đồ thị dự báo nêu record, horizon, tham số và MAE/RMSE từ đúng lần chạy. | Bảng kết quả nối tới notebook. |
| QC3 | 3.2–3.4 | Các bảng ML/CNN/ST-MEM ghi riêng điều kiện nhãn, split, ngưỡng; không kết luận hơn/kém từ thí nghiệm không tương đương. | Bảng metric-to-source và giới hạn. |
| QC4 | 4.1–4.2 | Trang tổng quan mở, đủ bảy mục, dữ liệu/đồ thị có nhãn và nguồn. | Checklist Chrome/Edge, ảnh màn hình. |
| QC5 | 4.3 | HR/RR chỉ hiển thị mẫu đã phát; điểm ST-MEM chỉ hiện sau cửa sổ 9 giây; các cờ được ghi là minh họa. | Bản ghi thao tác và kiểm tra dấu thời gian. |
| QC6 | 4.1–4.4 | Bản phát hành mở offline với JS data và thư viện đồ thị cục bộ; hướng dẫn xem không bắt người chấm tái huấn luyện. | Biên bản thử bản sao sạch, README. |
| QC7 | 5.1–5.2 | Report, WBS, CSV/XML dùng cùng 16 mã gói, 27 ngày làm việc, 240 giờ, 6 thành viên và 5 điểm kiểm tra được gộp vào gói việc. | Bảng đối chiếu phiên bản và kết quả kiểm tra số học. |
| QC8 | 5.1–5.3 | Không còn lỗi chặn trình diễn; lỗi còn lại có mức độ, người xử lý và quyết định chấp nhận. | Defect log, kết quả retest, biên bản nghiệm thu. |

## 4. Kiểm soát và điểm kiểm tra chất lượng

| Điểm kiểm tra | Cuối ngày LV | Gói thực hiện | Điều kiện kiểm tra |
|---|---:|---|---|
| M1 | 3 | 1.3 | Scope, tiêu chí chất lượng và người kiểm tra đã được xác định. |
| M2 | 9 | 2.2 | Quy tắc dữ liệu, nhãn và split ổn định để chạy mô hình. |
| M3 | 20 | 3.4 | Các metric có nguồn và giới hạn; sai khác lớn được ghi riêng. |
| M4 | 22 | 4.3–4.4 | Hai trang, tài nguyên offline và README sẵn sàng cho QA. |
| M5 | 27 | 5.3 | QC1–QC8 được kiểm tra; PM ghi quyết định nghiệm thu nội bộ. |

Thời gian rà soát và ghi quyết định đã nằm trong effort của các gói trên; lịch không tạo task 0 giờ cho M1–M5.

Mỗi lỗi có ID, môi trường, bước tái hiện, kết quả mong đợi/thực tế, mức độ, người sửa, ngày retest và trạng thái. Lỗi chặn truy cập, sai nguồn chỉ số hoặc tạo hiểu lầm y tế phải được xử lý trước M5 hoặc có quyết định ngoại lệ ghi rõ. Việc thấy tệp trong kho không đồng nghĩa đã qua thử độc lập.

## 5. Quy tắc phiên bản

Giữ tách biệt baseline kế hoạch, kết quả kiểm tra thực tế và dự báo sửa đổi. Nếu thay đổi tiêu chí, ghi lý do, tác động WBS/lịch/chi phí/rủi ro và người quyết định. Chỉ số đánh giá được so với nguồn gốc của đúng phiên bản dữ liệu/mô hình; không thay một giá trị trong report mà không cập nhật bảng nguồn, demo và hồ sơ QA.
