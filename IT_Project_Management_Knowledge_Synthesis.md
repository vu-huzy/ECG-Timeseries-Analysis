# Tổng hợp kiến thức Quản lý dự án công nghệ thông tin

> Tổng hợp từ 12 PDF học phần, 542 trang PDF. Đã đối chiếu lớp chữ với bản hiển thị của từng trang; các bảng và hình được đọc ở bản hiển thị, nhất là những trang trích chữ không đầy đủ. Tài liệu này là **bản tổng hợp kiến thức**, không phải bản chép nguyên văn các slide.
>
> **Cách dẫn nguồn:** [Số nguồn, tr. số trang PDF]. Số trang được đếm từ trang đầu của từng PDF; số in trên slide đôi khi khác. Ví dụ [S08, tr. 56] là trang PDF thứ 56 của nguồn S08.

## 0. Danh mục nguồn và phạm vi

Các PDF gốc nằm trong thư mục **D:\IT Managament**.

| Mã | Tệp PDF | Số trang | Nội dung chính |
|---|---|---:|---|
| S01 | Chapter 0_Introduction_IT Project Managemant_E.pdf | 14 | Mục tiêu học phần, cấu trúc 6 chương, cách đánh giá |
| S02 | Chapter1_IT_Project_Management_EN1.pdf | 34 | Khái niệm dự án CNTT, vòng đời, bên liên quan, vai trò PM, tiêu chí thành công |
| S03 | Chapter2_IT_Project_Management_EN_1.pdf | 56 | Bối cảnh, mục tiêu, MOV, chọn dự án, business case, project charter, SDLC |
| S04 | Chapter3_IT_Project_Management_CommunicationPlan.pdf | 32 | Kế hoạch truyền thông, kênh, phương pháp và ma trận truyền thông |
| S05 | Chapter3_IT_Project_Management_Cost Management.pdf | 36 | Chi phí, ước lượng, ngân sách, dự phòng và EVM |
| S06 | Chapter3_IT_Project_Management_Project scope management.pdf | 35 | Kế hoạch tổng hợp, quản lý phạm vi, WBS |
| S07 | Chapter3_IT_Project_Management_RiskPlan.pdf | 48 | Quy trình rủi ro, risk register, phân tích và ứng phó |
| S08 | Chapter3_IT_Project_Management_Schedule Management.pdf | 97 | Hoạt động, phụ thuộc, ước lượng, PERT, FP, COCOMO, CPM, Gantt |
| S09 | Chapter4_IT_Project_Management_Excecuting IT Project_1.pdf | 64 | Cơ cấu tổ chức, nguồn lực, RAM/RACI, bố trí và phát triển nhóm |
| S10 | Contemporary IT Project Management.pdf | 24 | Agile, làm việc từ xa, AI, lập kế hoạch cho dự án dữ liệu/ML |
| S11 | Practicing IT Project Management.pdf | 36 | SDLC, Waterfall/Agile/Lean, cải tiến quy trình, AI hỗ trợ |
| S12 | Practicing IT Project Management_06 Risk Management_v2.pdf | 66 | Bảng nghiên cứu về rủi ro và 5 bước thực hành tích hợp WBS/MS Project |

**Giới hạn nguồn:** S01 nêu cả chương kiểm soát và đóng dự án, nhưng 12 PDF này không có bài giảng riêng đầy đủ cho hai chương đó. S06 liệt kê kế hoạch chất lượng và mua sắm, nhưng bộ PDF không có chuyên đề riêng về chất lượng hoặc mua sắm. Các mẫu thực hành về các phần này ở cuối tài liệu được ghi là **gợi ý áp dụng**, không gán nhầm cho slide. Các con số thị trường, báo cáo CHAOS và nghiên cứu được giữ đúng bối cảnh/trang của slide; tài liệu này không xem chúng là số liệu thị trường hiện hành. [S01, tr. 4–10; S02, tr. 6–12; S06, tr. 3; S11, tr. 4]

## 1. Bức tranh tổng thể

### 1.1. Dự án, vận hành, sản phẩm và lợi ích

- **Dự án** là nỗ lực có tính tạm thời nhằm tạo ra sản phẩm, dịch vụ hoặc kết quả độc nhất. Nó có mục tiêu, điểm bắt đầu/kết thúc và giới hạn về phạm vi, thời gian, chi phí. **Vận hành** là hoạt động lặp lại, tiếp diễn để duy trì dịch vụ/sản phẩm. Một dự án có thể tạo ra hệ thống mới rồi chuyển hệ thống đó cho bộ phận vận hành. [S02, tr. 15, 18–19]
- **Sản phẩm/đầu ra** là thứ nhóm bàn giao và có thể kiểm tra được: phần mềm, tài liệu, bộ dữ liệu, dịch vụ. **Kết quả/lợi ích (outcome)** là tác động rộng hơn sau khi dùng đầu ra, ví dụ thời gian xử lý giảm hoặc doanh thu tăng. Bàn giao xong phần mềm chưa tự động chứng minh đã tạo lợi ích kinh doanh. [S02, tr. 16; S03, tr. 15–17]
- **Chương trình (program)** điều phối các dự án liên quan để có lợi ích chung; **danh mục (portfolio)** tập hợp dự án/chương trình/hoạt động để thực hiện chiến lược. [S02, tr. 16]
- **Quản lý dự án CNTT** áp dụng kiến thức, kỹ năng, công cụ và kỹ thuật để đáp ứng yêu cầu dự án. PM lãnh đạo và điều phối nhóm; người có chuyên môn thực hiện phần việc kỹ thuật của mình. [S02, tr. 17, 30; S09, tr. 5]

| Góc nhìn | Dự án | Vận hành |
|---|---|---|
| Thời gian | Có điểm bắt đầu và kết thúc | Liên tục |
| Công việc | Tạo kết quả riêng, có tính mới | Lặp lại và ổn định hơn |
| Nhân sự | Nhóm tạm thời, liên chức năng | Cơ cấu chức năng lâu dài |
| Ngân sách | Phê duyệt theo dự án | Theo kỳ vận hành |
| Kết thúc | Đóng/chuyển giao khi đạt hoặc không còn đạt mục tiêu | Duy trì dịch vụ |

Diễn giải từ bảng so sánh của bài giảng. [S02, tr. 18–19]

### 1.2. Vòng đời, nhóm quy trình và các lĩnh vực quản lý

Slide trình bày năm nhóm hoạt động **khởi tạo → lập kế hoạch → thực hiện → theo dõi/kiểm soát → kết thúc**. Theo dõi/kiểm soát diễn ra song song với thực hiện, không phải chỉ đợi làm xong mới kiểm tra. Các lĩnh vực được liệt kê gồm phạm vi, lịch, chi phí, chất lượng, nhân lực, truyền thông, rủi ro, mua sắm và tích hợp. [S02, tr. 21–25]

~~~mermaid
flowchart LR
    A["Bối cảnh và cơ hội"] --> B["Business case / lựa chọn"]
    B --> C["Project charter"]
    C --> D["Kế hoạch tổng hợp"]
    D --> E["Thực hiện và tạo sản phẩm"]
    E --> F["Nghiệm thu, bàn giao, đánh giá"]
    D <--> G["Theo dõi và kiểm soát thay đổi"]
    E <--> G
~~~

Một dự án được đánh giá qua **thời hạn, chi phí, kỳ vọng khách hàng, hiệu quả nhóm và giá trị kinh doanh**. Làm đúng lịch nhưng sản phẩm không giải quyết nhu cầu vẫn khó coi là thành công. Các nguyên nhân thất bại nêu trong slide gồm phạm vi mơ hồ, mục tiêu không rõ, thông tin thiếu, quản lý yếu và chọn công nghệ không phù hợp. [S02, tr. 26–27]

### 1.3. Vai trò PM và các bên liên quan

**Sponsor/chủ dự án** bảo trợ chiến lược và nguồn lực; **PM** tổ chức, phối hợp, theo dõi và điều chỉnh; **nhóm dự án** tạo đầu ra; **khách hàng/người dùng** đưa yêu cầu và đánh giá kết quả; **nhà cung cấp** giao nguồn lực hoặc dịch vụ; **cơ quan quản trị** đặt ràng buộc và phê duyệt. Cần phân biệt **khách hàng trả tiền/đặt hàng** với **người dùng trực tiếp**: cả hai góc nhìn đều cần được thu thập khi thiết kế sản phẩm. [S02, tr. 20, 30; S03, tr. 4–6, 21–22]

PM cần kết hợp kỹ năng kỹ thuật, giao tiếp và nhìn tổng thể; slide cũng nêu ba nhóm kỹ năng quản lý dự án kỹ thuật, lãnh đạo, chiến lược/kinh doanh. Cơ cấu tổ chức và RACI giúp PM giao việc rõ ràng thay vì tự làm mọi hạng mục. [S02, tr. 31–33; S09, tr. 17–18, 26–32]

## 2. Khởi tạo và lựa chọn dự án

### 2.1. Phân tích bối cảnh

Trước khi chọn giải pháp, xác định vấn đề, mục tiêu chiến lược, các bên liên quan, nguồn lực sẵn có, điều kiện bên ngoài và ràng buộc. Các công cụ xuất hiện trong slide: **PEST/PESTLE** xem môi trường vĩ mô; **Porter 5 lực lượng** xem sức ép ngành; **SWOT** tách điểm mạnh/yếu nội bộ và cơ hội/đe dọa bên ngoài; **BCG** phân loại vị thế danh mục; sơ đồ stakeholder thể hiện các mối quan hệ xung quanh dự án. Công cụ là khung để đặt câu hỏi, không thay cho dữ liệu và quyết định của người có thẩm quyền. [S03, tr. 4–11, 18–22]

### 2.2. Từ goal đến SMART objective và MOV

- **Goal**: đích rộng, ví dụ cải thiện trải nghiệm mua hàng.
- **Objective**: kết quả cụ thể, đo được và có thời hạn, ví dụ tăng tỷ trọng bán hàng trực tuyến lên 20% tổng doanh thu trong 12 tháng. Khi viết SMART, nêu chỉ số, mức gốc, mức đích, hạn đạt và cách đo. [S03, tr. 12–15]
- **MOV — Measurable Organizational Value**: giá trị tổ chức kỳ vọng từ dự án, phải đo được, có giá trị, được thống nhất và kiểm chứng được. Giá trị có thể thuộc tài chính, chiến lược, vận hành, khách hàng hoặc xã hội. Hình của slide nối **tầm nhìn/sứ mệnh → chiến lược tổ chức → MOV**, nghĩa là mục tiêu dự án phải giải thích được đóng góp vào mục tiêu lớn hơn. [S03, tr. 16–17]

**Ví dụ diễn giải:** “Hoàn thành trang web” là đầu ra; “giảm 30% thời gian người dùng tìm một bản ghi, đo trong ba tháng sau triển khai” là một MOV khả kiểm chứng hơn. Ví dụ này do bản tổng hợp xây dựng để minh họa nguyên tắc của slide.

### 2.3. Đánh giá và chọn dự án

Quy trình slide đề xuất: (1) xác định chiến lược, (2) phân tích đặc điểm doanh nghiệp, (3) xác định stakeholder, (4) so sánh phương án. Ngoài phân tích định tính, có thể dùng NPV, ROI, IRR, thời gian hoàn vốn và bảng chấm điểm đa tiêu chí. Bảng “10 things to select project” cho mỗi tiêu chí trọng số 0,1 chỉ là **ví dụ**; trong thực tế phải xác định trọng số theo ưu tiên của tổ chức, tiêu chí không được trùng lặp quá mức, và điểm số cần có căn cứ. [S03, tr. 18–24, 40]

| Chỉ số | Công thức/cách hiểu | Dùng để |
|---|---|---|
| NPV | Tổng dòng tiền thuần đã chiết khấu trừ đầu tư ban đầu | So sánh giá trị tiền hiện tại |
| ROI | Lợi nhuận ròng / chi phí đầu tư, theo kỳ và phạm vi đã nêu | Đo tỷ lệ sinh lợi đơn giản |
| IRR | Mức chiết khấu làm NPV = 0 | So sánh tỷ suất sinh lợi nội bộ |
| Payback | Thời điểm dòng tiền tích lũy bù đầu tư ban đầu | Xem tốc độ thu hồi vốn |
| Điểm có trọng số | Tổng của trọng số × điểm tiêu chí | Cân cả yếu tố phi tài chính |

Với dòng tiền thuần CF_t, đầu tư ban đầu C_0 và lãi suất chiết khấu r:

**NPV = −C_0 + Σ(t = 1…T) CF_t / (1 + r)^t**.

Ví dụ của slide: đầu tư 5.000.000, dòng tiền sáu năm lần lượt 800.000; 1.200.000; 1.200.000; 2.000.000; 1.600.000; 1.600.000, r = 9%, cho **NPV ≈ 1.081.349**. NPV dương theo giả định dòng tiền/lãi suất của ví dụ; kết luận đầu tư vẫn phải xem rủi ro và các phương án khác. [S03, tr. 25–29]

**IRR** là nghiệm của NPV(r) = 0. Slide minh họa phép nội suy khi NPV ở r_1 = 20% bằng 684 và ở r_2 = 30% bằng −928: IRR xấp xỉ **20% + 10% × 684/(684 + 928) = 24,24%**. Đây là ước lượng nội suy; khi dòng tiền đổi dấu nhiều lần có thể có nhiều nghiệm hoặc IRR khó diễn giải. [S03, tr. 37–39]

### 2.4. Business case và project charter

| Tài liệu | Câu hỏi chính | Nội dung tối thiểu | Thời điểm |
|---|---|---|---|
| **Business case** | Có nên đầu tư? Vì sao? | Vấn đề, phương án, lợi ích, chi phí, rủi ro, stakeholder, giả định, đề xuất chấp nhận/từ chối/hoãn/sửa | Trước hoặc trong khởi tạo |
| **Project charter** | Ai cho phép làm gì, trong giới hạn nào? | Mục đích, mục tiêu, phạm vi cấp cao, stakeholder, mốc lớn, ngân sách sơ bộ, rủi ro/giả định, quyền hạn PM | Khi ủy quyền dự án |

Business case thuyết phục người ra quyết định về giá trị; charter xác nhận sự đồng thuận cấp cao và quyền triển khai. Charter không thay thế bản mô tả phạm vi chi tiết, WBS hay lịch. Hình quy trình trong slide cho thấy **business case → project plan/charter → thực hiện/kiểm soát → đóng và đánh giá**. [S03, tr. 41–48; S02, tr. 21]

**Mẫu khởi tạo ngắn:**

1. Vấn đề/cơ hội và bằng chứng hiện trạng.
2. MOV, chỉ số đo, mốc kiểm tra sau bàn giao.
3. Các phương án và lý do chọn.
4. Phạm vi trong/ngoài, sản phẩm bàn giao và tiêu chí chấp nhận cấp cao.
5. Sponsor, PM, khách hàng/người dùng, quyền quyết định.
6. Mốc thời gian, ngân sách sơ bộ, giả định, ràng buộc và rủi ro lớn.
7. Quyết định: phê duyệt, yêu cầu sửa hoặc dừng.

## 3. Lựa chọn cách phát triển phần mềm

Các slide phân biệt **Waterfall** (phân tích/thiết kế/xây dựng/kiểm thử/bàn giao theo các chặng chính, phù hợp hơn khi yêu cầu ổn định), **incremental** (giao từng phần giá trị), **iterative** (lặp để hoàn thiện giải pháp), và **Scrum** (làm việc theo Sprint, kiểm tra và điều chỉnh thường xuyên). Không nên chọn phương pháp chỉ vì phổ biến; xem độ ổn định yêu cầu, rủi ro, quy mô, năng lực nhóm, mức tham gia của khách hàng và yêu cầu kiểm soát. [S03, tr. 49–54; S11, tr. 6–10]

| Cách làm | Khi phù hợp | Kế hoạch và điểm kiểm tra |
|---|---|---|
| Waterfall | Yêu cầu ít đổi, phụ thuộc bàn giao rõ | Mốc phê duyệt từng chặng; kiểm soát thay đổi chặt |
| Incremental | Có thể giao từng tập tính năng độc lập | Mỗi increment có tiêu chí nghiệm thu và bàn giao |
| Iterative | Cần học từ bản thử rồi sửa dần | Mỗi vòng có bản đánh giá và quyết định vòng tiếp |
| Scrum/Agile | Cần ưu tiên lại theo phản hồi thường xuyên | Product backlog, Sprint planning, Daily Scrum, Review, Retrospective, Increment |
| Lean/Kanban | Muốn giảm thời gian chờ và giới hạn việc đang làm | Trực quan luồng việc, giới hạn WIP, đo tắc nghẽn |

Các thành phần Scrum nêu trong bài thực hành gồm Product Owner, Scrum Master, Developers; sự kiện Sprint, Planning, Daily Scrum, Review, Retrospective; hiện vật Product Backlog, Sprint Backlog và Increment. Agile có thể tăng tính tự chủ nhưng cũng có áp lực và chi phí phối hợp; tác động đến sự hài lòng của nhóm không mặc nhiên tích cực. [S11, tr. 8–10; S10, tr. 6]

Lean nhấn mạnh giá trị do khách hàng xác định, loại bỏ lãng phí, chất lượng ngay trong quá trình, học hỏi, giao nhanh theo bước nhỏ, huy động nhân viên và cải tiến liên tục. Các kỹ thuật minh họa: giảm WIP, cân bằng tải, trực quan công việc và tự động hóa hợp lý. [S11, tr. 11–14]

## 4. Kế hoạch quản lý dự án và phạm vi

### 4.1. Kế hoạch tổng hợp, baseline và tài liệu hỗ trợ

**Project management plan** phối hợp các kế hoạch con, hướng dẫn thực hiện/kiểm soát, ghi giả định và lựa chọn, thiết lập baseline và lịch rà soát. Bản kế hoạch có thể cập nhật qua kiểm soát thay đổi; **baseline đã phê duyệt** là mốc so sánh, không tự ý sửa mỗi khi thực tế lệch. Kế hoạch cần vừa sức dự án: dự án nhỏ có thể dùng bộ tài liệu gọn, dự án lớn cần các kế hoạch chuyên biệt. [S06, tr. 4–10]

| Nhóm trong slide | Ví dụ |
|---|---|
| Kế hoạch quản lý | Phạm vi/yêu cầu, lịch, chi phí, chất lượng, nguồn lực, truyền thông, rủi ro, mua sắm |
| Tài liệu dự án | Danh sách và thuộc tính hoạt động, assumption/issue/change log, ước lượng, milestone list, lịch, sơ đồ mạng, scope statement, phân công nhóm, quality metrics/report |
| Baseline quan trọng | Phạm vi, lịch, chi phí sau khi được phê duyệt |

Slide S06 phân biệt **kế hoạch quản lý** với **project documents**; tài liệu sau là hiện vật làm việc được cập nhật theo quá trình. [S06, tr. 7–8]

### 4.2. Quản lý phạm vi

Sáu việc chính: **lập cách quản lý phạm vi → thu thập yêu cầu → xác định phạm vi → tạo WBS → xác nhận/nghiệm thu phạm vi → kiểm soát phạm vi**. Thu thập yêu cầu qua phỏng vấn, khảo sát, quan sát, benchmark hoặc workshop. Scope statement phải nêu mô tả sản phẩm, các đầu ra, tiêu chí chấp nhận và ranh giới ngoài phạm vi; ví dụ server trên slide cho thấy bản mô tả cụ thể hơn sẽ dễ ước lượng và phê duyệt hơn. [S06, tr. 11–23]

**Scope creep** là mở rộng mục tiêu/tính năng/đầu ra mà không có phê duyệt tương ứng về lịch, tiền, người. Một thay đổi **được phê duyệt qua quy trình** không phải scope creep. Khi nhận đề nghị thay đổi, ghi yêu cầu → phân tích tác động phạm vi/lịch/chi phí/chất lượng/rủi ro → người có thẩm quyền quyết định → cập nhật baseline và thông báo. [S12, tr. 5–10; S05, tr. 28–30]

### 4.3. WBS: phân rã toàn bộ phạm vi

WBS là cấu trúc **hướng theo sản phẩm bàn giao** để thể hiện **100% công việc thuộc phạm vi**. Hình cây, bảng mã số và ví dụ software release đều mô tả cùng nguyên tắc: mỗi cấp cha bằng tổng phạm vi của các cấp con, gói công việc chỉ xuất hiện một lần, mỗi phần tử có một chủ sở hữu rõ ràng. Nhóm thực hiện nên tham gia lập WBS; thông tin của gói được ghi trong WBS dictionary. [S06, tr. 24–33]

**Quy tắc sử dụng:**

1. Bắt đầu từ các đầu ra lớn, phân rã dần đến gói có thể ước lượng, giao người, kiểm tra và nghiệm thu.
2. Mỗi gói có **mã**, mô tả đầu ra, ranh giới, người sở hữu, tiêu chí hoàn thành, bằng chứng, giả định và liên kết đến yêu cầu.
3. Đặt tên đầu ra bằng danh từ/cụm danh từ; hoạt động trong lịch bằng động từ. Ví dụ WBS “Bộ dữ liệu đã làm sạch”, activity “kiểm tra bản ghi thiếu”.
4. WBS trả lời **làm ra cái gì**, chưa tự xác định thứ tự trước/sau; thứ tự thuộc kế hoạch lịch.
5. Kiểm tra quy tắc 100%, không trùng lặp; xử lý yêu cầu mới qua kiểm soát thay đổi.

Các bước trên diễn giải các nguyên tắc và hình WBS trong slide. [S06, tr. 25–33; S08, tr. 16–19]

**Phân biệt PBS / WBS / activity list:**

| Thành phần | Tập trung vào | Ví dụ |
|---|---|---|
| PBS | Cấu phần của sản phẩm | Bộ dữ liệu, mô hình, giao diện |
| WBS | Toàn bộ đầu ra/công việc cần giao để hoàn thành dự án, kể cả quản lý và kiểm thử | 1.1 Kế hoạch, 1.2 Bộ dữ liệu, 1.3 Mô hình, 1.4 Hồ sơ kiểm thử |
| Activity list | Hành động để tạo một work package | Thu thập dữ liệu, làm sạch, kiểm tra, duyệt |

S06 có hình PBS/TBS và ba hình WBS dạng cây/bảng. S08 minh họa đường đi **WBS → work package → activity**, cho thấy lịch chi tiết cần truy vết được về WBS. [S06, tr. 28–33; S08, tr. 17–18]

**Ví dụ WBS gọn cho dự án CNTT/dữ liệu, do bản tổng hợp đề xuất:**

| Mã | Gói bàn giao | Người sở hữu vai trò | Điều kiện hoàn thành |
|---|---|---|---|
| 1.1 | Charter và kế hoạch đã duyệt | PM | Có quyết định của sponsor |
| 1.2 | Bộ yêu cầu và tiêu chí chấp nhận | Analyst/Product Owner | Khách hàng xác nhận phiên bản |
| 1.3 | Dữ liệu sẵn sàng | Data lead | Kiểm tra quyền sử dụng, chuẩn, chất lượng dữ liệu |
| 1.4 | Thiết kế giải pháp | Tech lead | Thiết kế được rà soát |
| 1.5 | Phần mềm/mô hình phiên bản thử | Dev/ML lead | Chạy được và có kết quả kiểm thử |
| 1.6 | Hồ sơ kiểm thử và nghiệm thu | QA/Test lead | Có kết quả, lỗi tồn và quyết định chấp nhận |
| 1.7 | Tài liệu bàn giao và lessons learned | PM + các lead | Có người nhận, hướng dẫn vận hành và biên bản |

Ví dụ áp dụng thêm công việc **phê duyệt dữ liệu, chuẩn dữ liệu, làm sạch, mốc data-ready, thử nghiệm mô hình, ngưỡng hiệu năng, theo dõi mô hình và nghiệm thu** mà S10 yêu cầu khi lập WBS cho dự án ML/DS. [S10, tr. 18–24]

## 5. Lập và kiểm soát lịch dự án

### 5.1. Chuỗi lập lịch đúng

**WBS hoàn chỉnh → danh sách activity và milestone → thuộc tính hoạt động → phụ thuộc → ước lượng nguồn lực/công sức/thời lượng → sơ đồ mạng và lịch → kiểm tra đường găng, tải người → phê duyệt baseline → cập nhật thực tế.** Kế hoạch quản lý lịch cần nêu đơn vị thời gian, độ chính xác của ước lượng, lịch làm việc, ngưỡng phải báo cáo/đổi kế hoạch, cách đo tiến độ và mẫu báo cáo. [S08, tr. 11–23, 69, 83–97]

Một **milestone** là sự kiện đáng kể, thông thường không có duration: phê duyệt charter, chốt thiết kế, hoàn thành kiểm thử, go-live, bàn giao. Mốc không phải hoạt động kéo dài nhiều ngày; nếu cần công sức chuẩn bị, thêm các activity riêng trước mốc. [S08, tr. 23–24]

**Activity attributes** có thể ghi: ID/tên/mô tả, nguồn lực và kỹ năng cần, vật tư, ràng buộc ngày, predecessor/successor, loại quan hệ, lead/lag và giả định. Các thuộc tính phải thống nhất với WBS dictionary. [S08, tr. 16, 19–22]

### 5.2. Phụ thuộc, sơ đồ mạng và lịch Gantt

| Quan hệ | Ý nghĩa | Ví dụ |
|---|---|---|
| FS (Finish-to-Start) | B bắt đầu sau khi A kết thúc | Duyệt thiết kế rồi mới triển khai |
| SS (Start-to-Start) | B bắt đầu sau khi A bắt đầu | Bắt đầu kiểm tra dữ liệu khi bắt đầu nhận dữ liệu |
| FF (Finish-to-Finish) | B kết thúc sau khi A kết thúc | Rà soát tài liệu hoàn tất cùng bản phát hành |
| SF (Start-to-Finish) | B chỉ kết thúc sau khi A bắt đầu | Quan hệ hiếm, cần giải thích rõ |

Slide minh họa bốn quan hệ FS/SS/FF/SF bằng thanh thời gian. Phụ thuộc có thể **bắt buộc, tùy chọn, nội bộ hoặc bên ngoài**. **Lead** cho phép chồng lấn, **lag** là khoảng chờ. Dùng lead/lag có lý do, không dùng để che một hoạt động thực tế chưa được ghi vào WBS. Sơ đồ **AOA/ADM** vẽ hoạt động trên mũi tên, còn **AON/PDM** vẽ hoạt động trong ô và mũi tên là quan hệ; Gantt nhấn vào lịch theo trục thời gian. [S08, tr. 27–33, 84–95]

### 5.3. Phân biệt effort, duration và lịch

- **Effort/Work**: tổng công sức, đo bằng giờ/ngày công của người thực hiện.
- **Duration**: thời gian lịch mà hoạt động chiếm, kể cả lúc chờ/không làm trực tiếp.
- **Calendar**: ngày, ca, kỳ nghỉ và mức sẵn sàng thực tế của nguồn lực.

Ví dụ một việc cần 16 giờ công không tự động xong trong hai ngày nếu người được giao chỉ có 4 giờ/ngày hoặc đang chờ phản hồi. Với một người và điều kiện đơn giản, duration xấp xỉ work / (giờ làm hữu dụng mỗi ngày × tỷ lệ phân bổ). Khi nhiều người cùng làm, phải xét phần việc có chia độc lập được không và chi phí phối hợp; Brooks' Law trong slide cảnh báo thêm người vào dự án phần mềm đã trễ có thể làm trễ hơn. [S08, tr. 35, 73–75; S04, tr. 29]

### 5.4. Các kỹ thuật ước lượng

| Kỹ thuật | Cách làm | Khi hữu ích / giới hạn |
|---|---|---|
| Tương tự (analogous) | Dựa dự án đã làm tương tự | Nhanh, cần so điều kiện giống/khác |
| Top-down | Ước lượng tổng rồi phân bổ xuống | Có giới hạn tổng nhưng dễ ép các gói |
| Bottom-up | Người làm ước từng activity nhỏ rồi cộng | Cụ thể hơn, tốn công; bắt đầu từ WBS |
| Delphi | Nhiều chuyên gia ước độc lập, lặp để giảm chênh | Giảm ảnh hưởng người nói lớn nhất |
| Parametric | Dùng đơn vị đo × hệ số năng suất đã hiệu chuẩn | Phụ thuộc chất lượng dữ liệu/hệ số |
| Time-box | Giới hạn thời gian để tạo mức giá trị khả thi | Tốt khi ưu tiên phạm vi; không làm biến mất công việc |
| PERT ba điểm | Kết hợp lạc quan, khả dĩ nhất, bi quan | Thể hiện bất định tốt hơn một con số |

Slide cũng nhắc “guesstimating”: đoán số không có cơ sở là cách nhanh nhưng thiếu tin cậy. Áp lực lịch, yêu cầu thay đổi, kỹ năng nhóm, phụ thuộc, môi trường làm việc và công việc bị bỏ sót đều làm sai ước lượng. [S08, tr. 38–49, 69–81]

**PERT:** với O (optimistic), M (most likely), P (pessimistic), thời lượng kỳ vọng **ET = (O + 4M + P)/6**. Ví dụ “Requirements Definition” của slide: (8 + 4×30 + 40)/6 = **28**. Tám activity trong bảng slide cộng lại **140** đơn vị thời gian kỳ vọng; tổng này chỉ là tổng effort/thời lượng từng activity, **không tự động là duration của cả dự án nếu có hoạt động song song**. [S08, tr. 66–71]

### 5.5. Function Point (FP) và COCOMO

Function Point ước lượng kích thước chức năng theo năm loại: **EI** (đầu vào ngoài), **EO** (đầu ra ngoài), **EQ** (truy vấn ngoài), **EIF** (tệp dữ liệu do hệ khác quản lý mà ta đọc), **ILF** (tệp logic do hệ thống quản lý). Hình ranh giới ứng dụng giúp quyết định dữ liệu nào là nội bộ và đâu là giao diện bên ngoài. [S08, tr. 51–54]

| Loại | Trọng số thấp / vừa / cao | Số lượng ví dụ thấp / vừa / cao | Điểm đã kiểm tra |
|---|---|---|---:|
| EI | 3 / 4 / 6 | 3 / 5 / 4 | 53 |
| EO | 4 / 5 / 7 | 4 / 2 / 1 | 33 |
| EQ | 3 / 4 / 6 | 2 / 5 / 3 | 44 |
| EIF | 5 / 7 / 10 | 0 / 2 / 0 | 14 |
| ILF | 7 / 10 / 15 | 3 / 2 / 1 | 56 |
| **UAF** | | | **200** |

Với tổng mức ảnh hưởng TDI = 40 trong bảng 14 đặc tính hệ thống, **VAF = 0,65 + 0,01×TDI = 1,05**; **FP điều chỉnh = UAF×VAF = 210**. Trang 56 có lỗi hiển thị ở **ô EO**: phép nhân trong ô không khớp tổng 33 và số lượng EO ở trang 55. Bảng trên dùng số lượng/trọng số nhất quán của trang 55, tổng đúng 200. [S08, tr. 55–58]

Ví dụ COCOMO cơ bản của slide cho hệ **semi-detached**: 200 FP × 53 LOC/FP = 10.600 LOC = 10,6 KDSI; effort = 3 × 10,6^1,12 ≈ **42,21 person-months**; duration = 2,5 × 42,21^0,35 ≈ **9,26 tháng**; nhân sự trung bình theo công thức ≈ 42,21 / 9,26 = **4,56 người**. Đây là ví dụ mô hình lịch sử với giả định cụ thể, không nên dùng hệ số ấy cho dự án khác khi chưa hiệu chuẩn. [S08, tr. 59–64]

### 5.6. CPM, float và đường găng

Với hoạt động i:

- **ES_i = max(EF của mọi predecessor)**; activity đầu tiên có thể lấy ES = 0.
- **EF_i = ES_i + duration_i**.
- Đi ngược từ thời điểm kết thúc dự án: **LF_i = min(LS của mọi successor)**.
- **LS_i = LF_i − duration_i**.
- **Total float = LS − ES = LF − EF**. Đường dài nhất trong sơ đồ mạng quyết định thời gian hoàn thành sớm nhất; những activity có float bằng 0 nằm trên đường găng trong giả định lịch đó.

Hình ví dụ A–J ở slide cho đường PERT dài nhất **A–B–D–G–I–J = 20,5 ngày**, các đường khác ngắn hơn. Đường găng có thể thay đổi khi duration hoặc quan hệ đổi; muốn rút lịch có thể cân nhắc tăng nguồn lực ở việc có thể chia (crashing) hoặc chồng lấn hợp lý (fast tracking), đồng thời đánh giá chi phí/rủi ro tăng. [S08, tr. 89–97]

**Resource leveling** dời việc để xử lý quá tải nguồn lực và có thể đổi ngày kết thúc; **resource smoothing** dùng khoảng float để làm phẳng tải mà cố giữ ngày kết thúc. Biểu đồ nhân sự theo tháng ở S09 cho thấy tổng nhu cầu thay đổi theo pha, không thể suy ra “mỗi người có cùng số giờ” chỉ từ duration dự án. [S09, tr. 47–52]

## 6. Quản lý chi phí và EVM

### 6.1. Phân loại và ước lượng

**Chi phí cố định/biến đổi/hỗn hợp** mô tả biến động theo khối lượng; **trực tiếp/gián tiếp** mô tả khả năng quy về đầu ra; **hữu hình/vô hình** mô tả khả năng quy đổi tiền; **sunk cost** đã chi không thể thu hồi; **opportunity cost** là lợi ích của phương án tốt nhất bị bỏ qua. **Life-cycle costing** nhìn cả xây dựng, vận hành, bảo trì và kết thúc; không chỉ tiền trước ngày go-live. [S05, tr. 7–11]

Quy trình chi phí: xác định nguồn lực và đơn giá → ước chi phí của gói/hoạt động → phân bổ theo thời gian để có **cost baseline** → ghi actual cost → dự báo và kiểm soát thay đổi. Bảng WBS chi phí của slide cộng các phần quản lý, thiết bị, phần mềm, kiểm thử, đào tạo/hỗ trợ và dự phòng; bảng theo tháng cho thấy **time-phased budget**, tức ngân sách không phải một con số tổng đứng riêng. [S05, tr. 12–13, 19–24]

| Loại ước lượng trong slide | Giai đoạn | Dải sai số minh họa của slide |
|---|---|---|
| ROM | Rất sớm, sàng lọc phương án | −25% đến +75% |
| Budgetary | Lập ngân sách ban đầu | −10% đến +25% |
| Definitive | Trước mua sắm/thực hiện, có chi tiết | −5% đến +10% |

Dải trên là **minh họa của bài giảng**, không phải cam kết độ chính xác cho mọi tổ chức/dự án. Có thể ước bằng analogous, parametric, PERT/ba điểm, bottom-up hoặc FP; phải ghi giả định, đơn vị, ngày giá, nguồn đơn giá và người kiểm tra. Bảng mức lương PM/AD/Dev/Tester trong slide là **bài tập đơn giá giả định**, không đại diện chi phí hiện hành của thị trường. [S05, tr. 15–18, 26]

### 6.2. Baseline và dự phòng

Hình “Project Budget Component” phân biệt:

- **Ước lượng chi phí activity/work package**: nền tảng của ngân sách.
- **Contingency reserve**: cho rủi ro đã nhận diện và lượng hóa, nằm trong **cost baseline**.
- **Management reserve**: cho bất định chưa biết, nằm trong **project budget** nhưng ngoài cost baseline; chỉ đưa vào baseline sau khi thay đổi được duyệt.

Không tính dự phòng hai lần ở gói công việc và ở tổng. Phải mô tả điều kiện dùng, người phê duyệt và số dư; “10% dự phòng” không tự chứng minh đủ nếu chưa gắn với phân tích rủi ro. [S05, tr. 22–24; S07, tr. 16–20]

### 6.3. Earned Value Management (EVM)

| Ký hiệu | Ý nghĩa | Công thức/chỉ dẫn |
|---|---|---|
| BAC | Ngân sách baseline tại lúc hoàn thành | Tổng ngân sách được duyệt |
| PV | Giá trị kế hoạch đến ngày báo cáo | Ngân sách của phần đáng lẽ hoàn thành |
| EV | Giá trị thu được từ phần **thực sự hoàn thành** | Ngân sách quy cho phần được xác nhận hoàn thành |
| AC | Chi phí thực tế đã phát sinh | Số thực chi có bằng chứng |
| CV | Chênh lệch chi phí | EV − AC |
| SV | Chênh lệch lịch dưới đơn vị tiền | EV − PV |
| CPI | Hiệu suất chi phí | EV / AC |
| SPI | Hiệu suất tiến độ | EV / PV |
| EAC | Dự báo tổng chi phí nếu CPI hiện tại tiếp tục | BAC / CPI, chỉ là một kịch bản |

Hình ví dụ của slide: **BAC = 100.000; đến tháng 6 dự kiến 50% nên PV = 50.000; thực tế hoàn thành 25% nên EV = 25.000; AC = 27.000**. Do đó **CV = −2.000; SV = −25.000; CPI ≈ 0,926; SPI = 0,5; EAC theo giả định trên ≈ 108.000**. CV âm/CPI dưới 1 nói về **vượt chi so với giá trị tạo ra**; SV âm/SPI dưới 1 nói về **chậm so với giá trị theo lịch**. CPI bằng 1 là đúng nhịp chi phí, không có nghĩa đúng lịch. [S05, tr. 29–36]

**Điều kiện dùng EVM:** phải có baseline theo thời gian, tiêu chí đo hoàn thành đáng tin cậy và chi phí thực tế được ghi nhận. “% hoàn thành” ước cảm tính hoặc giờ công khai cho cân bảng không đủ để khẳng định EV/AC; dữ liệu ước lượng và dữ liệu thực tế phải đặt ở cột riêng. [S05, tr. 22, 29–33; S10, tr. 21–22]

## 7. Chất lượng và nghiệm thu: phần được nêu, phần cần áp dụng thêm

S06 liệt kê **quality management plan, quality metrics, quality control measurements/report** trong bộ kế hoạch và tài liệu; S02 nêu đáp ứng kỳ vọng khách hàng như một tiêu chí thành công; S03 yêu cầu **acceptance criteria** trong scope statement; S10 yêu cầu mốc ngưỡng hiệu năng và acceptance testing cho dự án ML. Bộ 12 PDF **không có chuyên đề chất lượng chi tiết**, vì vậy phần sau là **mẫu áp dụng từ các nguyên tắc đó**, không phải chép một quy trình riêng của slide. [S02, tr. 26; S03, tr. 45–48; S06, tr. 8, 20; S10, tr. 19–21]

| Nội dung kế hoạch chất lượng cần xác định | Câu hỏi kiểm tra |
|---|---|
| Tiêu chí chấp nhận | Sản phẩm đạt mức nào thì được người có quyền chấp nhận? |
| Chỉ số và ngưỡng | Đo bằng dữ liệu/mẫu thử nào, ngưỡng đạt là bao nhiêu? |
| Người tạo và người kiểm | Ai thực hiện, ai kiểm tra độc lập khi cần, ai quyết định nghiệm thu? |
| Bằng chứng | Test case, biên bản, log lỗi, kết quả benchmark ở đâu? |
| Xử lý lỗi | Phân cấp lỗi, người sửa, hạn sửa, retest, điều kiện đóng lỗi? |
| Thay đổi | Nếu tiêu chí/ngưỡng đổi thì ai đánh giá tác động và phê duyệt? |

Với sản phẩm ML/DS, nên bổ sung phê duyệt dữ liệu/tiêu chuẩn dữ liệu, kiểm tra data readiness, kết quả đối chiếu với ngưỡng hiệu năng và kế hoạch theo dõi mô hình sau bàn giao. [S10, tr. 19–24]

## 8. Tổ chức dự án và quản lý nhân sự

### 8.1. Từ nhu cầu công việc đến cơ cấu nhóm

Nguồn lực được hoạch định **sau khi hiểu yêu cầu và chia công việc**: xác định vai trò, kỹ năng, quyền hạn, quan hệ báo cáo, số người theo pha và khi nào cần họ. Đầu vào gồm kế hoạch dự án, nhu cầu nguồn lực của activity, môi trường doanh nghiệp và tài sản quy trình. Đầu ra là kế hoạch nhân sự gồm cơ cấu tổ chức, mô tả vai trò, kế hoạch tuyển/chọn, lịch khả dụng, đào tạo, ghi nhận, thay thế và giải phóng người. [S09, tr. 5–16, 38–43]

**Sơ đồ cơ cấu tổ chức** cho biết *ai báo cáo/điều phối với ai*. **Mô tả vị trí** cho biết chức năng, trách nhiệm, quyền quyết định, năng lực cần. **RAM** nối gói WBS với người/nhóm được giao. **RACI** là một cách mã hóa RAM để rõ ai làm, ai chịu trách nhiệm cuối cùng, ai được hỏi ý kiến và ai cần được báo. Đây là các hiện vật liên kết với nhau, không phải ba bản thay thế nhau. Hình của S09 đặt org chart, responsibility matrix và role description cạnh nhau để thể hiện sự khác biệt này. [S09, tr. 17–18, 26–34]

~~~mermaid
flowchart TD
    Sponsor["Sponsor / người phê duyệt"] --> PM["Project Manager"]
    PM --> BA["Phân tích yêu cầu / Product Owner"]
    PM --> Tech["Tech Lead / Dev"]
    PM --> Data["Data / ML Lead"]
    PM --> QA["QA / kiểm thử"]
    PM --> Ops["Triển khai / vận hành"]
    User["Khách hàng và người dùng"] -. "xác nhận nhu cầu, nghiệm thu" .-> BA
    User -. "phản hồi" .-> QA
~~~

Sơ đồ trên là **ví dụ áp dụng**, không quy định dự án nào cũng phải đủ từng vị trí riêng. Một người có thể kiêm vai trò ở dự án nhỏ, nhưng trách nhiệm và quyền phê duyệt vẫn phải ghi rõ.

### 8.2. RAM và RACI

| Ký hiệu | Nghĩa | Câu hỏi |
|---|---|---|
| R — Responsible | Người/nhóm trực tiếp làm | Ai tạo đầu ra? |
| A — Accountable | Người chịu trách nhiệm cuối cùng/duyệt kết quả | Ai ra quyết định cuối cho hàng công việc này? |
| C — Consulted | Người cần trao đổi hai chiều trước khi làm/duyệt | Cần ý kiến chuyên môn của ai? |
| I — Informed | Người cần nhận thông tin một chiều | Ai cần biết kết quả? |

Một hàng RACI nên có **một A rõ ràng**, ít nhất một R, và tránh C/I dày đặc không cần thiết. Một người có thể đồng thời A/R nếu tự thực hiện và được giao quyền chịu trách nhiệm. Với công việc đòi hỏi phê duyệt bên ngoài, không tự gán PM là người phê duyệt thay sponsor/khách hàng. Hình RACI nhỏ ở S09 tr. 30 minh họa từng activity có cột người; hình **ma trận lớn tr. 32** nhóm cột theo Project Leadership, Project Team Members, Project Sub-Teams và External Resources, hàng theo khởi tạo/lập kế hoạch/thực hiện/kiểm soát/đóng. Ma trận lớn là cách tổng quát để nhìn toàn vòng đời, sau đó có thể lập hàng chi tiết theo WBS. [S09, tr. 26, 30–32]

**Ví dụ RACI gọn, do bản tổng hợp xây dựng:**

| Đầu ra/công việc | Sponsor | PM | Analyst | Tech lead | QA | User |
|---|---|---|---|---|---|---|
| Duyệt charter | A | R | C | I | I | C |
| Xác nhận yêu cầu | I | C | R | C | C | A |
| Duyệt kế hoạch WBS/lịch | A | R | C | C | C | I |
| Xây dựng phiên bản thử | I | I | C | A/R | C | I |
| Kế hoạch kiểm thử | I | C | C | C | A/R | C |
| Nghiệm thu sản phẩm | I | C | C | C | R | A |

Hình khác ở S09 tr. 29 dùng bộ ký hiệu **A/P/R/I/S** theo nghĩa riêng “Accountable / Participant / Review Required / Input Required / Sign-off Required”; **không được đọc chữ R ở hình đó theo nghĩa Responsible của RACI**. Khi đưa vào báo cáo, phải công bố bảng chú giải của hệ ký hiệu mình dùng. [S09, tr. 29–30]

**Cách lập RACI:** liệt kê gói/hoạt động, liệt kê người và tổ chức liên quan, gán vai trò, rà soát hàng/cột bị quá tải hoặc thiếu A/R, thống nhất với người liên quan. RACI không thay cho ước lượng giờ công; hai người có cùng tổng giờ vẫn có công việc và mức trách nhiệm khác nhau. [S09, tr. 31]

### 8.3. Bố trí, cân bằng và phát triển nhóm

Biểu đồ tăng trưởng nhân sự theo tháng của S09 cho thấy số người yêu cầu tăng khi chuyển sang lập trình, kiểm thử/triển khai; cần có **resource calendar** và **histogram** thay vì chỉ lấy một tổng số người cho cả dự án. Kiểm tra quá tải theo tuần/pha, kỹ năng, thời điểm người có mặt và các dự án khác đang tranh nguồn lực. Khi quá tải, có thể dời việc không găng, leveling hoặc smoothing. [S09, tr. 42–52]

Phát triển nhóm gồm đào tạo, phản hồi, phối hợp và xử lý xung đột. Slide đưa các mô hình Maslow, Herzberg, Theory X/Y và Tuckman để hiểu động lực/diễn biến nhóm; xem chúng là **khung suy nghĩ**, không chẩn đoán cố định cho từng người. Về thực hành, PM cần bảo đảm người có đủ năng lực, môi trường làm việc tốt, phản hồi hữu ích, và cơ chế giải quyết trở ngại. [S09, tr. 54–64]

## 9. Kế hoạch truyền thông dự án

Truyền thông dự án không chỉ là gửi tin, mà gồm **lập kế hoạch → tạo/phân phối/lưu trữ/truy xuất thông tin → theo dõi phản hồi và chỉnh cách truyền thông**. Các slide về quy trình truyền thông tại S04 tr. 7–9 bị ghi nhầm tiêu đề “quality management”; nội dung thực tế là communication management. [S04, tr. 5–10]

Với n người có khả năng trao đổi trực tiếp từng cặp, số **kênh tiềm năng = n(n − 1)/2**; 6 người có 15 cặp. Đây là số cặp tối đa về mặt toán học, **không phải chỉ tiêu phải mở 15 luồng chat**. Ma trận truyền thông giúp giảm thông tin thừa và tránh bỏ sót người quyết định. [S04, tr. 14–16]

| Phương thức | Đặc điểm | Ví dụ phù hợp |
|---|---|---|
| **Interactive** | Hai chiều, có phản hồi ngay | Họp giải quyết vấn đề, demo, thương lượng |
| **Push** | Gửi cho người nhận xác định | Báo cáo tuần, yêu cầu phê duyệt, thông báo |
| **Pull** | Người cần tự truy cập nguồn chung | Dashboard, kho tài liệu, hướng dẫn |

Chọn công nghệ theo độ khẩn, khả dụng, dễ dùng, mức nhạy cảm/bảo mật, ngôn ngữ, múi giờ và văn hóa. Email thích hợp cho quyết định chính thức; chat cho câu hỏi nhanh; họp/video cho vấn đề phức tạp; dashboard cho số liệu theo dõi. Nên lưu quyết định, phiên bản tài liệu và đường dẫn đến bằng chứng vào kho chung. [S04, tr. 11–13, 17–23]

**Mẫu ma trận truyền thông, diễn giải từ bảng S04 tr. 27:**

| Bên nhận | Nội dung và mục đích | Tần suất/sự kiện | Kênh/định dạng | Người chuẩn bị | Người duyệt nếu cần | Nơi lưu |
|---|---|---|---|---|---|---|
| Nhóm dự án | Việc xong, việc tới, blocker | Hằng ngày/tuần | Stand-up + bảng việc | Lead từng phần | PM khi có thay đổi baseline | Task board |
| Sponsor | Mốc, chi phí, rủi ro lớn, quyết định cần duyệt | Theo kỳ/mốc | Báo cáo ngắn + biên bản | PM | Sponsor phản hồi/phê duyệt | Kho dự án |
| Khách hàng/người dùng | Demo, yêu cầu, phản hồi và nghiệm thu | Mỗi increment/mốc | Demo + mẫu phản hồi | Product/BA | Đại diện khách hàng | Requirement log |
| Nhà cung cấp | Hạn giao, ràng buộc, yêu cầu thay đổi | Theo hợp đồng | Email/portal | Điều phối mua sắm | Người có thẩm quyền hợp đồng | Contract log |

Kế hoạch truyền thông cần ghi thêm quyền tiếp cận, thời gian, mức chi tiết, người phát hành thông tin mật, tuyến **escalation**, cách sửa ma trận và các ràng buộc lưu trữ. Biên bản họp nên có *quyết định, người chịu trách nhiệm, hạn hoàn thành*; chỉ ghi “đã họp” không giúp điều hành. [S04, tr. 24–27]

**Lưu ý khi đọc slide:** tỷ lệ 58%/35%/7% ở S04 tr. 30 được trình bày như quy tắc tổng quát về giao tiếp mặt đối mặt; không dùng tỷ lệ này để tính hiệu quả truyền thông của dự án. Quyết định thực tế nên dựa trên nhu cầu người nhận, thông điệp, xác nhận đã hiểu và bằng chứng phản hồi.

## 10. Quản lý rủi ro

### 10.1. Khái niệm và quy trình

Rủi ro là **sự kiện/điều kiện không chắc chắn** có thể ảnh hưởng tiêu cực (**threat**) hoặc tích cực (**opportunity**) đến mục tiêu. Khi đã xảy ra và cần xử lý ngay, nó trở thành **issue**; risk register nên gắn với issue log nhưng không đồng nhất hai loại. Sơ đồ “risk management cycle” mô tả chu trình lặp, không phải làm một lần lúc viết báo cáo. [S07, tr. 5–12; S12, tr. 17–23]

Quy trình: **lập kế hoạch rủi ro → nhận diện → phân tích định tính → phân tích định lượng nếu cần → lập phương án ứng phó → theo dõi/kiểm soát**. Kế hoạch rủi ro quy định phương pháp, vai trò, ngân sách/lịch, danh mục, thang xác suất/tác động, ngưỡng chấp nhận, chu kỳ theo dõi và nơi lưu tài liệu. [S07, tr. 10–15]

Các nguồn rủi ro trong hình cây và bảng bài giảng gồm **kinh doanh/khách hàng/nhà cung cấp, kỹ thuật (phần cứng/phần mềm/mạng), tổ chức (nhân sự/quy trình), quản lý dự án (ước lượng/truyền thông/nguồn lực)**. S12 bổ sung nguy cơ **scope creep** do yêu cầu mơ hồ, kiểm soát thay đổi yếu và giao tiếp thiếu. [S07, tr. 21–22; S12, tr. 9–10, 32–33]

### 10.2. Nhận diện và risk register

Nhận diện qua brainstorm có điều phối, phỏng vấn, Delphi ẩn danh, SWOT, checklist từ bài học cũ, “5 Whys” và sơ đồ xương cá. Nên đi theo từng mã WBS để không bỏ rủi ro của một gói công việc; nêu cả cơ hội, không chỉ mối đe dọa. Hình “5 Whys” đi từ vấn đề về nguyên nhân gốc; hình xương cá nhóm nguyên nhân theo nhánh để không vội chọn một lý do bề mặt. [S07, tr. 23–28; S12, tr. 34–39, 60–61]

**Cấu trúc risk register đề xuất từ slide:**

| Trường | Ý nghĩa |
|---|---|
| ID, WBS liên quan, ngày ghi | Truy vết rủi ro đến việc cụ thể |
| Sự kiện, nguyên nhân, hậu quả | Viết theo mẫu “nếu… do… thì…” |
| Nhóm rủi ro và trạng thái | Kỹ thuật/nhân sự/phạm vi…, mở/đang theo dõi/đã đóng |
| Xác suất, tác động, thời điểm | Theo thang thống nhất của dự án |
| Mức ưu tiên và xếp hạng | Để chọn rủi ro xử lý trước |
| Trigger / dấu hiệu sớm | Điều kiện kích hoạt kế hoạch dự phòng |
| Phương án và chi phí/thời gian dự phòng | Việc phải làm trước/sau khi xảy ra |
| Risk owner và người theo dõi | Ai quyết định, ai cập nhật |
| Residual/secondary risk | Rủi ro còn lại hoặc phát sinh do ứng phó |

Slide ghi các trường ID, rank, tên, mô tả, nhóm, nguyên nhân, trigger, phản ứng, owner, xác suất/tác động và trạng thái; mẫu trên thêm WBS/ngày để hỗ trợ thực hành. [S07, tr. 35–38; S12, tr. 46–49, 61]

### 10.3. Định tính, định lượng và đọc bảng nghiên cứu

**Định tính:** đặt xác suất trên một trục, tác động trên trục kia; phân lớp cao/vừa/thấp hoặc dùng điểm ưu tiên theo quy tắc đã công bố. Slide dùng thang ví dụ xác suất 1/2/4/6, tác động 1/2/6/8 và mức “gần đến lúc xảy ra” 1/2/4/6. Đây là **điểm thứ bậc**, không phải xác suất 1%, 2%, 4%, 6%; không nhân vào số tiền như EMV khi chưa quy đổi thành xác suất thực. Hình ma trận và “cây rủi ro” nhấn mạnh ưu tiên rủi ro có khả năng/tác động cao. [S07, tr. 29–34; S12, tr. 40–45]

**Top Ten Risk Item Tracking:** theo kỳ, ghi hạng hiện tại, hạng kỳ trước, số lần ở danh sách và tiến độ xử lý. Nó làm nổi các rủi ro dai dẳng, nhưng không nên loại mọi rủi ro ngoài top 10 khỏi register. [S07, tr. 39–41]

**Định lượng:** dùng decision tree/EMV, mô phỏng hoặc sensitivity analysis khi quyết định và mức rủi ro đủ lớn. **EMV của một nhánh = xác suất × kết quả tiền; EMV của phương án = tổng EMV các nhánh loại trừ nhau**. Hình ví dụ cho Project 1: 0,2×300.000 + 0,8×(−40.000) = **28.000**; Project 2: 0,2×(−50.000) + 0,1×(−20.000) + 0,7×60.000 = **30.000**. Theo tiêu chí EMV, phương án 2 cao hơn 2.000, nhưng mức chịu rủi ro và ràng buộc khác vẫn cần xét. [S07, tr. 42–44; S12, tr. 53–55]

Bảng nghiên cứu được đưa **trong slide S12** (dẫn Menezes Jr và cộng sự, 2019) cho thấy số lần xuất hiện của một số yếu tố: thiếu kỹ năng nhân sự **55**, yêu cầu mơ hồ **44**, cam kết yếu từ user/customer **37**, thay đổi yêu cầu **32**, đưa công nghệ mới vào **30**. Bảng phân nhóm có Product Engineering **483** lần, Development Environment **416**, Program Constraints **515**; trong Product Engineering, Requirements chiếm **244/483 ≈ 51%**. Đây là **tần suất được tổng hợp trong nghiên cứu được slide trích**, không phải xác suất những rủi ro ấy xảy ra trong dự án của người đọc. Bảng theo lớp còn cho ví dụ rủi ro riêng về kiểm thử thiếu, kế hoạch yếu, xung đột nhóm, ước lượng sai và lịch phi thực tế. [S12, tr. 11–15]

### 10.4. Ứng phó và dự phòng

| Với threat | Ý nghĩa | Ví dụ |
|---|---|---|
| Avoid | Đổi kế hoạch để loại nguyên nhân | Bỏ tích hợp không bắt buộc có rủi ro quá lớn |
| Mitigate | Giảm khả năng hoặc tác động | Thử tích hợp sớm, dự phòng nhà cung cấp |
| Transfer | Chuyển một phần hậu quả cho bên khác | Hợp đồng/bảo hiểm, vẫn cần quản lý |
| Accept | Chấp nhận có chủ ý | Theo dõi hoặc lập khoản dự phòng |

Với opportunity, sơ đồ phản ứng nêu **exploit** (tận dụng chắc chắn), **enhance** (tăng khả năng/lợi ích), **share** (hợp tác) và **accept**. **Contingency plan** kích hoạt khi trigger xảy ra; **fallback plan** dùng khi phương án chính không hiệu quả. **Residual risk** còn sau ứng phó; **secondary risk** do chính biện pháp ứng phó tạo ra. [S07, tr. 16–20, 45–47; S12, tr. 56–57, 63–64]

**Quy trình thực hành năm bước ở S12:** (1) gắn risk với WBS, (2) phân tích P/I và tác động lịch/chi phí, (3) giao risk owner và thêm việc giảm thiểu cần thiết, (4) thực hiện khi trigger hoặc chủ động trước trigger, (5) rà soát, báo cáo, cập nhật register/baseline qua phê duyệt. Khi mô phỏng tác động rủi ro trong MS Project, giữ rõ **kịch bản rủi ro**, **baseline được duyệt** và **actual**; không lặng lẽ kéo dài các task và gọi đó là “thực tế”. [S12, tr. 60–65]

## 11. Các chủ đề đương đại và cải tiến cách làm

### 11.1. Chọn phương pháp theo đặc điểm dự án

S10 đối chiếu các cách phát triển, lập kế hoạch Agile và các nghiên cứu về mức hài lòng của nhóm. Bài học có thể dùng là **chọn cách làm theo độ ổn định yêu cầu, khả năng nhận phản hồi, mức phụ thuộc kỹ thuật và ràng buộc quản trị**; không suy ra rằng mọi dự án gắn nhãn Agile đều thành công hơn. Phần nghiên cứu trên slide là gợi ý để đặt giả thuyết, không phải bằng chứng đủ để khẳng định nhân quả cho nhóm của mình. [S10, tr. 4–8, 16–18]

| Điều kiện | Cách lập kế hoạch phù hợp | Điểm cần kiểm soát |
|---|---|---|
| Yêu cầu và đầu ra ổn định; có cổng phê duyệt bắt buộc | Lập mốc/giai đoạn chi tiết hơn từ đầu | Quản lý thay đổi, nghiệm thu từng mốc |
| Yêu cầu còn thay đổi; người dùng phản hồi thường xuyên | Chia increment/sprint, lập chi tiết cho vòng gần | Product backlog, demo, định nghĩa hoàn thành |
| Hệ thống nghiên cứu/ML, kết quả thử nghiệm bất định | Chốt tiêu chí đánh giá và các mốc thử nghiệm, lập lại kế hoạch sau mỗi kết quả | Dữ liệu, baseline đo lường, quyết định go/no-go |

Bảng là **diễn giải áp dụng** từ S03, S10 và S11; không phải bảng quy định nguyên văn của một nguồn. [S03, tr. 43–55; S10, tr. 16–24; S11, tr. 7–10]

### 11.2. Agile, Lean và cải tiến quy trình

Trong Agile, ước lượng có thể dùng **kích thước tương đối** (ví dụ story point), sau đó quan sát tốc độ hoàn thành của chính nhóm để dự báo số vòng cần thiết. Story point không đổi thẳng thành giờ của từng người nếu chưa có dữ liệu hiệu chỉnh; năng lực nhóm, độ mới của công việc và rủi ro phải được xét riêng. Sprint/review là mốc để xem sản phẩm và điều chỉnh backlog. [S10, tr. 16–18; S11, tr. 8–10]

Lean nhấn mạnh giảm chờ đợi, làm lại, bàn giao không cần thiết và **work in progress (WIP)** quá cao; quan sát luồng việc và giải quyết nút thắt. Kanban trực quan hóa trạng thái và giới hạn WIP; Scrum định nhịp bằng Sprint, vai trò và sự kiện. Hai cách có thể kết hợp, nhưng mỗi nhóm cần quy ước cụ thể: “xong” là gì, khi nào kéo việc mới, ai gỡ blocker, đo lead/cycle time thế nào. **Software Process Improvement (SPI)** là cải tiến quy trình liên tục dựa trên vấn đề và số liệu, không chỉ viết thêm quy định. [S11, tr. 9–14, 20–22]

### 11.3. Nhóm từ xa và AI hỗ trợ

Với nhóm phân tán, cần thống nhất giờ đồng bộ, kênh cho quyết định khẩn, kho tài liệu chung, trạng thái task, cách bàn giao giữa múi giờ, cách phản hồi và kiểm tra hiểu đúng. S10 nêu làm việc từ xa, sự hài lòng và thành công dự án như các chủ đề nghiên cứu; khi áp dụng phải đo trên bối cảnh nhóm thật, không suy diễn một kết quả phổ quát. [S10, tr. 6–8]

Các slide S10–S11 gợi ý AI hỗ trợ tóm tắt họp, tạo bản nháp WBS/backlog, tìm rủi ro, gợi ý ước lượng, phát hiện blocker, hỗ trợ code/test và phân tích tài liệu. **Người phụ trách vẫn phải kiểm tra nguồn, tính đúng, quyền dữ liệu, tính bảo mật, thiên lệch và tác động đến baseline trước khi dùng đầu ra AI để ra quyết định.** Nên ghi “AI đã hỗ trợ bước nào, ai kiểm tra, bằng chứng kiểm tra gì” trong hồ sơ dự án. Slide cũng nói bằng chứng thực nghiệm cho các tính năng AI cụ thể còn chưa đủ; vì vậy không gán mức tiết kiệm thời gian hay tăng chất lượng cố định cho AI. [S10, tr. 7–15, 19–22; S11, tr. 22–30]

### 11.4. Dự án dữ liệu/ML: mốc theo bằng chứng

Ví dụ WBS của S10 tách **định nghĩa bài toán → dữ liệu → chuẩn bị/khám phá dữ liệu → mô hình và thử nghiệm → đánh giá/kiểm chứng → triển khai/bàn giao**. Từng mốc nên có sản phẩm chứng minh: yêu cầu và thước đo; nguồn dữ liệu và quyền truy cập; bộ dữ liệu làm sạch; kết quả thử nghiệm có baseline; báo cáo đánh giá sai số; tài liệu vận hành. Nếu mô hình không đạt ngưỡng, kế hoạch cần cổng quyết định cho thử nghiệm tiếp, thay phạm vi hoặc dừng. **Không thể cam kết trước độ chính xác chỉ bằng việc gán ngày hoàn thành task “huấn luyện mô hình”.** [S10, tr. 19–24]

## 12. Cách đọc các hình, bảng và sơ đồ quan trọng

Các trang sau chứa thông tin dễ mất khi chỉ trích chữ PDF. Bảng này ghi **cách đọc và ý nghĩa quản lý** của hình/bảng, không chép lại nguyên hình.

| Hình/bảng gốc | Cách đọc chi tiết | Hệ quả khi làm dự án |
|---|---|---|
| S02 tr. 21–25: vòng đời và nhóm quy trình | Các giai đoạn tạo sản phẩm đi cùng hoạt động quản lý; kiểm soát liên tục cắt ngang thực hiện. | Đừng gom mọi việc kiểm tra vào cuối dự án. |
| S03 tr. 16–17: sơ đồ MOV | Mũi tên từ tầm nhìn/chiến lược đến giá trị đo được rồi mới đến dự án. | Viết chỉ tiêu lợi ích trước khi chọn giải pháp kỹ thuật. |
| S03 tr. 18–24: bản đồ stakeholder và bảng chọn dự án | Các ô/cột là mức ảnh hưởng, lợi ích, trọng số và điểm của từng phương án; số điểm phụ thuộc giả định đầu vào. | Nêu rõ người ra quyết định và lý do của từng trọng số. |
| S03 tr. 51–55: SDLC/Waterfall/iterative | Thứ tự pha của Waterfall khác vòng lặp phản hồi của iterative/incremental. | Chọn mốc bàn giao phù hợp cách phát triển. |
| S06 tr. 26–33: scope statement và cây WBS | WBS phân rã từ đầu ra cấp cao xuống gói công việc; các nhánh cùng cấp cộng thành toàn bộ phạm vi. | Đánh mã, đặt tiêu chí nghiệm thu và owner cho từng gói; tránh bỏ sót và chồng lặp. |
| S08 tr. 17, 28–35: sơ đồ phụ thuộc | Mũi tên thể hiện quan hệ trước/sau; FS/SS/FF/SF khác nhau ở điểm bắt đầu/kết thúc. | Không gán tất cả task nối tiếp nếu chúng có thể song song. |
| S08 tr. 55–58: bảng Function Point | Hàng là loại chức năng, cột là mức độ phức tạp, từng ô = số lượng × trọng số; cộng UAF rồi nhân VAF. | Kiểm tra từng ô, vì bảng ví dụ có một hàng EO ghi sai phép nhân. |
| S08 tr. 67–71, 89–97: PERT/CPM và mạng công việc | PERT dùng ba ước lượng; forward pass cho ES/EF, backward pass cho LS/LF; đường có float bằng 0 là critical path trong ví dụ. | Dự phòng phải xét đường găng, không chỉ cộng ngày tùy ý vào từng task. |
| S05 tr. 20–24: các mức dự toán | Tổng chi phí trực tiếp/gián tiếp, dự phòng rủi ro đã nhận diện, baseline, rồi dự phòng quản lý để thành budget. | Không trộn contingency với management reserve. |
| S05 tr. 34–35: bảng EVM | Cùng một ngày đo PV, EV, AC; CV/SV là hiệu, CPI/SPI là tỉ lệ. | Báo cáo tiền đã tiêu và giá trị hoàn thành riêng. |
| S09 tr. 17–18, 26–32: cơ cấu, RAM, RACI | Sơ đồ tổ chức thể hiện tuyến báo cáo; RAM nối WBS với người/đơn vị; RACI cho mỗi công việc biết ai làm, ai chịu trách nhiệm cuối, ai được hỏi, ai được báo. | PM không phải người thực hiện tất cả deliverable. |
| S09 tr. 46–49: histogram/biểu đồ tăng trưởng nhân sự | Trục thời gian cho biết bao nhiêu người/nhóm kỹ năng cần ở từng kỳ; đường tăng/giảm gắn với nhu cầu công việc. | So nguồn lực theo kỳ, tránh phân việc vượt năng lực. |
| S04 tr. 24–27: ma trận truyền thông | Mỗi hàng nối đối tượng với nội dung, người gửi, thời điểm, kênh và định dạng. | Không dùng cùng một báo cáo cho mọi stakeholder. |
| S07 tr. 29–34, 42–45: ma trận xác suất/tác động và cây quyết định | Ma trận dùng thang thứ bậc để ưu tiên; cây quyết định nhân xác suất thực với kết quả tiền để tính EMV. | Không coi điểm 1/2/4/6 là phần trăm. |
| S12 tr. 11–15: bảng yếu tố rủi ro nghiên cứu | Số ở cột là số lần yếu tố xuất hiện trong dữ liệu nghiên cứu, theo từng lớp và nhóm; các nhóm có tổng khác nhau. | Dùng làm checklist nhận diện, không đưa thẳng vào xác suất dự án. |
| S12 tr. 60–65: risk gắn với WBS/MS Project | Rủi ro được nối với task, có owner, tác động và kế hoạch; ảnh minh họa việc thêm/so sánh tác động lên lịch. | Giữ bản baseline và kịch bản rủi ro tách biệt. |

## 13. Ghép kiến thức thành một kế hoạch và báo cáo dự án

### 13.1. Chuỗi truy vết bắt buộc

Một báo cáo có thể kiểm tra được khi mỗi yêu cầu quan trọng đi qua chuỗi sau:

~~~text
Mục tiêu / MOV → yêu cầu và phạm vi → deliverable → mã WBS
  → hoạt động & quan hệ phụ thuộc → lịch và mốc nghiệm thu
  → người thực hiện / RACI → nguồn lực & ngân sách
  → tiêu chí chất lượng → rủi ro → bằng chứng nghiệm thu
~~~

Nếu một task trong lịch không có deliverable hoặc lý do quản lý tương ứng, xem lại vì có thể là việc ngoài phạm vi. Nếu một deliverable không có người làm, kinh phí hoặc tiêu chí chấp nhận, kế hoạch chưa thực thi được. Đây là **khung tổng hợp áp dụng** từ các chương, không phải một bảng xuất hiện nguyên dạng trong slide. [S03, tr. 16–17, 29–41; S06, tr. 24–33; S08, tr. 8–20; S09, tr. 26–32; S07, tr. 35–38]

### 13.2. Bộ tài liệu tối thiểu và cổng kiểm tra

| Thời điểm | Tài liệu / bằng chứng | Người dẫn dắt và điểm kiểm tra |
|---|---|---|
| Khởi tạo | Bối cảnh, business case, MOV, charter, stakeholder list | Sponsor duyệt lý do và thẩm quyền; PM xác nhận mục tiêu/giới hạn. |
| Lập kế hoạch | Scope statement, WBS/dictionary, schedule, cost baseline, org chart, RAM/RACI, communication plan, risk register, tiêu chí nghiệm thu | Lead chuyên môn ước lượng phần mình; PM tích hợp; sponsor/khách hàng duyệt baseline theo thẩm quyền. |
| Thực hiện | Deliverable, bản dựng, dữ liệu, tài liệu kỹ thuật, biên bản họp và quyết định | Owner từng gói tạo bằng chứng; PM theo dõi và gỡ phụ thuộc. |
| Kiểm soát | So sánh actual với baseline, EVM nếu phù hợp, log thay đổi, issue/risk log, kết quả kiểm thử | Chủ thay đổi đánh giá tác động phạm vi/lịch/chi phí/chất lượng trước phê duyệt. |
| Kết thúc | Biên bản nghiệm thu, bàn giao, hướng dẫn vận hành, quyết toán, bài học kinh nghiệm, đo MOV sau triển khai | Người nhận xác nhận; sponsor chấp thuận đóng/chuyển giai đoạn. |

Hai hàng cuối là **gợi ý thực hành tổng hợp**, vì bộ PDF không có chuyên đề riêng đầy đủ cho kiểm soát và đóng dự án. [S01, tr. 4–10; S02, tr. 21–25; S05, tr. 28–35]

### 13.3. Phân bổ việc và thời gian cho từng người

Mỗi gói WBS nên có **một owner chịu trách nhiệm điều phối giao phẩm**, người thực hiện kỹ thuật có thể là một hoặc nhiều người. Tính workload theo **effort** (giờ/ngày công), rồi phân theo kỹ năng, sức chứa ở từng tuần và các quan hệ phụ thuộc. **Duration** của gói việc là số ngày trên lịch; cộng duration của mọi gói để chia đều cho thành viên sẽ sai nếu có việc song song, nghỉ, chờ duyệt hoặc nhiều người cùng làm. [S08, tr. 37–47; S09, tr. 24–32, 46–49]

Nếu bài tập yêu cầu một mô hình phân bổ **giả định** để trình bày công bằng, ghi rõ giả định, tổng effort và công thức chia. Không ghi số giả định là *actual* hay dựng lại nhật ký làm việc như dữ kiện đã quan sát. Có thể chia đều tổng effort mục tiêu cho N người rồi điều chỉnh từng gói theo chuyên môn, sau đó báo phần sai lệch giữa các thành viên; PM vẫn giữ việc điều phối, tích hợp và ra quyết định trong thẩm quyền, không nhận tất cả task kỹ thuật. Đây là cách diễn giải nhất quán giữa WBS, RACI và biểu đồ nguồn lực. [S06, tr. 26–33; S08, tr. 37–47; S09, tr. 26–32, 46–49]

## 14. Bảng công thức và quy tắc tra cứu nhanh

| Chủ đề | Công thức / quy tắc | Cách dùng và lưu ý |
|---|---|---|
| Kênh truyền thông | `n(n−1)/2` | Số cặp liên hệ tiềm năng của n người, không phải số kênh phải dùng. [S04, tr. 14–16] |
| NPV | `Σ CF_t/(1+r)^t − I_0` | CF ở cùng đơn vị tiền và r theo cùng kỳ. [S03, tr. 25–27] |
| ROI đơn giản | `(Lợi ích − Chi phí)/Chi phí × 100%` | Xác định rõ kỳ tính và loại chi phí/lợi ích. [S03, tr. 28–29] |
| PERT | `ET = (O + 4M + P)/6` | Ba ước lượng lạc quan, khả dĩ, bi quan; thời gian kỳ vọng không bảo đảm hạn hoàn thành. [S08, tr. 66–71] |
| PERT variance | `((P−O)/6)^2` | Dùng khi giả định PERT phù hợp; phương sai đường đi là tổng phương sai task trên đường nếu giả định độc lập. [S08, tr. 66–71] |
| CPM | `EF=ES+d`; `LS=LF−d`; `TF=LS−ES=LF−EF` | Forward pass: ES bằng EF lớn nhất của tiền nhiệm; backward pass: LF bằng LS nhỏ nhất của kế nhiệm. [S08, tr. 89–97] |
| Function Point | `UAF=Σ(số chức năng×trọng số)`; `VAF=0,65+0,01×TDI`; `FP=UAF×VAF` | Theo bộ trọng số/thang hiệu chỉnh trong slide, không mặc định cho mọi phương pháp FP hiện hành. [S08, tr. 55–58] |
| Cost variance | `CV=EV−AC` | Âm: giá trị hoàn thành thấp hơn chi phí đã chi. [S05, tr. 28–35] |
| Schedule variance | `SV=EV−PV` | Âm: giá trị hoàn thành thấp hơn kế hoạch tại ngày đo; đơn vị là tiền, không phải ngày. [S05, tr. 28–35] |
| Cost performance | `CPI=EV/AC` | Dưới 1: vượt chi so với giá trị hoàn thành. [S05, tr. 28–35] |
| Schedule performance | `SPI=EV/PV` | Dưới 1: chậm so với kế hoạch theo thước đo EV. [S05, tr. 28–35] |
| Dự báo EAC | `EAC=BAC/CPI` | Một giả định: hiệu suất chi phí hiện tại tiếp tục cho phần còn lại; có công thức khác nếu giả định thay đổi. [S05, tr. 34–35] |
| EMV | `Σ p_i×x_i` | Chỉ dùng khi các nhánh loại trừ nhau, xác suất là xác suất thực và tổng bằng 1. [S07, tr. 42–44] |
| RACI | Mỗi hoạt động có 1 A; ≥1 R; C/I theo nhu cầu | Phân biệt R làm việc và A chịu trách nhiệm cuối/phê duyệt. [S09, tr. 27–32] |

## 15. Các điểm chưa khớp hoặc cần hiểu thận trọng trong nguồn

| Nguồn | Quan sát khi đối chiếu chữ, bảng/hình và phép tính | Cách dùng trong bản tổng hợp |
|---|---|---|
| S08 tr. 56 | Hàng **EO** của bảng Function Point có phép nhân ở ô không khớp trọng số và tổng 33 của hàng. | Dùng trọng số được giới thiệu ở tr. 55 cùng số lượng chức năng để tính lại **EO=33**, từ đó UAF=200, VAF=1,05, FP=210. [S08, tr. 55–58] |
| S08 tr. 72 | Slide viết `140/(1−0,45)=280`, nhưng phép chia cho **0,55** cho kết quả khoảng **254,55**. | Ghi kết quả số học đúng; không dùng 280 làm đầu vào lịch. |
| S08 tr. 97 | Công thức backward pass in **LF của công việc = min LF của công việc kế nhiệm**. | Dùng quy tắc chuẩn của mạng công việc: **LF = min LS của các kế nhiệm**; đối chiếu mạng và đường găng ở các trang trước. [S08, tr. 89–97] |
| S05 tr. 36 | Câu mô tả **CPI = 1** như “on schedule”. | CPI phản ánh **chi phí**; SPI phản ánh **tiến độ** theo EVM. [S05, tr. 28–35] |
| S04 tr. 7–9 | Tiêu đề slide ghi “quality management”, nhưng nội dung là các bước quản lý truyền thông. | Xếp vào phần truyền thông theo nội dung, không vào chất lượng. |
| S04 tr. 30 | Tỷ lệ giao tiếp 58/35/7 được nêu như quy tắc chung. | Không dùng tỷ lệ này để dự báo kết quả truyền thông dự án. |
| S07 tr. 31–34 | Thang điểm định tính có nhãn lặp/không nhất quán ở một số mức; 1/2/4/6 là thang ưu tiên. | Dùng định nghĩa mức do dự án tự công bố; không coi điểm là xác suất thực. |
| S09 tr. 29 so với tr. 30–32 | Một hình dùng ký tự A/P/R/I/S với nghĩa riêng; trong đó R có thể là **Review Required**, khác R=Responsible của RACI. | Đọc chú giải của từng ma trận; khi lập RACI dùng một bộ ký hiệu R/A/C/I nhất quán. |
| S12 tr. 11–15 | Bảng cho số lần xuất hiện trong một nghiên cứu được slide trích. | Xem là dữ liệu tham khảo để nhận diện rủi ro, không chuyển thành tỷ lệ xảy ra trong dự án hiện tại. |
| S12 tr. 60–65 | Ví dụ điều chỉnh thời gian/chi phí task để thể hiện tác động rủi ro. | Lưu như kịch bản hoặc thay đổi được duyệt; phân biệt baseline, forecast và actual. |

**Phạm vi kiểm chứng:** các phép tính trên được tính lại từ số liệu xuất hiện trong PDF; tài liệu này không kiểm chứng độc lập các nghiên cứu, con số thị trường hay ấn bản tiêu chuẩn mà slide dẫn. Thuật ngữ và công thức được giải thích để học và áp dụng cho bài tập; khi tổ chức có quy trình riêng, dùng quy trình được phê duyệt của tổ chức.

## 16. Lộ trình ôn tập và áp dụng

1. **Đọc nền tảng:** mục 1–3 để phân biệt mục tiêu kinh doanh, dự án và cách phát triển sản phẩm. Tự viết một business case ngắn và chỉ rõ MOV. [S02–S03]
2. **Lập kế hoạch tích hợp:** mục 4–8; từ deliverable dựng WBS, hoạt động, lịch, ước lượng và RACI; kiểm tra mỗi gói đều có người và tiêu chí hoàn thành. [S05–S06, S08–S09]
3. **Điều hành nhóm:** mục 9–10; lập ma trận truyền thông và risk register gắn mã WBS; chọn kênh và người nhận theo quyết định cần đưa ra. [S04, S07, S12]
4. **Kiểm soát và điều chỉnh:** tính EV/PV/AC tại cùng một ngày, đối chiếu lịch/chi phí với baseline; đánh giá thay đổi và rủi ro trước khi sửa kế hoạch. [S05, S07–S08]
5. **Chọn cách làm hiện đại phù hợp:** dùng mục 11 để cân nhắc Agile/Lean, phối hợp từ xa và AI; ghi rõ giả định và người kiểm tra kết quả. [S10–S11]

Khi viết báo cáo học phần, dùng **mục 13 làm checklist liên kết**, **mục 14 để tra công thức** và **mục 15 để tránh lặp lỗi từ slide**. Các bảng ví dụ trong bản tổng hợp là mẫu để điều chỉnh theo dự án cụ thể, không thay cho dữ liệu, thẩm quyền phê duyệt và minh chứng thật của dự án.
