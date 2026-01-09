---
description: "功能實作的任務清單範本"
---

# 任務清單：[FEATURE NAME]

**輸入**: 來自 `/specs/[###-feature-name]/` 的設計文件
**前提條件**: plan.md (必要), spec.md (用戶故事必要), research.md, data-model.md, contracts/

**測試**: 下列範例包含測試任務。根據「高可測試性」原則，建議優先撰寫測試。

**組織**: 任務按用戶故事分組，以實現每個故事的獨立開發與測試。

## 格式：`[ID] [P?] [Story] 描述`

- **[P]**: 可並存執行（不同文件，無依賴關係）
- **[Story]**: 此任務所屬的用戶故事（例如：US1, US2, US3）
- 描述中請包含確切的文件路徑

## 路徑規範

- **單一項目**: `src/`, `tests/` 位於根目錄
- 路徑範例假設為單一項目結構 - 請根據 plan.md 調整

<!-- 
  ============================================================================
  重要：下方的任務僅為說明用途的範例。
  
  `/speckit.tasks` 指令必須根據以下內容替換為實際任務：
  - 來自 spec.md 的用戶故事
  - 來自 plan.md 的功能需求
  - 來自 data-model.md 的實體
  
  任務必須按用戶故事組織，以便每個故事可以：
  - 獨立實作
  - 獨立測試
  - 作為 MVP 增量交付
  ============================================================================
-->

## 第一階段：基礎設施 (Shared Infrastructure)

**目的**: 項目初始化與基本結構

- [ ] T001 按照實作計畫建立項目結構
- [ ] T002 初始化項目依賴
- [ ] T003 [P] 配置 linting 與格式化工具

---

## 第二階段：核心基礎 (Foundational)

**目的**: 在實作任何用戶故事之前必須完成的核心基礎設施

**⚠️ 關鍵**: 在此階段完成前，不得開始用戶故事的工作

- [ ] T004 設置數據庫模式與遷移框架
- [ ] T005 [P] 實現身份驗證/授權框架
- [ ] T006 [P] 設置 API 路由與中間件結構
- [ ] T007 建立所有故事依賴的基礎模型/實體
- [ ] T008 配置錯誤處理與日誌紀錄設施

**檢查點**: 基礎設施就緒 - 現在可以並行開始用戶故事的實作

---

## 第三階段：用戶故事 1 - [標題] (優先級：P1) 🎯 MVP

**目標**: [簡短描述此故事交付的內容]

**獨立測試**: [如何驗證此故事獨立運作]

### 用戶故事 1 的測試 ⚠️

> **注意：先撰寫這些測試，確保在實作前門檻失敗**

- [ ] T010 [P] [US1] 在 tests/contract/test_[name].py 中編寫合約測試
- [ ] T011 [P] [US1] 在 tests/integration/test_[name].py 中編寫集成測試

### 用戶故事 1 的實作

- [ ] T012 [P] [US1] 在 src/models/[entity1].py 中建立模型
- [ ] T013 [P] [US1] 實現業務邏輯
- [ ] T014 [US1] 實現端點/功能
- [ ] T015 [US1] 添加驗證與錯誤處理
- [ ] T016 [US1] 為用戶故事 1 添加日誌紀錄

**檢查點**: 此時，用戶故事 1 應能完全獨立運作且可被測試


## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T018 [P] [US2] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T019 [P] [US2] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 2

- [ ] T020 [P] [US2] Create [Entity] model in src/models/[entity].py
- [ ] T021 [US2] Implement [Service] in src/services/[service].py
- [ ] T022 [US2] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T023 [US2] Integrate with User Story 1 components (if needed)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T024 [P] [US3] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T025 [P] [US3] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 3

- [ ] T026 [P] [US3] Create [Entity] model in src/models/[entity].py
- [ ] T027 [US3] Implement [Service] in src/services/[service].py
- [ ] T028 [US3] Implement [endpoint/feature] in src/[location]/[file].py

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in docs/
- [ ] TXXX Code cleanup and refactoring
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX [P] Additional unit tests (if requested) in tests/unit/
- [ ] TXXX Security hardening
- [ ] TXXX Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
