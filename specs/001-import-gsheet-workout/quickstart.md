# Garmin Import Plan 快速開始

## 前置需求

- Python 3.10+
- Garmin Connect 帳號 (Email/Password)
- 一個符合規範的訓練計畫 CSV/Excel 檔案 或 Google Sheet 連結

## 安裝

```bash
git clone ...
cd garmin-import-plan
pip install -r requirements.txt
```

## 使用方式

### 1. 準備輸入檔案

檔案格式必須符合教練菜單規範：
- 使用 `Day X` 作為區塊標題
- 包含列標題：`動作`, `組數`, `重量`, `次數`
- 支援複雜次數如 `"8,7,6,6"` 或 `8-12`
- 支援算式重量如 `25+2.3` 或 `自身`

範例 CSV:
```csv
Day 1
Day 1 - Chest Day
動作,組數,重量,次數
深蹲,4,100,5
```

### 2. 執行匯入

單一檔案匯入 (批量處理所有 Day):
```bash
python -m src.cli.main path/to/plan.csv --email YOUR_EMAIL
```

指定特定 Day 匯入:
```bash
python -m src.cli.main path/to/plan.csv --day "Day 1" --email YOUR_EMAIL
```

使用 Google Sheet 連結 (公開或有權限):
```bash
python -m src.cli.main "https://docs.google.com/spreadsheets/d/KEY/edit" --email YOUR_EMAIL
```

### 3. 排難解疑

- **重複匯入**: 預設會跳過名稱相同的訓練。使用 `--force` 參數強制建立副本。
- **認證失敗**: 請確認 Email/Password 正確。支援 MFA 嗎？目前 Garth 處理基礎 MFA 提示，CLI 可能需要互動。
- **格式錯誤**: 檢查 CSV 是否有正確的標題行。

## 開發者

執行測試:
```bash
pytest tests/
```
