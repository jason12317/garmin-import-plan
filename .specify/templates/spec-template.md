# 功能規格書：[FEATURE NAME]

**功能分支**: `[###-feature-name]`  
**建立日期**: [DATE]  
**狀態**: 草案  
**輸入**: 用戶描述："$ARGUMENTS"

## 用戶場景與測試 *(強制)*

<!--
  重要：用戶故事應按重要性排序為用戶旅程。
  每個用戶故事/旅程必須是可獨立測試的 - 這意味著即使你只實作其中一個，
  你仍應有一個可交付價值的最小可行性產品 (MVP)。
  
  為每個故事分配優先級 (P1, P2, P3 等)，其中 P1 最為關鍵。
-->

### 用戶故事 1 - [簡短標題] (優先級：P1)

[用平實的語言描述此用戶旅程]

**為什麼是此優先級**: [解釋其價值以及為何具有此優先級別]

**獨立測試**: [描述如何獨立測試此功能 - 例如：「可以透過 [特定動作] 進行全面測試並交付 [特定價值]」]

**驗收場景**:

1. **假設** [初始狀態]，**當** [操作]，**則** [預期結果]
2. **假設** [初始狀態]，**當** [操作]，**則** [預期結果]

---

### 用戶故事 2 - [簡短標題] (優先級：P2)

[用平實的語言描述此用戶旅程]

**為什麼是此優先級**: [解釋其價值]

**獨立測試**: [描述如何獨立測試]

**驗收場景**:

1. **假設** [初始狀態]，**當** [操作]，**則** [預期結果]

---

### 邊界情況

- [邊界條件] 時會發生什麼？
- 系統如何處理 [錯誤情境]？

## 需求 *(強制)*

### 功能需求

- **FR-001**: 系統「必須」(MUST) [特定能力]
- **FR-002**: 系統「必須」(MUST) [特定能力]  

### 關鍵實體 *(若涉及數據則包含)*

- **[Entity 1]**: [其代表的意義，關鍵屬性，不包含實作細節]

- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]
