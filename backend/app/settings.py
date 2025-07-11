import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')  # Default to gemini now
HUGGINGFACE_DEFAULT_MODEL = os.getenv('HUGGINGFACE_DEFAULT_MODEL', 'HuggingFaceH4/zephyr-7b-beta')
CRITERIA_PATH = os.path.join(os.path.dirname(__file__), 'models/audit_criteria.json') 