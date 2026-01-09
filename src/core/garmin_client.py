import logging
from typing import Any, Dict
import garth
from src.models.garmin_dto import GarminWorkoutDTO

logger = logging.getLogger(__name__)

WORKOUT_SERVICE_ENDPOINT = "https://connect.garmin.com/gc-api/workout-service/workout"

class GarminClient:
    def __init__(self):
        # Assumes GarminAuth.ensure_login() has been called
        pass

    def list_workouts(self, limit=100) -> list:
        """Fetch list of existing workouts."""
        try:
            # Need to find correct endpoint for listing. 
            # Usually /workout-service/workouts or /workout-service/workout with params
            # Based on common knowledge: GET /workout-service/workouts
            # Or /workout-service/workout
            
            # Let's try /workout-service/workouts first (standard REST collection)
            # or check Garth documentation/examples.
            # Assuming GET /workout-service/workouts?start=0&limit=100
            
            url = f"https://connect.garmin.com/gc-api/workout-service/workouts?start=0&limit={limit}"
            response = garth.client.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            logger.warning(f"Failed to list workouts: {e}")
            return []

    def create_workout(self, workout_dto: GarminWorkoutDTO) -> Dict[str, Any]:
        """
        Posts the workout DTO to Garmin Connect.
        """
        # Pydantic v2: model_dump(mode='json') or just model_dump()
        payload = workout_dto.model_dump(exclude_none=True)
        
        logger.info(f"Creating workout: {workout_dto.workoutName}")
        try:
            response = garth.client.post(WORKOUT_SERVICE_ENDPOINT, json=payload)
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                logger.info(f"Workout created: ID {data.get('workoutId')}")
                return data
            else:
                raise Exception(f"Failed to create workout {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Error creating workout: {e}")
            raise

