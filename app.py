import streamlit as st
import os
import sys
import os

# Add the project root directory to the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from src.core.auth import GarminAuth
from src.core.parser import WorkoutParser
from src.core.garmin_client import GarminClient
from src.utils.logger import setup_logger

# 設定 Streamlit 頁面
st.set_page_config(page_title="Garmin 課表匯入工具", page_icon="🏃")

# 設定 Logger
logger = setup_logger(__name__)

# CSS 樣式優化
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #0078D7;
        color: white;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🏃 Garmin 課表匯入工具")
    st.markdown("將 Google Sheet 課表匯入至 Garmin Connect")

    # 側邊欄：帳號設定
    with st.sidebar:
        st.header("🔐 帳號設定")
        
        # 嘗試從 Secrets 或環境變數讀取預設值
        default_email = os.getenv("GARMIN_EMAIL") or (st.secrets["GARMIN_EMAIL"] if "GARMIN_EMAIL" in st.secrets else "")
        default_password = os.getenv("GARMIN_PASSWORD") or (st.secrets["GARMIN_PASSWORD"] if "GARMIN_PASSWORD" in st.secrets else "")

        email = st.text_input("Garmin Email", value=default_email)
        password = st.text_input("Garmin Password", value=default_password, type="password")
        
        st.info("您的帳號密碼僅用於本次連線，不會被儲存。")
        
        st.divider()
        st.markdown("### 關於")
        st.markdown("此工具協助您將教練安排的 Google Sheet 課表快速匯入 Garmin 手錶。")

    # 主畫面：匯入設定
    col1, col2 = st.columns([3, 1])
    
    with col1:
        sheet_url = st.text_input(
            "Google Sheet 網址", 
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="請貼上包含課表的 Google Sheet 完整網址"
        )
    
    with col2:
         day_input = st.text_input(
            "今天是哪一天？", 
            value="Day1",
            placeholder="Day1, Day2...",
            help="對應 Excel 表格中的標籤名稱，例如 'Day 1' 或 'Day1'"
        )

    force_import = st.checkbox("強制覆寫現有課表", value=False, help="如果勾選，將會嘗試建立即便名稱重複的課表")

    if st.button("🚀 開始匯入", type="primary"):
        if not email or not password:
            st.error("請在側邊欄輸入 Garmin 帳號與密碼！")
            return
        
        if not sheet_url:
            st.error("請輸入 Google Sheet 網址！")
            return

        # 建立一個容器來顯示進度
        status_container = st.container()
        
        with st.status("正在處理中...", expanded=True) as status:
            # 1. 登入 Garmin
            try:
                status.write("正在登入 Garmin Connect...")
                # 在 Cloud 環境可能沒有 ~/.garth，所以直接傳入帳密
                # 我們修改 GarminAuth 讓它在 login 時也能處理
                # 這裡直接用 garth.login 也可以，但在這專案架構下呼叫 GarminAuth.ensure_login 比較好
                # 不過該函數被設計為優先讀檔。如果沒有 ~/.garth，它會用傳入的參數登入。
                # 為了確保在 Cloud 環境每次都成功，我們強迫重新登入或確保傳入參數被使用
                GarminAuth.ensure_login(email, password)
                status.write("✅ Garmin 登入成功")
            except Exception as e:
                status.update(label="登入失敗", state="error")
                st.error(f"登入失敗: {str(e)}")
                return

            # 2. 解析課表
            try:
                status.write(f"正在讀取 Google Sheet ({day_input})...")
                garmin_client = GarminClient()
                parser = WorkoutParser(garmin_client=garmin_client)
                
                # 解析
                if day_input:
                    workout_dto = parser.parse_file(sheet_url, target_day=day_input)
                    workouts_to_import = [workout_dto] if workout_dto else []
                else:
                    workouts_to_import = parser.parse_file(sheet_url)

                if not workouts_to_import:
                    status.update(label="找不到課表", state="error")
                    st.warning(f"在 {day_input} 找不到任何可匯入的課表。請確認分頁名稱是否正確。")
                    return
                
                status.write(f"✅ 成功解析 {len(workouts_to_import)} 個課表")
                
            except Exception as e:
                status.update(label="解析失敗", state="error")
                st.error(f"解析 Google Sheet 失敗: {str(e)}")
                st.markdown("請確認：\n1. 網址是否正確\n2. Token 是否已設定正確 (環境變數)\n3. 表格格式是否符合預期")
                return

            # 3. 匯入 Garmin
            client = garmin_client
            existing_workout_names = set()
            
            if not force_import:
                status.write("檢查現有課表...")
                try:
                    existing_list = client.list_workouts()
                    for w in existing_list:
                        if 'workoutName' in w:
                            existing_workout_names.add(w['workoutName'])
                except Exception as e:
                    logger.warning(f"無法取得現有課表列表，將略過檢查: {e}")

            success_count = 0
            
            progress_bar = status.container()
            
            for idx, workout in enumerate(workouts_to_import):
                if not workout:
                    continue
                
                workout_name = workout.workoutName
                
                if not force_import and workout_name in existing_workout_names:
                    st.warning(f"⚠️ 跳過 '{workout_name}' (已存在)")
                    continue

                try:
                    status.write(f"正在匯入: **{workout_name}** ...")
                    client.create_workout(workout)
                    st.success(f"✅ 成功匯入: **{workout_name}**")
                    success_count += 1
                except Exception as e:
                    st.error(f"❌ 匯入失敗 '{workout_name}': {e}")
            
            status.update(label="處理完成", state="complete")

        if success_count > 0:
            st.balloons()
            st.success(f"🎉 總共成功匯入 {success_count} 個課表！請至 Garmin Connect APP 同步您的手錶。")

if __name__ == "__main__":
    main()
