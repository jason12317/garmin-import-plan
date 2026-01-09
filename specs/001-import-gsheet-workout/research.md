# 研究報告：Garmin 訓練匯入技術細節

## 1. Garth 身份驗證研究
- **決策**: 使用 `garth.login(username, password)` 並搭配 `garth.save("~/.garth")` 進行會話持久化。
- **原因**: Garth 支援處理 Garmin 的 SSO 流程，且能自動管理 Cookie 與 Token，避免手動處理複雜的 `connect-csrf-token`。
- **備選方案**: 手動從瀏覽器擷取 Cookie (太過繁瑣)。

## 2. Garmin Workout API 結構分析
- **端點**: `POST https://connect.garmin.com/gc-api/workout-service/workout`
- **關鍵觀察**:
    - `sportType`: 肌力訓練為 `"sportTypeKey": "strength_training"` (ID 5)。
    - `workoutSegments`: 包含步驟數組。
    - `workoutSteps`: 支持 `ExecutableStepDTO` 與 `RepeatGroupDTO` (重複組)。
    - 重複組內部可以巢狀包含步驟，並自定義 `numberOfIterations`。
    - 每一練習步驟需要 `exerciseName` 與 `category`。

## 3. 教練試算表解析研究 (基於範例表格)
- **結構規律**:
    - 以 `DayX` 作為訓練日分塊的標題。
    - 表格列標題為：`動作`, `組數`, `重量`, `實際使用重量`, `次數` 等。
    - 關鍵字 `高強度間歇` 或 `極低強度有氧` 可能代表額外的 Workout 段落。
- **數據清洗**:
    - **動作 (Exercise)**: 需要映射到 Garmin 的練習資料庫。
    - **重量 (Weight)**: 需處理 `自身` (=0kg), `77.5` (浮點數), `25+2.3` (求和解析)。
    - **組次 (Sets/Reps)**: `組數: 4`, `次數: 8,7,6,6`。這代表 Garmin Workout 需建立 4 個 `ExecutableStepDTO`，每個步驟有不同的次數。
- **解析器實作思路**: 
    - 使用 `pandas` 讀取並偵測 `Day` 關鍵字單元格。
    - 向下掃描直到下一個空行或 `Day` 標題。
    - 對於每一行，如果 `次數` 包含逗號，拆分為多個 Set。

## 4. 步驟解析語法 (DSL) 設計
為了進階支援，DSL 需能處理：
- 格式: `[動作名稱] | [組數] | [重量] | [次數]`
- 範例: `槓鈴深蹲 | 4 | 77.5 | 8,7,6,6`

---
**待釐清事項已解決**:
- 驗證方式 -> Garth
- 資料來源 -> 支持 GSheet/CSV/XLSX
- API 解析 -> 已根據 CURL 樣例完成對應
