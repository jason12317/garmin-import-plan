import pandas as pd
import re
from src.utils.logger import setup_logger

import os
from typing import List, Optional, Union, Dict
from difflib import SequenceMatcher
from src.models.garmin_dto import (
    GarminWorkoutDTO,
    GarminWorkoutSegment,
    GarminExecutableStep,
    GarminEndCondition,
    GarminEndConditionUnit,
    GarminStepType,
    GarminRepeatGroup,
    GarminWeightUnit
)

# Google Sheets API imports
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
from google.oauth2 import service_account
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json
import os.path

logger = setup_logger(__name__)

class WorkoutParser:
    def __init__(self, garmin_client=None):
        self.exercise_mapping = self._load_exercise_mapping()
        self.category_mapping = self._load_category_mapping()
        self.garmin_client = garmin_client
        self.learned_mapping = {}  # Store learned exercise mappings from existing workouts
        self.is_w1_training = False  # Track if current training is W1
    
    def _create_rest_step(self, step_order: int, rest_seconds: int = 90) -> GarminExecutableStep:
        """Create a rest step with specified duration"""
        return GarminExecutableStep(
            stepId=None,
            stepOrder=step_order,
            description="",
            stepType=GarminStepType(stepTypeKey="rest", stepTypeId=5, displayOrder=5),
            endCondition=GarminEndCondition(conditionTypeKey="time", conditionTypeId=2, displayOrder=2),
            endConditionValue=rest_seconds,
            endConditionUnit=GarminEndConditionUnit(unitKey="second", factor=1),
            category=None,
            exerciseName=None,
            weightValue=None,
            weightUnit=GarminWeightUnit(unitKey="kilogram") if False else None
        )
        
    def _load_exercise_mapping(self) -> Dict[str, str]:
        """Load exercise name mapping from properties file"""
        mapping = {}
        properties_file = "exercise_zh_tw.properties"
        
        if os.path.exists(properties_file):
            try:
                with open(properties_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            mapping[value.strip()] = key.strip()
                logger.info(f"Loaded {len(mapping)} exercise mappings")
            except Exception as e:
                logger.warning(f"Failed to load exercise mapping: {e}")
        else:
            logger.warning(f"Exercise mapping file not found: {properties_file}")
            
        return mapping
    
    def _load_category_mapping(self) -> Dict[str, str]:
        """Load category mapping from properties file"""
        mapping = {}
        properties_file = "exercise_category_mapping.properties"
        
        if os.path.exists(properties_file):
            try:
                with open(properties_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            mapping[key.strip()] = value.strip()
                logger.info(f"Loaded {len(mapping)} category mappings")
            except Exception as e:
                logger.error(f"Failed to load category mapping: {e}")
        else:
            logger.warning(f"Category mapping file not found: {properties_file}")
            
        return mapping
    
    def _learn_from_existing_workouts(self):
        """Learn exercise mappings from existing W1_DayX workouts"""
        try:
            # Get list of existing workouts
            workouts = self.garmin_client.list_workouts(limit=200)
            if not workouts:
                logger.info("No existing workouts found to learn from")
                return
            
            # Look for W1_Day patterns
            w1_workouts = []
            for workout in workouts:
                workout_name = workout.get('workoutName', '')
                if 'W1_Day' in workout_name:
                    w1_workouts.append(workout)
            
            if not w1_workouts:
                logger.info("No W1_DayX workouts found to learn from")
                return
            
            logger.info(f"Found {len(w1_workouts)} W1_DayX workouts to learn from")
            
            # Get detailed info for each W1 workout
            for workout in w1_workouts:
                workout_id = workout.get('workoutId')
                workout_name = workout.get('workoutName')
                if workout_id:
                    try:
                        details = self.garmin_client.get_workout(workout_id)
                        self._extract_exercise_mappings(details, workout_name)
                    except Exception as e:
                        logger.warning(f"Failed to get details for workout {workout_name}: {e}")
            
            logger.info(f"Learned {len(self.learned_mapping)} exercise mappings from existing workouts")
            
        except Exception as e:
            logger.warning(f"Failed to learn from existing workouts: {e}")
    
    def _extract_exercise_mappings(self, workout_details: dict, workout_name: str):
        """Extract exercise name and category mappings from workout details"""
        try:
            segments = workout_details.get('workoutSegments', [])
            for segment in segments:
                steps = segment.get('workoutSteps', [])
                self._extract_from_steps(steps, workout_name)
        except Exception as e:
            logger.warning(f"Failed to extract mappings from {workout_name}: {e}")
    
    def _extract_from_steps(self, steps: list, workout_name: str):
        """Recursively extract exercise mappings from workout steps"""
        for step in steps:
            if step.get('type') == 'RepeatGroupDTO':
                # Handle repeat group
                inner_steps = step.get('workoutSteps', [])
                self._extract_from_steps(inner_steps, workout_name)
            elif step.get('type') == 'ExecutableStepDTO':
                # Extract exercise info
                description = step.get('description', '')
                exercise_name = step.get('exerciseName')
                category = step.get('category')
                
                if description and exercise_name:
                    # Extract Chinese name from description (before \n)
                    chinese_name = description.split('\n')[0].strip()
                    if chinese_name and chinese_name != '':
                        self.learned_mapping[chinese_name] = {
                            'exerciseName': exercise_name,
                            'category': category,
                            'source': workout_name
                        }
                        logger.debug(f"Learned: {chinese_name} -> {exercise_name} (from {workout_name})")
    
    def _load_google_sheets_service(self, skip_oauth=False):
        """Load Google Sheets service with authentication (supports both service account and OAuth2)"""
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        
        if skip_oauth:
            logger.info("Skipping OAuth authentication")
            return None
        
        # Try OAuth2 user credentials first (for personal Google accounts)
        creds = None
        token_file = "google_sheets_token.json"
        credentials_file = "google_sheets_oauth_credentials.json"
        
        # 1. Try Loading from Environment Variable (Secure way for Cloud)
        env_token_json = os.getenv("GOOGLE_SHEETS_TOKEN_JSON")
        if env_token_json:
            try:
                token_info = json.loads(env_token_json)
                creds = Credentials.from_authorized_user_info(token_info, SCOPES)
                logger.info("Loaded Google Sheets credentials from environment variable")
            except Exception as e:
                logger.warning(f"Failed to load credentials from environment variable: {e}")

        # 2. The file google_sheets_token.json stores the user's access and refresh tokens
        if not creds and os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed Google OAuth2 credentials")
                except RefreshError as e:
                    logger.warning(f"Failed to refresh credentials: {e}")
                    creds = None
            
            if not creds:
                if os.path.exists(credentials_file):
                    # OAuth2 flow for user authentication
                    flow = Flow.from_client_secrets_file(credentials_file, SCOPES)
                    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'  # For desktop apps
                    
                    auth_url, _ = flow.authorization_url(prompt='consent')
                    
                    print(f"\n請開啟以下網址進行 Google 帳號認證：")
                    print(f"{auth_url}")
                    print(f"\n完成授權後，請複製授權碼並貼上：")
                    print(f"(如果遇到權限錯誤，請按 Ctrl+C 退出並將 Google Sheet 設為公開存取)")
                    
                    try:
                        auth_code = input("授權碼: ").strip()
                        
                        if not auth_code:
                            logger.warning("No authorization code provided")
                            return None
                            
                    except (KeyboardInterrupt, EOFError):
                        logger.info("User cancelled OAuth flow")
                        return None
                    
                    try:
                        if not auth_code:
                            logger.warning("No authorization code provided")
                            return None
                            
                        flow.fetch_token(code=auth_code)
                        creds = flow.credentials
                        
                        # Save the credentials for the next run
                        with open(token_file, 'w') as token:
                            token.write(creds.to_json())
                        
                        logger.info("Successfully authenticated with Google OAuth2")
                    except Exception as e:
                        logger.error(f"OAuth2 authentication failed: {e}")
                        return None
                else:
                    # Fallback to service account
                    creds = None
                    service_account_file = "google_sheets_credentials.json"
                    
                    # 1. Try Environment Variable for Service Account
                    env_sa_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
                    if env_sa_json:
                        try:
                            sa_info = json.loads(env_sa_json)
                            creds = service_account.Credentials.from_service_account_info(
                                sa_info, scopes=SCOPES
                            )
                            logger.info("Using Google Sheets API service account from Environment Variable")
                        except Exception as e:
                            logger.warning(f"Failed to load service account from environment: {e}")

                    # 2. Try Local File
                    if not creds and os.path.exists(service_account_file):
                        try:
                            creds = service_account.Credentials.from_service_account_file(
                                service_account_file, scopes=SCOPES
                            )
                            logger.info("Using Google Sheets API service account from local file")
                        except Exception as e:
                            logger.error(f"Failed to load service account from file: {e}")
                            return None
                    
                    if not creds:
                        logger.warning("No Google Sheets credentials found")
                        return None
        
        if creds:
            try:
                service = build('sheets', 'v4', credentials=creds)
                logger.info("Google Sheets API service loaded successfully")
                return service
            except Exception as e:
                logger.error(f"Failed to build Google Sheets service: {e}")
                return None
        
        return None
    
    def _read_google_sheet_with_api(self, spreadsheet_id: str, sheet_id: str = None, skip_oauth=False) -> tuple:
        """Read Google Sheet using API with authentication. Returns (DataFrame, sheet_name)"""
        service = self._load_google_sheets_service(skip_oauth=skip_oauth)
        if not service:
            raise Exception("Google Sheets API service not available. Please set up credentials.")
        
        try:
            # Get sheet name from sheet_id if provided
            range_name = "A:ZZ"  # Read all columns
            sheet_name = None
            if sheet_id:
                # Get sheet metadata to find sheet name by gid
                sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
                sheets = sheet_metadata.get('sheets', '')
                
                for sheet in sheets:
                    if str(sheet['properties']['sheetId']) == sheet_id:
                        sheet_name = sheet['properties']['title']
                        range_name = f"{sheet_name}!A:ZZ"
                        break
            
            # Call the Sheets API
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                logger.warning('No data found in Google Sheet.')
                return pd.DataFrame(), sheet_name
            
            # Convert to DataFrame
            df = pd.DataFrame(values)
            logger.info(f"Successfully read Google Sheet with {len(df)} rows from sheet '{sheet_name}'")
            return df, sheet_name
            
        except Exception as e:
            logger.error(f"Failed to read Google Sheet via API: {e}")
            raise e
    
    def _extract_spreadsheet_info(self, url: str) -> tuple:
        """Extract spreadsheet ID and sheet ID from Google Sheets URL"""
        import re
        
        # Extract spreadsheet ID
        spreadsheet_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        if not spreadsheet_match:
            raise ValueError("Invalid Google Sheets URL")
        
        spreadsheet_id = spreadsheet_match.group(1)
        
        # Extract sheet ID (gid)
        sheet_id = None
        gid_match = re.search(r'[#&]gid=([0-9]+)', url)
        if gid_match:
            sheet_id = gid_match.group(1)
        
        return spreadsheet_id, sheet_id
    
    def _find_best_exercise_match(self, exercise_name: str, threshold: float = 0.7) -> Optional[dict]:
        """Find the best matching exercise mapping from learned data or static mapping"""
        if not exercise_name:
            return None
            
        # First check learned mappings from existing workouts (highest priority)
        if exercise_name in self.learned_mapping:
            learned_info = self.learned_mapping[exercise_name]
            logger.debug(f"Using learned mapping: {exercise_name} -> {learned_info['exerciseName']} (category: {learned_info['category']}) from {learned_info['source']}")
            return {
                'exerciseName': learned_info['exerciseName'],
                'category': learned_info['category']
            }
            
        # Check for exact matches in static mapping (fallback to exerciseName only)
        if exercise_name in self.exercise_mapping:
            return {
                'exerciseName': self.exercise_mapping[exercise_name],
                'category': None
            }
            
        # Apply special mapping rules for common exercises
        special_match = self._apply_special_mapping_rules(exercise_name)
        if special_match:
            return {
                'exerciseName': special_match,
                'category': None
            }
            
        # Clean the exercise name for better matching
        cleaned_name = self._clean_exercise_name(exercise_name)
        
        best_match = None
        best_score = 0.0
        
        for mapped_name, exercise_key in self.exercise_mapping.items():
            # Calculate similarity using SequenceMatcher
            similarity1 = SequenceMatcher(None, cleaned_name, mapped_name).ratio()
            similarity2 = SequenceMatcher(None, exercise_name, mapped_name).ratio()
            similarity = max(similarity1, similarity2)
            
            # Check for exact substring matches
            if cleaned_name in mapped_name:
                similarity = max(similarity, 0.9)
            elif mapped_name in cleaned_name:
                similarity = max(similarity, 0.85)
                
            # Check for key word matching (more specific exercises preferred)
            key_words_match = self._calculate_keyword_similarity(cleaned_name, mapped_name)
            if key_words_match > 0.7:
                similarity = max(similarity, key_words_match)
                
            if similarity > best_score and similarity >= threshold:
                best_score = similarity
                best_match = exercise_key
                
        if best_match:
            logger.debug(f"Mapped '{exercise_name}' to '{best_match}' (score: {best_score:.2f})")
            
        return best_match
    
    def _apply_special_mapping_rules(self, exercise_name: str) -> Optional[str]:
        """Apply special mapping rules for common Chinese exercise names"""
        # Define special mappings for common exercises
        special_mappings = {
            '槓鈴深蹲': 'SQUAT_BARBELL_BACK_SQUAT',
            '槓鈴前蹲': 'SQUAT_BARBELL_FRONT_SQUAT', 
            '槓鈴後蹲': 'SQUAT_BARBELL_BACK_SQUAT',
            '槓鈴臥推': 'BENCH_PRESS_BARBELL_BENCH_PRESS',
            '槓鈴寬握臥推': 'BENCH_PRESS_BARBELL_BENCH_PRESS',
            '槓鈴窄握臥推': 'BENCH_PRESS_CLOSE_GRIP_BARBELL_BENCH_PRESS',
            '槓鈴硬舉': 'DEADLIFT_BARBELL_DEADLIFT',
            '槓鈴借力推': 'SHOULDER_PRESS_BARBELL_PUSH_PRESS',
            '啞鈴臥推': 'BENCH_PRESS_DUMBBELL_BENCH_PRESS',
            '啞鈴上斜臥推': 'BENCH_PRESS_INCLINE_DUMBBELL_BENCH_PRESS',
            '啞鈴下斜臥推': 'BENCH_PRESS_DECLINE_DUMBBELL_BENCH_PRESS',
            '啞鈴借力推': 'SHOULDER_PRESS_DUMBBELL_PUSH_PRESS',
            '三頭下拉': 'TRICEPS_EXTENSION_TRICEPS_PRESSDOWN',
            '三頭肌下拉': 'TRICEPS_EXTENSION_TRICEPS_PRESSDOWN',
            '滑輪下拉': 'PULL_UP_WIDE_GRIP_LAT_PULLDOWN',
            '寬握滑輪下拉': 'PULL_UP_WIDE_GRIP_LAT_PULLDOWN',
            '啞鈴划船': 'ROW_ONE_ARM_DUMBBELL_ROW',
            '啞鈴單臂划船': 'ROW_ONE_ARM_DUMBBELL_ROW',
            '啞鈴雙手划船': 'ROW_DUMBBELL_ROW',
            '機械式坐姿划船': 'ROW_SEATED_CABLE_ROW',
            '機械式側平舉': 'LATERAL_RAISE_CABLE_LATERAL_RAISE',
            '啞鈴側平舉': 'LATERAL_RAISE_DUMBBELL_LATERAL_RAISE',
            '機械式後飛鳥': 'FLY_CABLE_REAR_FLY',
            '啞鈴飛鳥': 'FLY_DUMBBELL_FLY'
        }
        
        # Check for exact match
        if exercise_name in special_mappings:
            logger.info(f"Special mapping: '{exercise_name}' -> '{special_mappings[exercise_name]}'")
            return special_mappings[exercise_name]
            
        # Check for partial matches
        for key, value in special_mappings.items():
            if key in exercise_name or exercise_name in key:
                logger.info(f"Partial special mapping: '{exercise_name}' -> '{value}'")
                return value
                
        return None
    
    def _clean_exercise_name(self, name: str) -> str:
        """Clean exercise name for better matching"""
        # Remove common English additions
        name = re.sub(r'\s*\([^)]*\)', '', name)  # Remove parentheses content
        name = re.sub(r'\s+push\s+press.*$', '', name, flags=re.IGNORECASE)  # Remove "push press" suffix
        name = re.sub(r'\s+press.*$', '', name, flags=re.IGNORECASE)  # Remove other "press" variations
        # Remove extra whitespace
        name = re.sub(r'\s+', '', name)
        return name.strip()
    
    def _calculate_keyword_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity based on key exercise words"""
        # Define important keywords
        keywords = ['槓鈴', '啞鈴', '深蹲', '臥推', '硬舉', '划船', '下拉', '推舉', '彎舉', '側平舉', '飛鳥', '機械']
        
        name1_keywords = [kw for kw in keywords if kw in name1]
        name2_keywords = [kw for kw in keywords if kw in name2]
        
        if not name1_keywords or not name2_keywords:
            return 0.0
            
        common_keywords = set(name1_keywords) & set(name2_keywords)
        total_keywords = set(name1_keywords) | set(name2_keywords)
        
        if total_keywords:
            return len(common_keywords) / len(total_keywords)
        return 0.0

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
        sheet_name = None
        try:
            if file_path.startswith("http") or file_path.endswith('.csv') or "format=csv" in file_path:
                # Try Google Sheets API first for Google Sheets URLs
                if "docs.google.com/spreadsheets" in original_path:
                    try:
                        spreadsheet_id, sheet_id = self._extract_spreadsheet_info(original_path)
                        logger.info(f"Attempting to read Google Sheet via API: {spreadsheet_id}")
                        df, sheet_name = self._read_google_sheet_with_api(spreadsheet_id, sheet_id)
                    except Exception as api_error:
                        logger.warning(f"Google Sheets API failed: {api_error}")
                        # Check if it's an OAuth error and try skipping OAuth
                        if "OAuth" in str(api_error) or "access_denied" in str(api_error) or "authorization" in str(api_error).lower():
                            logger.info("OAuth authentication failed, trying CSV export method directly")
                            try:
                                df = pd.read_csv(file_path, header=None)
                            except Exception as csv_error:
                                if "401" in str(csv_error) or "Unauthorized" in str(csv_error):
                                    logger.error("Google Sheets access denied. Please:")
                                    logger.error("1. Set up Google Sheets API credentials (google_sheets_credentials.json), OR")
                                    logger.error("2. Make the sheet publicly accessible:")
                                    logger.error("   - Open your Google Sheet")
                                    logger.error("   - Click 'Share' button")
                                    logger.error("   - Change access to 'Anyone with the link can view'")
                                    raise Exception(f"Google Sheets access denied: {csv_error}")
                                else:
                                    raise csv_error
                        else:
                            logger.info("Falling back to CSV export method")
                            try:
                                df = pd.read_csv(file_path, header=None)
                            except Exception as csv_error:
                                if "401" in str(csv_error) or "Unauthorized" in str(csv_error):
                                    logger.error("Google Sheets access denied. Please:")
                                    logger.error("1. Set up Google Sheets API credentials (google_sheets_credentials.json), OR")
                                    logger.error("2. Make the sheet publicly accessible:")
                                    logger.error("   - Open your Google Sheet")
                                    logger.error("   - Click 'Share' button")
                                    logger.error("   - Change access to 'Anyone with the link can view'")
                                    raise Exception(f"Google Sheets access denied: {csv_error}")
                                else:
                                    raise csv_error
                else:
                    # Regular CSV file or other HTTP URL
                    df = pd.read_csv(file_path, header=None)
            else:
                df = pd.read_excel(file_path, header=None)
        except Exception as e:
            logger.error(f"Failed to read file/url: {e}")
            raise e
            
        # Strategy: Iterate rows to find chunks
        # A chunk contains "Day1", "Day2", etc in any column
        # The header columns are in the same row as "DayX"
        
        workouts = []
        
        # Extract week info from sheet name or filename for workout naming
        import os
        filename = os.path.basename(original_path)
        # Prefer sheet name over filename for prefix
        week_info = sheet_name if sheet_name else self._extract_week_info(filename)
        
        # Check if this is W1 training
        self.is_w1_training = week_info == "W1"
        
        # Learn from existing W1_DayX workouts only if not W1 and client is provided
        if self.garmin_client and not self.is_w1_training:
            self._learn_from_existing_workouts()
        elif self.is_w1_training:
            logger.info("W1 training detected - skipping learning from existing workouts")
        
        # Pre-process dataframe to list of lists for easier handling
        rows = df.values.tolist()
        
        idx = 0
        while idx < len(rows):
            row = rows[idx]
            
            # Look for "DayX" pattern in any column
            day_found = None
            day_col_idx = -1
            
            for col_idx, cell in enumerate(row):
                cell_str = str(cell).strip() if pd.notna(cell) else ""
                # Match Day1, Day2, Day3 etc. (not "Day 1" with space) OR Day X format
                if re.match(r'^Day\d+$', cell_str) or cell_str.startswith("Day"):
                    day_found = cell_str
                    day_col_idx = col_idx
                    break
            
            if day_found:
                # Check if this "Day" block is what we want (if target_day specified)
                is_target = (target_day is None) or (target_day in day_found)
                
                # Generate workout name using filename week info for new format only
                if re.match(r'^Day\d+$', day_found):
                    workout_name = f"{week_info}_{day_found}" if week_info else day_found
                else:
                    # For old format, check for extended name in next row
                    next_row_idx = idx + 1
                    workout_name = day_found
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
                    logger.info(f"Found workout block: {workout_name} at row {idx}, col {day_col_idx}")
                    
                    # Use appropriate parsing method based on format
                    if re.match(r'^Day\d+$', day_found):  # New format: Day1, Day2, etc.
                        workout_dto, last_processed_idx = self._parse_block_new_format(rows, idx, day_col_idx, workout_name)
                    else:  # Old format: Day 1, Day 2, etc.
                        # For old format, use original logic
                        header_row_expected = idx + 1
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
                    idx += 1
            else:
                idx += 1

        if target_day:
            raise ValueError(f"Target day '{target_day}' not found in file.")
            
        return workouts

    def _extract_week_info(self, filename: str) -> str:
        """Extract week information from filename like 'xxx_W1.csv' -> 'W1'"""
        # Look for pattern like W1, W2, etc.
        match = re.search(r'W(\d+)', filename)
        if match:
            return f"W{match.group(1)}"
        return ""
    
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
            # Try "保留" first, fallback to "RPE" for old format
            try:
                col_rir = header.index("保留")
            except ValueError:
                col_rir = header.index("RPE")

        except ValueError as e:
            logger.warning(f"Header row missing required columns at line {header_row_idx}: {e}")
            logger.warning(f"Available headers: {header}")
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
                
            # Check if this is a cardio exercise (usually the last meaningful exercise)
            cardio_keywords = ["間歇", "有氧", "跑步", "單車", "游泳", "划船機"]
            is_cardio = any(keyword in exercise for keyword in cardio_keywords)
            
            # Process current exercise first, then decide whether to continue
            should_stop_after_this = is_cardio
                
            # Try to map exercise name to standard mapping
            exercise_mapping = self._find_best_exercise_match(exercise)
            if exercise_mapping:
                # Use learned mapping directly
                api_exercise_name = exercise_mapping['exerciseName']
                category = exercise_mapping['category']
                logger.info(f"Mapped exercise: '{exercise}' -> Category: '{category}', Name: '{api_exercise_name}'")
                display_exercise_name = exercise
            else:
                # Use original name for both API and display
                api_exercise_name = exercise
                display_exercise_name = exercise
                category = None
                
            # Parse Sets
            try:
                sets_val = int(float(str(row[col_sets]))) if pd.notna(row[col_sets]) else 1
            except:
                sets_val = 1
                
            # Parse Weight
            raw_weight = str(row[col_weight])
            weight_val = self.parse_weight(raw_weight)
            
            # Parse Reps (Raw String for display)
            raw_reps = str(row[col_reps]).strip()
            if raw_reps.lower() == "nan": raw_reps = ""
            if raw_reps.endswith(".0"): raw_reps = raw_reps[:-2]

            # Parse RIR
            rir_str = ""
            if col_rir != -1:
                val = str(row[col_rir]).strip()
                if val and val.lower() != "nan":
                    rir_str = val
            
            # Create Steps
            # Logic: Always use RepeatGroup if sets > 1 (Simplified per request)
            # Put details in description for self-evaluation
            
            # Format Description
            step_desc = f"{display_exercise_name}"
            details = []
            if weight_val > 0:
                details.append(f"重: {weight_val}kg")
            if raw_reps:
                details.append(f"次: {raw_reps}")
            if rir_str:
                details.append(f"保留: {rir_str}")
                
            if details:
                step_desc += "\n" + " | ".join(details)
            
            single_step = GarminExecutableStep(
                stepId=None,
                stepOrder=1, # Inside loop
                description=step_desc,
                exerciseName=api_exercise_name,  # Use mapped name for API
                category=category if not self.is_w1_training else None,  # Skip category for W1
                stepType=GarminStepType(stepTypeKey="interval", stepTypeId=3),
                endCondition=GarminEndCondition(conditionTypeKey="lap.button", conditionTypeId=1),
                endConditionValue=None,
                weightValue=weight_val if weight_val > 0 else None,
                weightUnit=GarminWeightUnit(unitKey="kilogram") if weight_val > 0 else None
            )
            
            if sets_val > 1:
                # Create RepeatGroup with rest step
                rest_step = self._create_rest_step(step_order=2, rest_seconds=90)
                repeat_group = GarminRepeatGroup(
                    stepOrder=len(steps) + 1,
                    numberOfIterations=sets_val,
                    workoutSteps=[single_step, rest_step],
                    smartRepeat=False
                )
                steps.append(repeat_group)
            else:
                # Single Step with rest
                single_step.stepOrder = len(steps) + 1
                steps.append(single_step)
                
                # Add rest step after each exercise
                rest_step = self._create_rest_step(step_order=len(steps) + 1, rest_seconds=90)
                steps.append(rest_step)
                
            curr_idx += 1
            
            # Stop parsing if this was a cardio exercise
            if should_stop_after_this:
                logger.info(f"Stopping parsing after cardio exercise: '{exercise}'")
                break
            
        # Construct DTO
        segment = GarminWorkoutSegment(segmentOrder=1, workoutSteps=steps)
        return GarminWorkoutDTO(workoutName=workout_name, workoutSegments=[segment]), curr_idx
    
    def _parse_block_new_format(self, all_rows: list, day_row_idx: int, day_col_idx: int, workout_name: str) -> tuple[Optional[GarminWorkoutDTO], int]:
        """Parse block using new format where Day1 is in a specific column and headers are in the same row"""
        # Returns (DTO, last_processed_row_index)
        
        if day_row_idx >= len(all_rows):
            return None, day_row_idx
            
        # The header is in the same row as DayX, starting from day_col_idx+1
        header_row = all_rows[day_row_idx]
        header = [str(x).strip() for x in header_row[day_col_idx+1:]]  # Skip DayX column and take the rest
        
        # Find required columns in the header
        try:
            col_exercise = header.index("動作") + day_col_idx + 1  # Adjust for original row position
            col_sets = header.index("組數") + day_col_idx + 1
            col_weight = header.index("重量") + day_col_idx + 1
            col_reps = header.index("次數") + day_col_idx + 1
            col_rir = header.index("保留") + day_col_idx + 1
        except ValueError as e:
            logger.warning(f"Header row missing required columns at line {day_row_idx}: {e}")
            logger.warning(f"Available headers: {header}")
            return None, day_row_idx
        
        # 2. Iterate data rows (starting from the row after DayX)
        steps = []
        curr_idx = day_row_idx + 1
        last_idx = curr_idx
        
        while curr_idx < len(all_rows):
            row = all_rows[curr_idx]
            last_idx = curr_idx
            
            # Check if we've reached the next Day block
            found_next_day = False
            for col_idx, cell in enumerate(row):
                cell_str = str(cell).strip() if pd.notna(cell) else ""
                if re.match(r'^Day\d+$', cell_str):
                    found_next_day = True
                    break
                    
            if found_next_day:
                break
            
            # Get exercise name
            exercise = ""
            if col_exercise < len(row):
                exercise = str(row[col_exercise]).strip() if pd.notna(row[col_exercise]) else ""
            
            # Skip empty exercises or instructions like "↑填日期"
            if not exercise or exercise.lower() == "nan" or "填日期" in exercise:
                curr_idx += 1
                continue
                
            # Check if this is a cardio exercise (usually the last meaningful exercise)
            cardio_keywords = ["間歇", "有氧", "跑步", "單車", "游泳", "划船機"]
            is_cardio = any(keyword in exercise for keyword in cardio_keywords)
            
            # Process current exercise first, then decide whether to continue
            should_stop_after_this = is_cardio
            
            # Try to map exercise name to standard mapping
            exercise_mapping = self._find_best_exercise_match(exercise)
            if exercise_mapping:
                # Use learned mapping directly
                api_exercise_name = exercise_mapping['exerciseName']
                category = exercise_mapping['category']
                logger.info(f"Mapped exercise: '{exercise}' -> Category: '{category}', Name: '{api_exercise_name}'")
                display_exercise_name = exercise
            else:
                # Use original name for both API and display
                api_exercise_name = exercise
                display_exercise_name = exercise
                category = None
            
            # Parse Sets
            try:
                sets_val = int(float(str(row[col_sets]))) if col_sets < len(row) and pd.notna(row[col_sets]) else 1
            except:
                sets_val = 1
                
            # Parse Weight
            raw_weight = ""
            if col_weight < len(row):
                raw_weight = str(row[col_weight])
            weight_val = self.parse_weight(raw_weight)
            
            # Parse Reps (Raw String for display)
            raw_reps = ""
            if col_reps < len(row):
                raw_reps = str(row[col_reps]).strip()
                if raw_reps.lower() == "nan": 
                    raw_reps = ""
                if raw_reps.endswith(".0"): 
                    raw_reps = raw_reps[:-2]

            # Parse RIR
            rir_str = ""
            if col_rir < len(row):
                val = str(row[col_rir]).strip()
                if val and val.lower() != "nan":
                    rir_str = val
            
            # Create Steps with same logic as original
            step_desc = f"{display_exercise_name}"
            details = []
            if weight_val > 0:
                details.append(f"重: {weight_val}kg")
            if raw_reps:
                details.append(f"次: {raw_reps}")
            if rir_str:
                details.append(f"保留: {rir_str}")
                
            if details:
                step_desc += "\n" + " | ".join(details)
            
            single_step = GarminExecutableStep(
                stepId=None,
                stepOrder=1, # Inside loop
                description=step_desc,
                exerciseName=api_exercise_name,  # Use mapped name for API
                category=category if not self.is_w1_training else None,  # Skip category for W1
                stepType=GarminStepType(stepTypeKey="interval", stepTypeId=3),
                endCondition=GarminEndCondition(conditionTypeKey="lap.button", conditionTypeId=1),
                endConditionValue=None,
                weightValue=weight_val if weight_val > 0 else None,
                weightUnit=GarminWeightUnit(unitKey="kilogram") if weight_val > 0 else None
            )
            
            if sets_val > 1:
                # Create RepeatGroup with rest step
                rest_step = self._create_rest_step(step_order=2, rest_seconds=90)
                repeat_group = GarminRepeatGroup(
                    stepOrder=len(steps) + 1,
                    numberOfIterations=sets_val,
                    workoutSteps=[single_step, rest_step],
                    smartRepeat=False
                )
                steps.append(repeat_group)
            else:
                # Single Step with rest
                single_step.stepOrder = len(steps) + 1
                steps.append(single_step)
                
                # Add rest step after each exercise
                rest_step = self._create_rest_step(step_order=len(steps) + 1, rest_seconds=90)
                steps.append(rest_step)
                
            curr_idx += 1
            
            # Stop parsing if this was a cardio exercise
            if should_stop_after_this:
                logger.info(f"Stopping parsing after cardio exercise: '{exercise}'")
                break
            
        # Construct DTO
        segment = GarminWorkoutSegment(segmentOrder=1, workoutSteps=steps)
        return GarminWorkoutDTO(workoutName=workout_name, workoutSegments=[segment]), curr_idx

    def parse_weight(self, value: str) -> float:
        """Parses weight string like '25+2.3', '18+2.3*2', or '自身'."""
        if not value or pd.isna(value) or value == "nan":
            return 0.0
        
        val_str = str(value).strip()
        
        if "自身" in val_str:
            return 0.0
        
        # Handle formulas - support basic arithmetic operations
        try:
            # Allow numbers, decimal points, and basic math operators
            if re.match(r'^[0-9\.\+\-\*\/\(\)\s]+$', val_str):
                result = float(eval(val_str))
                logger.debug(f"Calculated weight: {val_str} = {result}")
                return result
            return float(val_str)
        except Exception as e:
            logger.warning(f"Failed to parse weight '{val_str}': {e}")
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
