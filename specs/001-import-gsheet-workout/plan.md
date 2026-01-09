# 實作計畫：匯入 Google Sheet 訓練計畫至 Garmin Connect

**分支**: `001-import-gsheet-workout` | **日期**: 2026-01-08 | **規格書**: [spec.md](./spec.md)
**輸入**: 來自 `/specs/001-import-gsheet-workout/spec.md` 的功能規格

## 摘要

本計畫旨在透過反向工程 Garmin Connect API，實現將 Google Sheet 或本地文件（CSV/XLSX）中的訓練計畫自動匯入 Garmin 系統的功能。我們將使用 `garth` 函式庫處理身份驗證，並解析固定格式的輸入源以適應 Garmin Workout API 的 JSON 結構。

## 技術背景

**Language/Version**: Python 3.10+  
**Primary Dependencies**: `garth` (身份驗證), `pandas`, `openpyxl`, `requests`, `pydantic`  
**Storage**: 本地會話快取 (由 Garth 管理)  
**Testing**: `pytest`, `pytest-mock`  
**Target Platform**: CLI / 本地腳本
**Project Type**: 單一 Python 項目  
**Performance Goals**: 7 天訓練計畫匯入 < 30 秒  
**Constraints**: 必須解析複雜的試算表結構（跨列標題、非正規化表格、次數清單 `8,7,6,6`）  
**Scale/Scope**: 針對教練提供的特定「肌力訓練」表格設計（Day 分組格式）

## 憲法檢查 (Constitution Check)

*門檻：必須在 Phase 0 研究前通過。在 Phase 1 設計後重新檢查。*

- [x] **高品質與穩定性**: 使用強類型的 Pydantic 模型定義 Garmin API 結構，確保數據格式正確。
- [x] **高可測試性**: 將解析邏輯與 API 調用分離，對解析模組進行單元測試，對 API 調用進行 Mock 測試。
- [x] **最小可行性產品 (MVP)**: 優先實現「Garth 認證」與「單一訓練匯入」，次要實現批量與本地文件支援。
- [x] **避免過度設計**: 不建立複雜的資料庫，僅使用 CLI 進行操作。
- [x] **統一使用正體中文**: 文檔與開發計畫均使用正體中文。

## 項目結構

### 文檔 (此功能)

```text
specs/001-import-gsheet-workout/
├── plan.md              # 此文件
├── research.md          # Phase 0 產出
├── data-model.md        # Phase 1 產出
├── quickstart.md        # Phase 1 產出
├── contracts/           # Phase 1 產出
└── tasks.md             # Phase 2 產出
```

### 原始碼 (項目根目錄)

```text
src/
├── core/
│   ├── auth.py          # Garth 認證包裝
│   ├── garmin_client.py # API 調用封裝
│   └── parser.py        # Sheet/CSV/XLSX 解析邏輯
├── models/
│   ├── garmin_dto.py    # Garmin API JSON 模型 (Pydantic)
│   └── workout.py       # 內部通用訓練實體
├── cli/
│   └── main.py          # 指令進入點
└── utils/

tests/
├── unit/
├── integration/
└── mock_data/           # 包含範例 CURL 提供的 JSON
```

**結構決策**: 採用經典的 Python 模組化結構，將 API 資料傳輸對象 (DTO) 與內部業務邏輯分離。

## 複雜度追蹤

> **僅在憲法檢查有違規但必須證成時填寫**


| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
