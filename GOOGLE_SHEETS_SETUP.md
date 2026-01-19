# Google Sheets API 設定說明

## 步驟1: 建立 Google Cloud 專案和啟用 API

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Sheets API：
   - 在左側選單中選擇「API 和服務」>「程式庫」
   - 搜尋 "Google Sheets API"
   - 點擊並啟用

## 步驟2: 建立服務帳戶

1. 在 Google Cloud Console 中，前往「API 和服務」>「憑證」
2. 點擊「建立憑證」>「服務帳戶」
3. 輸入服務帳戶名稱和描述
4. 點擊「建立並繼續」
5. 授予角色：「基本」>「檢視者」（或根據需求選擇）
6. 點擊「完成」

## 步驟3: 下載 JSON 金鑰檔案

1. 在憑證頁面中，找到剛建立的服務帳戶
2. 點擊服務帳戶電子郵件
3. 前往「金鑰」標籤
4. 點擊「新增金鑰」>「建立新金鑰」
5. 選擇 JSON 格式
6. 下載檔案並重新命名為 `google_sheets_credentials.json`
7. 將檔案放在專案根目錄

## 步驟4: 分享 Google Sheet 給服務帳戶

1. 開啟您的 Google Sheet
2. 點擊右上角的「共用」按鈕
3. 將服務帳戶的電子郵件地址加入編輯者（從 JSON 檔案中的 "client_email" 欄位取得）
4. 設定權限為「檢視者」

## 範例 credentials 檔案結構：

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

## 替代方案：公開分享

如果不想設定 API 憑證，也可以將 Google Sheet 設為公開：

1. 開啟 Google Sheet
2. 點擊「共用」
3. 將存取權限改為「知道連結的任何人都可以檢視」
4. 確保不是選擇「受限制」

程式會先嘗試使用 API 憑證，如果沒有憑證則會回退到 CSV 匯出方法。