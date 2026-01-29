import os
import json
import garth
import logging

logger = logging.getLogger(__name__)

SESSION_DIR = os.path.expanduser("~/.garth")

def get_session_json():
    """Reads the local ~/.garth directory and returns a JSON string of its content."""
    if not os.path.exists(SESSION_DIR):
        return None
    
    session_data = {}
    # garth usually stores files like 'oauth1_token', 'oauth2_token', 'scope' etc.
    try:
        for filename in os.listdir(SESSION_DIR):
            file_path = os.path.join(SESSION_DIR, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    session_data[filename] = f.read().strip()
        return json.dumps(session_data)
    except Exception as e:
        logger.error(f"Error packing session: {e}")
        return None

def restore_session_from_json(json_str):
    """Restores the session files to ~/.garth from a JSON string."""
    try:
        if not os.path.exists(SESSION_DIR):
            os.makedirs(SESSION_DIR, exist_ok=True)
            
        data = json.loads(json_str)
        for filename, content in data.items():
            # Security check: filename should be simple
            if '/' in filename or '\\' in filename or filename.startswith('.'):
                continue
                
            path = os.path.join(SESSION_DIR, filename)
            with open(path, 'w') as f:
                f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error restoring session: {e}")
        return False
