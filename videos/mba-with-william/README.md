# MBA English with William

Series video dọc 9:16: nhân vật **William** (~35 tuổi, giọng Anh-Mỹ) đứng trên sân khấu, mỗi tập nói đúng **6 câu** về một chủ đề MBA, kèm phụ đề tiếng Anh tô sáng từng từ.

## Thêm một tập mới

1. Tạo `series/day-XX.json` (copy từ `day-02.json`), sửa `day`, `topic`, `subtitle` và 6 câu trong `sentences`.
2. Tạo giọng đọc và composition:
   ```bash
   node scripts/make-episode.mjs XX
   ```
3. Kiểm tra và render:
   ```bash
   npx hyperframes check
   npx hyperframes render -q delivery -o renders/william-mba-day-XX.mp4
   ```

Giọng đọc dùng Kokoro (`am_michael`, tốc độ 1.08 + xử lý âm thanh cho giọng sáng và rõ), chạy offline. Lần đầu cần cài:
`uv venv ~/.venvs/kokoro && VIRTUAL_ENV=~/.venvs/kokoro uv pip install kokoro-onnx soundfile`.

## Cấu trúc

- `series/` — kịch bản từng ngày (JSON)
- `scripts/template.html` — sân khấu + nhân vật William (SVG) + phụ đề; **sửa giao diện ở đây**
- `scripts/make-episode.mjs` — TTS → ghép câu → nhạc nền (tự nhỏ khi William nói) → khẩu hình → thời gian từng từ → sinh `index.html`
- `scripts/make-bgm.py` — tạo nhạc nền 118 BPM (không bản quyền); chỉnh mức nhạc bằng `MUSIC_DB` trong make-episode.mjs
- `index.html` — composition của tập vừa build (tự sinh, không sửa tay)
- `renders/` — video đã xuất

## Lộ trình chủ đề gợi ý

| Ngày | Chủ đề |
| --- | --- |
| 1 | Strategic Leadership |
| 2 | Competitive Advantage |
| 3 | SWOT Analysis |
| 4 | Market Segmentation |
| 5 | Value Proposition |
| 6 | Financial Statements |
| 7 | Cash Flow Management |
| 8 | Supply Chain Management |
| 9 | Change Management |
| 10 | Corporate Social Responsibility |
