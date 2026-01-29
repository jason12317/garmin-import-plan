import garth
import os
import logging
import streamlit as st
from src.utils.session_manager import restore_session_from_json

logger = logging.getLogger(__name__)
SESSION_DIR = os.path.expanduser("~/.garth")

class GarminAuth:
    @staticmethod
    def ensure_login(email: str = None, password: str = None):
        """
        Attempts to resume a session from ~/.garth.
        Also attempts to restore session from Environment Variable (for Cloud).
        If that fails or session is missing, logs in with provided credentials.
        """
        # 0. Try to hijack login via Secrets (GARMIN_SESSION_JSON)
        # Check Streamlit secrets or Env var
        env_session = os.getenv("GARMIN_SESSION_JSON")
        if not env_session and hasattr(st, "secrets") and "GARMIN_SESSION_JSON" in st.secrets:
             env_session = st.secrets["GARMIN_SESSION_JSON"]

        if env_session:
             logger.info("Found GARMIN_SESSION_JSON in environment, restoring...")
             if restore_session_from_json(env_session):
                 logger.info("Session files restored from environment.")

        if os.path.exists(SESSION_DIR):
            try:
                garth.resume(SESSION_DIR)
                # Verify validation? garth usually checks expiry on resume
                logger.info("Resumed session from ~/.garth")
                return
            except Exception as e:
                logger.warning(f"Failed to resume session: {e}")

        if not email or not password:
            # Fallback to env vars if not provided
            email = email or os.getenv("GARMIN_EMAIL")
            password = password or os.getenv("GARMIN_PASSWORD")

        if not email or not password:
            raise ValueError("Credentials (email/password) not found in args or environment variables.")

        logger.info(f"Logging in as {email}...")
        garth.login(email, password)
        garth.save(SESSION_DIR)
        logger.info("Login successful/Saved session.")
