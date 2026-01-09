import garth
import os
import logging

logger = logging.getLogger(__name__)
SESSION_DIR = os.path.expanduser("~/.garth")

class GarminAuth:
    @staticmethod
    def ensure_login(email: str = None, password: str = None):
        """
        Attempts to resume a session from ~/.garth.
        If that fails or session is missing, logs in with provided credentials.
        """
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
