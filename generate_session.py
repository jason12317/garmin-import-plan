import garth
import os
import json
import getpass
from src.utils.session_manager import get_session_json

def main():
    print("=== Garmin Session Exporter ===")
    print("This script will help you login to Garmin locally and generate a Session JSON string.")
    print("You can paste this string into Streamlit Secrets to bypass login on the cloud.")
    print("-" * 50)
    
    email = input("Enter Garmin Email: ").strip()
    password = getpass.getpass("Enter Garmin Password: ").strip()
    
    if not email or not password:
        print("Email and password are required.")
        return

    print("Logging in... (Check for MFA email code if asked)")
    try:
        garth.login(email, password)
        print("Login successful!")
        
        # Ensure session is saved
        garth.save(os.path.expanduser("~/.garth"))
        
        json_str = get_session_json()
        if json_str:
            print("\n" + "="*20 + " COPY BELOW " + "="*20)
            print(f"GARMIN_SESSION_JSON = '{json_str}'")
            print("="*20 + " COPY ABOVE " + "="*20)
            print("\nInstruction:")
            print("1. Copy the full line above.")
            print("2. Go to Streamlit Cloud -> App Settings -> Secrets.")
            print("3. Paste it there.")
        else:
            print("Failed to generate session JSON.")
            
    except Exception as e:
        print(f"Login failed: {e}")

if __name__ == "__main__":
    main()
