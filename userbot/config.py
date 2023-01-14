# -*- encoding: utf-8 -*-
"""Config vars module"""
import os
import dotenv

dotenv.load_dotenv()


def get_env(key, needed=False, default=None):
    """Get an env var or return exception."""
    if needed and key not in os.environ:
        raise Exception(f"{key} is not set in .env file")

    return os.environ.get(key) or default


api_id = get_env(key="API_ID", needed=True)
api_hash = get_env(key="API_HASH", needed=True)
document_root = get_env(key="DOCUMENT_ROOT")
chat_id = get_env(key="CHAT_ID")
interval = int(get_env(key="INTERVAL"))
caption = get_env(key="CAPTION")
start_date = get_env(key="START_DATE")
