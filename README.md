# Đánh giá tiềm năng NST — Team VN

Ứng dụng chấm điểm ứng viên/NST theo bộ tiêu chí nội bộ của **Team VN**
(mỗi câu 1–5 điểm), tự động phân loại kết quả và lưu vào kho dữ liệu.

Đây là bản tách riêng chỉ dành cho Team VN (không còn bước chọn team).
Nếu cần chỉnh lại tiêu chí Team VN, xem repo riêng `nst-scoring-vn`.

Đầu trang có 3 trường bắt buộc: **ID/Tên TikToker**, **Agency**, **Người chấm**.
Mọi lượt chấm sau khi bấm "Gửi kết quả" sẽ được lưu thành 1 dòng trong kho
dữ liệu (xem/tải lại được ngay trong app, mục **🗂️ Kho dữ liệu** ở cuối trang).

Team VN chấm theo 3 tuyến nội dung (NPC / Music / Beauty, mỗi tuyến tối đa
25 điểm) và đưa ra đề xuất ngách dựa trên tương quan điểm giữa các tuyến:

| Tình huống điểm | Kết luận & hành động |
|---|---|
| Một tuyến ≥ 18 điểm và cách tuyến thứ hai ≥ 4 điểm | **Ngách rõ nét**: kích hoạt ngay Playbook chuyên sâu của tuyến đó. |
| Hai tuyến chênh nhau ≤ 3 điểm | **Ngách kép**: chọn tuyến chi phí vận hành thấp hơn làm chính (ưu tiên: NPC > Beauty > Music), tuyến còn lại là "gia vị". |
| Cả 3 tuyến < 12 điểm | **Thiếu nền tảng**: đưa vào chuỗi NPC Basic (2 tuần) rồi đánh giá lại. |
| Nhóm Music cao nhưng câu B5 ≤ 3 | **Cảnh báo thiếu kỷ luật** lịch LIVE. |
| Nhóm Beauty cao nhưng câu C4 ≤ 3 | **Chệch trọng tâm**: thiếu Fan-service. |

Toàn bộ ngưỡng này (18, 4, 3, 12...) chỉnh được trong `config.json`, mục
`teams.VN.lane_analysis`.

Toàn bộ câu hỏi, thang điểm và ngưỡng phân loại có thể chỉnh trong
`config.json` — **không cần sửa code**.

## Cấu trúc project

```
nst-scoring-vn/
├── app.py            # Giao diện + logic chấm điểm (Streamlit)
├── storage.py         # Xử lý lưu kết quả (CSV local + đồng bộ Hugging Face Dataset)
├── config.json         # Câu hỏi, thang điểm, ngưỡng phân loại (chỉnh ở đây)
├── requirements.txt    # Thư viện cần thiết
└── README.md
```

## Chạy thử ở máy local

```bash
pip install -r requirements.txt
streamlit run app.py
```

Mở trình duyệt tại `http://localhost:8501`.

---

## ⚠️ Lưu ý quan trọng về deploy (đọc trước khi làm)

Hugging Face gần đây đã đổi chính sách: **Space chạy code (Docker — đây là
loại dùng cho Streamlit — hoặc Gradio) giờ yêu cầu gói trả phí** (HF PRO
~9 USD/tháng cho cá nhân). Chỉ Space "Static" (HTML/JS thuần) là miễn phí,
mà Static thì không chạy được Python/Streamlit.

➡️ Vì bạn cần **miễn phí và tốt nhất**, tôi khuyến nghị dùng
**Streamlit Community Cloud** (`share.streamlit.io`) — nền tảng chính chủ
của Streamlit, **miễn phí thật sự**, không cần đổi 1 dòng code nào trong
app này. Phần lưu kho dữ liệu lên Hugging Face Dataset (để dữ liệu không
mất khi app khởi động lại) vẫn hoạt động bình thường dù app chạy ở đâu,
vì nó chỉ gọi API của Hugging Face, không phụ thuộc nơi host.

Nếu bạn vẫn muốn host trên chính Hugging Face, xem mục "Phương án 2" ở cuối.

---

## PHƯƠNG ÁN 1 (khuyến nghị) — Deploy miễn phí lên Streamlit Community Cloud

### Bước 1 — Đưa code lên GitHub (miễn phí)

1. Tạo tài khoản tại https://github.com nếu chưa có.
2. Bấm **New repository**, đặt tên (vd `nst-scoring-vn`), chọn **Public**
   hoặc **Private** đều được, bấm **Create repository**.
3. Bấm **uploading an existing file**, kéo thả 4 file: `app.py`, `storage.py`,
   `config.json`, `requirements.txt` lên, bấm **Commit changes**.

### Bước 2 — Deploy lên Streamlit Community Cloud

1. Vào https://share.streamlit.io, bấm **Sign up** / **Continue with GitHub**
   (đăng nhập bằng chính tài khoản GitHub ở Bước 1) — hoàn toàn miễn phí.
2. Bấm **Create app** → chọn **"Yup, I have an app"**.
3. Chọn đúng repository, branch (`main`), và file chính là `app.py`.
4. Ở màn hình này bấm **"Advanced settings"** và chọn **Python 3.11** hoặc
   **3.12** trước khi Deploy (tránh lỗi build do Streamlit Cloud đôi khi
   tự chọn bản Python quá mới, chưa có sẵn wheel cho các thư viện trong
   `requirements.txt`).
5. (Tuỳ chọn) đặt tên miền phụ riêng ở mục "App URL", ví dụ
   `nst-scoring-vn.streamlit.app`.
6. Bấm **Deploy**. Sau ~1–2 phút app sẽ chạy tại URL dạng
   `https://<ten-app>.streamlit.app`.

### Bước 3 — (Khuyến nghị) Bật lưu kho dữ liệu vĩnh viễn qua Hugging Face Dataset

Mặc định app chỉ lưu CSV tạm trên máy chủ Streamlit Cloud (có thể mất khi
app "ngủ" và khởi động lại sau thời gian dài không ai truy cập). Để dữ liệu
không bao giờ mất, làm 4 bước sau (chỉ 1 lần):

1. Tạo Dataset repo trên Hugging Face: vào https://huggingface.co/new-dataset,
   đặt tên vd `nst-scoring-results-vn` (đuôi `-us` để không trùng/lẫn với
   dữ liệu của Team VN), chọn **Private**, **Create dataset**.
   Ghi nhớ đường dẫn `<ten-user>/nst-scoring-results-vn`.
2. Tạo Access Token: vào https://huggingface.co/settings/tokens → **New token**
   → quyền **Write** → **Create token** → copy lại.
3. Quay lại app trên Streamlit Cloud → vào **Manage app** (góc dưới phải khi
   đang xem app) → **Settings** → **Secrets**.
4. Dán nội dung sau vào ô Secrets (thay giá trị thật của bạn), rồi **Save**:

   ```toml
   HF_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxxxxx"
   HF_DATASET_REPO = "ten-user/nst-scoring-results-vn"
   ```

App sẽ tự khởi động lại. Từ giờ mỗi lần "Gửi kết quả", dữ liệu vừa lưu local
vừa tự động đẩy lên Dataset repo này — xem lại bất cứ lúc nào tại
`https://huggingface.co/datasets/<ten-user>/nst-scoring-results-vn`, kể cả khi
app trên Streamlit Cloud bị restart.

**Giới hạn của gói miễn phí Streamlit Community Cloud** (đủ dùng cho tuyển
dụng nội bộ, không cần lo): ~1 GB RAM, app tự "ngủ" nếu không ai truy cập
trong 12 giờ (mở lại thì tự thức dậy sau vài giây), không giới hạn số app
public, tối đa 1 app private.

---

## PHƯƠNG ÁN 2 — Vẫn muốn host trên chính Hugging Face Spaces

Chấp nhận trả phí HF PRO (~9 USD/tháng):

1. Nâng cấp tài khoản tại https://huggingface.co/pricing (chọn PRO).
2. Vào https://huggingface.co/new-space, đặt tên Space.
3. Ở màn hình chọn SDK, bấm vào ô **Docker** (dù bạn dùng Streamlit — kể từ
   khi HF gộp Streamlit vào nhóm template Docker) → trong danh sách 17
   template hiện ra, chọn **Streamlit**.
4. Upload 4 file `app.py`, `storage.py`, `config.json`, `requirements.txt`
   vào tab **Files**.
5. Vào **Settings → Variables and secrets** của Space, thêm:
   - Secret `HF_TOKEN` = access token quyền Write (tạo tại
     https://huggingface.co/settings/tokens).
   - Variable `HF_DATASET_REPO` = `<ten-user>/nst-scoring-results-vn` (tạo
     dataset repo như Bước 3 ở Phương án 1).
6. Space tự build và chạy tại `https://huggingface.co/spaces/<ten-user>/<ten-space>`.

---

## Tuỳ chỉnh thêm

- **Thêm/bớt câu hỏi hoặc nhóm câu hỏi:** sửa mảng `groups` trong `config.json`.
- **Đổi ngưỡng phân loại:** sửa mảng `classification.bands` trong `config.json`.
- **Đổi màu từng nhóm:** sửa trường `color` (mã hex) trong từng group.
- **Xem/tải kho dữ liệu:** mục "🗂️ Kho dữ liệu" ở cuối trang app, có nút tải
  CSV về máy bất cứ lúc nào.
