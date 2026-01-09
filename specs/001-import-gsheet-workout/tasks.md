---
description: "功能實作的任務清單：匯入 Google Sheet 訓練計畫至 Garmin Connect"
---

# 任務清單：匯入 Google Sheet 訓練計畫至 Garmin Connect

**輸入**: 來自 `/specs/001-import-gsheet-workout/` 的設計文件
**前提條件**: plan.md (必要), spec.md (用戶故事必要), research.md, data-model.md, contracts/

## 格式：`[ID] [P?] [Story] 描述`

- **[P]**: 可並行執行（不同文件，無依賴關係）
- **[Story]**: 此任務所屬的用戶故事（US1, US2）
- 描述中包含確切的文件路徑

---

## 第一階段：基礎設施 (Shared Infrastructure)

**目的**: 項目初始化與基本結構建立

- [x] T001 根據實作計畫建立 `src/` 與 `tests/` 目錄結構
- [x] T002 初始化 Python 虛擬環境並安裝 `garth`, `pandas`, `openpyxl`, `requests`, `pydantic`
- [x] T003 [P] 配置 `pytest` 測試框架與相關 Mock 工具
- [x] T004 [P] 設定 linting (ruff/flake8) 與格式化 (black) 工具

---

## 第二階段：核心基礎 (Foundational)

**目的**: 在實作用戶故事之前必須完成的核心 DTO 與認證邏輯

- [x] T005 [P] 根據 API CURL 定義 Pydantic DTO 模型於 `src/models/garmin_dto.py`
- [x] T006 [P] 建立內部通用訓練模型於 `src/models/workout.py`
- [x] T007 實作 Garth 身份驗證包裝於 `src/core/auth.py`
- [x] T008 實作基礎 Garmin API 客戶端（含 POST 原型）於 `src/core/garmin_client.py`
- [x] T009 [P] 在 `tests/mock_data/` 中建立基於教練表格的測試用 CSV/XLSX 檔案

---

## 第三階段：用戶故事 1 - 基礎單一訓練匯入 (優先級：P1) 🎯 MVP

**目標**: 實作解析本地試算表檔案（CSV/XLSX，即教練表格的導出檔）中的「單日 (Day1)」訓練並成功匯入 Garmin

**獨立測試**: 使用 `tests/mock_data/` 中的單日訓練檔案，執行 CLI 後驗證 Garmin API 被正確呼叫且數據映射無誤（Mock 測試）。

### 用戶故事 1 的測試 ⚠️

- [x] T010 [P] [US1] 撰寫單日試算表解析的單元測試於 `tests/unit/test_parser.py`
- [x] T011 [P] [US1] 撰寫訓練匯入的集成測試 (使用 Mock API) 於 `tests/integration/test_import.py`

### 用戶故事 1 的實作

- [x] T012 [US1] 實作單日「動作/組數/重量/次數」的解析邏輯於 `src/core/parser.py`
- [x] T013 [US1] 實作 `8,7,6,6` 格式的次數拆解邏輯於 `src/core/parser.py`
- [x] T014 [US1] 實作算式解析（如 `25+2.3`）與「自身」重量處理於 `src/core/parser.py`
- [x] T015 [US1] 建立 `garmin_client.py` 中的 `create_workout` 方法
- [x] T016 [US1] 實作 CLI 進入點於 `src/cli/main.py` 以支援單一檔案匯入指令

**檢查點**: 用戶故事 1 應能解析並匯入表格中的首個 Day 區塊。

---

## 第四階段：用戶故事 2 - 批量計畫匯入 (優先級：P2)

**目標**: 支援解析整個試算表中的多個 Day 標題並執行批量匯入

**獨立測試**: 提供包含 Day1, Day2, Day3 的檔案，驗證 API 被呼叫三次。

### 用戶故事 2 的實作

- [x] T017 [US1] 增強 `src/core/parser.py` 識別多個 `DayX` 標題分塊的邏輯
- [x] T018 [US2] 在 `src/cli/main.py` 中實作循環匯入多個訓練計畫的邏輯
- [x] T019 [P] [US2] 增加對 Google Sheet 公開導出連結的支援於 `src/core/parser.py`

---

## 第五階段：完善與磨光 (Polish)

**目的**: 錯誤處理、日誌與文檔優化

- [x] T020 [P] 實作匯入失敗時的詳細錯誤日誌於 `src/utils/logger.py`
- [x] T021 更新 `README.md` 與 `quickstart.md` 說明教練表格的特定規範
- [x] T022 [P] 實作重複訓練項目的檢測邏輯（名稱與日期比對）

---

## 依賴關係圖

1. **Setup (T001-T004)** -> **Foundational (T005-T008)**
2. **Foundational** -> **US1 Implementation (T012-T016)**
3. **US1 Implementation** -> **US2 Implementation (T017-T019)**
4. **All US Phases** -> **Polish Phase (T020-T022)**

---

## 並行執行範例

### 團隊 A (模型與認證)
- T005 [P] 定義 DTO 模型
- T007 實作 Auth 包裝

### 團隊 B (解析與測試)
- T009 [P] 準備 Mock 數據
- T010 [P] 撰寫解析測試
