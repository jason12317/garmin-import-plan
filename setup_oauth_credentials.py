#!/usr/bin/env python3
"""
設定 OAuth2 憑證的輔助工具
這個腳本會指導您如何設定 OAuth2 認證來使用您的個人 Google 帳號存取 Google Sheets
"""

import json
import os

def create_oauth_credentials():
    """創建 OAuth2 憑證檔案"""
    
    print("=== Google Sheets OAuth2 設定指南 ===\n")
    
    print("請按照以下步驟設定 OAuth2 認證：")
    print("\n1. 前往 Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    
    print("\n2. 選擇您的專案 (marine-lacing-323805)")
    
    print("\n3. 前往「API 和服務」>「憑證」")
    
    print("\n4. 點選「建立憑證」>「OAuth 用戶端 ID」")
    
    print("\n5. 應用程式類型選擇「桌面應用程式」")
    
    print("\n6. 輸入名稱，例如 'Garmin Workout Importer - Desktop'")
    
    print("\n7. 點選「建立」")
    
    print("\n8. 下載 JSON 憑證檔案")
    
    print("\n9. 將下載的檔案重新命名為 'google_sheets_oauth_credentials.json'")
    
    print("\n10. 將檔案放置在專案根目錄")
    
    print("\n完成後，執行以下指令測試:")
    print("python3 -m src.cli.main \"您的Google Sheets URL\" --email jason12317@gmail.com")
    
    print("\n程式會自動開啟瀏覽器進行 Google 帳號認證。")
    
    # 創建範本檔案
    oauth_template = {
        "installed": {
            "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
            "project_id": "marine-lacing-323805", 
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "YOUR_CLIENT_SECRET",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
        }
    }
    
    template_file = "google_sheets_oauth_credentials.json.template"
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(oauth_template, f, indent=2, ensure_ascii=False)
    
    print(f"\n已創建範本檔案: {template_file}")
    print("請將實際的 client_id 和 client_secret 填入正確的憑證檔案中。")

if __name__ == "__main__":
    create_oauth_credentials()