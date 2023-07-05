from dotenv import load_dotenv

load_dotenv()

import os

DB_PATH = os.getenv("DB_PATH")
DATA_PATH = os.getenv("DATA_PATH")
