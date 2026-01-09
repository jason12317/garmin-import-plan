# garmin-import-plan 開發指南

自動生成自所有功能計畫。最後更新日期：2026-01-08

## 使用技術

[從所有 PLAN.MD 文件中提取]

## 項目結構

```text
[來自計畫的實際結構]
```

## 指令

[僅包含活躍技術的指令]

## 代碼風格

[語言特定，僅適用於正在使用的語言]

## 最近變更

[最後 3 個功能及其內容]

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

## Active Technologies
- Python 3.10+ + `garth` (身份驗證), `pandas` & `openpyxl` (資料解析), `requests` (API 調用), `google-auth` & `google-api-python-client` (Google Sheet 讀取) (001-import-gsheet-workout)
- 本地會話快取 (由 Garth 管理), 無需額外數據庫 (001-import-gsheet-workout)
- Python 3.10+ + `garth` (身份驗證), `pandas`, `openpyxl`, `requests`, `pydantic` (001-import-gsheet-workout)

## Recent Changes
- 001-import-gsheet-workout: Added Python 3.10+ + `garth` (身份驗證), `pandas` & `openpyxl` (資料解析), `requests` (API 調用), `google-auth` & `google-api-python-client` (Google Sheet 讀取)
