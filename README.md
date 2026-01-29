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

python3 -m src.cli.main "https://docs.google.com/spreadsheets/d/1eTW7OSs0pNerj8XujtU9RgLzGZ0JP1CTEs24i6bBwms/edit?gid=1615008567#gid=1615008567" --email jason12317@gmail.com --day Day3

```

## Web App (Streamlit)

本專案提供圖形化網頁介面，方便手機或非技術人員使用。

### 本地執行

```bash
# 啟動 Streamlit
streamlit run app.py
```

### 雲端部署 (Streamlit Cloud)

若要部署至免費的 [Streamlit Cloud](https://streamlit.io/cloud)，請遵循以下資安設定，**切勿上傳 token json 檔案至 GitHub**。

#### 1. 準備環境變數

在 Streamlit Cloud 的 "Advanced Settings" -> "Secrets" 區域，貼上您的憑證內容。支援以下變數：

**A. Google Sheets User Token** (推薦，個人權限)
變數名稱: `GOOGLE_SHEETS_TOKEN_JSON`
內容: 複製本地 `google_sheets_token.json` 的全部內容。

**B. Google Service Account** (備用)
變數名稱: `GOOGLE_SHEETS_CREDENTIALS_JSON`
內容: 複製本地 `google_sheets_credentials.json` 的全部內容。

**C. Garmin 帳密預設值** (可選，方便登入)
```toml
GARMIN_EMAIL = "your_email@example.com"
GARMIN_PASSWORD = "your_password"
```

#### 2. 注意事項
- 專案已設定 `.gitignore` 忽略所有 `*.json` 與 `.streamlit/secrets.toml`，確保憑證不進版控。
- 程式會優先讀取環境變數，若無環境變數才會嘗試讀取本地檔案。

## 開發

本專案使用 `garth` 處理 Garmin SSO 驗證。

測試：
```bash
pytest tests/
```
