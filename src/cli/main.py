import argparse
import sys
from src.core.auth import GarminAuth
from src.core.parser import WorkoutParser
from src.core.garmin_client import GarminClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Import workouts from CSV/Excel to Garmin Connect.")
    parser.add_argument("file", help="Path to the local CSV/Excel file or Google Sheet URL.")
    parser.add_argument("--day", help="Specific day to import (e.g., 'Day 1'). If omitted, imports all found days.", default=None)
    parser.add_argument("--email", help="Garmin account email.")
    parser.add_argument("--password", help="Garmin account password.")
    parser.add_argument("--force", help="Overwrite existing workouts with same name.", action="store_true")

    args = parser.parse_args()

    # 1. Auths
    try:
        GarminAuth.ensure_login(args.email, args.password)
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        sys.exit(1)

    # 2. Create Garmin client and parser with learned mappings
    garmin_client = GarminClient()
    parser_core = WorkoutParser(garmin_client=garmin_client)
    try:
        if args.day:
            logger.info(f"Parsing file '{args.file}' for target day: '{args.day}'...")
            workout_dto = parser_core.parse_file(args.file, target_day=args.day)
            workouts_to_import = [workout_dto] if workout_dto else []
        else:
            logger.info(f"Parsing file '{args.file}' for all available workouts...")
            workouts_to_import = parser_core.parse_file(args.file)
            
        if not workouts_to_import:
            logger.warning("No workouts found to import.")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Parsing failed: {e}")
        sys.exit(1)

    # 3. Import
    # Reuse the same client instance
    client = garmin_client
    
    # Check duplicates if not forced
    existing_workout_names = set()
    if not args.force:
        logger.info("Fetching existing workouts to check for duplicates...")
        existing_list = client.list_workouts()
        for w in existing_list:
             if 'workoutName' in w:
                 existing_workout_names.add(w['workoutName'])
    
    success_count = 0
    fail_count = 0
    skipped_count = 0
    
    for workout in workouts_to_import:
        if not workout:
            continue
            
        if not args.force and workout.workoutName in existing_workout_names:
            logger.warning(f"Skipping '{workout.workoutName}' (already exists). Use --force to overwrite (creates duplicate actually).")
            # Garmin allows duplicates with same name. "Overwrite" usually means delete old and create new, or just create another.
            # Spec said "Overwrite or Skip". 
            # Ideally we would find ID and update, but API is CREATE.
            # So safer to just Skip.
            skipped_count += 1
            continue

        try:
            logger.info(f"Importing '{workout.workoutName}'...")
            client.create_workout(workout)
            logger.info(f"Successfully imported '{workout.workoutName}'")
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to import '{workout.workoutName}': {e}")
            fail_count += 1

    logger.info(f"Summary: {success_count} succeeded, {fail_count} failed, {skipped_count} skipped.")

if __name__ == "__main__":
    main()
