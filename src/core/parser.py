import pandas as pd
import re
import logging
from typing import List, Optional, Union
from src.models.garmin_dto import (
    GarminWorkoutDTO, 
    GarminWorkoutSegment, 
    GarminExecutableStep, 
    GarminEndCondition,
    GarminStepType,
    GarminStepTarget,
    GarminRepeatGroup
)

logger = logging.getLogger(__name__)

class WorkoutParser:
    def __init__(self):
        pass

    def parse_file(self, file_path: str, target_day: str = None) -> Union[GarminWorkoutDTO, List[GarminWorkoutDTO]]:
        """
        Parses a local CSV/Excel file or Google Sheet URL.
        If target_day is provided, returns single GarminWorkoutDTO.
        If not, logic for batch import (US2) triggers.
        """
        original_path = file_path
        file_path = self._transform_gsheet_url(file_path)
        
        logger.info(f"Loading from: {file_path}")
        
        # Load file
        try:
            if file_path.startswith("http") or file_path.endswith('.csv') or "format=csv" in file_path:
                df = pd.read_csv(file_path, header=None)
            else:
                df = pd.read_excel(file_path, header=None)
        except Exception as e:
            logger.error(f"Failed to read file/url: {e}")
            raise e
            
        # Strategy: Iterate rows to find chunks
        # A chunk starts with "Day X..."
        # Then we look for the header row: "動作,組數..."
        
        workouts = []
        
        # Simple iterator for MVP (US1) - Find specific day
        current_day_name = None
        start_row_idx = -1
        
        # Pre-process dataframe to list of lists for easier handling
        rows = df.values.tolist()
        
        idx = 0
        while idx < len(rows):
            row = rows[idx]
            first_cell = str(row[0]).strip() if pd.notna(row[0]) else ""
            
            # Detect Day Header
            if first_cell.startswith("Day"):
                # Check if this "Day" block is what we want (if target_day specified)
                # Or if no target_day, we process all "Day" blocks
                
                is_target = (target_day is None) or (target_day in first_cell)
                
                # Check for second header line (e.g. Day 1 -> Day 1 - Chest)
                # If the NEXT row also starts with Day, we jump to it and use it as name
                next_row_idx = idx + 1
                workout_name = first_cell
                header_row_expected = idx + 1
                
                if next_row_idx < len(rows):
                    next_cell = str(rows[next_row_idx][0]).strip() if pd.notna(rows[next_row_idx][0]) else ""
                    if next_cell.startswith("Day"):
                        # Use this as the main title
                        workout_name = next_cell
                        header_row_expected = idx + 2
                        if target_day and target_day in next_cell:
                            is_target = True

                if is_target:
                    logger.info(f"Found workout block: {workout_name}")
                    workout_dto, last_processed_idx = self._parse_block(rows, header_row_expected, workout_name)
                    
                    if workout_dto:
                        if target_day:
                            return workout_dto # Return immediately
                        workouts.append(workout_dto)
                    
                    # Advance index to skip processed rows
                    if last_processed_idx > idx:
                        idx = last_processed_idx
                    else:
                        idx += 1
                else:
                    # Not the target day, but we need to skip this block to avoid re-triggering
                    # Just advance one by one? Or try to find end?
                    # Safer to just advance one, and rely on "is_target" check logic 
                    # but since we support parsing "Day 1" then finding "Day 1 - Chest" next line,
                    # we handled the double-header logic above.
                    idx += 1
            else:
                idx += 1

        if target_day:
            raise ValueError(f"Target day '{target_day}' not found in file.")
            
        return workouts

    def _transform_gsheet_url(self, url: str) -> str:
        """Transforms a standard Google Sheet Edit URL to an Export CSV URL."""
        if "docs.google.com/spreadsheets" in url and "/edit" in url:
            # https://docs.google.com/spreadsheets/d/KEY/edit#gid=123
            try:
                base = url.split("/edit")[0]
                gid = "0"
                # Check fragment or query
                if "gid=" in url:
                    # simplistic extraction
                    import re
                    match = re.search(r'gid=(\d+)', url)
                    if match:
                        gid = match.group(1)
                
                return f"{base}/export?format=csv&gid={gid}"
            except:
                return url
        return url

    def _parse_block(self, all_rows: list, header_row_idx: int, workout_name: str) -> tuple[Optional[GarminWorkoutDTO], int]:
        # Returns (DTO, last_processed_row_index)
        # 1. Identify columns from header row
        if header_row_idx >= len(all_rows):
            return None, header_row_idx
            
        header = [str(x).strip() for x in all_rows[header_row_idx]]
        try:
            col_exercise = header.index("動作")
            col_sets = header.index("組數")
            col_weight = header.index("重量")
            col_reps = header.index("次數")
        except ValueError:
            logger.warning(f"Header row missing required columns at line {header_row_idx}")
            return None, header_row_idx
            
        # 2. Iterate data rows
        steps = []
        curr_idx = header_row_idx + 1
        
        last_idx = curr_idx
        
        while curr_idx < len(all_rows):
            row = all_rows[curr_idx]
            last_idx = curr_idx
            
            exercise = str(row[col_exercise]).strip() if pd.notna(row[col_exercise]) else ""
            
            # Stop condition: Empty exercise or next Day
            # Note: If we see "Day..." in first column, it's the start of next block.
            first_col = str(row[0]).strip() if pd.notna(row[0]) else ""
            if first_col.startswith("Day"):
                # We found next day, STOP processing this block. 
                # Do NOT increment index so outer loop catches it.
                break
                
            # If exercise is empty but not Day, it might be just blank line.
            if not exercise or exercise.lower() == "nan":
                 # Check if it's truly end of block? 
                 # Usually yes. But let's check if first column is Day.
                 # If just blank, we skip or stop? 
                 # Let's assume blank line = end of steps for this day.
                 # But we need to verify if next lines are blank too.
                 # For safety, let's stop.
                 curr_idx += 1
                 continue         
            
            # Parse Sets
            
            # Stop condition: Empty exercise or next Day
            if not exercise or exercise.lower() == "nan" or exercise.startswith("Day"):
                break
                
            # Parse Sets
            try:
                sets_val = int(float(str(row[col_sets]))) if pd.notna(row[col_sets]) else 1
            except:
                sets_val = 1
                
            # Parse Weight
            raw_weight = str(row[col_weight])
            weight_val = self.parse_weight(raw_weight)
            
            # Parse Reps
            raw_reps = str(row[col_reps])
            reps_list = self.parse_reps_string(raw_reps)
            
            # Logic: If Reps list < Sets, cycle/repeat last? Or default to 8?
            # If Reps list > Sets, truncate?
            # Usually strict match or broadcast single value
            
            if len(reps_list) == 1:
                reps_list = reps_list * sets_val
            elif len(reps_list) < sets_val:
                # Pad with last value
                reps_list += [reps_list[-1]] * (sets_val - len(reps_list))
                
            # Create Steps
            # Improved logic: Check if all reps are identical
            # If identical, create a RepeatGroup
            # If different, create individual steps
            
            all_reps_same = all(r == reps_list[0] for r in reps_list)
            
            if all_reps_same and sets_val > 1:
                # Create one step wrapped in RepeatGroup
                reps = reps_list[0]
                
                single_step = GarminExecutableStep(
                    stepId=None,
                    stepOrder=1, # Inside loop
                    description=exercise, # Put Name in description/notes
                    exerciseName=exercise,
                    stepType=GarminStepType(stepTypeKey="interval", stepTypeId=3),
                    endCondition=GarminEndCondition(conditionTypeKey="reps", conditionTypeId=10),
                    endConditionValue=float(reps)
                )
                
                # Add Weight Target logic if needed
                if weight_val > 0:
                     # For strength, often just "Description" is used unless we map to strict targets
                     pass 
                
                repeat_group = GarminRepeatGroup(
                    stepOrder=len(steps) + 1,
                    numberOfIterations=sets_val,
                    workoutSteps=[single_step],
                    smartRepeat=False
                )
                steps.append(repeat_group)
                
            else:
                # Create individual steps
                for i in range(sets_val):
                    reps = reps_list[i] if i < len(reps_list) else 8
                    
                    step = GarminExecutableStep(
                        stepId=None,
                        stepOrder=len(steps) + 1,
                        description=exercise, # Put Name in description/notes
                        exerciseName=exercise,
                        stepType=GarminStepType(stepTypeKey="interval", stepTypeId=3), # Default to interval
                        endCondition=GarminEndCondition(conditionTypeKey="reps", conditionTypeId=10),
                        endConditionValue=float(reps)
                    )
                    
                    steps.append(step)
                
            curr_idx += 1
            
        # Construct DTO
        segment = GarminWorkoutSegment(segmentOrder=1, workoutSteps=steps)
        return GarminWorkoutDTO(workoutName=workout_name, workoutSegments=[segment]), curr_idx

    def parse_weight(self, value: str) -> float:
        """Parses weight string like '25+2.3' or '自身'."""
        if not value or pd.isna(value) or value == "nan":
            return 0.0
        
        val_str = str(value).strip()
        
        if "自身" in val_str:
            return 0.0
        
        # Handle formulas
        try:
            # Dangerous eval? Restricted char set: 0-9 . + - / *
            if re.match(r'^[0-9\.\+\-\s]+$', val_str):
                return float(eval(val_str))
            return float(val_str)
        except:
            return 0.0

    def parse_reps_string(self, value: str) -> List[float]:
        """Parses reps like '8,7,6,6' or '8-12'."""
        if not value or pd.isna(value) or value == "nan":
            return [1.0]
            
        val_str = str(value).strip()
        
        # Comma separated
        if "," in val_str:
            parts = val_str.split(",")
            results = []
            for p in parts:
                results.append(self._parse_single_rep(p))
            return results
            
        return [self._parse_single_rep(val_str)]

    def _parse_single_rep(self, chunk: str) -> float:
        chunk = chunk.strip()
        # Range '8-12' -> return 8
        if "-" in chunk:
            try:
                return float(chunk.split("-")[0])
            except:
                return 0.0
        try:
            return float(chunk)
        except:
            return 0.0
