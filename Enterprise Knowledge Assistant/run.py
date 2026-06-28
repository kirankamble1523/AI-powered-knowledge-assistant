import os
import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parent))

if __name__ == "__main__":
    print("--- Starting Enterprise Knowledge Assistant ---")
    print("API Endpoint: http://127.0.0.1:8000")
    print("Web Interface: http://127.0.0.1:8000/")
    print("Press Ctrl+C to stop.")
    print("-------------------------------------------------")
    
    # Run the FastAPI app with Uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
