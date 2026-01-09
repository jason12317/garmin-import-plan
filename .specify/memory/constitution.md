<!--
Version change: 0.0.0 → 1.0.0
List of modified principles:
- [NEW] I. 高品質與穩定性 (High Quality & Stability)
- [NEW] II. 高可測試性 (Testability)
- [NEW] III. 最小可行性產品 (MVP)
- [NEW] IV. 避免過度設計 (No Overdesign)
- [NEW] V. 統一使用正體中文 (Unified Traditional Chinese)
Added sections: 技術規範與安全要求, 開發流程與品質門檻
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md (✅ updated)
- .specify/templates/spec-template.md (✅ updated)
- .specify/templates/tasks-template.md (✅ updated)
Follow-up TODOs: None
-->

# Garmin Import Plan 憲法

## 核心原則

### I. 高品質與穩定性
我們追求代碼的精確與穩定。每一行代碼都必須經過深思熟慮，確保系統的可讀性與可維護性。禁止任何可能導致系統不穩定的捷徑，確保在處理 Garmin 數據時的準確性。

### II. 高可測試性
所有的功能實作必須是可測試的。代碼設計應優先考慮測試可行性，確保關鍵邏輯擁有自動化測試覆蓋。測試必須作為代碼正確性的唯一權威驗證，並在 CI/CD 流程中嚴格執行。

### III. 最小可行性產品 (MVP)
專注於核心價值的交付。在開發初期，僅實作達成目標所必須的功能。透過快速迭代收集反饋，避免在需求未明確前投入過多資源開發非必要功能。

### IV. 避免過度設計 (No Overdesign)
保持設計的簡單性。僅針對當前的需求進行架構與設計，不為假設性的未來需求增加複雜性。遵循 YAGNI 原則，採用最簡單且有效的解決方案。

### V. 統一使用正體中文
為了確保團隊溝通的高精確度與一致性，所有項目文檔、開發計畫、任務清單及 AI 回應一律使用正體中文。

## 技術規範與安全要求
數據處理與儲存必須遵守隱私保護原則。優先採用強類型語言與自動化檢查工具，以降低運行時錯誤。

## 開發流程與品質門檻
1. **測試驅動**: 優先撰寫測試案例，確保功能符合預期。
2. **代碼審閱**: 所有的變更必須經過審核，並驗證是否符合本項目的核心原則。

## 治理規範
本憲法高於所有其他開發實務；任何修改均需記錄、審查並擬定遷移計劃。PR 必須驗證是否符合本規範。

**Version**: 1.0.0 | **Ratified**: 2026-01-08 | **Last Amended**: 2026-01-08

