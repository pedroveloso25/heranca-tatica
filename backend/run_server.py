import sys
import os

# Garantir que o diretorio atual esta no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[0]}")

import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
