# 資料模型設計：Garmin 訓練匯入

## 實體定義

### 1. Workout (訓練)
- `name`: string (訓練名稱)
- `sport_type`: SportType (運動類型)
- `segments`: List[WorkoutSegment]

### 2. WorkoutSegment (訓練航段)
- `order`: int
- `steps`: List[BaseStep]

### 3. BaseStep (基礎步驟 - 抽象)
- `step_order`: int
- `step_type`: StepType (Warmup, Interval, Recovery, Rest)

### 4. ExecutableStep (可執行步驟 - 繼承 BaseStep)
- `exercise_name`: string (練習名稱)
- `category`: string (練習類別)
- `target_type`: TargetType
- `end_condition`: EndCondition (LapButton, Time, Distance, Reps)
- `end_condition_value`: float (若次數清單為 8,7,6,6，則分解為四個步驟，此值分別為 8, 7, 6, 6)
- `weight`: Optional[float] (支援數值計算，如 25+2.3 -> 27.3)

### 5. RepeatGroup (重複組 - 繼承 BaseStep)
- `iterations`: int
- `steps`: List[ExecutableStep]
- `skip_last_rest`: bool

## 映射邏輯 (Mapping)
- 從 CSV/Sheet 標題 `Workout Name` -> `Workout.name`
- 從 `Steps` 字串解析出的結構 -> `Workout.segments[0].steps`

## Pydantic 模型結構 (用於 API 交換)
見 `src/models/garmin_dto.py` 的實作預期：
- `GarminWorkoutDTO`: 頂層對象
- `GarminStepDTO`: 支持 `ExecutableStepDTO` 與 `RepeatGroupDTO` 種類
