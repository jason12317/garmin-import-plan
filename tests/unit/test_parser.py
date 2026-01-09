import pytest
import os
from src.core.parser import WorkoutParser
from src.models.garmin_dto import GarminWorkoutDTO, GarminExecutableStep

SAMPLE_CSV = "tests/mock_data/sample_coach_plan.csv"

@pytest.fixture
def parser():
    return WorkoutParser()

def test_parse_day_1_basic(parser):
    """Test parsing Day 1 from the sample CSV."""
    if not os.path.exists(SAMPLE_CSV):
        pytest.skip("Sample CSV not found")
        
    workout_dto = parser.parse_file(SAMPLE_CSV, target_day="Day 1")
    
    assert isinstance(workout_dto, GarminWorkoutDTO)
    assert workout_dto.workoutName == "Day 1 - Chest/Back"
    # Verify segments
    assert len(workout_dto.workoutSegments) == 1
    segment = workout_dto.workoutSegments[0]
    
    # "平板槓鈴臥推,4,77.5,,8,7,6,6"
    # This should generate 4 steps (8 reps, 7 reps, 6 reps, 6 reps)
    # Plus other exercises.
    # Total exercises in Day 1: 
    # 1. 臥推 (4 sets)
    # 2. 上斜 (4 sets)
    # 3. 划船 (4 sets)
    # 4. 下拉 (4 sets)
    # 5. 三頭 (3 sets)
    # 6. 二頭 (3 sets)
    # Total steps = 4+4+4+4+3+3 = 22 steps
    
    assert len(segment.workoutSteps) == 22
    
    # Verify first step (Bench Press, 77.5kg, 8 reps)
    step1 = segment.workoutSteps[0]
    assert isinstance(step1, GarminExecutableStep)
    assert step1.exerciseName == "平板槓鈴臥推"
    assert step1.endCondition.conditionTypeKey == "reps"
    assert step1.endConditionValue == 8.0
    # Add check for weight if mapped (Target)
    # assert step1.target.targetValueOne == 77.5

def test_parse_reps_list(parser):
    """Test parsing string '8,7,6,6'."""
    reps_list = parser.parse_reps_string("8,7,6,6")
    assert reps_list == [8, 7, 6, 6]

def test_parse_weight_formula(parser):
    """Test parsing weight formulas."""
    assert parser.parse_weight("25+2.3") == 27.3
    assert parser.parse_weight("自身") == 0.0
    assert parser.parse_weight("77.5") == 77.5

def test_parse_batch_days(parser):
    """Test parsing multiple days (Day 1 and Day 2)."""
    if not os.path.exists(SAMPLE_CSV):
        pytest.skip("Sample CSV not found")
        
    workouts = parser.parse_file(SAMPLE_CSV)
    
    assert isinstance(workouts, list)
    # Day 1 - Chest/Back and Day 2 - Legs
    # Sample file has Day 1 and Day 2 blocks.
    assert len(workouts) == 2
    
    w1 = workouts[0]
    w2 = workouts[1]
    
    assert "Chest/Back" in w1.workoutName
    assert "Legs" in w2.workoutName
    
    # Day 2 check
    # 3 exercises: Squat(5), Deadlift(3), Lunge(3) = 11 steps
    assert len(w2.workoutSegments[0].workoutSteps) == 11

