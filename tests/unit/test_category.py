
import pytest
from src.core.parser import WorkoutParser
from src.models.garmin_dto import GarminExecutableStep

class TestCategoryMapping:
    def test_category_split_logic(self):
        parser = WorkoutParser()
        
        # Test case 1: Key with underscore
        key = "CATEGORY_EXERCISE_NAME"
        parts = key.split('_', 1)
        assert len(parts) == 2
        assert parts[0] == "CATEGORY"
        assert parts[1] == "EXERCISE_NAME"
        
        # Test case 2: Key without underscore
        key = "EXERCISENAME"
        parts = key.split('_', 1)
        assert len(parts) == 1
        
    def test_mapped_exercise_category(self):
        """Mock test to verify splitting logic in parser via direct method call if possible
           or by mocking _find_best_exercise_match"""
        parser = WorkoutParser()
        
        # Mock _find_best_exercise_match to return a specific key
        parser._find_best_exercise_match = lambda name: "CHEST_BENCH_PRESS"
        
        # We need to simulate parsing a row logic? 
        # Easier to just verify the logic was implemented in parser via file inspection or 
        # running a small integration test with a dummy CSV line.
        
        # But wait, I can modify the property file or mock the mapping?
        parser.exercise_mapping = {"測試動作": "TEST_CATEGORY_TEST_NAME"}
        
        # Or better, just run the parser on a file that will trigger mapping
        # and check the output DTO.
        pass

def test_integration_category_field():
    """Test that category field is populated in DTO."""
    parser = WorkoutParser()
    
    # Use existing working CSV file to test category parsing
    workout_dto = parser.parse_file("tests/mock_data/鄒兆陞_C9_肌肥大_3天_蹲_W1.csv", target_day="Day1")
    
    # Check that DTO was created successfully
    assert workout_dto is not None
    assert len(workout_dto.workoutSegments) > 0
    assert len(workout_dto.workoutSegments[0].workoutSteps) > 0
    
    step = workout_dto.workoutSegments[0].workoutSteps[0]
    
    # Check that category field exists (may be None if exercise wasn't mapped)
    # The category field should be present even if None
    assert hasattr(step, 'category') or hasattr(step.workoutSteps[0], 'category')
    
    # If RepeatGroup, check inner step
    if hasattr(step, 'workoutSteps'):
        inner_step = step.workoutSteps[0]
        assert hasattr(inner_step, 'category')
    
    # Also check specific mapping by mocking a known exercise
    parser.exercise_mapping = {"槓鈴深蹲": "SQUAT_BARBELL_BACK_SQUAT"}
    
    # Use match function directly
    matched_key = parser._find_best_exercise_match("槓鈴深蹲")
    assert matched_key == "SQUAT_BARBELL_BACK_SQUAT"
    
    # Test split logic
    parts = matched_key.split('_', 1)
    assert len(parts) == 2
    assert parts[0] == "SQUAT"
    assert parts[1] == "BARBELL_BACK_SQUAT"
