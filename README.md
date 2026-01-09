# Garmin Import Plan

這是一個反向工程工具，用於將 Google Sheet 或 Excel/CSV 格式的教練訓練菜單自動匯入至 Garmin Connect。

## 功能

- [x] **單日匯入**: 支援一次解析一個 `Day X` 區塊。
- [x] **批量匯入**: 自動掃描並匯入檔案中所有的 `Day` 區塊。
- [x] **Google Sheet 整合**: 直接讀取公開或有權限的 Google Sheet 網址。
- [x] **複雜語法解析**:
    - 支援 `8,7,6,6` 此類遞減組數自動拆分為多個 Garmin 步驟。
    - 支援 `25+2.3` 等重量算式解析。
    - 支援 `自身` 關鍵字（解析為 0kg）。
- [x] **重複檢測**: 匯入前檢查是否已有同名訓練，避免重複建立。

## 快速開始

請參閱 [specs/001-import-gsheet-workout/quickstart.md](specs/001-import-gsheet-workout/quickstart.md) 了解詳細的使用方式與檔案格式規範。

## 執行範例

```bash
# 匯入本地檔案
python -m src.cli.main ./my_plan.xlsx --email user@example.com

# 匯入 Google Sheet
python -m src.cli.main "https://docs.google.com/spreadsheets/d/..." --email user@example.com
```

## 開發

本專案使用 `garth` 處理 Garmin SSO 驗證。

測試：
```bash
pytest tests/
```
