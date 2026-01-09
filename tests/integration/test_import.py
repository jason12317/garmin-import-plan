import pytest
from unittest.mock import MagicMock, patch
from src.core.garmin_client import GarminClient
from src.models.garmin_dto import GarminWorkoutDTO

def test_create_workout_integration():
    """
    Test the flow of creating a workout using the client.
    We mock the underlying garth.client.post to avoid real API calls.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"workoutId": 12345, "workoutName": "Test Workout"}
    
    with patch('garth.client.post', return_value=mock_response) as mock_post:
        # 1. Prepare Data
        client = GarminClient()
        dto = GarminWorkoutDTO(workoutName="Test Workout")
        
        # 2. Act
        result = client.create_workout(dto)
        
        # 3. Assert
        assert result['workoutId'] == 12345
        mock_post.assert_called_once()
        # Verify payload structure in call args
        args, kwargs = mock_post.call_args
        payload = kwargs['json']
        assert payload['workoutName'] == "Test Workout"
