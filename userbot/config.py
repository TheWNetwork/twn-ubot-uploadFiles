# -*- encoding: utf-8 -*-
"""Config vars module"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    api_id = os.environ.get('API_ID')
    api_hash = os.environ.get('API_HASH')
    document_root = os.environ.get('DOCUMENT_ROOT')
    chat_id = os.environ.get('CHAT_ID')
    interval = int(os.environ.get('INTERVAL'))
    caption = os.environ.get('CAPTION')
    start_date = os.environ.get('START_DATE')
