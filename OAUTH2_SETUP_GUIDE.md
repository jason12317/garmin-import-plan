# OAuth2 桌面應用程式憑證設定詳細步驟

## 📋 完整設定流程

### 步驟 1：前往 Google Cloud Console
1. 開啟瀏覽器前往：https://console.cloud.google.com/
2. 使用您的 Google 帳號（jason12317@gmail.com）登入

### 步驟 2：選擇專案
1. 在頁面頂部的專案選擇器中，點選下拉選單
2. 選擇專案：**marine-lacing-323805**
   - 如果看不到此專案，請確認您已經被授權存取

### 步驟 3：啟用 Google Sheets API（如果未啟用）
1. 在左側選單中點選 **「API 和服務」** > **「程式庫」**
2. 在搜尋框中輸入：`Google Sheets API`
3. 點選 **「Google Sheets API」**
4. 如果尚未啟用，點選 **「啟用」** 按鈕

### 步驟 4：設定 OAuth 同意畫面（首次設定需要）
1. 在左側選單中點選 **「API 和服務」** > **「OAuth 同意畫面」**
2. 選擇 **「外部」**（因為是個人使用）
3. 點選 **「建立」**
4. 填寫必要資訊：
   - **應用程式名稱**：`Garmin Workout Importer`
   - **使用者支援電子郵件**：選擇您的 email
   - **開發人員聯絡資訊**：輸入您的 email
5. 點選 **「儲存並繼續」**
6. 在 **「範圍」** 頁面，點選 **「新增或移除範圍」**
7. 搜尋並選擇：`https://www.googleapis.com/auth/spreadsheets.readonly`
8. 點選 **「更新」** > **「儲存並繼續」**
9. 在 **「測試使用者」** 頁面，點選 **「新增使用者」**
10. 輸入您的 email：`jason12317@gmail.com`
11. 點選 **「儲存並繼續」**

### 步驟 5：建立 OAuth2 用戶端 ID
1. 在左側選單中點選 **「API 和服務」** > **「憑證」**
2. 點選頁面頂部的 **「建立憑證」**
3. 選擇 **「OAuth 用戶端 ID」**

### 步驟 6：設定應用程式類型
1. **應用程式類型**：選擇 **「桌面應用程式」**
2. **名稱**：輸入 `Garmin Workout Importer - Desktop`
3. 點選 **「建立」**

### 步驟 7：下載憑證
1. 在彈出的對話框中，點選 **「下載 JSON」**
2. 將下載的檔案儲存到您的電腦

### 步驟 8：設定憑證檔案
1. 找到剛下載的 JSON 檔案（通常命名類似 `client_secret_xxx.apps.googleusercontent.com.json`）
2. 將檔案重新命名為：`google_sheets_oauth_credentials.json`
3. 將檔案移動到專案根目錄：
   ```
   /Users/Jason/IdeaProjects/try/garmin/garmin-import-plan/google_sheets_oauth_credentials.json
   ```

### 步驟 9：驗證檔案結構
您的 OAuth2 憑證檔案應該看起來像這樣：
```json
{
  "installed": {
    "client_id": "xxxxx.apps.googleusercontent.com",
    "project_id": "marine-lacing-323805",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-xxxxx",
    "redirect_uris": ["http://localhost"]
  }
}
```

## 🧪 測試設定

完成上述步驟後，執行以下指令測試：

```bash
python3 -m src.cli.main "https://docs.google.com/spreadsheets/d/1eTW7OSs0pNerj8XujtU9RgLzGZ0JP1CTEs24i6bBwms/edit?gid=2084313299#gid=2084313299" --email jason12317@gmail.com
```

## 🔐 首次認證流程

第一次執行時，程式會：

1. **顯示認證網址**：程式會顯示一個 Google 認證網址
2. **開啟瀏覽器**：複製網址到瀏覽器中開啟
3. **Google 登入**：使用您的 `jason12317@gmail.com` 登入
4. **授權應用程式**：點選「允許」授權程式存取 Google Sheets
5. **複製授權碼**：Google 會顯示一個授權碼
6. **貼回程式**：將授權碼貼到終端機的提示中

## 📁 最終專案結構

設定完成後，您的專案應該包含：

```
garmin-import-plan/
├── google_sheets_credentials.json          # 服務帳戶憑證（已存在）
├── google_sheets_oauth_credentials.json    # OAuth2 憑證（新增）
├── google_sheets_token.json               # OAuth2 token（自動生成）
├── pyproject.toml
└── ...
```

## ⚡ 重要提醒

- OAuth2 憑證設定完成後，您就能直接使用自己的 Google 帳號存取所有有權限的 Google Sheets
- 不需要手動分享試算表給服務帳戶
- 認證 token 會自動儲存，下次使用不需要重新登入
- 所有憑證檔案已加入 `.gitignore`，不會被意外提交

準備好設定了嗎？🚀