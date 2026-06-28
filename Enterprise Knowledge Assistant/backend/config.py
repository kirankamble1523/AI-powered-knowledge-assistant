import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_STORE_DIR = BASE_DIR / "vector_store"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
VECTOR_STORE_DIR.mkdir(exist_ok=True)

# Try to extract keys from Desktop/API.txt if not in environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not OPENAI_API_KEY:
    desktop_api_path = Path("C:/Users/kiran Vishnu Kamble/Desktop/API.txt")
    if desktop_api_path.exists():
        try:
            with open(desktop_api_path, "r", encoding="utf-8") as f:
                content = f.read()
                new_key = None
                old_key = None
                for line in content.split("\n"):
                    if "NeW OPEN AI KEY :" in line:
                        new_key = line.split("NeW OPEN AI KEY :")[1].strip()
                    elif "OPEN AI KEY :" in line:
                        old_key = line.split("OPEN AI KEY :")[1].strip()
                    elif "gemini api key :" in line:
                        key = line.split("gemini api key :")[1].strip()
                        if key:
                            GEMINI_API_KEY = key
                
                OPENAI_API_KEY = new_key if new_key else old_key
        except Exception as e:
            print(f"Error reading API.txt: {e}")

# Set env variables so libraries can use them
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# Configuration Settings
DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", 800))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("DEFAULT_CHUNK_OVERLAP", 100))
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")  # Let's use gpt-4o-mini
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

print(f"[Config] Loaded API Keys. OpenAI API Key present: {bool(OPENAI_API_KEY)}, Gemini API Key present: {bool(GEMINI_API_KEY)}")
