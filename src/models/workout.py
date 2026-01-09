from typing import List, Optional, Union
from pydantic import BaseModel, Field

class WorkoutStep(BaseModel):
    order: int
    exercise_name: str
    category: str = "strength"
    weight_kg: Optional[float] = None
    reps: Optional[int] = None
    duration_secs: Optional[float] = None
    rest_secs: Optional[float] = None
    notes: Optional[str] = None

class Workout(BaseModel):
    name: str
    date: Optional[str] = None  # YYYY-MM-DD
    steps: List[WorkoutStep] = []
    raw_source: Optional[str] = None

class TrainingDay(BaseModel):
    day_name: str
    workouts: List[Workout] = []
