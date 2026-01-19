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
    # This should generate 1 RepeatGroup with 4 iterations
    # Plus other exercises.
    # Total exercises in Day 1: 
    # 1. 臥推 (4 sets) -> 1 RepeatGroup
    # 2. 上斜 (4 sets) -> 1 RepeatGroup
    # 3. 划船 (4 sets) -> 1 RepeatGroup
    # 4. 下拉 (4 sets) -> 1 RepeatGroup
    # 5. 三頭 (3 sets) -> 1 RepeatGroup
    # 6. 二頭 (3 sets) -> 1 RepeatGroup
    # Total steps = 6 RepeatGroups
    
    assert len(segment.workoutSteps) == 6
    
    # Verify first step (Bench Press, 77.5kg, RepeatGroup with 4 iterations)
    step1 = segment.workoutSteps[0]
    assert hasattr(step1, 'numberOfIterations')
    assert step1.numberOfIterations == 4
    
    # Check the inner exercise step
    inner_step = step1.workoutSteps[0]
    # After mapping, exerciseName should be the mapped key
    # "平板槓鈴臥推" should map to a bench press key
    assert "BENCH_PRESS" in inner_step.exerciseName or inner_step.exerciseName == "平板槓鈴臥推"
    assert inner_step.weightValue == 77.5

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
    # 3 exercises: Squat(5), Deadlift(3), Lunge(3) = 3 RepeatGroups
    assert len(w2.workoutSegments[0].workoutSteps) == 3

def test_parse_new_format_csv(parser):
    """Test parsing new format CSV (鄒兆陞_C9_肌肥大_3天_蹲_W1.csv)."""
    new_format_csv = "tests/mock_data/鄒兆陞_C9_肌肥大_3天_蹲_W1.csv"
    
    if not os.path.exists(new_format_csv):
        pytest.skip("New format CSV not found")
        
    # Test parsing Day1 specifically
    workout_dto = parser.parse_file(new_format_csv, target_day="Day1")
    
    assert isinstance(workout_dto, GarminWorkoutDTO)
    assert workout_dto.workoutName == "W1_Day1"  # Should extract W1 from filename
    
    # Verify segments
    assert len(workout_dto.workoutSegments) == 1
    segment = workout_dto.workoutSegments[0]
    
    # Should have the exercises from Day1:
    # 槓鈴深蹲, 槓鈴寬握臥推, 槓鈴借力推push press, 三頭下拉, 啞鈴上斜臥推, 原地熊爬, 高強度間歇
    # Most are 2 sets, so should have 7 steps (6 RepeatGroups + 1 ExecutableStep for 高強度間歇)
    assert len(segment.workoutSteps) == 7
    
    # Verify first exercise (槓鈴深蹲)
    first_step = segment.workoutSteps[0]
    # This should be a RepeatGroup with 2 iterations
    assert hasattr(first_step, 'numberOfIterations')
    assert first_step.numberOfIterations == 2
    
    # Check the exercise name in the inner step
    inner_step = first_step.workoutSteps[0]
    # After mapping, exerciseName should be the mapped key 
    # "槓鈴深蹲" should map to "SQUAT_BARBELL_BACK_SQUAT" 
    assert "SQUAT" in inner_step.exerciseName or inner_step.exerciseName == "槓鈴深蹲"
    assert inner_step.weightValue == 75.0  # Weight from CSV

def test_parse_new_format_all_days(parser):
    """Test parsing all days from new format CSV."""
    new_format_csv = "tests/mock_data/鄒兆陞_C9_肌肥大_3天_蹲_W1.csv"
    
    if not os.path.exists(new_format_csv):
        pytest.skip("New format CSV not found")
        
    workouts = parser.parse_file(new_format_csv)
    
    assert isinstance(workouts, list)
    # Should find Day1, Day2, Day3
    assert len(workouts) == 3
    
    # Check workout names
    workout_names = [w.workoutName for w in workouts]
    assert "W1_Day1" in workout_names
    assert "W1_Day2" in workout_names
    assert "W1_Day3" in workout_names

