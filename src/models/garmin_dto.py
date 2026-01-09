from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field

class GarminSportType(BaseModel):
    sportTypeKey: str = "strength_training"
    sportTypeId: int = 5
    displayOrder: int = 1

class GarminStepType(BaseModel):
    stepTypeKey: str = "interval"
    stepTypeId: int = 3
    displayOrder: int = 1

class GarminEndCondition(BaseModel):
    conditionTypeKey: str = "reps"
    conditionTypeId: int = 10
    displayOrder: int = 10

class GarminEndConditionUnit(BaseModel):
    unitKey: Optional[str] = None
    factor: Optional[float] = None

class GarminTargetType(BaseModel):
    workoutTargetTypeKey: Optional[str] = None
    workoutTargetTypeId: Optional[int] = None

class GarminStepTarget(BaseModel):
    targetType: Optional[GarminTargetType] = None
    targetValueOne: Optional[float] = None
    targetValueTwo: Optional[float] = None

class BaseStepDTO(BaseModel):
    stepId: Optional[int] = None
    stepOrder: Optional[int] = None

class GarminExecutableStep(BaseStepDTO):
    type: Literal["ExecutableStepDTO"] = "ExecutableStepDTO"
    childStepId: Optional[int] = None
    description: Optional[str] = None
    stepType: GarminStepType = Field(default_factory=GarminStepType)
    endCondition: GarminEndCondition = Field(default_factory=GarminEndCondition)
    endConditionValue: Optional[float] = None
    endConditionUnit: Optional[GarminEndConditionUnit] = None
    target: Optional[GarminStepTarget] = None
    exerciseName: Optional[str] = None
    # Additional fields often used for strength exercises (category etc are mapped inside exerciseName or separate objects?)
    # For now, sticking to the schema provided.

class GarminRepeatGroup(BaseStepDTO):
    type: Literal["RepeatGroupDTO"] = "RepeatGroupDTO"
    numberOfIterations: int
    workoutSteps: List['GarminStepDTO'] = []
    smartRepeat: bool = False

GarminStepDTO = Union[GarminExecutableStep, GarminRepeatGroup]

class GarminWorkoutSegment(BaseModel):
    segmentOrder: int = 1
    sportType: GarminSportType = Field(default_factory=GarminSportType)
    workoutSteps: List[GarminStepDTO] = []

class GarminWorkoutDTO(BaseModel):
    workoutName: str
    description: Optional[str] = None
    sportType: GarminSportType = Field(default_factory=GarminSportType)
    workoutSegments: List[GarminWorkoutSegment] = []
