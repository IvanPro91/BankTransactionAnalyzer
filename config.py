from dotenv import load_dotenv
import os

load_dotenv()

ROOT_DIR = os.path.dirname(__file__)
FILE_EXCEL = os.path.join(ROOT_DIR, "data/operations.xlsx")
USER_SETTINGS = os.path.join(ROOT_DIR, "user_settings.json")
API_KEY = os.getenv("API_KEY")
API_KEY_STOCKS = os.getenv("API_KEY_STOCKS")
